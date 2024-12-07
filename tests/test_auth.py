from contextlib import contextmanager
import pytest
import bcrypt
import sqlite3
from app.models.user import User

@pytest.fixture
def mock_db_connection(mocker):
    """Mock database connection for testing"""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Create mock context manager
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("app.models.user.get_db_connection", mock_get_db_connection)
    return mock_cursor

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'id': 1,
        'username': 'testuser',
        'password': 'testpass123',
        'salt': bcrypt.gensalt(),
    }

def test_user_creation(sample_user_data):
    """Test creating a user object"""
    user = User(
        id=sample_user_data['id'],
        username=sample_user_data['username'],
        salt=sample_user_data['salt'],
        hashed_password=bcrypt.hashpw(
            sample_user_data['password'].encode('utf-8'),
            sample_user_data['salt']
        )
    )
    assert user.id == sample_user_data['id']
    assert user.username == sample_user_data['username']

def test_create_user_success(mock_db_connection, sample_user_data):
    """Test successful user creation"""
    mock_db_connection.lastrowid = sample_user_data['id']
    
    user = User.create(
        username=sample_user_data['username'],
        password=sample_user_data['password']
    )
    
    assert user.id == sample_user_data['id']
    assert user.username == sample_user_data['username']

def test_create_user_duplicate_username(mock_db_connection, sample_user_data):
    """Test creating user with duplicate username"""
    mock_db_connection.execute.side_effect = sqlite3.IntegrityError
    
    with pytest.raises(ValueError, match="Username .* is already taken"):
        User.create(
            username=sample_user_data['username'],
            password=sample_user_data['password']
        )

def test_login_success(mock_db_connection, sample_user_data):
    """Test successful login"""
    # Prepare mock response
    salt = sample_user_data['salt']
    hashed_pass = bcrypt.hashpw(
        sample_user_data['password'].encode('utf-8'),
        salt
    )
    mock_db_connection.fetchone.return_value = {
        'id': sample_user_data['id'],
        'salt': salt,
        'password_hash': hashed_pass
    }
    
    user = User.login(
        username=sample_user_data['username'],
        password=sample_user_data['password']
    )
    
    assert user.id == sample_user_data['id']
    assert user.username == sample_user_data['username']

def test_login_invalid_username(mock_db_connection, sample_user_data):
    """Test login with invalid username"""
    mock_db_connection.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Invalid username or password"):
        User.login(
            username=sample_user_data['username'],
            password=sample_user_data['password']
        )

def test_login_invalid_password(mock_db_connection, sample_user_data):
    """Test login with invalid password"""
    salt = sample_user_data['salt']
    hashed_pass = bcrypt.hashpw(
        'different_password'.encode('utf-8'),
        salt
    )
    mock_db_connection.fetchone.return_value = {
        'id': sample_user_data['id'],
        'salt': salt,
        'password_hash': hashed_pass
    }
    
    with pytest.raises(ValueError, match="Invalid username or password"):
        User.login(
            username=sample_user_data['username'],
            password=sample_user_data['password']
        )

def test_update_password_success(mock_db_connection, sample_user_data):
    """Test successful password update"""
    user = User(
        id=sample_user_data['id'],
        username=sample_user_data['username'],
        salt=sample_user_data['salt'],
        hashed_password=bcrypt.hashpw(
            sample_user_data['password'].encode('utf-8'),
            sample_user_data['salt']
        )
    )

    user.update_password(
        current_password=sample_user_data['password'],
        new_password='new_password123'
    )

    assert mock_db_connection.execute.called

def test_update_password_incorrect_current(mock_db_connection, sample_user_data):
    """Test password update with incorrect current password"""
    user = User(
        id=sample_user_data['id'],
        username=sample_user_data['username'],
        salt=sample_user_data['salt'],
        hashed_password=bcrypt.hashpw(
            sample_user_data['password'].encode('utf-8'),
            sample_user_data['salt']
        )
    )
    
    with pytest.raises(ValueError, match="Current password is incorrect"):
        user.update_password(
            current_password='wrong_password',
            new_password='new_password123'
        )

def test_get_by_id_success(mock_db_connection, sample_user_data):
    """Test successful user retrieval by ID"""
    mock_db_connection.fetchone.return_value = {
        'id': sample_user_data['id'],
        'username': sample_user_data['username'],
        'salt': sample_user_data['salt'],
        'password_hash': bcrypt.hashpw(
            sample_user_data['password'].encode('utf-8'),
            sample_user_data['salt']
        )
    }
    
    user = User.get_by_id(sample_user_data['id'])
    
    assert user.id == sample_user_data['id']
    assert user.username == sample_user_data['username']

def test_get_by_id_not_found(mock_db_connection):
    """Test user retrieval with non-existent ID"""
    mock_db_connection.fetchone.return_value = None
    
    result = User.get_by_id(999)
    assert result is None