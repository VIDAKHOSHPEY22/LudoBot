"""
Start Handler Module
Handles the /start command and main menu interactions for the Ludo bot.
Manages user registration, welcome messages, and navigation.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.matchmaking_service_simple import MatchmakingService
from database.db_manager import DatabaseManager
from assets.messages import Messages
from assets.emojis import Emojis
import logging

logger = logging.getLogger(__name__)

class StartHandler:
    """
    Handles the /start command and main menu functionality.
    Manages user registration, welcome messages, and main navigation.
    """
    
    def __init__(self, matchmaking: MatchmakingService, db: DatabaseManager):
        """
        Initialize the start handler.
        
        Args:
            matchmaking: MatchmakingService instance for game management
            db: DatabaseManager instance for user data persistence
        """
        self.matchmaking = matchmaking
        self.db = db
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the /start command - Registers user and shows main menu.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # === USER REGISTRATION ===
        # Save or update user in database
        self.db.save_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Store user data in context for future use
        context.user_data['user_id'] = user.id
        context.user_data['chat_id'] = chat_id
        
        # === MAIN MENU KEYBOARD ===
        # Create inline keyboard with main navigation buttons
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.NEW_GAME} New Game", callback_data="new_game")],
            [InlineKeyboardButton(f"{Emojis.JOIN} Join Game", callback_data="join_game")],
            [InlineKeyboardButton(f"{Emojis.STATS} My Stats", callback_data="show_stats")],
            [InlineKeyboardButton(f"{Emojis.HELP} Help", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # === WELCOME MESSAGE ===
        # Personalize welcome message with user's name
        display_name = user.first_name or user.username or "Dear Player"
        welcome_text = Messages.WELCOME.format(
            name=display_name,
            emoji=Emojis.WAVE
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle the /help command - Displays game guide.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        await update.message.reply_text(
            Messages.HELP_TEXT,
            parse_mode='Markdown'
        )
    
    async def show_help_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle help button callback - Shows help text with back button.
        
        Args:
            update: Telegram update object containing callback query
            context: Callback context with bot data
        """
        query = update.callback_query
        await query.answer()
        
        # Show help with back to menu option
        await query.edit_message_text(
            Messages.HELP_TEXT,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )
    
    async def show_welcome_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Show welcome back message for returning users.
        Used when user reopens the bot or returns from a game.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user = update.effective_user
        display_name = user.first_name or user.username or "Player"
        
        # Show main menu with welcome back message
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.NEW_GAME} New Game", callback_data="new_game")],
            [InlineKeyboardButton(f"{Emojis.JOIN} Join Game", callback_data="join_game")],
            [InlineKeyboardButton(f"{Emojis.STATS} My Stats", callback_data="show_stats")],
            [InlineKeyboardButton(f"{Emojis.HELP} Help", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{Emojis.WAVE} Welcome back, {display_name}!\n"
            f"Ready to play some Ludo?",
            reply_markup=reply_markup
        )