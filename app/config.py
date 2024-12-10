from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

"""Env Variables"""
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
DB_PATH = os.getenv('DB_PATH', './db/stock_trading.db')
CREATE_DB = os.getenv('CREATE_DB', 'true').lower() == 'true'