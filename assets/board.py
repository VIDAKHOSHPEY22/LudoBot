"""
Ludo Board Generator
This module generates text-based representations of the Ludo game board
using emojis for display in Telegram messages.
"""

class LudoBoard:
    """
    Generate Ludo board as text with emojis for Telegram messages.
    Provides both full and simple board representations.
    """
    
    @staticmethod
    def generate_board(game_state):
        """
        Generate a detailed text-based board with emojis.
        
        Args:
            game_state (dict): The current state of the game containing:
                - game_id: Unique game identifier
                - status: Current game status (waiting, playing, finished)
                - dice_value: Current dice value
                - board: Board state with players and their tokens
                - current_turn: Username of the player whose turn it is
            
        Returns:
            str: Formatted text board with emojis and separators
        """
        board = []
        
        # === HEADER SECTION ===
        board.append("🎯 **Ludo Game Board**")
        board.append("═" * 30)  # Double-line separator
        
        # === GAME INFORMATION ===
        board.append(f"🆔 Game ID: `{game_state.get('game_id', 'N/A')}`")
        board.append(f"📊 Status: {game_state.get('status', 'N/A')}")
        board.append(f"🎲 Dice: {game_state.get('dice_value', '❌')}")
        board.append("")  # Empty line for spacing
        
        # === PLAYERS SECTION ===
        # Iterate through all players in the game
        for player in game_state.get('board', {}).get('players', []):
            color = player.get('color', '⚪')          # Player's color emoji
            name = player.get('username', 'Unknown')   # Player's display name
            finished = player.get('finished', 0)       # Number of finished tokens
            
            # Build token display list
            tokens = []
            for token in player.get('tokens', []):
                status = token.get('status', '')
                if status == 'home':
                    tokens.append("🏠")                # Token at home
                elif status == 'finished':
                    tokens.append("🏆")                # Token finished
                else:
                    pos = token.get('position', 0)
                    tokens.append(f"📍{pos}")          # Token on board with position
            
            # Display player information
            board.append(f"{color} **{name}**")
            board.append(f"   Tokens: {' '.join(tokens)}")
            board.append(f"   ✅ Finished: {finished}/4")
            board.append("")  # Empty line between players
        
        # === CURRENT TURN INDICATOR ===
        current_turn = game_state.get('current_turn', '')
        if current_turn:
            board.append(f"🔄 **Turn: {current_turn}**")
        
        # === FOOTER ===
        board.append("═" * 30)
        board.append("🎲 Use the button below to roll the dice")
        
        # Join all lines with newline characters
        return "\n".join(board)
    
    @staticmethod
    def generate_simple_board(game):
        """
        Generate a simplified board representation using emojis.
        More compact version suitable for quick status updates.
        
        Args:
            game: LudoGame instance containing:
                - players: List of Player objects
                - dice: Dice instance with current_value
                - current_player_index: Index of current player
            
        Returns:
            str: Simplified text board with emojis
        """
        lines = []
        
        # === HEADER ===
        lines.append("🎯 **Ludo Online**")
        lines.append("─" * 25)  # Single-line separator
        
        # === PLAYERS SECTION ===
        for player in game.players:
            color_emoji = player.color.value          # Player's color emoji
            name = player.get_username_display()      # Display name (respects anonymity)
            finished = len(player.get_finished_tokens())  # Count finished tokens
            
            # Build token status string
            tokens_str = ""
            for token in player.tokens:
                if token.status.value == "home":
                    tokens_str += "🏠"    # Token at home
                elif token.status.value == "finished":
                    tokens_str += "⭐"    # Token finished
                else:
                    tokens_str += "🚀"    # Token in play
            
            # Display player with their tokens
            lines.append(f"{color_emoji} {name}: {tokens_str} ({finished}/4)")
        
        # === DICE AND TURN INFORMATION ===
        lines.append("─" * 25)
        
        # Display current dice value
        dice_value = game.dice.current_value if game.dice.current_value else '❌'
        lines.append(f"🎲 Dice: {dice_value}")
        
        # Display whose turn it is
        current_player = game.players[game.current_player_index].get_username_display() if game.players else '-'
        lines.append(f"🔄 Turn: {current_player}")
        
        return "\n".join(lines)