import pytest
from contextlib import contextmanager
import sqlite3

from meal_max.models.kitchen_model import Meal
from meal_max.models.kitchen_model import create_meal, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats

@pytest.fixture()
def sample_meal1():
    """Fixture to provide a sample meal for testing."""
    return Meal(id=1, meal="Spaghetti Carbonara", cuisine="Italian", price=15.99, difficulty="MED")

@pytest.fixture()
def sample_meal2():
    """Fixture to provide another sample meal for testing."""
    return Meal(id=2, meal="Caesar Salad", cuisine="American", price=12.99, difficulty="LOW")

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None
    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    return mock_conn, mock_cursor # Return both as a tuple

##################################################
# Meal Class Test Cases
##################################################

def test_meal_creation():
    """Test creating a valid meal object."""
    meal = Meal(id=1, meal="Pasta", cuisine="Italian", price=12.99, difficulty="LOW")
    assert meal.id == 1
    assert meal.meal == "Pasta"
    assert meal.cuisine == "Italian"
    assert meal.price == 12.99
    assert meal.difficulty == "LOW"

def test_meal_invalid_price():
    """Test creating a meal with invalid price raises error."""
    with pytest.raises(ValueError, match="Price must be a positive value."):
        Meal(id=1, meal="Pasta", cuisine="Italian", price=-5.0, difficulty="LOW")

def test_meal_invalid_difficulty():
    """Test creating a meal with invalid difficulty raises error."""
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=1, meal="Pasta", cuisine="Italian", price=12.99, difficulty="EASY")

##################################################
# Create Meal Test Cases
##################################################

def test_create_meal(mock_cursor):
    """Test successfully creating a new meal."""
    mock_conn, mock_cursor = mock_cursor
    
    create_meal("Pasta", "Italian", 12.99, "LOW")
    
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_create_meal_invalid_price():
    """Test creating a meal with invalid price raises error."""
    with pytest.raises(ValueError, match="Invalid price: -5.0. Price must be a positive number."):
        create_meal("Pasta", "Italian", -5.0, "LOW")

def test_create_meal_invalid_difficulty():
    """Test creating a meal with invalid difficulty raises error."""
    with pytest.raises(ValueError, match="Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal("Pasta", "Italian", 12.99, "EASY")

def test_create_duplicate_meal(mock_cursor):
    """Test creating a duplicate meal raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.IntegrityError
    
    with pytest.raises(ValueError, match="Meal with name 'Pasta' already exists"):
        create_meal("Pasta", "Italian", 12.99, "LOW")

##################################################
# Delete Meal Test Cases
##################################################

def test_delete_meal(mock_cursor):
    """Test successfully deleting a meal."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [False]  # meal exists and is not deleted
    
    delete_meal(1)
    
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()

def test_delete_nonexistent_meal(mock_cursor):
    """Test deleting a nonexistent meal raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)

def test_delete_already_deleted_meal(mock_cursor):
    """Test deleting an already deleted meal raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [True]  # meal is already deleted
    
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

##################################################
# Get Meal Test Cases
##################################################

def test_get_meal_by_id(mock_cursor):
    """Test successfully retrieving a meal by ID."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [1, "Pasta", "Italian", 12.99, "LOW", False]
    
    meal = get_meal_by_id(1)
    
    assert isinstance(meal, Meal)
    assert meal.id == 1
    assert meal.meal == "Pasta"
    assert meal.cuisine == "Italian"
    assert meal.price == 12.99
    assert meal.difficulty == "LOW"

def test_get_meal_by_name(mock_cursor):
    """Test successfully retrieving a meal by name."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [1, "Pasta", "Italian", 12.99, "LOW", False]
    
    meal = get_meal_by_name("Pasta")
    
    assert isinstance(meal, Meal)
    assert meal.meal == "Pasta"

def test_get_nonexistent_meal_by_id(mock_cursor):
    """Test retrieving a nonexistent meal by ID raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)

def test_get_deleted_meal_by_id(mock_cursor):
    """Test retrieving a deleted meal by ID raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [1, "Pasta", "Italian", 12.99, "LOW", True]
    
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

##################################################
# Leaderboard Test Cases
##################################################

def test_get_leaderboard(mock_cursor):
    """Test successfully retrieving the leaderboard."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 12.99, "LOW", 10, 7, 0.7),
        (2, "Salad", "American", 8.99, "LOW", 8, 5, 0.625)
    ]
    
    leaderboard = get_leaderboard()
    
    assert len(leaderboard) == 2
    assert leaderboard[0]['meal'] == "Pasta"
    assert leaderboard[0]['wins'] == 7
    assert leaderboard[0]['win_pct'] == 70.0

def test_get_leaderboard_invalid_sort(mock_cursor):
    """Test getting leaderboard with invalid sort parameter raises error."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")

##################################################
# Update Stats Test Cases
##################################################

def test_update_meal_stats(mock_cursor):
    """Test successfully updating meal statistics."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [False]  # meal exists and is not deleted
    
    update_meal_stats(1, "win")
    
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()

def test_update_stats_invalid_result(mock_cursor):
    """Test updating stats with invalid result raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [False]
    
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_meal_stats(1, "invalid")

def test_update_deleted_meal_stats(mock_cursor):
    """Test updating stats for a deleted meal raises error."""
    mock_conn, mock_cursor = mock_cursor
    mock_cursor.fetchone.return_value = [True]  # meal is deleted
    
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")