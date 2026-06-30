"""
Matchmaking Service Module
Handles player queue management and game creation.
Matches players together and manages active games.
"""

from typing import Dict, List, Optional, Tuple
import asyncio
import uuid
from datetime import datetime, timedelta
from game.core.ludo_game import LudoGame
import logging

logger = logging.getLogger(__name__)


class MatchmakingService:
    """
    Simple matchmaking service without Redis - for testing purposes.
    Manages player queues, game creation, and active game tracking.
    """
    
    def __init__(self):
        """
        Initialize the matchmaking service.
        """
        # Active games dictionary: game_id -> LudoGame instance
        self.active_games: Dict[str, LudoGame] = {}
        
        # Waiting players dictionary: user_id -> player_data
        self.waiting_players: Dict[int, Dict] = {}
        
        # Cleanup task reference
        self._cleanup_task = None
        self._running = True
        
        logger.info("✅ MatchmakingService (Simple version) started")
    
    async def start_cleanup(self):
        """
        Start the automatic cleanup task for expired games.
        """
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("✅ Cleanup task started")
    
    async def _cleanup_loop(self):
        """
        Background task that periodically cleans up expired games.
        Runs every 60 seconds.
        """
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                self._cleanup_expired()
            except asyncio.CancelledError:
                logger.info("⏹️ Cleanup task stopped")
                break
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")
    
    def _cleanup_expired(self):
        """
        Remove expired games from active games.
        """
        expired_games = []
        
        # Find expired games
        for game_id, game in self.active_games.items():
            try:
                if game.is_expired():
                    expired_games.append(game_id)
            except AttributeError:
                # If is_expired method doesn't exist, keep the game
                logger.warning(f"⚠️ Game {game_id} has no is_expired method")
                continue
        
        # Remove expired games
        for game_id in expired_games:
            logger.info(f"🗑️ Removed expired game: {game_id}")
            del self.active_games[game_id]
    
    def add_to_queue(self, user_id: int, chat_id: int, username: str = None) -> bool:
        """
        Add a player to the matchmaking queue.
        
        Args:
            user_id: Telegram user ID
            chat_id: Chat ID where the player is
            username: Player's display name
            
        Returns:
            bool: True if added successfully, False if already in queue
        """
        # Check if player is already in queue
        if user_id in self.waiting_players:
            return False
        
        # Add player to queue
        self.waiting_players[user_id] = {
            "chat_id": chat_id,
            "username": username or f"Player_{user_id}",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"➕ Player {user_id} added to queue. Queue size: {len(self.waiting_players)}")
        return True
    
    def remove_from_queue(self, user_id: int) -> bool:
        """
        Remove a player from the matchmaking queue.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if removed successfully
        """
        if user_id in self.waiting_players:
            del self.waiting_players[user_id]
            logger.info(f"➖ Player {user_id} removed from queue. Queue size: {len(self.waiting_players)}")
            return True
        return False
    
    def find_match(self) -> Optional[Tuple[str, List[Dict]]]:
        """
        Find a match for players in the queue.
        Creates a new game with 2-4 players.
        
        Returns:
            Optional[Tuple[str, List[Dict]]]: (game_id, players_data) or None
        """
        # Need at least 2 players
        if len(self.waiting_players) < 2:
            return None
        
        # Get players from queue (up to 4)
        players = list(self.waiting_players.items())
        
        if len(players) >= 4:
            matched = players[:4]
        else:
            matched = players[:max(2, len(players))]
        
        # Remove matched players from queue
        for user_id, _ in matched:
            del self.waiting_players[user_id]
        
        # Create new game
        game_id = str(uuid.uuid4())[:8]
        game = LudoGame(game_id)
        
        # Add players to game
        players_data = []
        for user_id, data in matched:
            game.add_player(user_id, data["username"])
            players_data.append({
                "user_id": user_id,
                "username": data["username"],
                "chat_id": data["chat_id"]
            })
        
        # Start the game
        game.start_game()
        self.active_games[game_id] = game
        
        logger.info(f"🎮 New game created: {game_id} with {len(players_data)} players")
        return game_id, players_data
    
    def get_game(self, game_id: str) -> Optional[LudoGame]:
        """
        Get a game by its ID.
        
        Args:
            game_id: Game identifier
            
        Returns:
            Optional[LudoGame]: Game instance or None
        """
        return self.active_games.get(game_id)
    
    def get_game_by_player(self, user_id: int) -> Optional[LudoGame]:
        """
        Get the game a player is currently in.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Optional[LudoGame]: Game instance or None
        """
        for game in self.active_games.values():
            if game.get_player(user_id):
                return game
        return None
    
    def get_waiting_count(self) -> int:
        """
        Get the number of players waiting in queue.
        
        Returns:
            int: Number of waiting players
        """
        return len(self.waiting_players)
    
    def get_active_games_count(self) -> int:
        """
        Get the number of active games.
        
        Returns:
            int: Number of active games
        """
        return len(self.active_games)
    
    def get_queue_players(self) -> List[Dict]:
        """
        Get all players currently in queue.
        
        Returns:
            List[Dict]: List of player data
        """
        return list(self.waiting_players.values())
    
    def cancel_game(self, game_id: str) -> bool:
        """
        Cancel an active game.
        
        Args:
            game_id: Game identifier
            
        Returns:
            bool: True if game was cancelled
        """
        if game_id in self.active_games:
            game = self.active_games[game_id]
            game.status = "cancelled"
            del self.active_games[game_id]
            logger.info(f"❌ Game {game_id} cancelled")
            return True
        return False
    
    def cancel_all_games(self):
        """
        Cancel all active games.
        Used during shutdown.
        """
        for game_id in list(self.active_games.keys()):
            self.cancel_game(game_id)
        logger.info("❌ All games cancelled")
    
    def clear_queue(self):
        """
        Clear all players from the queue.
        Used during shutdown.
        """
        self.waiting_players.clear()
        logger.info("🧹 Queue cleared")
    
    def shutdown(self):
        """
        Shutdown the matchmaking service.
        Cancels cleanup task and cleans up resources.
        """
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Clean up games and queue
        self.cancel_all_games()
        self.clear_queue()
        
        logger.info("🛑 MatchmakingService shutdown complete")
    
    def get_stats(self) -> Dict:
        """
        Get service statistics.
        
        Returns:
            Dict: Service statistics
        """
        return {
            "active_games": len(self.active_games),
            "waiting_players": len(self.waiting_players),
            "total_games_created": len(self.active_games),  # Total since last restart
        }