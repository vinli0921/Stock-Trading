import logging
import sqlite3
import bcrypt
from typing import Optional, Dict

from app.utils.logger import configure_logger
from app.utils.sql_utils import get_db_connection
from app.models.portfolio import PortfolioManager

logger = logging.getLogger(__name__)
configure_logger(logger)

class User:
    """User class to manage user authentication and portfolio interactions"""
    
    def __init__(self, id: int, username: str, salt: bytes, hashed_password: bytes):
        self.id = id
        self.username = username
        self._salt = salt
        self._hashed_password = hashed_password
        self._portfolio_manager = PortfolioManager()

    @classmethod
    def login(cls, username: str, password: str) -> 'User':
        """
        Authenticate user and return User instance if successful.

        Args:
            username (str): The user's username
            password (str): The user's password

        Returns:
            User: User instance if login successful

        Raises:
            ValueError: If username is invalid or password is incorrect
            sqlite3.Error: For any database errors
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                logger.info("Attempting to login user with username %s", username)

                cursor.execute(
                    "SELECT id, salt, password_hash FROM users WHERE username = ?", 
                    (username,)
                )
                row = cursor.fetchone()

                if not row:
                    logger.warning("User with username %s not found", username)
                    raise ValueError("Invalid username or password")

                user_id, salt, stored_hash = row['id'], row['salt'], row['password_hash']
                
                # Verify password
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    logger.info("Successfully logged in user: %s", username)
                    
                    # Update last login timestamp
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (user_id,)
                    )
                    conn.commit()
                    
                    return cls(user_id, username, salt, stored_hash)
                else:
                    logger.warning("Invalid password attempt for user: %s", username)
                    raise ValueError("Invalid username or password")

        except sqlite3.Error as e:
            logger.error("Database error during login: %s", str(e))
            raise

    @classmethod
    def create(cls, username: str, password: str) -> 'User':
        """
        Create a new user account.

        Args:
            username (str): The desired username
            password (str): The user's password

        Returns:
            User: New User instance

        Raises:
            ValueError: If username is invalid or already exists
            sqlite3.Error: For any database errors
        """
        if not username or not password:
            raise ValueError("Username and password are required")

        try:
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt)
                    VALUES (?, ?, ?)
                """, (username, password_hash, salt))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                logger.info("Successfully created new user: %s", username)
                return cls(user_id, username, salt, password_hash)

        except sqlite3.IntegrityError as e:
            logger.error("Failed to create user - username '%s' already exists", username)
            raise ValueError(f"Username '{username}' is already taken") from e
        except sqlite3.Error as e:
            logger.error("Database error while creating user: %s", str(e))
            raise

    def update_password(self, current_password: str, new_password: str) -> None:
        """Change the user's password"""
        if not bcrypt.checkpw(current_password.encode('utf-8'), self._hashed_password):
            raise ValueError("Current password is incorrect")

        try:
            new_salt = bcrypt.gensalt()
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), new_salt)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                    (new_hash, new_salt, self.id)
                )
                conn.commit()
            
            self._salt = new_salt
            self._hashed_password = new_hash
            logger.info("Successfully updated password for user: %s", self.username)

        except sqlite3.Error as e:
            logger.error("Database error while updating password: %s", str(e))
            raise

    # Portfolio methods
    def get_portfolio(self) -> Dict:
        """Get user's current portfolio with real-time values"""
        return self._portfolio_manager.get_portfolio(self.id)

    def buy_stock(self, symbol: str, quantity: int) -> Dict:
        """Buy shares of a stock"""
        return self._portfolio_manager.buy_stock(self.id, symbol, quantity)

    def sell_stock(self, symbol: str, quantity: int) -> Dict:
        """Sell shares of a stock"""
        return self._portfolio_manager.sell_stock(self.id, symbol, quantity)

    def get_transaction_history(self) -> Dict:
        """Get user's transaction history"""
        return self._portfolio_manager.get_transaction_history(self.id)

    @staticmethod
    def get_stock_info(symbol: str) -> Dict:
        """Get detailed information about a stock"""
        return PortfolioManager().get_stock_info(symbol)

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Retrieve user by ID"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, salt, password_hash FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                    
                return User(
                    id=row['id'],
                    username=row['username'],
                    salt=row['salt'],
                    hashed_password=row['password_hash']
                )

        except sqlite3.Error as e:
            logger.error("Database error while retrieving user: %s", str(e))
            raise