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
# Song Management
#
##########################################################

clear_catalog() {
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

############################################################
#
# Playlist Management
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

prep_combatant(){
  id=$1
  meal=$2
  cuisine=$3
  price=$4
  difficulty=$5
  echo "Adding meal to combatants: $meal - $cuisine - $price - $difficulty..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added to combatants successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add meal to combatants."
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

# Health checks
check_health
check_db

# Clear the catalog
clear_catalog
# clear_meals
# create_meal "Curry" "Indian" 10 "MED"
# create_meal "Pasta" "Italian" 12 "LOW"



#playlist
clear_combatants

prep_combatant 1 "Curry" "Indian" 10 "MED"
prep_combatant 2 "Pasta" "Italian" 12 "LOW"

get_combatants
battle

echo "All tests passed successfully!"
