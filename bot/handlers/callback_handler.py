"""
Callback Handler Module
Handles all inline keyboard button callbacks for the Ludo bot.
Manages game actions like rolling dice, moving tokens, and game flow.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError
from services.matchmaking_service_simple import MatchmakingService
from assets.messages import Messages
from assets.emojis import Emojis
from assets.board import LudoBoard
import asyncio
import logging

logger = logging.getLogger(__name__)

class CallbackHandler:
    """
    Handles all callback queries from inline keyboards.
    Manages game actions, queue operations, and navigation.
    """
    
    def __init__(self, matchmaking: MatchmakingService):
        """
        Initialize the callback handler.
        
        Args:
            matchmaking: MatchmakingService instance for game management
        """
        self.matchmaking = matchmaking
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Main callback router - dispatches to appropriate handler based on callback data.
        
        Args:
            update: Telegram update object
            context: Callback context with bot data
        """
        query = update.callback_query
        data = query.data
        user_id = update.effective_user.id
        
        try:
            # Route to appropriate handler based on callback data prefix
            if data == "new_game":
                await self._handle_new_game(query, context)
            elif data == "join_game":
                await self._handle_join_game(query, context)
            elif data == "show_stats":
                await self._handle_show_stats(query, context)
            elif data == "show_help":
                await self._handle_show_help(query, context)
            elif data == "back_to_menu":
                await self._handle_back_to_menu(query, context)
            elif data == "refresh_board":
                await self._handle_refresh_board(query, context)
            elif data.startswith("roll_dice_"):
                game_id = data.replace("roll_dice_", "")
                await self._handle_roll_dice(query, context, game_id, user_id)
            elif data.startswith("move_token_"):
                parts = data.split("_")
                game_id = parts[2]
                token_id = int(parts[3])
                await self._handle_move_token(query, context, game_id, user_id, token_id)
            elif data.startswith("skip_turn_"):
                game_id = data.replace("skip_turn_", "")
                await self._handle_skip_turn(query, context, game_id, user_id)
            elif data.startswith("leave_game_"):
                game_id = data.replace("leave_game_", "")
                await self._handle_leave_game(query, context, game_id, user_id)
            elif data == "cancel_queue":
                await self._handle_cancel_queue(query, context, user_id)
            else:
                await query.answer("❌ Invalid command!")
                
        except (TimedOut, NetworkError) as e:
            logger.warning(f"⚠️ Network error in handle_callback: {e}")
            await query.answer("⚠️ Network error! Please try again.", show_alert=True)
        except Exception as e:
            logger.error(f"❌ Error in handle_callback: {e}")
            await query.answer("❌ An error occurred!", show_alert=True)
    
    async def _handle_new_game(self, query, context):
        """
        Handle 'New Game' button - adds player to matchmaking queue.
        
        Args:
            query: Callback query object
            context: Callback context
        """
        await query.answer()
        
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        username = query.from_user.username or f"Player_{user_id}"
        
        # Check if player is already in a game
        existing_game = self.matchmaking.get_game_by_player(user_id)
        if existing_game:
            await query.edit_message_text(
                f"{Emojis.WARNING} You are already in a game!\n"
                f"Game ID: `{existing_game.game_id}`"
            )
            return
        
        # Add player to queue
        if self.matchmaking.add_to_queue(user_id, chat_id, username):
            keyboard = [
                [InlineKeyboardButton(f"{Emojis.CANCEL} Cancel", callback_data="cancel_queue")]
            ]
            
            await query.edit_message_text(
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
                await self._start_game_notification(query, context, game_id, players)
        else:
            await query.edit_message_text(
                f"{Emojis.WARNING} You are already in the queue!"
            )
    
    async def _handle_join_game(self, query, context):
        """
        Handle 'Join Game' button - adds player to existing queue.
        
        Args:
            query: Callback query object
            context: Callback context
        """
        await query.answer()
        
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        username = query.from_user.username or f"Player_{user_id}"
        
        # Check if player is already in a game
        existing_game = self.matchmaking.get_game_by_player(user_id)
        if existing_game:
            await query.edit_message_text(
                f"{Emojis.WARNING} You are already in a game!"
            )
            return
        
        # Add to queue
        if self.matchmaking.add_to_queue(user_id, chat_id, username):
            await query.edit_message_text(
                f"{Emojis.CHECK} Added to queue!\n"
                f"Players in queue: {self.matchmaking.get_waiting_count()}"
            )
            
            # Try to find a match
            match = self.matchmaking.find_match()
            if match:
                game_id, players = match
                await self._start_game_notification(query, context, game_id, players)
        else:
            await query.edit_message_text(
                f"{Emojis.WARNING} You are already in the queue!"
            )
    
    async def _handle_show_stats(self, query, context):
        """
        Handle 'Show Stats' button - displays user statistics.
        
        Args:
            query: Callback query object
            context: Callback context
        """
        await query.answer()
        await query.edit_message_text(
            f"{Emojis.STATS} Use `/stats` command to view your statistics.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
            ])
        )
    
    async def _handle_show_help(self, query, context):
        """
        Handle 'Show Help' button - displays game guide.
        
        Args:
            query: Callback query object
            context: Callback context
        """
        await query.answer()
        await query.edit_message_text(
            Messages.HELP_TEXT,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
            ])
        )
    
    async def _handle_back_to_menu(self, query, context):
        """
        Handle 'Back to Menu' button - returns to main menu.
        
        Args:
            query: Callback query object
            context: Callback context
        """
        await query.answer()
        
        # Main menu keyboard
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.NEW_GAME} New Game", callback_data="new_game")],
            [InlineKeyboardButton(f"{Emojis.JOIN} Join Game", callback_data="join_game")],
            [InlineKeyboardButton(f"{Emojis.STATS} My Stats", callback_data="show_stats")],
            [InlineKeyboardButton(f"{Emojis.HELP} Help", callback_data="show_help")]
        ]
        
        await query.edit_message_text(
            f"{Emojis.WAVE} Welcome to the main menu!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _handle_refresh_board(self, query, context):
        """
        Handle 'Refresh Board' button - updates the game board display.
        
        Args:
            query: Callback query object
            context: Callback context
        """
        await query.answer()
        
        user_id = query.from_user.id
        game = self.matchmaking.get_game_by_player(user_id)
        
        if not game:
            await query.edit_message_text(
                f"{Emojis.WARNING} You are not in any active game!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
                ])
            )
            return
        
        # Generate and display updated board
        game_state = game.get_game_state()
        board_text = LudoBoard.generate_board(game_state)
        
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.DICE} Roll Dice", callback_data=f"roll_dice_{game.game_id}")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_board")],
            [InlineKeyboardButton(f"{Emojis.LEAVE} Leave", callback_data=f"leave_game_{game.game_id}")]
        ]
        
        await query.edit_message_text(
            board_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _handle_roll_dice(self, query, context, game_id: str, user_id: int):
        """
        Handle 'Roll Dice' button - rolls dice and updates game state.
        
        Args:
            query: Callback query object
            context: Callback context
            game_id: ID of the game
            user_id: ID of the player rolling
        """
        await query.answer()
        
        game = self.matchmaking.get_game(game_id)
        if not game:
            await query.edit_message_text(f"{Emojis.WARNING} Game not found!")
            return
        
        # Roll the dice
        success, result = await game.roll_dice(user_id)
        
        if not success:
            await query.answer(result.get('error', 'Error rolling dice'), show_alert=True)
            return
        
        # Get dice emoji
        dice_emoji = self._get_dice_emoji(result['dice_value'])
        game_state = game.get_game_state()
        board_text = LudoBoard.generate_board(game_state)
        
        # Build response message
        message = f"{board_text}\n\n"
        message += f"{Emojis.DICE} {result['player']} rolled: {dice_emoji} **{result['dice_value']}**\n"
        
        if result['is_six']:
            message += f"{Emojis.SIX} Rolled a 6! One more turn! 🎯\n"
        
        # Check if any tokens can move
        if not result['can_move']:
            message += f"{Emojis.WARNING} No tokens can move.\n"
        else:
            message += f"{Emojis.MOVE} Select a token to move:\n"
            
            player = game.get_player(user_id)
            if player:
                keyboard = []
                
                # Create buttons for each movable token
                for token in player.tokens:
                    if token.can_move(result['dice_value']):
                        status_emoji = "🏠" if token.status.value == "home" else "🚀"
                        status_text = "Home" if token.status.value == "home" else f"Pos {token.position}"
                        keyboard.append([
                            InlineKeyboardButton(
                                f"{status_emoji} Token {token.id + 1} ({status_text})",
                                callback_data=f"move_token_{game_id}_{token.id}"
                            )
                        ])
                
                # Add action buttons
                row = []
                if keyboard:
                    row.append(InlineKeyboardButton("⏭️ Skip", callback_data=f"skip_turn_{game_id}"))
                row.append(InlineKeyboardButton("🔄 Board", callback_data="refresh_board"))
                keyboard.append(row)
                
                await query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
        
        # No moves available or turn changed
        keyboard = [
            [InlineKeyboardButton("🔄 Board", callback_data="refresh_board")],
            [InlineKeyboardButton(f"{Emojis.LEAVE} Leave", callback_data=f"leave_game_{game_id}")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _handle_move_token(self, query, context, game_id: str, user_id: int, token_id: int):
        """
        Handle token movement - moves selected token on the board.
        
        Args:
            query: Callback query object
            context: Callback context
            game_id: ID of the game
            user_id: ID of the player
            token_id: ID of the token to move
        """
        await query.answer()
        
        game = self.matchmaking.get_game(game_id)
        if not game:
            await query.edit_message_text(f"{Emojis.WARNING} Game not found!")
            return
        
        # Move the token
        success, result = await game.move_token(user_id, token_id)
        
        if not success:
            await query.answer(result.get('error', 'Error moving token'), show_alert=True)
            return
        
        # Update board display
        game_state = game.get_game_state()
        board_text = LudoBoard.generate_board(game_state)
        
        message = f"{board_text}\n\n"
        message += f"{Emojis.MOVE} Token **{token_id + 1}** moved!\n"
        
        if result.get('new_position', -1) >= 0:
            message += f"📍 New position: **{result['new_position']}**\n"
        
        if result.get('eaten', False):
            message += f"{Emojis.EAT} 💥 Opponent token eaten!\n"
        
        # Check for winner
        if result.get('winner'):
            message += f"\n🏆 **{Emojis.WIN} Winner: {result['winner']}** 🏆\n"
            message += f"{Emojis.CONGRATS} 🎉 Congratulations! Game over!"
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"{Emojis.NEW_GAME} New Game", callback_data="new_game")],
                    [InlineKeyboardButton("📊 Stats", callback_data="show_stats")],
                    [InlineKeyboardButton("🔙 Menu", callback_data="back_to_menu")]
                ])
            )
            return
        
        # Show game controls
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.DICE} Roll Dice", callback_data=f"roll_dice_{game_id}")],
            [InlineKeyboardButton("🔄 Board", callback_data="refresh_board")],
            [InlineKeyboardButton(f"{Emojis.LEAVE} Leave", callback_data=f"leave_game_{game_id}")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _handle_skip_turn(self, query, context, game_id: str, user_id: int):
        """
        Handle 'Skip Turn' button - passes turn to next player.
        
        Args:
            query: Callback query object
            context: Callback context
            game_id: ID of the game
            user_id: ID of the player skipping
        """
        await query.answer()
        
        game = self.matchmaking.get_game(game_id)
        if not game:
            await query.edit_message_text(f"{Emojis.WARNING} Game not found!")
            return
        
        # Skip to next turn
        game.next_turn()
        game_state = game.get_game_state()
        board_text = LudoBoard.generate_board(game_state)
        
        message = f"{board_text}\n\n"
        message += f"⏭️ Turn skipped!\n"
        message += f"🔄 Next turn: **{game_state['current_turn']}**"
        
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.DICE} Roll Dice", callback_data=f"roll_dice_{game_id}")],
            [InlineKeyboardButton("🔄 Board", callback_data="refresh_board")],
            [InlineKeyboardButton(f"{Emojis.LEAVE} Leave", callback_data=f"leave_game_{game_id}")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _handle_leave_game(self, query, context, game_id: str, user_id: int):
        """
        Handle 'Leave Game' button - removes player from game.
        
        Args:
            query: Callback query object
            context: Callback context
            game_id: ID of the game
            user_id: ID of the player leaving
        """
        await query.answer()
        
        game = self.matchmaking.get_game(game_id)
        if game:
            game.remove_player(user_id)
            
            # Cancel game if not enough players
            if len(game.players) < 2:
                self.matchmaking.cancel_game(game_id)
                await query.edit_message_text(
                    f"{Emojis.WARNING} Game cancelled due to insufficient players.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
                    ])
                )
            else:
                await query.edit_message_text(
                    f"{Emojis.LEAVE} You left the game.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
                    ])
                )
        else:
            await query.edit_message_text(
                f"{Emojis.WARNING} Game not found!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
                ])
            )
    
    async def _handle_cancel_queue(self, query, context, user_id: int):
        """
        Handle 'Cancel Queue' button - removes player from matchmaking queue.
        
        Args:
            query: Callback query object
            context: Callback context
            user_id: ID of the player
        """
        await query.answer()
        
        if self.matchmaking.remove_from_queue(user_id):
            await query.edit_message_text(
                f"{Emojis.CANCEL} You left the queue.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
                ])
            )
        else:
            await query.edit_message_text(
                f"{Emojis.WARNING} You are not in the queue!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
                ])
            )
    
    async def _start_game_notification(self, query, context, game_id: str, players: list):
        """
        Notify all players when a game starts.
        
        Args:
            query: Callback query object
            context: Callback context
            game_id: ID of the new game
            players: List of player data dictionaries
        """
        game = self.matchmaking.get_game(game_id)
        if not game:
            return
        
        # Generate game board
        game_state = game.get_game_state()
        board_text = LudoBoard.generate_board(game_state)
        
        message = f"🎯 **Game Started!**\n\n{board_text}"
        
        # Create game control keyboard
        keyboard = [
            [InlineKeyboardButton(f"{Emojis.DICE} Roll Dice", callback_data=f"roll_dice_{game_id}")],
            [InlineKeyboardButton("🔄 Board", callback_data="refresh_board")],
            [InlineKeyboardButton(f"{Emojis.LEAVE} Leave", callback_data=f"leave_game_{game_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send notification to each player with error handling
        for player_data in players:
            try:
                await context.bot.send_message(
                    chat_id=player_data['chat_id'],
                    text=message,
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
    
    def _get_dice_emoji(self, value: int) -> str:
        """
        Get Unicode dice emoji for a given value.
        
        Args:
            value: Dice value (1-6)
            
        Returns:
            str: Unicode dice emoji character
        """
        emojis = {
            1: "⚀",
            2: "⚁", 
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
        return emojis.get(value, "🎲")