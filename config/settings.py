"""
Configuration Settings Module
Loads environment variables and provides configuration settings for the bot.
All sensitive data is loaded from .env file with fallback defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Central configuration class for the Ludo bot.
    All settings are loaded from environment variables with sensible defaults.
    """
    
    # === BOT CONFIGURATION ===
    # Telegram Bot Token - Get from @BotFather
    # Format: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your token")
    
    # Owner/Admin User ID - For admin commands and monitoring
    # Can be found using @userinfobot
    OWNER_ID = int(os.getenv("OWNER_ID", "your owner id"))
    
    # === DATABASE CONFIGURATION ===
    # SQLite database file path
    # Can be changed to PostgreSQL: postgresql://user:pass@localhost/dbname
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ludo.db")
    
    # === SECURITY CONFIGURATION ===
    # Secret key for JWT tokens and session encryption
    SECRET_KEY = os.getenv("SECRET_KEY", "your secret")
    
    # === GAME CONFIGURATION ===
    # Maximum number of players per game
    MAX_PLAYERS = 4
    
    # Minimum players required to start a game
    MIN_PLAYERS = 2
    
    # Maximum value on the dice (standard Ludo uses 6)
    DICE_MAX = 6
    
    # Size of the game board (52 positions in standard Ludo)
    BOARD_SIZE = 52
    
    # Number of tokens per player (4 in standard Ludo)
    TOKEN_COUNT = 4
    
    # === TIMEOUT CONFIGURATIONS ===
    # Time (in seconds) allowed for a player's turn before auto-pass
    TURN_TIMEOUT = 60
    
    # Time (in seconds) to wait for players before game expires
    WAITING_TIMEOUT = 120
    
    # === TELEGRAM CONFIGURATION ===
    # API base URL (can be changed for proxy or testing)
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.telegram.org/bot")
    
    # === REDIS CONFIGURATION (Optional) ===
    # Redis URL for caching and session management
    # Uncomment to enable Redis
    # REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # === LOGGING CONFIGURATION ===
    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Log file path (optional)
    # LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")


# Create a singleton instance for easy importing
settings = Settings()


# === HELPER FUNCTIONS ===
def get_settings_dict() -> dict:
    """
    Get all settings as a dictionary (for debugging and monitoring).
    Sensitive values are masked.
    
    Returns:
        dict: Dictionary of all settings with sensitive values masked
    """
    settings_dict = {
        'BOT_TOKEN': '***MASKED***' if settings.BOT_TOKEN else None,
        'OWNER_ID': settings.OWNER_ID,
        'DATABASE_URL': settings.DATABASE_URL,
        'SECRET_KEY': '***MASKED***' if settings.SECRET_KEY else None,
        'MAX_PLAYERS': settings.MAX_PLAYERS,
        'MIN_PLAYERS': settings.MIN_PLAYERS,
        'DICE_MAX': settings.DICE_MAX,
        'BOARD_SIZE': settings.BOARD_SIZE,
        'TOKEN_COUNT': settings.TOKEN_COUNT,
        'TURN_TIMEOUT': settings.TURN_TIMEOUT,
        'WAITING_TIMEOUT': settings.WAITING_TIMEOUT,
        'API_BASE_URL': settings.API_BASE_URL,
        'LOG_LEVEL': settings.LOG_LEVEL,
    }
    return settings_dict


def validate_settings() -> bool:
    """
    Validate critical settings to ensure bot can run properly.
    
    Returns:
        bool: True if all critical settings are valid
    """
    errors = []
    
    # Check BOT_TOKEN
    if not settings.BOT_TOKEN or len(settings.BOT_TOKEN) < 10:
        errors.append("BOT_TOKEN is missing or too short")
    
    # Check OWNER_ID
    if settings.OWNER_ID <= 0:
        errors.append("OWNER_ID must be a valid positive integer")
    
    # Check DATABASE_URL
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is empty")
    
    # Check game settings
    if settings.MAX_PLAYERS < 2 or settings.MAX_PLAYERS > 8:
        errors.append("MAX_PLAYERS should be between 2 and 8")
    
    if settings.MIN_PLAYERS < 2 or settings.MIN_PLAYERS > settings.MAX_PLAYERS:
        errors.append("MIN_PLAYERS must be between 2 and MAX_PLAYERS")
    
    if settings.TURN_TIMEOUT < 10:
        errors.append("TURN_TIMEOUT should be at least 10 seconds")
    
    if settings.WAITING_TIMEOUT < 30:
        errors.append("WAITING_TIMEOUT should be at least 30 seconds")
    
    # Log errors if any
    if errors:
        import logging
        logger = logging.getLogger(__name__)
        for error in errors:
            logger.error(f"❌ Configuration Error: {error}")
        return False
    
    return True


def reload_settings():
    """
    Reload settings from environment variables.
    Useful when .env file has been updated while bot is running.
    """
    load_dotenv(override=True)
    # Re-initialize settings
    global settings
    settings = Settings()
    import logging
    logging.info("🔄 Settings reloaded successfully")