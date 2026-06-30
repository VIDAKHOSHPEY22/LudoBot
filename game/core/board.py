"""
Board Module
Represents the Ludo game board with all its positions and mechanics.
Handles token movement, collision detection, and safe positions.
"""

from typing import List, Dict, Optional, Tuple
from .player import Player, Token, PlayerColor, TokenStatus


class Board:
    """
    Ludo game board with 52 positions, safe spots, and token management.
    Handles all board-level game logic including movement and collisions.
    """
    
    def __init__(self):
        """
        Initialize the game board.
        - Board has 52 standard positions (0-51)
        - Safe positions protect tokens from being eaten
        - Players and tokens are tracked in dictionaries
        """
        # Board size in standard Ludo (52 positions around the board)
        self.size = 52
        
        # Safe positions where tokens cannot be eaten
        # These are star positions on the board
        self.safe_positions = [0, 8, 13, 21, 26, 34, 39, 47]
        
        # Players mapped by their color
        self.players: Dict[PlayerColor, Player] = {}
        
        # Token positions map: position -> {token_id: token}
        # Used for fast collision detection
        self.token_positions: Dict[int, Dict[int, Token]] = {}
    
    def add_player(self, player: Player):
        """
        Add a player to the board.
        
        Args:
            player: Player object to add
        """
        self.players[player.color] = player
        self._update_token_map()
    
    def _update_token_map(self):
        """
        Update the token position map for fast lookups.
        Only tracks tokens that are currently on the board (PLAYING status).
        """
        self.token_positions.clear()
        for player in self.players.values():
            for token in player.tokens:
                if token.status == TokenStatus.PLAYING:
                    if token.position not in self.token_positions:
                        self.token_positions[token.position] = {}
                    self.token_positions[token.position][token.id] = token
    
    def get_token_at(self, position: int) -> List[Token]:
        """
        Get all tokens at a specific position on the board.
        
        Args:
            position: Board position (0-51)
            
        Returns:
            List[Token]: List of tokens at the position
        """
        if position in self.token_positions:
            return list(self.token_positions[position].values())
        return []
    
    def is_safe(self, position: int) -> bool:
        """
        Check if a position is safe (protected from being eaten).
        
        Args:
            position: Board position to check
            
        Returns:
            bool: True if position is safe
        """
        return position in self.safe_positions
    
    def can_move_to(self, token: Token, steps: int) -> bool:
        """
        Check if a token can move to a new position.
        
        Args:
            token: Token to move
            steps: Number of steps to move
            
        Returns:
            bool: True if the move is valid
        """
        # Check if token can physically move this many steps
        if not token.can_move(steps):
            return False
        
        # Tokens at home can only move out with a 6
        if token.status == TokenStatus.HOME:
            return steps == 6
        
        # Calculate new position
        new_pos = token.position + steps
        
        # Check if new position is beyond the finish line
        if new_pos > self.size + 4:
            return False
        
        # Check for collisions with opponent tokens (except on safe positions)
        if not self.is_safe(new_pos):
            opponents = self.get_token_at(new_pos)
            for opp_token in opponents:
                if opp_token.color != token.color:
                    return True  # Can eat opponent's token
        
        return True
    
    def move_token(self, token: Token, steps: int) -> Optional[Token]:
        """
        Move a token and handle any collisions.
        
        Args:
            token: Token to move
            steps: Number of steps to move
            
        Returns:
            Optional[Token]: Eaten opponent token, or None if no collision
        """
        # Validate the move
        if not self.can_move_to(token, steps):
            return None
        
        # Move the token
        old_pos = token.position
        token.move(steps, self.size)
        
        # Check for collisions with opponent tokens
        if token.status == TokenStatus.PLAYING:
            opponents = self.get_token_at(token.position)
            for opp_token in opponents:
                # If opponent token is on the same position and not on a safe spot
                if opp_token.color != token.color and not self.is_safe(token.position):
                    # Send opponent token back home
                    opp_token.status = TokenStatus.HOME
                    opp_token.position = -1
                    self._update_token_map()
                    return opp_token
        
        # Update token map and return
        self._update_token_map()
        return None
    
    def get_winner(self) -> Optional[Player]:
        """
        Check if any player has won the game.
        
        Returns:
            Optional[Player]: Winner player or None if no winner
        """
        for player in self.players.values():
            if player.has_won():  # All 4 tokens finished
                return player
        return None
    
    def get_board_state(self) -> Dict:
        """
        Get the complete board state for display or storage.
        
        Returns:
            Dict: Board state with players, tokens, and positions
        """
        state = {
            "players": [],
            "positions": {}
        }
        
        # Gather all player data
        for color, player in self.players.items():
            player_data = {
                "color": color.value,
                "username": player.get_username_display(),
                "tokens": [],
                "finished": len(player.get_finished_tokens()),
                "score": player.score
            }
            
            # Gather token data for this player
            for token in player.tokens:
                token_data = {
                    "id": token.id,
                    "position": token.position,
                    "status": token.status.value,
                    "is_safe": self.is_safe(token.position) if token.status == TokenStatus.PLAYING else False
                }
                player_data["tokens"].append(token_data)
            
            state["players"].append(player_data)
        
        return state
    
    def get_token_count_at_position(self, position: int) -> int:
        """
        Get the number of tokens at a specific position.
        
        Args:
            position: Board position
            
        Returns:
            int: Number of tokens at the position
        """
        return len(self.get_token_at(position))
    
    def get_player_at_position(self, position: int) -> Optional[PlayerColor]:
        """
        Get the player color of the first token at a position.
        
        Args:
            position: Board position
            
        Returns:
            Optional[PlayerColor]: Player color or None if position is empty
        """
        tokens = self.get_token_at(position)
        if tokens:
            return tokens[0].color
        return None
    
    def is_position_blocked(self, position: int, player_color: PlayerColor) -> bool:
        """
        Check if a position is blocked by an opponent's token.
        
        Args:
            position: Board position
            player_color: Player color to check against
            
        Returns:
            bool: True if position is blocked by opponent
        """
        tokens = self.get_token_at(position)
        for token in tokens:
            if token.color != player_color and not self.is_safe(position):
                return True
        return False
    
    def clear_board(self):
        """
        Reset the board to initial state.
        Removes all tokens from the board.
        """
        self.token_positions.clear()
        for player in self.players.values():
            for token in player.tokens:
                token.status = TokenStatus.HOME
                token.position = -1
        self._update_token_map()