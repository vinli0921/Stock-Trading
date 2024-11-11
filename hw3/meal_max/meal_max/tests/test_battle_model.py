import pytest
from contextlib import contextmanager
from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of PlaylistModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_status(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_status")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_meal1():
    #89
    return Meal(1, 'curry', 'Indian', 15, 'HIGH')

@pytest.fixture
def sample_meal2():
    #138
    return Meal(2, 'pasta', 'Italian', 20, 'MED')

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.battle_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a song to the playlist."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'curry'

def test_add_more_meal_to_combatants(battle_model, sample_meal1):
    """Test error when adding a duplicate song to the playlist by ID."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)
        
        
def test_clear_combatants(battle_model, sample_meal1, caplog):
    """Test clearing the entire playlist."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants should be empty after clearing"
    assert "Clearing the combatants list." in caplog.text, "Expected message when clearing the combatants"

def test_get_combatants(battle_model, sample_combatants):
    """Test successfully retrieving all songs from the playlist."""
    battle_model.combatants.extend(sample_combatants)

    all_combatants = battle_model.get_combatants()
    assert all_combatants[0].id == 1
    assert all_combatants[0].meal == 'curry'
    assert all_combatants[0].cuisine == 'Indian'
    assert all_combatants[0].price == 15
    assert all_combatants[0].difficulty == 'HIGH'

    assert len(all_combatants) == 2
    assert all_combatants[1].id == 2
    assert all_combatants[1].meal == 'pasta'
    
def test_get_battle_score(battle_model, sample_meal1, caplog):
    score=battle_model.get_battle_score(sample_meal1)
    assert score==89.000, "Score should be the same"
    assert "Calculating battle score for curry: price=15.000, cuisine=Indian, difficulty=HIGH" in caplog.text, caplog.text
    
    
def test_battle(battle_model, sample_combatants, mocker, sample_meal2, caplog):
    battle_model.combatants.extend(sample_combatants)
    mocker.patch("meal_max.models.battle_model.get_random", return_value=.50)
    mocker.patch("meal_max.models.battle_model.update_meal_stats")
    winner=battle_model.battle()
    assert winner==sample_meal2.meal
    assert "Score for curry: 89.000" in caplog.text, "Expected message when battle"
    assert "Score for pasta: 138.000" in caplog.text, "Expected message when battle"
    assert len(battle_model.combatants)==1, "length isn't 1"
    
    
def test_battle_less_than_two(battle_model, sample_combatants, mocker, sample_meal1):
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle() 
