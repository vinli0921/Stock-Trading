# Stock Trading Application

## Overview
A Flask-based web application that provides a backend API for managing stock portfolios and executing trades. The application integrates with Alpha Vantage API for real-time stock data and provides user authentication, portfolio management, and transaction tracking.

## Features
- User account management (create account, login, update password)
- Portfolio management (view holdings, calculate total value)
- Stock trading (buy and sell stocks)
- Stock information lookup (current price, historical data)
- Real-time portfolio value calculation

## Tech Stack
- Python 3.11
- Flask (Web Framework)
- SQLite (Database)
- SQLAlchemy (ORM)
- Alpha Vantage API (Stock Data)
- Docker (Containerization)

## Project Structure
```
stock-trading/
├── app/
│   ├── models/                     # Database models
│   ├── routes/                     # API endpoints
│   └── utils/                      # Utility functions
├── sql/                            # Database setup
│   ├── create_db.sh
│   ├── create_users_table.sql
│   └── create_portfolio_table.sql
├── tests/                          # Unit tests
│   ├── test_auth.py
│   ├── test_portfolio.py
│   └── test_stock.py
├── .env                            # Environment variables
├── Dockerfile                      # Docker configuration
├── entrypoint.sh                   # Shell script to create application entry point
├── README.md                       # Project documentation
├── requirements.txt                # Python dependencies
├── setup_venv.sh                   # Shell script to create and start virtual env
└── smoketest.sh                    # Smoke test script
```

## Setup Instructions

