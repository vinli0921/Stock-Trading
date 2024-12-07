from flask import Blueprint, jsonify, make_response, request, Response
from app.models.user import User

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/api/portfolio/<int:user_id>', methods=['GET'])
def get_portfolio(user_id: int) -> Response:
    """Get user's portfolio"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        portfolio = user.get_portfolio()
        return make_response(jsonify({
            'status': 'success',
            'portfolio': portfolio
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@portfolio_bp.route('/api/portfolio/buy', methods=['POST'])
def buy_stock() -> Response:
    """Buy stock for user's portfolio"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        symbol = data.get('symbol')
        quantity = data.get('quantity')

        if not all([user_id, symbol, quantity]):
            return make_response(jsonify({
                'error': 'user_id, symbol, and quantity are required'
            }), 400)

        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        transaction = user.buy_stock(symbol, int(quantity))
        return make_response(jsonify({
            'status': 'success',
            'transaction': transaction
        }), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@portfolio_bp.route('/api/portfolio/sell', methods=['POST'])
def sell_stock() -> Response:
    """Sell stock from user's portfolio"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        symbol = data.get('symbol')
        quantity = data.get('quantity')

        if not all([user_id, symbol, quantity]):
            return make_response(jsonify({
                'error': 'user_id, symbol, and quantity are required'
            }), 400)

        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        transaction = user.sell_stock(symbol, int(quantity))
        return make_response(jsonify({
            'status': 'success',
            'transaction': transaction
        }), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@portfolio_bp.route('/api/portfolio/history/<int:user_id>', methods=['GET'])
def get_transaction_history(user_id: int) -> Response:
    """Get user's transaction history"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)

        history = user.get_transaction_history()
        return make_response(jsonify({
            'status': 'success',
            'history': history
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)