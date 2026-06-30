"""
Dice Module
Handles dice rolling mechanics and history tracking for the Ludo game.
Includes special rules for consecutive sixes and dice history.
"""

import random
from typing import List, Optional


class Dice:
    """
    Dice class with Ludo-specific rules.
    Tracks current value and consecutive sixes for special gameplay.
    """
    
    def __init__(self):
        """
        Initialize the dice.
        - Starts with no value (0)
        - Tracks consecutive sixes for bonus turns
        - Maximum 3 consecutive sixes allowed
        """
        self.current_value = 0
        self.consecutive_sixes = 0
        self.max_consecutive_sixes = 3  # Standard Ludo rule
    
    def roll(self) -> int:
        """
        Roll the dice and return the result.
        
        Rules:
        - Random value between 1 and 6
        - Track consecutive sixes for bonus turns
        - Reset consecutive sixes on non-six rolls
        
        Returns:
            int: Dice value (1-6)
        """
        # Generate random dice value
        self.current_value = random.randint(1, 6)
        
        # Track consecutive sixes
        if self.current_value == 6:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0
        
        return self.current_value
    
    def can_continue(self) -> bool:
        """
        Check if the player gets another turn.
        
        Ludo rules:
        - Rolling a 6 gives another turn
        - Maximum 3 consecutive sixes allowed
        
        Returns:
            bool: True if player can continue rolling
        """
        return (self.current_value == 6 and 
                self.consecutive_sixes <= self.max_consecutive_sixes)
    
    def is_six(self) -> bool:
        """
        Check if the current roll is a six.
        
        Returns:
            bool: True if current value is 6
        """
        return self.current_value == 6
    
    def get_value(self) -> int:
        """
        Get the current dice value.
        
        Returns:
            int: Current dice value (0 if not rolled yet)
        """
        return self.current_value
    
    def reset(self):
        """
        Reset the dice to initial state.
        Used when a player's turn ends.
        """
        self.current_value = 0
        self.consecutive_sixes = 0
    
    def get_consecutive_sixes(self) -> int:
        """
        Get the count of consecutive sixes rolled.
        
        Returns:
            int: Number of consecutive sixes
        """
        return self.consecutive_sixes
    
    def has_max_sixes(self) -> bool:
        """
        Check if maximum consecutive sixes have been reached.
        
        Returns:
            bool: True if at max consecutive sixes
        """
        return self.consecutive_sixes >= self.max_consecutive_sixes


class DiceHistory:
    """
    Tracks dice roll history for display and statistics.
    Maintains a rolling window of recent rolls.
    """
    
    def __init__(self):
        """
        Initialize dice history.
        - Maximum 10 rolls stored by default
        - History starts empty
        """
        self.history: List[int] = []
        self.max_history = 10
    
    def add_roll(self, value: int):
        """
        Add a new roll to the history.
        
        Args:
            value: Dice value to add (1-6)
        """
        self.history.append(value)
        
        # Maintain maximum history size
        if len(self.history) > self.max_history:
            self.history.pop(0)  # Remove oldest
    
    def get_last_rolls(self, count: int = 3) -> List[int]:
        """
        Get the most recent rolls.
        
        Args:
            count: Number of recent rolls to return (default: 3)
            
        Returns:
            List[int]: List of recent dice values
        """
        if count <= 0:
            return []
        
        # Return up to 'count' rolls from the end
        return self.history[-count:]
    
    def get_all_rolls(self) -> List[int]:
        """
        Get the complete roll history.
        
        Returns:
            List[int]: All stored dice values
        """
        return self.history.copy()  # Return copy to prevent modification
    
    def clear(self):
        """
        Clear the roll history.
        """
        self.history.clear()
    
    def get_average(self) -> float:
        """
        Calculate the average of all rolls.
        
        Returns:
            float: Average roll value (0 if no rolls)
        """
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)
    
    def get_six_count(self) -> int:
        """
        Count how many sixes have been rolled.
        
        Returns:
            int: Number of sixes in history
        """
        return self.history.count(6)
    
    def get_roll_count(self) -> int:
        """
        Get total number of rolls in history.
        
        Returns:
            int: Total rolls tracked
        """
        return len(self.history)
    
    def get_summary(self) -> dict:
        """
        Get a summary of the dice history.
        
        Returns:
            dict: Summary statistics
        """
        if not self.history:
            return {
                "total": 0,
                "average": 0.0,
                "sixes": 0,
                "max": 0,
                "min": 0
            }
        
        return {
            "total": len(self.history),
            "average": sum(self.history) / len(self.history),
            "sixes": self.history.count(6),
            "max": max(self.history),
            "min": min(self.history)
        }