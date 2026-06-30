"""
Ludo Game Core Module
Manages the complete Ludo game logic including turns, moves, and game state.
Handles the main game loop and player interactions.
"""

from typing import List, Dict, Optional, Tuple
import asyncio
import random
from datetime import datetime, timedelta
from .board import Board
from .dice import Dice, DiceHistory
from .player import Player, PlayerColor


class GameStatus:
    """
    Game status constants.
    Represents the current state of a game.
    """
    WAITING = "waiting"          # Waiting for players to join
    STARTING = "starting"        # About to start
    PLAYING = "playing"          # Game in progress
    FINISHED = "finished"        # Game completed
    CANCELLED = "cancelled"      # Game cancelled


class LudoGame:
    """
    Main Ludo game class managing all game logic.
    Handles players, turns, dice rolling, token movement, and game state.
    """
    
    def __init__(self, game_id: str):
        """
        Initialize a new Ludo game.
        
        Args:
            game_id: Unique identifier for this game
        """
        # Game identification
        self.game_id = game_id
        
        # Game components
        self.board = Board()                    # Game board
        self.dice = Dice()                      # Dice for rolling
        self.dice_history = DiceHistory()       # Track dice rolls
        
        # Game state
        self.status = GameStatus.WAITING        # Current game status
        self.players: List[Player] = []         # List of players
        self.current_player_index = 0           # Index of current player
        
        # Timestamps
        self.created_at = datetime.now()        # Game creation time
        self.last_activity = datetime.now()     # Last activity time
        
        # Timeouts (in seconds)
        self.turn_timeout = 60                  # Max time per turn
        self.waiting_timeout = 120              # Max wait for players
        
        # Anonymous mode
        self.anonymous_mode = False             # Hide player identities
        self.chat_id = None                     # Associated chat ID
        self.message_id = None                  # Associated message ID
    
    def is_expired(self) -> bool:
        """
        Check if the game has expired due to inactivity.
        
        Returns:
            bool: True if the game has expired
        """
        if self.status == GameStatus.WAITING:
            # Waiting games expire after waiting_timeout seconds
            return (datetime.now() - self.last_activity) > timedelta(seconds=self.waiting_timeout)
        elif self.status == GameStatus.PLAYING:
            # Active games expire after 5 turns timeout
            return (datetime.now() - self.last_activity) > timedelta(seconds=self.turn_timeout * 5)
        elif self.status == GameStatus.FINISHED:
            # Finished games expire after 1 hour
            return (datetime.now() - self.last_activity) > timedelta(seconds=3600)
        return False
    
    def add_player(self, user_id: int, username: str) -> Tuple[bool, Optional[Player]]:
        """
        Add a player to the game.
        
        Args:
            user_id: Telegram user ID
            username: Player's display name
            
        Returns:
            Tuple[bool, Optional[Player]]: (success, player_object)
        """
        # Check if game is still waiting for players
        if self.status != GameStatus.WAITING:
            return False, None
        
        # Check maximum players (4)
        if len(self.players) >= 4:
            return False, None
        
        # Check for duplicate player
        if any(p.user_id == user_id for p in self.players):
            return False, None
        
        # Assign available color
        used_colors = [p.color for p in self.players]
        available_colors = [c for c in PlayerColor.get_colors() if c not in used_colors]
        
        if not available_colors:
            return False, None
        
        color = available_colors[0]
        
        # Create and add player
        player = Player(user_id=user_id, username=username, color=color)
        self.players.append(player)
        self.board.add_player(player)
        self.last_activity = datetime.now()
        
        return True, player
    
    def remove_player(self, user_id: int) -> bool:
        """
        Remove a player from the game.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if player was removed successfully
        """
        player = self.get_player(user_id)
        if not player:
            return False
        
        # Remove from player list and board
        self.players.remove(player)
        del self.board.players[player.color]
        
        # Cancel game if not enough players
        if len(self.players) < 2 and self.status == GameStatus.PLAYING:
            self.status = GameStatus.CANCELLED
        
        return True
    
    def get_player(self, user_id: int) -> Optional[Player]:
        """
        Get a player by user ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Optional[Player]: Player object or None
        """
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None
    
    def start_game(self) -> bool:
        """
        Start the game.
        
        Returns:
            bool: True if game started successfully
        """
        # Need at least 2 players
        if len(self.players) < 2:
            return False
        
        # Must be in waiting state
        if self.status != GameStatus.WAITING:
            return False
        
        # Start the game
        self.status = GameStatus.PLAYING
        self.current_player_index = random.randint(0, len(self.players) - 1)
        self.players[self.current_player_index].current_turn = True
        self.last_activity = datetime.now()
        
        return True
    
    async def roll_dice(self, user_id: int) -> Tuple[bool, Dict]:
        """
        Roll the dice for a player.
        
        Args:
            user_id: Telegram user ID of the player
            
        Returns:
            Tuple[bool, Dict]: (success, result_data)
        """
        # Validate player
        player = self.get_player(user_id)
        if not player:
            return False, {"error": "Player not found"}
        
        # Validate game state
        if self.status != GameStatus.PLAYING:
            return False, {"error": "Game is not in progress"}
        
        # Validate turn
        if not player.current_turn:
            return False, {"error": "Not your turn"}
        
        # Roll the dice
        dice_value = self.dice.roll()
        self.dice_history.add_roll(dice_value)
        
        # Check if any tokens can move
        active_tokens = player.get_active_tokens()
        can_move = False
        
        for token in active_tokens:
            if token.can_move(dice_value):
                can_move = True
                break
        
        # Special case: if rolled 6 and have tokens at home
        if dice_value == 6 and not can_move:
            home_tokens = [t for t in player.tokens if t.status.value == "home"]
            if home_tokens:
                can_move = True
        
        # If can't move and not a six, end turn
        if not can_move and dice_value != 6:
            self.next_turn()
        
        # Prepare result
        result = {
            "dice_value": dice_value,
            "can_move": can_move,
            "is_six": dice_value == 6,
            "player": player.get_username_display(),
            "consecutive_sixes": self.dice.consecutive_sixes
        }
        
        self.last_activity = datetime.now()
        return True, result
    
    async def move_token(self, user_id: int, token_id: int) -> Tuple[bool, Dict]:
        """
        Move a specific token for a player.
        
        Args:
            user_id: Telegram user ID
            token_id: ID of the token to move
            
        Returns:
            Tuple[bool, Dict]: (success, result_data)
        """
        # Validate player
        player = self.get_player(user_id)
        if not player:
            return False, {"error": "Player not found"}
        
        # Validate game state
        if self.status != GameStatus.PLAYING:
            return False, {"error": "Game is not in progress"}
        
        # Validate turn
        if not player.current_turn:
            return False, {"error": "Not your turn"}
        
        # Find the token
        token = next((t for t in player.tokens if t.id == token_id), None)
        if not token:
            return False, {"error": "Token not found"}
        
        # Move the token
        steps = self.dice.current_value
        eaten_token = self.board.move_token(token, steps)
        
        # Prepare result
        result = {
            "token_id": token_id,
            "new_position": token.position,
            "status": token.status.value,
            "eaten": eaten_token is not None,
            "player": player.get_username_display()
        }
        
        # Check for winner
        winner = self.board.get_winner()
        if winner:
            self.status = GameStatus.FINISHED
            result["winner"] = winner.get_username_display()
        
        # Check for extra turn (rolled a 6)
        if self.dice.current_value == 6 and not winner:
            if self.dice.consecutive_sixes < 3:
                result["continue_turn"] = True
                return True, result
        
        # Move to next turn
        self.next_turn()
        return True, result
    
    def next_turn(self):
        """
        Move to the next player's turn.
        Skips players who have already won.
        """
        if self.status != GameStatus.PLAYING:
            return
        
        # End current player's turn
        if self.players:
            self.players[self.current_player_index].current_turn = False
        
        # Find next player who hasn't won
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        attempts = 0
        while self.players[self.current_player_index].has_won() and attempts < len(self.players):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            attempts += 1
        
        # Set new current player
        self.players[self.current_player_index].current_turn = True
        self.dice.reset()
        self.last_activity = datetime.now()
    
    def get_game_state(self) -> Dict:
        """
        Get the complete game state for display or storage.
        
        Returns:
            Dict: Complete game state
        """
        board_state = self.board.get_board_state()
        
        return {
            "game_id": self.game_id,
            "status": self.status,
            "players_count": len(self.players),
            "current_turn": self.players[self.current_player_index].get_username_display() if self.players else None,
            "dice_value": self.dice.current_value,
            "dice_history": self.dice_history.get_last_rolls(),
            "board": board_state,
            "created_at": self.created_at.isoformat(),
            "is_anonymous": self.anonymous_mode
        }
    
    def get_player_turn_order(self) -> List[str]:
        """
        Get the turn order of all players.
        
        Returns:
            List[str]: Player names in turn order
        """
        order = []
        for i in range(len(self.players)):
            idx = (self.current_player_index + i) % len(self.players)
            order.append(self.players[idx].get_username_display())
        return order
    
    def is_full(self) -> bool:
        """
        Check if the game has reached maximum players.
        
        Returns:
            bool: True if game is full (4 players)
        """
        return len(self.players) >= 4
    
    def can_start(self) -> bool:
        """
        Check if the game can be started.
        
        Returns:
            bool: True if game can start
        """
        return len(self.players) >= 2 and self.status == GameStatus.WAITING