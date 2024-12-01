from contextlib import contextmanager
import logging
import os
import sqlite3
from app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

# load the db path from the environment with a default value
DB_PATH = os.getenv("DB_PATH", "./sql/stock_trading.db")

def check_database_connection():
    """Check the database connection
    
    Raises:
        Exception: If the database connection is not OK
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # This ensures the connection is actually active
        cursor.execute("SELECT 1;")
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

def check_tables_exist():
    """Check if all required tables exist
    
    Raises:
        Exception: If any required table does not exist
    """
    required_tables = ['users', 'portfolio', 'transactions']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for table in required_tables:
            try:
                cursor.execute(f"SELECT 1 FROM {table} LIMIT 1;")
                logger.info(f"Table '{table}' exists")
            except sqlite3.Error as e:
                error_message = f"Table '{table}' check error: {e}"
                logger.error(error_message)
                raise Exception(error_message) from e
                
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Database check error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite database connection.
    
    Yields:
        sqlite3.Connection: The SQLite connection object.
    
    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Return dictionary-like objects for rows
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error("Database connection error: %s", str(e))
        raise e
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

def execute_query(query, params=None):
    """
    Execute a SQL query and return the results.
    
    Args:
        query (str): The SQL query to execute
        params (tuple, optional): Parameters for the query. Defaults to None.
    
    Returns:
        list: The query results
        
    Raises:
        sqlite3.Error: If there's a database error
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            raise