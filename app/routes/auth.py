from flask import Blueprint, jsonify, make_response, request, Response
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/users/create-account', methods=['POST'])
def create_account() -> Response:
    """Create a new user account"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return make_response(jsonify({
                'error': 'Username and password are required'
            }), 400)

        user = User.create(username, password)
        return make_response(jsonify({
            'message': 'Account created successfully',
            'user_id': user.id
        }), 201)

    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@auth_bp.route('/users/login', methods=['POST'])
def login() -> Response:
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return make_response(jsonify({
                'error': 'Username and password are required'
            }), 400)

        user = User.login(username, password)
        return make_response(jsonify({
            'message': 'Login successful',
            'user_id': user.id
        }), 200)

    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 401)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@auth_bp.route('/users/update-password', methods=['POST'])
def update_password() -> Response:
    """Update user password"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not all([user_id, current_password, new_password]):
            return make_response(jsonify({
                'error': 'All fields are required'
            }), 400)

        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify({
                'error': 'User not found'
            }), 404)

        user.update_password(current_password, new_password)
        return make_response(jsonify({
            'message': 'Password updated successfully'
        }), 200)

    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    
@auth_bp.route('/users/clear', methods=['DELETE'])
def clear_users() -> Response:
    """Clear all users from the database"""
    try:
        User.clear_all()
        return make_response(jsonify({
            'status': 'success',
            'message': 'All users cleared'
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)