### Alpha Vantage
1. Get your free API key at:\
[API signup](https://www.alphavantage.co/)

2. API documentation:\
[Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)\
Please look through the documentation thoroughly to understand how to use the requests

### Local Development
1. Create a virtual environment and install dependencies:
```bash
chmod +x setup_venv.sh
source setup_venv.sh
```

2. Create `.env` file:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
DB_PATH=./sql/stock_trading.db
CREATE_DB=true
```

3. Initialize the database:
```bash
chmod +x sql/create_db.sh
./sql/create_db.sh
```

4. Run the application:
```bash
python3 -m app.py
```

### Docker Setup
1. Build the Docker image:
```bash
docker build -t stock-trading-app .
```

2. Run the container:
```bash
docker run -p 5000:5000 -v $(pwd)/db:/app/db stock-trading-app
```

## API Documentation

## Base URL
`http://localhost:5001/api`

## Health Check Routes

### Check Service Health
- **Route Name and Path**: `GET /health`
- **Purpose**: Verify the application service is running and healthy
- **Response Format**:
```json
{
    "status": "healthy"
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/health"
```
```json
{
    "status": "healthy"
}
```

### Check Database Health
- **Route Name and Path**: `GET /db-check`
- **Purpose**: Verify database connection is healthy
- **Response Format**:
```json
{
    "database_status": "healthy"
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/db-check"
```
```json
{
    "database_status": "healthy"
}
```

## Authentication Routes

### Create Account
- **Route Name and Path**: `POST /users/create-account`
- **Purpose**: Register a new user account
- **Request Body Format**:
```json
{
    "username": "string",
    "password": "string"
}
```
- **Response Format**:
```json
{
    "message": "Account created successfully",
    "user_id": "integer"
}
```
- **Example**:
```bash
curl -X POST "http://localhost:5001/api/users/create-account" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123"}'
```
```json
{
    "message": "Account created successfully",
    "user_id": 1
}
```

### Login
- **Route Name and Path**: `POST /users/login`
- **Purpose**: Authenticate user credentials
- **Request Body Format**:
```json
{
    "username": "string",
    "password": "string"
}
```
- **Response Format**:
```json
{
    "message": "Login successful",
    "user_id": "integer"
}
```
- **Example**:
```bash
curl -X POST "http://localhost:5001/api/users/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123"}'
```
```json
{
    "message": "Login successful",
    "user_id": 1
}
```

### Update Password
- **Route Name and Path**: `POST /users/update-password`
- **Purpose**: Change user's password
- **Request Body Format**:
```json
{
    "user_id": "integer",
    "current_password": "string",
    "new_password": "string"
}
```
- **Response Format**:
```json
{
    "message": "Password updated successfully"
}
```
- **Example**:
```bash
curl -X POST "http://localhost:5001/api/users/update-password" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "current_password": "password123", "new_password": "newpassword123"}'
```
```json
{
    "message": "Password updated successfully"
}
```

### Clear Users
- **Route Name and Path**: `DELETE /users/clear`
- **Purpose**: Remove all users (development/testing)
- **Response Format**:
```json
{
    "status": "success",
    "message": "All users cleared"
}
```
- **Example**:
```bash
curl -X DELETE "http://localhost:5001/api/users/clear"
```
```json
{
    "status": "success",
    "message": "All users cleared"
}
```

## Portfolio Routes

### Get Portfolio
- **Route Name and Path**: `GET /portfolio/{user_id}`
- **Purpose**: Retrieve user's current portfolio holdings
- **Parameters**: 
  - Path: `user_id` (integer)
- **Response Format**:
```json
{
    "status": "success",
    "portfolio": {
        // Portfolio details specific to implementation
    }
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/portfolio/1"
```
```json
{
    "status": "success",
    "portfolio": {
        "holdings": [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "current_price": 150.50,
                "total_value": 1505.00
            }
        ]
    }
}
```

### Buy Stock
- **Route Name and Path**: `POST /portfolio/buy`
- **Purpose**: Purchase shares of a stock
- **Request Body Format**:
```json
{
    "user_id": "integer",
    "symbol": "string",
    "quantity": "integer"
}
```
- **Response Format**:
```json
{
    "status": "success",
    "transaction": {
        // Transaction details
    }
}
```
- **Example**:
```bash
curl -X POST "http://localhost:5001/api/portfolio/buy" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "symbol": "AAPL", "quantity": 10}'
```
```json
{
    "status": "success",
    "transaction": {
        "symbol": "AAPL",
        "quantity": 10,
        "price": 150.50,
        "total_cost": 1505.00,
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

### Sell Stock
- **Route Name and Path**: `POST /portfolio/sell`
- **Purpose**: Sell shares from portfolio
- **Request Body Format**:
```json
{
    "user_id": "integer",
    "symbol": "string",
    "quantity": "integer"
}
```
- **Response Format**:
```json
{
    "status": "success",
    "transaction": {
        // Transaction details
    }
}
```
- **Example**:
```bash
curl -X POST "http://localhost:5001/api/portfolio/sell" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "symbol": "AAPL", "quantity": 5}'
```
```json
{
    "status": "success",
    "transaction": {
        "symbol": "AAPL",
        "quantity": 5,
        "price": 151.00,
        "total_proceeds": 755.00,
        "timestamp": "2024-12-10T11:30:00Z"
    }
}
```

### Get Transaction History
- **Route Name and Path**: `GET /portfolio/history/{user_id}`
- **Purpose**: Retrieve user's trading history
- **Parameters**:
  - Path: `user_id` (integer)
- **Response Format**:
```json
{
    "status": "success",
    "history": [
        // Array of transactions
    ]
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/portfolio/history/1"
```
```json
{
    "status": "success",
    "history": [
        {
            "type": "BUY",
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.50,
            "timestamp": "2024-12-10T10:30:00Z"
        },
        {
            "type": "SELL",
            "symbol": "AAPL",
            "quantity": 5,
            "price": 151.00,
            "timestamp": "2024-12-10T11:30:00Z"
        }
    ]
}
```

### Clear Portfolios
- **Route Name and Path**: `DELETE /portfolio/clear`
- **Purpose**: Remove all portfolios (development/testing)
- **Response Format**:
```json
{
    "status": "success",
    "message": "All portfolios cleared"
}
```
- **Example**:
```bash
curl -X DELETE "http://localhost:5001/api/portfolio/clear"
```
```json
{
    "status": "success",
    "message": "All portfolios cleared"
}
```

## Stock Information Routes

### Validate Stock Symbol
- **Route Name and Path**: `GET /stock/{symbol}`
- **Purpose**: Verify if a stock symbol exists
- **Parameters**:
  - Path: `symbol` (string)
- **Response Format**:
```json
{
    "status": "success",
    "valid": "boolean"
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/stock/AAPL"
```
```json
{
    "status": "success",
    "valid": true
}
```

### Get Stock Price
- **Route Name and Path**: `GET /stock/price/{symbol}`
- **Purpose**: Get current stock price information
- **Parameters**:
  - Path: `symbol` (string)
- **Response Format**:
```json
{
    "status": "success",
    "price_info": {
        // Price information
    }
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/stock/price/AAPL"
```
```json
{
    "status": "success",
    "price_info": {
        "symbol": "AAPL",
        "current_price": 150.50,
        "change": 2.30,
        "change_percent": 1.55,
        "timestamp": "2024-12-10T12:00:00Z"
    }
}
```

### Get Stock History
- **Route Name and Path**: `GET /stock/history/{symbol}`
- **Purpose**: Retrieve historical price data
- **Parameters**:
  - Path: `symbol` (string)
  - Query: `outputsize` (string, "compact" or "full")
- **Response Format**:
```json
{
    "status": "success",
    "history": {
        // Historical data
    }
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/stock/history/AAPL?outputsize=compact"
```
```json
{
    "status": "success",
    "history": {
        "2024-12-10": {
            "open": 149.00,
            "high": 151.20,
            "low": 148.80,
            "close": 150.50,
            "volume": 1234567
        }
        // Additional historical data entries...
    }
}
```

### Get Company Information
- **Route Name and Path**: `GET /stock/company/{symbol}`
- **Purpose**: Get detailed company information
- **Parameters**:
  - Path: `symbol` (string)
- **Response Format**:
```json
{
    "status": "success",
    "company_info": {
        // Company details
    }
}
```
- **Example**:
```bash
curl -X GET "http://localhost:5001/api/stock/company/AAPL"
```
```json
{
    "status": "success",
    "company_info": {
        "name": "Apple Inc.",
        "description": "Technology company that designs and manufactures smartphones, computers, tablets, and wearables.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": "2.5T",
        "exchange": "NASDAQ"
    }
}
```

## Error Handling
All routes return appropriate HTTP status codes:
- 200: Successful operation
- 400: Bad request (invalid input)
- 401: Unauthorized
- 404: Resource not found
- 500: Server error

Error responses include a message explaining the error:
```json
{
    "error": "Error message description"
}
```

## Testing
Run the test suite:
```bash
python3 -m pytest tests/
```

## Contributing
1. Clone the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
