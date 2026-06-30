"""
Game Handler Module
Handles all game-related commands and operations for the Ludo bot.
Manages game creation, joining, leaving, and game flow.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError
from services.matchmaking_service_simple import MatchmakingService
from database.db_manager import DatabaseManager
from assets.messages import Messages
from assets.emojis import Emojis
from assets.board import LudoBoard
import logging

logger = logging.getLogger(__name__)

class GameHandler:
    """
    Handles all game-related commands including:
    - Starting new games
    - Joining queues
    - Leaving games
    - Viewing statistics
    - Canceling games
    """
    
    def __init__(self, matchmaking: MatchmakingService, db: DatabaseManager):
        """
        Initialize the game handler.
        
        Args:
            matchmaking: MatchmakingService instance for game management
            db: DatabaseManager instance for user statistics
        """
        self.matchmaking = matchmaking
        self.db = db
    
    async def new_game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /newgame command - Creates a new game and adds player to queue.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        username = update.effective_user.username or f"Player_{user_id}"
        
        # Check if player is already in a game
        existing_game = self.matchmaking.get_game_by_player(user_id)
        if existing_game:
            await update.message.reply_text(
                f"{Emojis.WARNING} You are already in a game!\n"
                f"Game ID: `{existing_game.game_id}`"
            )
            return
        
        # Add player to matchmaking queue
        if self.matchmaking.add_to_queue(user_id, chat_id, username):
            keyboard = [
                [InlineKeyboardButton(f"{Emojis.CANCEL} Cancel", callback_data="cancel_queue")]
            ]
            
            await update.message.reply_text(
                f"{Emojis.SEARCHING} Searching for players...\n\n"
                f"Players in queue: {self.matchmaking.get_waiting_count()}\n"
                f"Need 2 players to start.\n\n"
                f"💡 Invite your friends:\n"
                f"`/join` to join the queue",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            # Try to find a match
            match = self.matchmaking.find_match()
            if match:
                game_id, players = match
                await self._start_game_notification(update, context, game_id, players)
        else:
            await update.message.reply_text(
                f"{Emojis.WARNING} You are already in the queue!"
            )
    
    async def join_game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /join command - Joins the matchmaking queue.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        username = update.effective_user.username or f"Player_{user_id}"
        
        # Check if player is already in a game
        existing_game = self.matchmaking.get_game_by_player(user_id)
        if existing_game:
            await update.message.reply_text(
                f"{Emojis.WARNING} You are already in a game!"
            )
            return
        
        # Add to queue
        if self.matchmaking.add_to_queue(user_id, chat_id, username):
            await update.message.reply_text(
                f"{Emojis.CHECK} Added to queue!\n"
                f"Players in queue: {self.matchmaking.get_waiting_count()}"
            )
            
            # Try to find a match
            match = self.matchmaking.find_match()
            if match:
                game_id, players = match
                await self._start_game_notification(update, context, game_id, players)
        else:
            await update.message.reply_text(
                f"{Emojis.WARNING} You are already in the queue!"
            )
    
    async def leave_game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /leave command - Leaves the current game or queue.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user_id = update.effective_user.id
        
        # Try to remove from queue first
        if self.matchmaking.remove_from_queue(user_id):
            await update.message.reply_text(
                f"{Emojis.LEAVE} You left the queue."
            )
            return
        
        # If not in queue, try to leave active game
        game = self.matchmaking.get_game_by_player(user_id)
        if game:
            if game.remove_player(user_id):
                await update.message.reply_text(
                    f"{Emojis.LEAVE} You left the game."
                )
                
                # Check if game was cancelled due to insufficient players
                if game.status == "cancelled":
                    await update.message.reply_text(
                        f"{Emojis.WARNING} Game cancelled due to insufficient players."
                    )
                return
        
        await update.message.reply_text(
            f"{Emojis.WARNING} You are not in any game or queue."
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /stats command - Displays user statistics.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user_id = update.effective_user.id
        stats = self.db.get_user_stats(user_id)
        
        if not stats:
            await update.message.reply_text(
                f"{Emojis.STATS} You haven't played any games yet!"
            )
            return
        
        # Format statistics message
        stats_text = Messages.STATS_TEXT.format(
            total_games=stats.get('total_games', 0),
            wins=stats.get('wins', 0),
            losses=stats.get('losses', 0),
            score=stats.get('score', 0),
            win_rate=stats.get('win_rate', 0)
        )
        
        await update.message.reply_text(stats_text)
    
    async def cancel_game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /cancel command - Cancels the current game.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        user_id = update.effective_user.id
        game = self.matchmaking.get_game_by_player(user_id)
        
        if game:
            self.matchmaking.cancel_game(game.game_id)
            await update.message.reply_text(
                f"{Emojis.CANCEL} Game cancelled successfully."
            )
        else:
            await update.message.reply_text(
                f"{Emojis.WARNING} You are not in any active game."
            )
    
    async def _start_game_notification(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       game_id: str, players: list):
        """
        Notify all players when a game starts.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
            game_id: ID of the new game
            players: List of player data dictionaries
        """
        game = self.matchmaking.get_game(game_id)
        if not game:
            return
        
        # Build player list keyboard
        keyboard = []
        for player_data in players:
            player = game.get_player(player_data['user_id'])
            if player:
                color_emoji = player.color.value
                keyboard.append([
                    InlineKeyboardButton(
                        f"{color_emoji} {player.get_username_display()}",
                        callback_data=f"player_{player_data['user_id']}"
                    )
                ])
        
        # Add game control buttons
        keyboard.append([InlineKeyboardButton(f"{Emojis.DICE} Roll Dice", callback_data=f"roll_dice_{game_id}")])
        keyboard.append([InlineKeyboardButton(f"{Emojis.LEAVE} Leave Game", callback_data=f"leave_game_{game_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Prepare game start message
        game_state = game.get_game_state()
        board_text = LudoBoard.generate_board(game_state)
        
        message_text = f"🎯 **Game Started!**\n\n{board_text}"
        
        # Send notification to all players with error handling
        for player_data in players:
            try:
                await context.bot.send_message(
                    chat_id=player_data['chat_id'],
                    text=message_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except (TimedOut, NetworkError) as e:
                logger.warning(f"⚠️ Network error for {player_data['user_id']}: {e}")
                # Retry with simpler message
                try:
                    await asyncio.sleep(2)
                    await context.bot.send_message(
                        chat_id=player_data['chat_id'],
                        text=f"🎯 **Game Started!**\n🆔: `{game_id}`\nUse the buttons to play.",
                        parse_mode='Markdown'
                    )
                except Exception as e2:
                    logger.error(f"❌ Second attempt failed for {player_data['user_id']}: {e2}")
            except Exception as e:
                logger.error(f"❌ Error sending to {player_data['user_id']}: {e}")