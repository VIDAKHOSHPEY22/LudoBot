"""
Chat Handler Module
Handles all text messages and chat functionality within the game.
Supports both private chats and group messaging for in-game communication.
"""

from telegram import Update
from telegram.ext import ContextTypes
from assets.messages import Messages
from assets.emojis import Emojis
import logging

logger = logging.getLogger(__name__)

class ChatHandler:
    """
    Handles text messages from users, including private and group chats.
    Manages in-game chat broadcasting and message filtering.
    """
    
    def __init__(self):
        """
        Initialize the chat handler.
        Stores active game chats for group message routing.
        """
        # Store active game chats mapping: chat_id -> game
        self.game_chats = {}
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Main message handler - processes all text messages.
        
        Args:
            update: Telegram update object containing the message
            context: Callback context with bot data
        """
        user = update.effective_user
        message = update.message
        chat_id = message.chat_id
        
        # === GROUP CHAT HANDLING ===
        # Check if message is from a group or supergroup
        if message.chat.type in ['group', 'supergroup']:
            # Check if this group is associated with an active game
            game = context.bot_data.get(f'game_chat_{chat_id}')
            if game:
                # Broadcast message to all game players
                await self._broadcast_to_game(context, game, user, message.text)
                return
        
        # === PRIVATE CHAT HANDLING ===
        # Respond to private messages with guidance
        await message.reply_text(
            f"{Emojis.CHAT} Your message was received!\n"
            f"Use /start to begin playing the Ludo game."
        )
    
    async def _broadcast_to_game(self, context: ContextTypes.DEFAULT_TYPE, game, user, text):
        """
        Broadcast a message to all players in a game.
        
        Args:
            context: Callback context with bot data
            game: The game instance
            user: The user who sent the message
            text: The message text to broadcast
        """
        # === ANTI-SPAM PROTECTION ===
        # Limit message length to prevent abuse
        if len(text) > 500:
            text = text[:500] + "..."
        
        # === BROADCAST TO ALL PLAYERS ===
        # Send the message to every player except the sender
        for player in game.players:
            if player.user_id != user.id:
                try:
                    # Format message with sender's name
                    sender_name = user.first_name or user.username or "Player"
                    await context.bot.send_message(
                        chat_id=player.user_id,
                        text=f"💬 {sender_name}: {text}"
                    )
                except Exception as e:
                    # Log error but continue with other players
                    logger.error(f"Failed to send message to {player.user_id}: {e}")
    
    async def register_game_chat(self, chat_id: int, game):
        """
        Register a group chat as an active game chat.
        
        Args:
            chat_id: ID of the group chat
            game: The game instance associated with this chat
        """
        self.game_chats[chat_id] = game
        logger.info(f"✅ Game chat registered: {chat_id}")
    
    async def unregister_game_chat(self, chat_id: int):
        """
        Unregister a group chat when the game ends.
        
        Args:
            chat_id: ID of the group chat to unregister
        """
        if chat_id in self.game_chats:
            del self.game_chats[chat_id]
            logger.info(f"🗑️ Game chat unregistered: {chat_id}")
    
    async def get_game_chat(self, chat_id: int):
        """
        Get the game associated with a group chat.
        
        Args:
            chat_id: ID of the group chat
            
        Returns:
            Game instance or None if not found
        """
        return self.game_chats.get(chat_id)