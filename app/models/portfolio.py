from datetime import datetime
import logging
from typing import List, Dict

from app.utils.logger import configure_logger
from app.utils.sql_utils import get_db_connection, execute_query
from app.models.stock import StockAPI

logger = logging.getLogger(__name__)
configure_logger(logger)

class PortfolioManager:
    def __init__(self):
        """Initialize the PortfolioManager with StockAPI instance"""
        self.stock_api = StockAPI()

    def get_portfolio(self, user_id: int) -> Dict:
        """
        Get user's current portfolio with real-time values
        
        Args:
            user_id: The ID of the user
            
        Returns:
            dict: Portfolio information including:
                - holdings: list of stock holdings with current values
                - total_value: current total portfolio value
        """
        try:
            # Get user's holdings from database
            query = """
                SELECT symbol, quantity, average_price
                FROM portfolio
                WHERE user_id = ? AND quantity > 0
            """
            holdings = execute_query(query, (user_id,))
            
            portfolio_data = {
                'holdings': [],
                'total_value': 0.0
            }
            
            # Get current prices and calculate values
            for holding in holdings:
                current_price = self.stock_api.get_stock_price(holding['symbol'])
                holding_value = holding['quantity'] * current_price['close']
                holding_info = {
                    'symbol': holding['symbol'],
                    'quantity': holding['quantity'],
                    'average_price': holding['average_price'],
                    'current_price': current_price['close'],
                    'total_value': holding_value,
                    'gain_loss': holding_value - (holding['quantity'] * holding['average_price'])
                }
                portfolio_data['holdings'].append(holding_info)
                portfolio_data['total_value'] += holding_value
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error getting portfolio for user {user_id}: {e}")
            raise

    def buy_stock(self, user_id: int, symbol: str, quantity: int) -> Dict:
        """
        Process a stock purchase
        
        Args:
            user_id: The ID of the user
            symbol: The stock symbol to buy
            quantity: Number of shares to buy
            
        Returns:
            dict: Transaction details
            
        Raises:
            ValueError: If quantity is invalid or symbol doesn't exist
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        try:
            # Validate symbol and get current price
            current_data = self.stock_api.get_stock_price(symbol)
            price = current_data['close']
            total_cost = price * quantity
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                try:
                    # Update portfolio
                    cursor.execute("""
                        INSERT INTO portfolio (user_id, symbol, quantity, average_price)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(user_id, symbol) DO UPDATE SET
                            quantity = quantity + ?,
                            average_price = ((average_price * quantity + ? * ?) / (quantity + ?))
                    """, (user_id, symbol, quantity, price, quantity, price, quantity, quantity))
                    
                    # Record transaction
                    cursor.execute("""
                        INSERT INTO transactions
                        (user_id, symbol, quantity, price, transaction_type)
                        VALUES (?, ?, ?, ?, 'BUY')
                    """, (user_id, symbol, quantity, price))
                    
                    transaction_id = cursor.lastrowid
                    conn.commit()
                    
                    return {
                        'transaction_id': transaction_id,
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': price,
                        'total_cost': total_cost,
                        'timestamp': datetime.now()
                    }
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error during buy transaction: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error buying stock: {e}")
            raise

    def sell_stock(self, user_id: int, symbol: str, quantity: int) -> Dict:
        """
        Process a stock sale
        
        Args:
            user_id: The ID of the user
            symbol: The stock symbol to sell
            quantity: Number of shares to sell
            
        Returns:
            dict: Transaction details
            
        Raises:
            ValueError: If quantity is invalid or user doesn't own enough shares
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        try:
            # Check if user has enough shares
            query = "SELECT quantity FROM portfolio WHERE user_id = ? AND symbol = ?"
            result = execute_query(query, (user_id, symbol))
            
            if not result or result[0]['quantity'] < quantity:
                raise ValueError("Insufficient shares for sale")
                
            # Get current price
            current_data = self.stock_api.get_stock_price(symbol)
            price = current_data['close']
            total_proceeds = price * quantity
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                try:
                    # Update portfolio
                    cursor.execute("""
                        UPDATE portfolio
                        SET quantity = quantity - ?
                        WHERE user_id = ? AND symbol = ?
                    """, (quantity, user_id, symbol))
                    
                    # Record transaction
                    cursor.execute("""
                        INSERT INTO transactions
                        (user_id, symbol, quantity, price, transaction_type)
                        VALUES (?, ?, ?, ?, 'SELL')
                    """, (user_id, symbol, quantity, price))
                    
                    transaction_id = cursor.lastrowid
                    conn.commit()
                    
                    return {
                        'transaction_id': transaction_id,
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': price,
                        'total_proceeds': total_proceeds,
                        'timestamp': datetime.now()
                    }
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error during sell transaction: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error selling stock: {e}")
            raise

    def get_transaction_history(self, user_id: int) -> List[Dict]:
        """
        Get user's transaction history
        
        Args:
            user_id: The ID of the user
            
        Returns:
            list: List of transactions
        """
        try:
            query = """
                SELECT *
                FROM transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """
            transactions = execute_query(query, (user_id,))
            
            return [{
                'transaction_id': t['id'],
                'symbol': t['symbol'],
                'quantity': t['quantity'],
                'price': t['price'],
                'type': t['transaction_type'],
                'timestamp': t['timestamp'],
                'total': t['price'] * t['quantity']
            } for t in transactions]
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            raise

    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get comprehensive stock information
        
        Args:
            symbol: The stock symbol to look up
            
        Returns:
            dict: Combined current price, company info, and historical data
        """
        try:
            current_price = self.stock_api.get_stock_price(symbol)
            company_info = self.stock_api.get_company_info(symbol)
            historical_data = self.stock_api.get_historical_data(symbol)
            
            return {
                'current_price': current_price,
                'company_info': company_info,
                'historical_data': historical_data
            }
            
        except Exception as e:
            logger.error(f"Error getting stock info: {e}")
            raise