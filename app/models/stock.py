import requests
import logging
from datetime import datetime, timedelta
from app.config import ALPHA_VANTAGE_API_KEY
from app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class StockAPI:
    def __init__(self):
        """
        Initialize the StockAPI with Alpha Vantage credentials and setup.
        
        Raises:
            ValueError: If the Alpha Vantage API key is not configured.
        """
        self.api_key = ALPHA_VANTAGE_API_KEY
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not found in environment variables")
        
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}  # Simple in-memory cache for stock data
        self.cache_duration = timedelta(minutes=15)  # Cache data for 15 minutes

    def _get_cached_data(self, cache_key):
        """
        Retrieve cached data if it exists and is still valid
        
        Args:
            cache_key (str): The key to look up in cache
            
        Returns:
            dict: Cached data if valid, None otherwise
        """
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                logger.debug(f"Cache hit for {cache_key}")
                return data
            else:
                logger.debug(f"Cache expired for {cache_key}")
                del self.cache[cache_key]
        return None

    def _cache_data(self, cache_key, data):
        """
        Store data in cache with current timestamp
        
        Args:
            cache_key (str): The key to store the data under
            data (dict): The data to cache
        """
        self.cache[cache_key] = (data, datetime.now())
        logger.debug(f"Cached data for {cache_key}")

    def get_stock_price(self, symbol):
        """
        Get the current price and other data for a stock using TIME_SERIES_DAILY
        
        Args:
            symbol (str): The stock symbol to look up
                
        Returns:
            dict: Latest stock price information
                
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response is invalid
        """
        cache_key = f"price_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key
            }
                
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Time Series (Daily)" not in data:
                logger.error(f"Invalid response format for {symbol}: {data}")
                raise ValueError(f"Invalid response for symbol {symbol}")

            # Get the most recent day's data
            daily_data = data["Time Series (Daily)"]
            latest_date = sorted(daily_data.keys())[-1]
            latest_data = daily_data[latest_date]
            
            result = {
                'symbol': symbol,
                'date': latest_date,
                'open': float(latest_data['1. open']),
                'high': float(latest_data['2. high']),
                'low': float(latest_data['3. low']),
                'close': float(latest_data['4. close']),
                'volume': int(latest_data['5. volume'])
            }

            self._cache_data(cache_key, result)
            return result

        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {str(e)}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response for {symbol}: {str(e)}")
            raise ValueError(f"Unable to get price for {symbol}")

    def get_company_info(self, symbol):
        """
        Get detailed company information using OVERVIEW endpoint
        
        Args:
            symbol (str): The stock symbol to look up
                
        Returns:
            dict: Company information as returned by the API
                
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response is invalid
        """
        cache_key = f"info_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
                
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Check if we got a valid response
            if not data or "Symbol" not in data:
                logger.error(f"Invalid response format for {symbol}: {data}")
                raise ValueError(f"Invalid response for symbol {symbol}")

            # Convert numeric values where appropriate
            numeric_fields = [
                'MarketCapitalization', 'EBITDA', 'PERatio', 'PEGRatio', 
                'BookValue', 'DividendPerShare', 'DividendYield', 'EPS',
                'RevenuePerShareTTM', 'ProfitMargin', 'OperatingMarginTTM',
                'ReturnOnAssetsTTM', 'ReturnOnEquityTTM', 'RevenueTTM',
                'GrossProfitTTM', 'DilutedEPSTTM', 'QuarterlyEarningsGrowthYOY',
                'QuarterlyRevenueGrowthYOY', 'AnalystTargetPrice', 'TrailingPE',
                'ForwardPE', 'PriceToSalesRatioTTM', 'PriceToBookRatio',
                'EVToRevenue', 'EVToEBITDA', 'Beta', '52WeekHigh', '52WeekLow',
                '50DayMovingAverage', '200DayMovingAverage', 'SharesOutstanding'
            ]

            result = data.copy()  # Start with a copy of all data
            
            # Convert numeric strings to appropriate types
            for field in numeric_fields:
                try:
                    if field in result and result[field]:
                        result[field] = float(result[field])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field} value '{result[field]}' for {symbol}")

            self._cache_data(cache_key, result)
            return result

        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {str(e)}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response for {symbol}: {str(e)}")
            raise ValueError(f"Unable to get company info for {symbol}")

    def get_historical_data(self, symbol, outputsize='compact'):
        """
        Get historical price data for a stock using TIME_SERIES_DAILY
        
        Args:
            symbol (str): The stock symbol to look up
            outputsize (str): Amount of data to retrieve ('compact' or 'full')
                            compact = latest 100 data points
                            full = 20+ years of historical data
            
        Returns:
            dict: Historical price data
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response is invalid or parameters are incorrect
        """
        cache_key = f"historical_{symbol}_{outputsize}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            if outputsize not in ['compact', 'full']:
                raise ValueError("outputsize must be either 'compact' or 'full'")
            
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "Time Series (Daily)" not in data:
                raise ValueError(f"Invalid response for symbol {symbol}")

            time_series = data["Time Series (Daily)"]
            result = {
                'symbol': symbol,
                'data': [{
                    'date': date,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                } for date, values in time_series.items()]
            }

            self._cache_data(cache_key, result)
            return result

        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {str(e)}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response for {symbol}: {str(e)}")
            raise ValueError(f"Unable to get historical data for {symbol}")

    def validate_symbol(self, symbol):
        """
        Validate if a stock symbol exists
        
        Args:
            symbol (str): The stock symbol to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.get_stock_price(symbol)
            return True
        except (requests.RequestException, ValueError):
            return False
