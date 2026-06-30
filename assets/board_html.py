"""
Ludo Board HTML Generator
This module generates an HTML representation of the Ludo game board
for display in Telegram WebView or browsers.
"""

class LudoBoardHTML:
    """
    Generate Ludo board as HTML for sending to Telegram.
    Creates a visually appealing board with player tokens, dice, and game status.
    """
    
    @staticmethod
    def generate_html(game_state):
        """
        Generate HTML of the game board.
        
        Args:
            game_state (dict): The current state of the game containing:
                - game_id: Unique game identifier
                - dice_value: Current dice value (0-6)
                - board: Board state with players and their tokens
                - current_turn: Username of the player whose turn it is
            
        Returns:
            str: Complete HTML document as a string
        """
        
        # HTML template with embedded CSS styling
        html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            /* Main container styling - dark theme with centering */
            body { 
                font-family: Arial, sans-serif; 
                direction: rtl;  /* Right-to-left for Persian/Farsi */
                padding: 20px; 
                background: #1a1a2e;  /* Dark blue background */
                color: #fff; 
            }
            
            /* Game board container - rounded card with shadow */
            .board { 
                background: #16213e; 
                border-radius: 15px; 
                padding: 20px; 
                max-width: 500px; 
                margin: auto; 
            }
            
            /* Header styling - gold color for emphasis */
            .header { 
                text-align: center; 
                color: #f5c842; 
                font-size: 24px; 
            }
            
            /* Dice display - large emoji for visibility */
            .dice { 
                font-size: 48px; 
                text-align: center; 
                margin: 10px 0; 
            }
            
            /* Individual player card */
            .player { 
                background: #0f3460; 
                border-radius: 10px; 
                padding: 10px; 
                margin: 10px 0; 
            }
            
            /* Player name styling */
            .player-name { 
                font-size: 18px; 
                font-weight: bold; 
            }
            
            /* Token container - flex layout for horizontal display */
            .tokens { 
                display: flex; 
                gap: 5px; 
                margin: 5px 0; 
            }
            
            /* Base token styling */
            .token { 
                padding: 5px 10px; 
                border-radius: 50%; 
                font-size: 14px; 
            }
            
            /* Token at home position - gray background */
            .token-home { 
                background: #555; 
                color: #fff; 
            }
            
            /* Token in play - green background */
            .token-playing { 
                background: #4CAF50; 
                color: #fff; 
            }
            
            /* Token finished - gold background */
            .token-finished { 
                background: #f5c842; 
                color: #000; 
            }
            
            /* Current turn indicator - green highlight */
            .turn { 
                text-align: center; 
                font-size: 20px; 
                color: #4CAF50; 
                margin-top: 15px; 
            }
            
            /* Status text - gray color for metadata */
            .status { 
                text-align: center; 
                color: #aaa; 
            }
        </style>
        </head>
        <body>
        <div class="board">
        """
        
        # === HEADER SECTION ===
        # Display game title and ID
        html += f'<div class="header">🎯 Ludo Game</div>'
        html += f'<div class="status">🆔 {game_state.get("game_id", "N/A")}</div>'
        
        # === DICE SECTION ===
        # Display current dice value with appropriate emoji
        dice_value = game_state.get('dice_value', 0)
        # Map dice value (0-6) to Unicode dice emojis
        dice_emojis = ["🎲", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        dice_emoji = dice_emojis[dice_value] if 0 <= dice_value <= 6 else "🎲"
        html += f'<div class="dice">{dice_emoji} {dice_value}</div>'
        
        # === PLAYERS SECTION ===
        # Iterate through all players and display their tokens
        for player in game_state.get('board', {}).get('players', []):
            color = player.get('color', '⚪')          # Player's color emoji
            name = player.get('username', 'Unknown')   # Player's display name
            finished = player.get('finished', 0)       # Number of finished tokens
            
            # Start player card
            html += f'''
            <div class="player">
                <div class="player-name">{color} {name}</div>
                <div class="tokens">
            '''
            
            # Display each token with appropriate status styling
            for token in player.get('tokens', []):
                status = token.get('status', '')
                if status == 'home':
                    # Token is at home - not yet in play
                    html += '<span class="token token-home">🏠</span>'
                elif status == 'finished':
                    # Token has reached the finish line
                    html += '<span class="token token-finished">⭐</span>'
                else:
                    # Token is actively moving on the board
                    html += '<span class="token token-playing">🚀</span>'
            
            # Show progress (finished tokens out of 4 total)
            html += f'</div><div>✅ {finished}/4</div></div>'
        
        # === TURN INDICATOR ===
        # Show which player's turn it is
        current_turn = game_state.get('current_turn', '')
        if current_turn:
            html += f'<div class="turn">🔄 Turn: {current_turn}</div>'
        
        # Close the board container and HTML document
        html += """
        </div>
        </body>
        </html>
        """
        
        return html