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

### Authentication Routes (*Proposed*)

#### Create Account
- **Route**: `/create-account`
- **Method**: `POST`
- **Purpose**: Register a new user
- **Request Format**:
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
    "user_id": integer
}
```

#### Login
- **Route**: `/login`
- **Method**: `POST`
- **Purpose**: Verify user credentials
- **Request Format**:
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
    "user_id": integer
}
```

### Portfolio Routes

#### View Portfolio
- **Route**: `/portfolio/<user_id>`
- **Method**: `GET`
- **Purpose**: Get user's current portfolio
- **Response Format**:
```json
{
    "holdings": [
        {
            "symbol": "string",
            "quantity": integer,
            "current_price": float,
            "total_value": float
        }
    ],
    "total_portfolio_value": float
}
```

#### Buy Stock
- **Route**: `/portfolio/buy`
- **Method**: `POST`
- **Purpose**: Purchase shares of a stock
- **Request Format**:
```json
{
    "user_id": integer,
    "symbol": "string",
    "quantity": integer
}
```
- **Response Format**:
```json
{
    "message": "Purchase successful",
    "transaction_id": integer,
    "price": float,
    "total_cost": float
}
```

#### Sell Stock
- **Route**: `/portfolio/sell`
- **Method**: `POST`
- **Purpose**: Sell shares of a stock
- **Request Format**:
```json
{
    "user_id": integer,
    "symbol": "string",
    "quantity": integer
}
```
- **Response Format**:
```json
{
    "message": "Sale successful",
    "transaction_id": integer,
    "price": float,
    "total_proceeds": float
}
```

### Stock Information Routes

#### Look Up Stock
- **Route**: `/stock/<symbol>`
- **Method**: `GET`
- **Purpose**: Get detailed stock information
- **Response Format**:
```json
{
    "symbol": "string",
    "company_name": "string",
    "current_price": float,
    "day_high": float,
    "day_low": float,
    "volume": integer
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
python3 -m pytest
```

## Contributing
1. Clone the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
