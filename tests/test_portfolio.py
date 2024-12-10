import pytest
from unittest.mock import Mock
from contextlib import contextmanager
from datetime import datetime
from app.models.portfolio import PortfolioManager
from app.models.stock import StockAPI

@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("app.models.portfolio.get_db_connection", mock_get_db_connection)

    return mock_conn

@pytest.fixture
def mock_execute_query(mocker):
    mock_exec_query = mocker.patch("app.models.portfolio.execute_query")
    mock_exec_query.return_value = []
    return mock_exec_query

@pytest.fixture
def mock_stock_api(mocker):
    mock_api = mocker.Mock(spec=StockAPI)
    mocker.patch("app.models.portfolio.StockAPI", return_value=mock_api)
    return mock_api

@pytest.fixture
def portfolio_manager(mock_stock_api):
    return PortfolioManager()

@pytest.fixture
def sample_stock_data():
    return {
        'symbol': 'AAPL',
        'date': '2024-03-06',
        'open': 100.0,
        'high': 105.0,
        'low': 99.0,
        'close': 102.0,
        'volume': 1000000
    }

@pytest.fixture
def sample_portfolio_data():
    return [
        {'symbol': 'AAPL', 'quantity': 10, 'average_price': 100.0},
        {'symbol': 'GOOGL', 'quantity': 5, 'average_price': 150.0}
    ]

######################################################
#
#    Portfolio Retrieval Function Test Cases
#
######################################################

def test_get_portfolio_empty(portfolio_manager, mock_execute_query):
    mock_execute_query.return_value = []
    portfolio = portfolio_manager.get_portfolio(1)
    assert portfolio['holdings'] == []
    assert portfolio['total_value'] == 0.0
    mock_execute_query.assert_called()

def test_get_portfolio_with_holdings(portfolio_manager, mock_execute_query, mock_stock_api, sample_portfolio_data, sample_stock_data):
    mock_execute_query.return_value = sample_portfolio_data
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    portfolio = portfolio_manager.get_portfolio(1)
    assert len(portfolio['holdings']) == 2
    assert portfolio['holdings'][0]['symbol'] == 'AAPL'
    assert portfolio['holdings'][0]['quantity'] == 10
    assert portfolio['total_value'] > 0
    mock_execute_query.assert_called()

def test_get_portfolio_api_failure(portfolio_manager, mock_execute_query, mock_stock_api, sample_portfolio_data):
    # Suppose one symbol fails
    mock_execute_query.return_value = sample_portfolio_data
    # Let get_stock_price raise an exception for the first symbol
    mock_stock_api.get_stock_price.side_effect = Exception("API Failure")
    with pytest.raises(Exception, match="API Failure"):
        portfolio_manager.get_portfolio(1)

######################################################
#
#    Buy/Sell Stock Functions Test Cases
#
######################################################

def test_buy_stock_success(portfolio_manager, mock_execute_query, mock_db_connection, mock_stock_api, sample_stock_data):
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    mock_execute_query.return_value = []
    result = portfolio_manager.buy_stock(1, 'AAPL', 10)
    assert result['symbol'] == 'AAPL'
    assert result['quantity'] == 10
    assert result['price'] == 102.0
    assert isinstance(result['timestamp'], datetime)
    assert mock_db_connection.cursor().execute.called
    assert mock_db_connection.commit.called

def test_buy_stock_invalid_quantity(portfolio_manager):
    with pytest.raises(ValueError, match="Quantity must be positive"):
        portfolio_manager.buy_stock(1, 'AAPL', 0)

    with pytest.raises(ValueError, match="Quantity must be positive"):
        portfolio_manager.buy_stock(1, 'AAPL', -5)

def test_buy_stock_nonexistent_symbol(portfolio_manager, mock_stock_api):
    # If symbol doesn't exist, let get_stock_price raise KeyError or return None
    mock_stock_api.get_stock_price.side_effect = KeyError("Symbol not found")
    with pytest.raises(KeyError, match="Symbol not found"):
        portfolio_manager.buy_stock(1, 'FAKE', 10)

