"""
Main Bot Module
Entry point for the Ludo Telegram Bot.
Initializes all handlers and starts the bot polling loop.
"""

import logging
import asyncio
import socket
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config.settings import settings
from bot.handlers.start_handler import StartHandler
from bot.handlers.game_handler import GameHandler
from bot.handlers.chat_handler import ChatHandler
from bot.handlers.callback_handler import CallbackHandler
from services.matchmaking_service_simple import MatchmakingService
from database.db_manager import db

# === NETWORK CONFIGURATION ===
# Set default socket timeout to prevent hanging connections
socket.setdefaulttimeout(30)

# === LOGGING CONFIGURATION ===
# Configure logging format and level for consistent output
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class LudoBot:
    """
    Main bot class that initializes and runs the Telegram bot.
    Manages all handlers and the main event loop.
    """
    
    def __init__(self):
        """
        Initialize the bot with all required components.
        Sets up services, handlers, and configuration.
        """
        # === BOT CONFIGURATION ===
        self.token = settings.BOT_TOKEN
        self.application = None
        
        # === SERVICES ===
        # Matchmaking service for game queue management
        self.matchmaking = MatchmakingService()
        
        # === HANDLERS ===
        # Initialize all handlers with their dependencies
        self.start_handler = StartHandler(self.matchmaking, db)
        self.game_handler = GameHandler(self.matchmaking, db)
        self.chat_handler = ChatHandler()
        self.callback_handler = CallbackHandler(self.matchmaking)
    
    def setup_handlers(self):
        """
        Register all command and callback handlers with the application.
        Each handler is mapped to a specific command or callback pattern.
        """
        # === COMMAND HANDLERS ===
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_handler.start_command))
        self.application.add_handler(CommandHandler("help", self.start_handler.help_command))
        
        # Game commands
        self.application.add_handler(CommandHandler("newgame", self.game_handler.new_game_command))
        self.application.add_handler(CommandHandler("join", self.game_handler.join_game_command))
        self.application.add_handler(CommandHandler("leave", self.game_handler.leave_game_command))
        self.application.add_handler(CommandHandler("stats", self.game_handler.stats_command))
        self.application.add_handler(CommandHandler("cancel", self.game_handler.cancel_game_command))
        
        # === CALLBACK QUERY HANDLER ===
        # Handles all inline keyboard button presses
        self.application.add_handler(CallbackQueryHandler(self.callback_handler.handle_callback))
        
        # === MESSAGE HANDLER ===
        # Handles regular text messages (non-commands) for chat functionality
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.chat_handler.handle_message
        ))
        
        # === ERROR HANDLER ===
        # Global error handler for all exceptions
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        """
        Global error handler for the bot.
        Logs errors and notifies users when possible.
        
        Args:
            update: Telegram update object
            context: Error context with exception details
        """
        error = context.error
        logger.error(f"❌ Error occurred: {error}")
        
        # Try to notify the user about the error
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred. Please try again."
                )
            except Exception as e:
                # Silently fail if we can't notify the user
                logger.error(f"Failed to send error notification: {e}")
    
    async def post_init(self):
        """
        Post-initialization tasks.
        Starts background services like the cleanup task.
        """
        await self.matchmaking.start_cleanup()
        logger.info("🧹 Cleanup service activated")
    
    def run(self):
        """
        Main entry point for running the bot.
        Sets up the application, starts polling, and handles the event loop.
        """
        # === BUILD APPLICATION ===
        # Create the Application instance with the bot token
        self.application = Application.builder().token(self.token).build()
        
        # Register all handlers
        self.setup_handlers()
        
        # === EVENT LOOP SETUP ===
        # Create a new event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run post-initialization tasks
        loop.run_until_complete(self.post_init())
        
        # === BOT STARTUP ===
        logger.info("🚀 Ludo Bot started successfully!")
        logger.info("🤖 @LudoGoPlayBot")
        logger.info(f"👥 Players in queue: {self.matchmaking.get_waiting_count()}")
        logger.info(f"🎮 Active games: {len(self.matchmaking.active_games)}")
        
        # === START POLLING ===
        # Begin polling for updates from Telegram
        try:
            self.application.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,  # Skip old updates on restart
                timeout=60,                  # Long timeout for slow connections
                read_timeout=60,
                write_timeout=60,
                pool_timeout=60
            )
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
        finally:
            # Clean up the event loop
            loop.close()
            logger.info("👋 Bot shutdown complete")


# === APPLICATION ENTRY POINT ===
if __name__ == "__main__":
    # Create and run the bot instance
    bot = LudoBot()
    bot.run()