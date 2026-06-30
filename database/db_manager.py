"""
Database Manager Module
Handles all database operations for the Ludo bot using SQLAlchemy ORM.
Manages users, game history, and game sessions.
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)

# Create declarative base for ORM models
Base = declarative_base()


class User(Base):
    """
    User model representing bot users.
    Stores user information and game statistics.
    """
    __tablename__ = 'users'
    
    # Primary key and Telegram user ID
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Telegram user ID
    username = Column(String(100))                          # Telegram username
    first_name = Column(String(100))                        # User's first name
    last_name = Column(String(100))                         # User's last name
    created_at = Column(DateTime, default=datetime.utcnow)  # Registration date
    
    # Game statistics
    total_games = Column(Integer, default=0)                # Total games played
    wins = Column(Integer, default=0)                       # Number of wins
    losses = Column(Integer, default=0)                     # Number of losses
    score = Column(Integer, default=0)                      # Total score (10 per win)
    
    # User status
    is_banned = Column(Boolean, default=False)              # Ban status
    
    # Relationships
    games = relationship("GameHistory", back_populates="player")


class GameHistory(Base):
    """
    Game history model storing individual game results for each player.
    """
    __tablename__ = 'game_history'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(50), nullable=False)            # Unique game identifier
    player_id = Column(Integer, ForeignKey('users.id'))     # Reference to user
    result = Column(String(20))                             # win, loss, draw
    position = Column(Integer)                              # Player's rank in game
    played_at = Column(DateTime, default=datetime.utcnow)   # Game date/time
    game_data = Column(JSON)                                # Full game state as JSON
    
    # Relationships
    player = relationship("User", back_populates="games")


class GameSession(Base):
    """
    Game session model for tracking active games.
    """
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, nullable=False)  # Session identifier
    game_id = Column(String(50))                                   # Reference to game
    players = Column(JSON)                                         # List of player IDs
    status = Column(String(20))                                    # waiting, playing, finished
    created_at = Column(DateTime, default=datetime.utcnow)         # Session start time
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    """
    Main database manager class handling all database operations.
    Provides CRUD operations for users, games, and statistics.
    """
    
    def __init__(self):
        """
        Initialize database connection and create tables if they don't exist.
        Supports SQLite (with thread-safe mode) and PostgreSQL.
        """
        # Configure engine based on database type
        if settings.DATABASE_URL.startswith('sqlite'):
            # SQLite with thread-safe mode for async operations
            self.engine = create_engine(
                settings.DATABASE_URL,
                echo=True,  # Log SQL queries (set to False in production)
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL or other databases
            self.engine = create_engine(
                settings.DATABASE_URL,
                echo=True
            )
        
        # Create all tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
        logger.info("✅ Database initialized successfully")
    
    def get_session(self):
        """
        Get a new database session.
        
        Returns:
            Session: SQLAlchemy session object
        """
        return self.Session()
    
    def save_user(self, user_id: int, username: str = None, 
                  first_name: str = None, last_name: str = None) -> User:
        """
        Save or update a user in the database.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username (optional)
            first_name: User's first name (optional)
            last_name: User's last name (optional)
            
        Returns:
            User: Saved user object
        """
        session = self.get_session()
        try:
            # Check if user already exists
            user = session.query(User).filter_by(user_id=user_id).first()
            
            if not user:
                # Create new user
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                logger.info(f"✅ New user registered: {user_id} ({username})")
            else:
                # Update existing user with new data
                if username:
                    user.username = username
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                logger.info(f"🔄 User updated: {user_id} ({username})")
            
            session.commit()
            return user
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error saving user {user_id}: {e}")
            raise e
        finally:
            session.close()
    
    def get_user(self, user_id: int) -> User:
        """
        Get a user by their Telegram ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User: User object or None if not found
        """
        session = self.get_session()
        try:
            return session.query(User).filter_by(user_id=user_id).first()
        finally:
            session.close()
    
    def save_game_result(self, game_id: str, player_id: int, 
                         result: str, position: int, game_data: dict):
        """
        Save a game result and update user statistics.
        
        Args:
            game_id: Unique game identifier
            player_id: User ID (from users table, not Telegram ID)
            result: 'win', 'loss', or 'draw'
            position: Player's rank in the game (1st, 2nd, etc.)
            game_data: Full game state as dictionary
        """
        session = self.get_session()
        try:
            # Create game history entry
            history = GameHistory(
                game_id=game_id,
                player_id=player_id,
                result=result,
                position=position,
                game_data=game_data
            )
            session.add(history)
            
            # Update user statistics
            user = session.query(User).filter_by(id=player_id).first()
            if user:
                user.total_games += 1
                if result == 'win':
                    user.wins += 1
                    user.score += 10  # 10 points per win
                elif result == 'loss':
                    user.losses += 1
                logger.info(f"📊 User {user.user_id} stats updated: +{result}")
            
            session.commit()
            logger.info(f"✅ Game result saved for game {game_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error saving game result: {e}")
            raise e
        finally:
            session.close()
    
    def get_user_stats(self, user_id: int) -> dict:
        """
        Get user statistics by Telegram ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            dict: Dictionary with user statistics or empty dict if not found
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return {}
            
            return {
                "total_games": user.total_games,
                "wins": user.wins,
                "losses": user.losses,
                "score": user.score,
                "win_rate": (user.wins / user.total_games * 100) if user.total_games > 0 else 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats for user {user_id}: {e}")
            return {}
        finally:
            session.close()
    
    def get_game_history(self, user_id: int, limit: int = 10) -> list:
        """
        Get recent game history for a user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of games to return
            
        Returns:
            list: List of game history entries
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return []
            
            games = (session.query(GameHistory)
                    .filter_by(player_id=user.id)
                    .order_by(GameHistory.played_at.desc())
                    .limit(limit)
                    .all())
            
            return games
        finally:
            session.close()
    
    def save_game_session(self, session_id: str, game_id: str, 
                          players: list, status: str):
        """
        Save an active game session.
        
        Args:
            session_id: Unique session identifier
            game_id: Game identifier
            players: List of player IDs (Telegram IDs)
            status: Current game status (waiting, playing, finished)
        """
        session = self.get_session()
        try:
            game_session = GameSession(
                session_id=session_id,
                game_id=game_id,
                players=json.dumps(players),
                status=status
            )
            session.add(game_session)
            session.commit()
            logger.info(f"✅ Game session saved: {session_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error saving game session: {e}")
            raise e
        finally:
            session.close()
    
    def update_game_session_status(self, session_id: str, status: str):
        """
        Update game session status.
        
        Args:
            session_id: Session identifier
            status: New status (waiting, playing, finished)
        """
        session = self.get_session()
        try:
            game_session = session.query(GameSession).filter_by(session_id=session_id).first()
            if game_session:
                game_session.status = status
                game_session.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"🔄 Session {session_id} status updated to {status}")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error updating session: {e}")
            raise e
        finally:
            session.close()
    
    def get_top_players(self, limit: int = 10) -> list:
        """
        Get top players by score.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            list: List of top players with their stats
        """
        session = self.get_session()
        try:
            players = (session.query(User)
                      .filter_by(is_banned=False)
                      .order_by(User.score.desc())
                      .limit(limit)
                      .all())
            
            return [{
                "username": p.username or f"Player_{p.user_id}",
                "score": p.score,
                "wins": p.wins,
                "games": p.total_games
            } for p in players]
        finally:
            session.close()


# Create a global database instance for easy importing
db = DatabaseManager()