"""
Player Module
Defines the Player and Token classes with their properties and methods.
Handles player colors, token status, movement logic, and display names.
"""

from typing import List, Optional, Dict
from enum import Enum
from dataclasses import dataclass, field


class PlayerColor(Enum):
    """
    Player color options with emoji representations.
    Each player gets a unique color when joining the game.
    """
    RED = "🔴"
    GREEN = "🟢"
    BLUE = "🔵"
    YELLOW = "🟡"
    
    @classmethod
    def get_colors(cls) -> List['PlayerColor']:
        """
        Get all available player colors.
        
        Returns:
            List[PlayerColor]: List of all color options
        """
        return [cls.RED, cls.GREEN, cls.BLUE, cls.YELLOW]
    
    @classmethod
    def get_color_by_index(cls, index: int) -> Optional['PlayerColor']:
        """
        Get a color by its index.
        
        Args:
            index: Index in the colors list (0-3)
            
        Returns:
            Optional[PlayerColor]: Color at the given index
        """
        colors = cls.get_colors()
        if 0 <= index < len(colors):
            return colors[index]
        return None


class TokenStatus(Enum):
    """
    Token status states.
    Represents where a token is on the board.
    """
    HOME = "home"          # Token is at home, not yet in play
    PLAYING = "playing"    # Token is on the board
    FINISHED = "finished"  # Token has reached the finish line


@dataclass
class Token:
    """
    Represents a game token (piece) for a player.
    Each player has 4 tokens of their color.
    """
    id: int                                    # Token ID (0-3)
    color: PlayerColor                         # Player's color
    position: int = -1                         # -1 = home, 0-51 = board, 52+ = finish
    status: TokenStatus = TokenStatus.HOME     # Current status
    is_safe: bool = False                      # True if on safe position
    
    def move(self, steps: int, board_size: int = 52):
        """
        Move the token on the board.
        
        Args:
            steps: Number of steps to move
            board_size: Size of the board (default 52)
        """
        # Token at home can only leave with a 6
        if self.status == TokenStatus.HOME:
            if steps == 6:  # Must roll a 6 to exit home
                self.position = 0
                self.status = TokenStatus.PLAYING
            return
        
        # Token in play moves forward
        if self.status == TokenStatus.PLAYING:
            new_pos = self.position + steps
            
            # Check if token reaches or passes finish line
            if new_pos >= board_size + 4:  # +4 is for the finish lane
                self.status = TokenStatus.FINISHED
                self.position = board_size + 4
            else:
                self.position = new_pos
    
    def can_move(self, steps: int) -> bool:
        """
        Check if the token can move the given number of steps.
        
        Args:
            steps: Number of steps to check
            
        Returns:
            bool: True if the token can move
        """
        # Token that already finished cannot move
        if self.status == TokenStatus.FINISHED:
            return False
        
        # Token at home can only move with a 6
        if self.status == TokenStatus.HOME:
            return steps == 6
        
        # Token in play can move as long as it doesn't exceed max position
        return (self.position + steps) <= 56  # Maximum board position
    
    def reset(self):
        """
        Reset token to home position.
        Used when token is eaten by an opponent.
        """
        self.position = -1
        self.status = TokenStatus.HOME
        self.is_safe = False
    
    def is_at_home(self) -> bool:
        """
        Check if token is at home.
        
        Returns:
            bool: True if token is at home
        """
        return self.status == TokenStatus.HOME
    
    def is_playing(self) -> bool:
        """
        Check if token is on the board.
        
        Returns:
            bool: True if token is in play
        """
        return self.status == TokenStatus.PLAYING
    
    def is_finished(self) -> bool:
        """
        Check if token has finished.
        
        Returns:
            bool: True if token has reached finish
        """
        return self.status == TokenStatus.FINISHED


@dataclass
class Player:
    """
    Represents a player in the game.
    Contains player data and their 4 tokens.
    """
    # Player identification
    user_id: int                      # Telegram user ID
    username: str                     # Display name
    
    # Game data
    color: PlayerColor                # Assigned color
    tokens: List[Token] = field(default_factory=list)  # 4 tokens
    
    # Player status
    is_ready: bool = False            # Ready to start game
    is_anonymous: bool = False        # Hide identity
    current_turn: bool = False        # Current turn flag
    
    # Statistics
    score: int = 0                    # Total score
    wins: int = 0                     # Number of wins
    losses: int = 0                   # Number of losses
    
    def __post_init__(self):
        """
        Initialize tokens if not provided.
        Creates 4 tokens of the player's color.
        """
        if not self.tokens:
            self.tokens = [Token(i, self.color) for i in range(4)]
    
    def get_active_tokens(self) -> List[Token]:
        """
        Get tokens that are currently on the board.
        
        Returns:
            List[Token]: Active tokens
        """
        return [t for t in self.tokens if t.status == TokenStatus.PLAYING]
    
    def get_finished_tokens(self) -> List[Token]:
        """
        Get tokens that have reached the finish line.
        
        Returns:
            List[Token]: Finished tokens
        """
        return [t for t in self.tokens if t.status == TokenStatus.FINISHED]
    
    def get_home_tokens(self) -> List[Token]:
        """
        Get tokens that are still at home.
        
        Returns:
            List[Token]: Home tokens
        """
        return [t for t in self.tokens if t.status == TokenStatus.HOME]
    
    def has_won(self) -> bool:
        """
        Check if the player has won the game.
        
        Returns:
            bool: True if all 4 tokens have finished
        """
        return len(self.get_finished_tokens()) == 4
    
    def get_username_display(self) -> str:
        """
        Get the display name, respecting anonymous mode.
        
        Returns:
            str: Display name
        """
        if self.is_anonymous:
            return f"Player #{self.user_id % 10000}"
        return self.username or f"Player {self.user_id}"
    
    def get_token_count(self) -> int:
        """
        Get total number of tokens (always 4).
        
        Returns:
            int: Total tokens
        """
        return len(self.tokens)
    
    def get_progress(self) -> int:
        """
        Get player's progress as a percentage.
        
        Returns:
            int: Progress percentage (0-100)
        """
        finished = len(self.get_finished_tokens())
        return (finished / 4) * 100
    
    def reset_tokens(self):
        """
        Reset all tokens to home position.
        Used when restarting a game.
        """
        for token in self.tokens:
            token.reset()
    
    def get_token_by_id(self, token_id: int) -> Optional[Token]:
        """
        Get a token by its ID.
        
        Args:
            token_id: Token ID (0-3)
            
        Returns:
            Optional[Token]: Token object or None
        """
        for token in self.tokens:
            if token.id == token_id:
                return token
        return None
    
    def add_score(self, points: int):
        """
        Add points to the player's score.
        
        Args:
            points: Points to add
        """
        self.score += points
    
    def add_win(self):
        """
        Increment win count.
        """
        self.wins += 1
    
    def add_loss(self):
        """
        Increment loss count.
        """
        self.losses += 1
    
    def to_dict(self) -> Dict:
        """
        Convert player to dictionary for serialization.
        
        Returns:
            Dict: Player data as dictionary
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "color": self.color.value,
            "is_anonymous": self.is_anonymous,
            "score": self.score,
            "wins": self.wins,
            "losses": self.losses,
            "tokens": [{
                "id": t.id,
                "position": t.position,
                "status": t.status.value,
                "is_safe": t.is_safe
            } for t in self.tokens]
        }