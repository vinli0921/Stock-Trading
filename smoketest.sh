#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Database Cleanup
#
##########################################################

clear_users() {
  echo "Clearing all users..."
  response=$(curl -s -X DELETE "$BASE_URL/users/clear")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Users cleared successfully."
  else
    echo "Failed to clear users."
    echo "Response: $response"
    exit 1
  fi
}

clear_portfolios() {
  echo "Clearing all portfolios..."
  response=$(curl -s -X DELETE "$BASE_URL/portfolio/clear")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Portfolios cleared successfully."
  else
    echo "Failed to clear portfolios."
    echo "Response: $response"
    exit 1
  fi
}

##########################################################
#
# Authentication Tests
#
##########################################################

create_account() {
  username=$1
  password=$2

  echo "Creating user ($username: $password)..."
  response=$(curl -s -X POST "$BASE_URL/users/create-account" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  if echo "$response" | grep -q '"message": "Account created successfully"'; then
    echo "User created successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to create user."
    echo "Response: $response"
    exit 1
  fi
}

login() {
  username=$1
  password=$2

  if [ "$ECHO_JSON" = true ]; then
    echo "Logging in user $username..."
  fi
  
  response=$(curl -s -X POST "$BASE_URL/users/login" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  if echo "$response" | grep -q '"message": "Login successful"'; then
    user_id=$(echo "$response" | jq -r '.user_id')
    
    if [ "$ECHO_JSON" = true ]; then
      echo "Debug - Full response: $response"
      echo "Debug - Extracted user_id: $user_id"
      echo "Login successful."
      echo "Response JSON:"
      echo "$response" | jq .
    fi
    
    # Only output the user_id itself
    echo "$user_id"
  else
    if [ "$ECHO_JSON" = true ]; then
      echo "Login failed."
      echo "Response: $response"
    fi
    exit 1
  fi
}

update_password() {
  local user_id=$1
  local current_password=$2
  local new_password=$3

  if [ "$ECHO_JSON" = true ]; then
    echo "Updating password for user ID: $user_id..."
  fi
  
  json_payload="{\"user_id\":$user_id,\"current_password\":\"$current_password\",\"new_password\":\"$new_password\"}"
  
  if [ "$ECHO_JSON" = true ]; then
    echo "Debug - JSON payload: $json_payload"
  fi
  
  response=$(curl -s -X POST "$BASE_URL/users/update-password" -H "Content-Type: application/json" \
    -d "$json_payload")

  if echo "$response" | grep -q '"message": "Password updated successfully"'; then
    echo "Password updated successfully."
  else
    echo "Failed to update password."
    echo "Response: $response"
    exit 1
  fi
}

##########################################################
#
# Portfolio Tests
#
##########################################################

get_portfolio() {
  user_id=$1

  echo "Getting portfolio for user $user_id..."
  response=$(curl -s -X GET "$BASE_URL/portfolio/$user_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Portfolio retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Portfolio JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get portfolio."
    echo "Response: $response"
    exit 1
  fi
}

buy_stock() {
  user_id=$1
  symbol=$2
  quantity=$3

  echo "Buying $quantity shares of $symbol for user $user_id..."
  response=$(curl -s -X POST "$BASE_URL/portfolio/buy" -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$user_id\", \"symbol\":\"$symbol\", \"quantity\":$quantity}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock purchase successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Transaction JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to buy stock."
    echo "Response: $response"
    exit 1
  fi
}

sell_stock() {
  user_id=$1
  symbol=$2
  quantity=$3

  echo "Selling $quantity shares of $symbol for user $user_id..."
  response=$(curl -s -X POST "$BASE_URL/portfolio/sell" -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$user_id\", \"symbol\":\"$symbol\", \"quantity\":$quantity}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock sale successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Transaction JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to sell stock."
    echo "Response: $response"
    exit 1
  fi
}

get_transaction_history() {
  user_id=$1

  echo "Getting transaction history for user $user_id..."
  response=$(curl -s -X GET "$BASE_URL/portfolio/history/$user_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Transaction history retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "History JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get transaction history."
    echo "Response: $response"
    exit 1
  fi
}

##########################################################
#
# Stock Information Tests
#
##########################################################

validate_stock() {
  symbol=$1

  echo "Validating stock symbol $symbol..."
  response=$(curl -s -X GET "$BASE_URL/stock/$symbol")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock symbol validation successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Validation Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to validate stock symbol."
    echo "Response: $response"
    exit 1
  fi
}

get_stock_price() {
  symbol=$1

  echo "Getting current price for $symbol..."
  response=$(curl -s -X GET "$BASE_URL/stock/price/$symbol")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock price retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Price Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get stock price."
    echo "Response: $response"
    exit 1
  fi
}

get_stock_history() {
  symbol=$1
  outputsize=$2

  echo "Getting price history for $symbol..."
  response=$(curl -s -X GET "$BASE_URL/stock/history/$symbol?outputsize=$outputsize")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Stock history retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "History JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get stock history."
    echo "Response: $response"
    exit 1
  fi
}

get_company_info() {
  symbol=$1

  echo "Getting company info for $symbol..."
  response=$(curl -s -X GET "$BASE_URL/stock/company/$symbol")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Company info retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Company Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get company info."
    echo "Response: $response"
    exit 1
  fi
}

# Run the tests
echo "Starting smoke tests..."

# Health checks
check_health
check_db

# Clear existing data
clear_users
clear_portfolios

# Authentication tests
create_account "testuser" "password123"
user_id=$(login "testuser" "password123")
if [ "$ECHO_JSON" = true ]; then
  echo "Debug - USER_ID after login: $user_id"
fi
update_password "$user_id" "password123" "newpassword123"
login "testuser" "newpassword123"

# Create a second test user
create_account "testuser2" "password456"
user_id2=$(login "testuser2" "password456")

# Stock information tests
validate_stock "AAPL"
get_stock_price "AAPL"
get_stock_history "AAPL" "compact"
get_company_info "AAPL"

# Portfolio tests
get_portfolio $user_id
buy_stock $user_id "AAPL" 10
get_portfolio $user_id
sell_stock $user_id "AAPL" 5
get_portfolio $user_id
get_transaction_history $user_id

# Test second user's portfolio
get_portfolio $user_id2
buy_stock $user_id2 "GOOGL" 5
get_portfolio $user_id2
get_transaction_history $user_id2

# Clean up after tests
clear_portfolios
clear_users

echo "All smoke tests completed successfully!"