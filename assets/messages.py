"""
Messages Module
Contains all static text messages used throughout the bot.
All messages support Markdown formatting and emoji placeholders.
"""

class Messages:
    """
    Centralized message repository for the Ludo bot.
    All user-facing text is defined here for easy modification and localization.
    """
    
    # === WELCOME MESSAGE ===
    # Displayed when user starts the bot with /start command
    # {emoji} - Wave emoji placeholder
    # {name} - User's first name or username
    WELCOME = """{emoji} Hello dear {name}! Welcome to **Ludo Game**!

🎲 Play online with your friends in real-time.

👇 Choose one of the options below:"""
    
    # === HELP TEXT ===
    # Comprehensive game guide and command reference
    HELP_TEXT = """🎯 **Ludo Game Guide**

🕹️ **How to Play:**
• 4-player online game
• Each player has 4 tokens
• Roll a 6-sided dice to move
• First player to get all tokens to the finish line wins

📋 **Commands:**
• `/newgame` - Start a new game
• `/join` - Join the waiting queue
• `/leave` - Leave the current game
• `/stats` - View your statistics
• `/cancel` - Cancel the current game
• `/help` - Show this guide

🎲 **Rules:**
• Roll a 6 to bring a token out of home
• Rolling a 6 gives you an extra turn
• Land on opponent's token to send it home
• Safe positions (⭐) protect your tokens

💡 **Tip:** Chat with other players in group mode!"""
    
    # === GAME START NOTIFICATION ===
    # Sent to all players when a game begins
    # {game_id} - Unique game identifier
    # {players_count} - Number of players in the game
    # {current_turn} - Name of the player starting
    GAME_START = """🎲 **Game Started!**

🆔 Game ID: `{game_id}`
👥 Players: {players_count}
🎯 Turn: {current_turn}

🤝 Good luck everyone!"""
    
    # === STATISTICS DISPLAY ===
    # Shows user's game statistics
    # {total_games} - Total games played
    # {wins} - Number of wins
    # {losses} - Number of losses
    # {score} - Total score
    # {win_rate:.1f} - Win percentage with one decimal
    STATS_TEXT = """📊 **Your Statistics:**

🎮 Total Games: {total_games}
🏆 Wins: {wins}
💔 Losses: {losses}
⭐ Score: {score}
📈 Win Rate: {win_rate:.1f}%"""
    
    # === WAITING QUEUE MESSAGE ===
    # Displayed when player is waiting for opponents
    # {emoji} - Searching emoji placeholder
    # {count} - Number of players currently in queue
    QUEUE_TEXT = """{emoji} Searching for players...

Players in queue: {count}

⏳ Please wait for the game to start..."""
    
    # === ADDITIONAL MESSAGES ===
    # Can be extended with more messages as needed
    
    # Error messages
    ERROR_GENERAL = "❌ An error occurred. Please try again."
    ERROR_NETWORK = "⚠️ Network error! Please check your connection."
    ERROR_TIMEOUT = "⏰ Request timed out. Please try again."
    
    # Game status messages
    STATUS_WAITING = "⏳ Waiting for more players... ({current}/{max})"
    STATUS_PLAYING = "🎯 Game in progress!"
    STATUS_FINISHED = "🏆 Game finished!"
    STATUS_CANCELLED = "❌ Game cancelled."
    
    # Player actions
    ACTION_JOIN = "✅ You have joined the queue!"
    ACTION_LEAVE = "🚪 You have left the game."
    ACTION_CANCEL = "❌ Game cancelled successfully."
    ACTION_QUEUE_CANCEL = "🚪 You have left the queue."
    
    # Turn messages
    TURN_YOUR = "🔄 **It's your turn!** Roll the dice! 🎲"
    TURN_OTHER = "🔄 **{player}'s turn.** Please wait."
    TURN_SKIP = "⏭️ Turn skipped!"
    TURN_WINNER = "🏆 **Winner: {player}** 🎉 Congratulations!"
    
    # Dice messages
    DICE_ROLL = "{player} rolled: {emoji} **{value}**"
    DICE_SIX = "🎯 Rolled a 6! One more turn!"
    DICE_CANT_MOVE = "⚠️ No tokens can move. Turn passed."
    
    # Token messages
    TOKEN_MOVED = "🚀 Token {id} moved to position {position}!"
    TOKEN_EATEN = "💥 Opponent token eaten!"
    TOKEN_FINISHED = "⭐ Token {id} finished! ({finished}/4)"
    
    # Board messages
    BOARD_REFRESH = "🔄 Board updated!"
    BOARD_EMPTY = "📭 No active game."
    
    # Queue messages
    QUEUE_JOIN = "🎮 You joined the queue! Players waiting: {count}"
    QUEUE_LEAVE = "🚪 You left the queue."
    QUEUE_FULL = "⚠️ Queue is full! Maximum {max} players."
    
    # Command feedback
    COMMAND_INVALID = "❌ Invalid command. Use /help for available commands."
    COMMAND_ONLY_PRIVATE = "🔒 This command only works in private chat."
    COMMAND_ONLY_GROUP = "👥 This command only works in groups."
    
    # Player messages
    PLAYER_NOT_FOUND = "❌ Player not found."
    PLAYER_ALREADY_IN_GAME = "⚠️ You are already in a game!"
    PLAYER_NOT_IN_GAME = "⚠️ You are not in any game."
    PLAYER_QUEUE_ALREADY = "⚠️ You are already in the queue!"
    PLAYER_NOT_IN_QUEUE = "⚠️ You are not in the queue."