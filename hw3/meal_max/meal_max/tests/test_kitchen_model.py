from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_meal_by_id,
    get_meal_by_name,
    get_leaderboard,
    update_meal_stats
)

######################################################
#    Fixtures
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

######################################################
#    Meal Class Tests
######################################################

def test_meal_creation_valid():
    """Test creating a valid meal object."""
    meal = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=12.99, difficulty="LOW")
    assert meal.id == 1
    assert meal.meal == "Spaghetti"
    assert meal.cuisine == "Italian"
    assert meal.price == 12.99
    assert meal.difficulty == "LOW"

def test_meal_invalid_price():
    """Test creating a meal with invalid price raises error."""
    with pytest.raises(ValueError, match="Price must be a positive value."):
        Meal(id=1, meal="Spaghetti", cuisine="Italian", price=-12.99, difficulty="LOW")

def test_meal_invalid_difficulty():
    """Test creating a meal with invalid difficulty raises error."""
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=1, meal="Spaghetti", cuisine="Italian", price=12.99, difficulty="EASY")

######################################################
#    Create and Delete Tests
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the database."""
    create_meal(meal="Spaghetti", cuisine="Italian", price=12.99, difficulty="MED")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Spaghetti", "Italian", 12.99, "MED")
    assert actual_arguments == expected_arguments

def test_create_meal_duplicate(mock_cursor):
    """Test creating a duplicate meal raises error."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError

    with pytest.raises(ValueError, match="Meal with name 'Spaghetti' already exists"):
        create_meal(meal="Spaghetti", cuisine="Italian", price=12.99, difficulty="MED")

def test_create_meal_invalid_price():
    """Test creating a meal with invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -12.99. Price must be a positive number."):
        create_meal(meal="Spaghetti", cuisine="Italian", price=-12.99, difficulty="MED")

def test_create_meal_invalid_difficulty():
    """Test creating a meal with invalid difficulty."""
    with pytest.raises(ValueError, match="Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Spaghetti", cuisine="Italian", price=12.99, difficulty="EASY")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal."""
    mock_cursor.fetchone.return_value = [False]
    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql
    assert actual_update_sql == expected_update_sql

def test_delete_meal_nonexistent(mock_cursor):
    """Test deleting a nonexistent meal."""
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test deleting an already deleted meal."""
    mock_cursor.fetchone.return_value = [True]
    
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_clear_meals(mock_cursor, mocker):
    """Test clearing all meals from the database."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="CREATE TABLE meals"))

    clear_meals()

    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()

######################################################
#    Get Meal Tests
######################################################

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by ID."""
    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 12.99, "MED", False)
    
    result = get_meal_by_id(1)
    
    assert isinstance(result, Meal)
    assert result.id == 1
    assert result.meal == "Spaghetti"
    assert result.cuisine == "Italian"
    assert result.price == 12.99
    assert result.difficulty == "MED"

def test_get_meal_by_id_nonexistent(mock_cursor):
    """Test retrieving a nonexistent meal by ID."""
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_deleted(mock_cursor):
    """Test retrieving a deleted meal by ID."""
    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 12.99, "MED", True)
    
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by name."""
    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 12.99, "MED", False)
    
    result = get_meal_by_name("Spaghetti")
    
    assert isinstance(result, Meal)
    assert result.meal == "Spaghetti"

def test_get_meal_by_name_nonexistent(mock_cursor):
    """Test retrieving a nonexistent meal by name."""
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with name Spaghetti not found"):
        get_meal_by_name("Spaghetti")

def test_get_meal_by_name_deleted(mock_cursor):
    """Test retrieving a deleted meal by name."""
    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 12.99, "MED", True)
    
    with pytest.raises(ValueError, match="Meal with name Spaghetti has been deleted"):
        get_meal_by_name("Spaghetti")

######################################################
#    Leaderboard Tests
######################################################

def test_get_leaderboard(mock_cursor):
    """Test retrieving the leaderboard."""
    mock_cursor.fetchall.return_value = [
        (1, "Spaghetti", "Italian", 12.99, "MED", 10, 7, 0.7),
        (2, "Pizza", "Italian", 15.99, "HIGH", 8, 5, 0.625)
    ]
    
    leaderboard = get_leaderboard()
    
    assert len(leaderboard) == 2
    assert leaderboard[0]['meal'] == "Spaghetti"
    assert leaderboard[0]['wins'] == 7
    assert leaderboard[0]['win_pct'] == 70.0

def test_get_leaderboard_by_win_pct(mock_cursor):
    """Test retrieving the leaderboard sorted by win percentage."""
    mock_cursor.fetchall.return_value = [
        (1, "Spaghetti", "Italian", 12.99, "MED", 10, 9, 0.9),
        (2, "Pizza", "Italian", 15.99, "HIGH", 20, 15, 0.75)
    ]
    
    leaderboard = get_leaderboard(sort_by="win_pct")
    
    assert leaderboard[0]['meal'] == "Spaghetti"
    assert leaderboard[0]['win_pct'] == 90.0

def test_get_leaderboard_invalid_sort(mock_cursor):
    """Test getting leaderboard with invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")

######################################################
#    Update Stats Tests
######################################################

def test_update_meal_stats_win(mock_cursor):
    """Test updating stats for a winning meal."""
    mock_cursor.fetchone.return_value = [False]
    
    update_meal_stats(1, "win")
    
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_query == expected_query

def test_update_meal_stats_loss(mock_cursor):
    """Test updating stats for a losing meal."""
    mock_cursor.fetchone.return_value = [False]
    
    update_meal_stats(1, "loss")
    
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_query == expected_query

def test_update_meal_stats_deleted(mock_cursor):
    """Test updating stats for a deleted meal."""
    mock_cursor.fetchone.return_value = [True]
    
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

def test_update_meal_stats_nonexistent(mock_cursor):
    """Test updating stats for a nonexistent meal."""
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        update_meal_stats(1, "win")

def test_update_meal_stats_invalid_result(mock_cursor):
    """Test updating stats with invalid result."""
    mock_cursor.fetchone.return_value = [False]
    
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_meal_stats(1, "invalid")