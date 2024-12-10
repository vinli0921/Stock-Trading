import pytest
import requests

from app.models.stock import StockAPI

@pytest.fixture
def stock_api():
    """Fixture to provide a new instance of StockAPI for each test."""
    return StockAPI()

@pytest.fixture
def sample_symbol1():
    return "AAPL"

@pytest.fixture
def sample_symbol2():
    return "GOOGL"

######################################################
#
#    Stock Price Functions Test Cases
#
######################################################

def test_get_stock_price_success(mocker, stock_api, sample_symbol1):
    """Test successfully getting current stock price."""
    mock_response = {
        "Time Series (Daily)": {
            "2024-12-10": {
                "1. open": "185.23",
                "2. high": "186.45",
                "3. low": "184.89",
                "4. close": "186.01",
                "5. volume": "45678912"
            }
        }
    }
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = stock_api.get_stock_price(sample_symbol1)
    
    assert result["symbol"] == sample_symbol1
    assert result["open"] == 185.23
    assert result["high"] == 186.45
    assert result["low"] == 184.89
    assert result["close"] == 186.01
    assert result["volume"] == 45678912

def test_get_stock_price_invalid_symbol(mocker, stock_api):
    """Test error when requesting an invalid stock symbol."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Error Message": "Invalid API call"}
    
    with pytest.raises(ValueError, match="Unable to get price for INVALID"):
        stock_api.get_stock_price("INVALID")

def test_get_stock_price_api_error(mocker, stock_api, sample_symbol1):
    """Test handling of API request failure."""
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.RequestException("API Error")
    
    with pytest.raises(requests.RequestException, match="API Error"):
        stock_api.get_stock_price(sample_symbol1)

def test_get_stock_price_cache(mocker, stock_api, sample_symbol1):
    """Test that caching works for stock price data."""
    mock_response = {
        "Time Series (Daily)": {
            "2024-12-10": {
                "1. open": "185.23",
                "2. high": "186.45",
                "3. low": "184.89",
                "4. close": "186.01",
                "5. volume": "45678912"
            }
        }
    }
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # First call should hit the API
    result1 = stock_api.get_stock_price(sample_symbol1)
    
    # Second call should use cache
    result2 = stock_api.get_stock_price(sample_symbol1)
    
    assert result1 == result2
    mock_get.assert_called_once()  # API should only be called once

######################################################
#
#    Company Info Functions Test Cases
#
######################################################

def test_get_company_info_success(mocker, stock_api, sample_symbol1):
    """Test successfully getting company information."""
    mock_response = {
        "Symbol": "AAPL",
        "Name": "Apple Inc",
        "Description": "Apple Inc. designs, manufactures, and markets smartphones",
        "MarketCapitalization": "2000000000",
        "PERatio": "25.6",
        "EPS": "5.89",
        "DividendYield": "0.65",
        "52WeekHigh": "190.23",
        "52WeekLow": "124.17"
    }
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = stock_api.get_company_info(sample_symbol1)
    
    assert result["Symbol"] == sample_symbol1
    assert result["Name"] == "Apple Inc"
    assert result["MarketCapitalization"] == 2000000000.0
    assert result["PERatio"] == 25.6
    assert result["EPS"] == 5.89
    assert result["DividendYield"] == 0.65

def test_get_company_info_invalid_symbol(mocker, stock_api):
    """Test error when requesting company info for an invalid symbol."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {}
    
    with pytest.raises(ValueError, match="Unable to get company info for INVALID"):
        stock_api.get_company_info("INVALID")

def test_get_company_info_api_error(mocker, stock_api, sample_symbol1):
    """Test handling of API request failure for company info."""
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.RequestException("API Error")
    
    with pytest.raises(requests.RequestException, match="API Error"):
        stock_api.get_company_info(sample_symbol1)

######################################################
#
#    Historical Data Functions Test Cases
#
######################################################

def test_get_historical_data_success(mocker, stock_api, sample_symbol1):
    """Test successfully getting historical data."""
    mock_response = {
        "Time Series (Daily)": {
            "2024-12-10": {
                "1. open": "185.23",
                "2. high": "186.45",
                "3. low": "184.89",
                "4. close": "186.01",
                "5. volume": "45678912"
            },
            "2024-12-09": {
                "1. open": "184.53",
                "2. high": "185.67",
                "3. low": "183.78",
                "4. close": "185.23",
                "5. volume": "43567891"
            }
        }
    }
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = stock_api.get_historical_data(sample_symbol1)
    
    assert result["symbol"] == sample_symbol1
    assert len(result["data"]) == 2
    assert result["data"][0]["date"] == "2024-12-10"
    assert result["data"][0]["open"] == 185.23
    assert result["data"][1]["date"] == "2024-12-09"
    assert result["data"][1]["close"] == 185.23

def test_get_historical_data_invalid_outputsize(stock_api, sample_symbol1):
    """Test error when providing invalid outputsize parameter."""
    with pytest.raises(ValueError, match="Unable to get historical data for AAPL"):
        stock_api.get_historical_data(sample_symbol1, outputsize="invalid")

def test_get_historical_data_api_error(mocker, stock_api, sample_symbol1):
    """Test handling of API request failure for historical data."""
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.RequestException("API Error")
    
    with pytest.raises(requests.RequestException, match="API Error"):
        stock_api.get_historical_data(sample_symbol1)

######################################################
#
#    Symbol Validation Function Test Cases
#
######################################################

def test_validate_symbol_success(mocker, stock_api, sample_symbol1):
    """Test successful validation of a valid stock symbol."""
    mock_response = {
        "Time Series (Daily)": {
            "2024-12-10": {
                "1. open": "185.23",
                "2. high": "186.45",
                "3. low": "184.89",
                "4. close": "186.01",
                "5. volume": "45678912"
            }
        }
    }
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    assert stock_api.validate_symbol(sample_symbol1) is True

def test_validate_symbol_invalid(mocker, stock_api):
    """Test validation of an invalid stock symbol."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Error Message": "Invalid API call"}
    
    assert stock_api.validate_symbol("INVALID") is False

def test_validate_symbol_api_error(mocker, stock_api, sample_symbol1):
    """Test symbol validation when API request fails."""
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.RequestException("API Error")
    
    assert stock_api.validate_symbol(sample_symbol1) is False