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

    # Default empty results
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    # Patch get_db_connection where PortfolioManager uses it
    mocker.patch("app.models.portfolio.get_db_connection", mock_get_db_connection)

    return mock_conn

@pytest.fixture
def mock_execute_query(mocker):
    # Patch execute_query where PortfolioManager uses it
    # This ensures that when PortfolioManager calls execute_query,
    # it gets this mock instead of calling the real function.
    mock_exec_query = mocker.patch("app.models.portfolio.execute_query")
    # By default, return empty list
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

def test_buy_stock_success(portfolio_manager, mock_execute_query, mock_db_connection, mock_stock_api, sample_stock_data):
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    # If the code doesn't query the portfolio first, just keep empty as default
    mock_execute_query.return_value = []
    result = portfolio_manager.buy_stock(1, 'AAPL', 10)
    assert result['symbol'] == 'AAPL'
    assert result['quantity'] == 10
    assert result['price'] == sample_stock_data['close']
    assert isinstance(result['timestamp'], datetime)
    # Check that we did some DB operations
    assert mock_db_connection.cursor().execute.called
    assert mock_db_connection.commit.called

def test_buy_stock_invalid_quantity(portfolio_manager):
    with pytest.raises(ValueError, match="Quantity must be positive"):
        portfolio_manager.buy_stock(1, 'AAPL', 0)

def test_sell_stock_success(portfolio_manager, mock_execute_query, mock_db_connection, mock_stock_api, sample_stock_data):
    # First call to execute_query: return holdings
    # Second call can be empty as default
    mock_execute_query.side_effect = [
        [{'quantity': 10}],
        []
    ]
    mock_stock_api.get_stock_price.return_value = sample_stock_data
    result = portfolio_manager.sell_stock(1, 'AAPL', 5)
    assert result['symbol'] == 'AAPL'
    assert result['quantity'] == 5
    assert result['price'] == sample_stock_data['close']
    assert isinstance(result['timestamp'], datetime)
    assert mock_db_connection.cursor().execute.called
    assert mock_db_connection.commit.called

def test_sell_stock_insufficient_shares(portfolio_manager, mock_execute_query):
    mock_execute_query.return_value = [{'quantity': 5}]
    with pytest.raises(ValueError, match="Insufficient shares for sale"):
        portfolio_manager.sell_stock(1, 'AAPL', 10)
    mock_execute_query.assert_called()

def test_get_transaction_history(portfolio_manager, mock_execute_query):
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