def test_sell_stock_success(portfolio_manager, mock_execute_query, mock_db_connection, mock_stock_api, sample_stock_data):
    mock_execute_query.side_effect = [
        [{'quantity': 10}],  # check shares
        []  # subsequent queries
    ]
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    result = portfolio_manager.sell_stock(1, 'AAPL', 5)
    assert result['symbol'] == 'AAPL'
    assert result['quantity'] == 5
    assert result['price'] == 102.0
    assert isinstance(result['timestamp'], datetime)
    assert mock_db_connection.cursor().execute.called
    assert mock_db_connection.commit.called

def test_sell_stock_insufficient_shares(portfolio_manager, mock_execute_query):
    mock_execute_query.return_value = [{'quantity': 5}]
    with pytest.raises(ValueError, match="Insufficient shares for sale"):
        portfolio_manager.sell_stock(1, 'AAPL', 10)

def test_sell_stock_nonexistent_symbol(portfolio_manager, mock_execute_query):
    # If portfolio doesn't return the symbol at all
    mock_execute_query.return_value = []
    with pytest.raises(ValueError, match="Insufficient shares for sale"):
        portfolio_manager.sell_stock(1, 'FAKE', 1)

def test_sell_stock_invalid_quantity(portfolio_manager):
    with pytest.raises(ValueError, match="Quantity must be positive"):
        portfolio_manager.sell_stock(1, 'AAPL', 0)

    with pytest.raises(ValueError, match="Quantity must be positive"):
        portfolio_manager.sell_stock(1, 'AAPL', -10)

######################################################
#
#    Stock Info and Transaction Info Functions Test Cases
#
######################################################

def test_get_transaction_history_empty(portfolio_manager, mock_execute_query):
    mock_execute_query.return_value = []
    history = portfolio_manager.get_transaction_history(1)
    assert history == []
    mock_execute_query.assert_called()

def test_get_transaction_history_non_empty(portfolio_manager, mock_execute_query):
    mock_transactions = [
        {
            'id': 1,
            'symbol': 'AAPL',
            'quantity': 10,
            'price': 100.0,
            'transaction_type': 'BUY',
            'timestamp': '2024-03-06 10:00:00'
        }
    ]
    mock_execute_query.return_value = mock_transactions
    history = portfolio_manager.get_transaction_history(1)
    assert len(history) == 1
    assert history[0]['symbol'] == 'AAPL'
    assert history[0]['type'] == 'BUY'
    mock_execute_query.assert_called()

def test_get_stock_info_full(portfolio_manager, mock_stock_api, sample_stock_data):
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    mock_stock_api.get_company_info.return_value = {'name': 'Apple Inc'}
    mock_stock_api.get_historical_data.return_value = {'data': [sample_stock_data]}
    info = portfolio_manager.get_stock_info('AAPL')
    assert 'current_price' in info
    assert 'company_info' in info
    assert 'historical_data' in info
    assert info['company_info']['name'] == 'Apple Inc'

def test_get_stock_info_missing_data(portfolio_manager, mock_stock_api):
    # Suppose company info returns empty and historical data fails
    mock_stock_api.get_stock_price.return_value = {'close': 200.0}
    mock_stock_api.get_company_info.return_value = {}
    mock_stock_api.get_historical_data.side_effect = Exception("No historical data")
    with pytest.raises(Exception, match="No historical data"):
        portfolio_manager.get_stock_info('AAPL')

def test_buy_stock_db_exception(portfolio_manager, mock_db_connection, mock_stock_api, sample_stock_data):
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    # Simulate DB failure during transaction
    mock_db_connection.cursor().execute.side_effect = Exception("DB Failure")
    with pytest.raises(Exception, match="DB Failure"):
        portfolio_manager.buy_stock(1, 'AAPL', 10)

def test_sell_stock_db_exception(portfolio_manager, mock_execute_query, mock_db_connection, mock_stock_api, sample_stock_data):
    mock_execute_query.return_value = [{'quantity': 10}]
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    mock_db_connection.cursor().execute.side_effect = Exception("DB Failure")
    with pytest.raises(Exception, match="DB Failure"):
        portfolio_manager.sell_stock(1, 'AAPL', 5)
