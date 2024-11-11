#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

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
# Kitchen
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal to db: $meal - $cuisine, $price, $difficulty"
  response=$(curl -s -X POST "$BASE_URL/create-meal" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

clear_meals() {
  echo "Clearing meals..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals cleared successfully."
  else
    echo "Failed to clear meals."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  meal_name_encoded=$(echo -n "$meal_name" | jq -s -R -r @uri)

  echo "Getting meal by name: $meal_name"
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name_encoded")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    echo $response
    exit 1
  fi
}

clear_catalog() {
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

############################################################
#
# Battle
#
############################################################

clear_combatants(){
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

prep_combatant() {
  meal=$1
  echo "Prepping combatant: $meal..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "$meal successfully prepped."
  else
    echo "Failed to prep meal: $(echo -n "$response" | jq -r .error)"
    exit 1
  fi
}

get_combatants(){
  echo "Retrieving all songs from playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all meals from combatant."
    exit 1
  fi
}

battle(){
  echo "Combatants start fighting"
  response=$(curl -s -X GET "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "A battle has happened successfully"
    if [ "$ECHO_JSON" = true ]; then
      echo "RESULT: "
      echo "$response" | jq .
    fi
  else
    echo "Battle Failed"
    exit 1
  fi
}

get_leaderboard() {
  echo "Getting leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}

# Health checks
check_health
check_db

# Clear the catalog
clear_catalog
clear_meals

# Kitchen checks
create_meal "Chicken Tikka Masala" "Indian" 10 "MED"
create_meal "Fetuccini Alfredo" "Italian" 12 "LOW"
create_meal "Bulgogi" "Korean" 15 "LOW"
create_meal "Hainan Chicken" "Chinese" 13 "MED"
create_meal "Shawarma" "Middle Eastern" 16 "HIGH"
create_meal "Sushi" "Japanese" 5.99 "LOW"

delete_meal_by_id 1

get_meal_by_id 2

get_meal_by_name "Bulgogi"

echo

# Clear the combatants
clear_combatants

# Battle checks
prep_combatant "Shawarma"
prep_combatant "Sushi"

get_combatants

battle

prep_combatant "Bulgogi"

battle

prep_combatant "Fetuccini Alfredo"

battle

get_leaderboard

echo "All tests passed successfully!"
