from flask import Blueprint, jsonify, make_response, request, Response
from app.models.stock import StockAPI

stock_bp = Blueprint('stock', __name__)
stock_api = StockAPI()

@stock_bp.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_info(symbol: str) -> Response:
    """Get detailed stock information"""
    try:
        info = stock_api.get_stock_info(symbol)
        return make_response(jsonify({
            'status': 'success',
            'stock_info': info
        }), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@stock_bp.route('/api/stock/price/<symbol>', methods=['GET'])
def get_stock_price(symbol: str) -> Response:
    """Get current stock price"""
    try:
        price_info = stock_api.get_stock_price(symbol)
        return make_response(jsonify({
            'status': 'success',
            'price_info': price_info
        }), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@stock_bp.route('/api/stock/history/<symbol>', methods=['GET'])
def get_stock_history(symbol: str) -> Response:
    """Get stock price history"""
    try:
        outputsize = request.args.get('outputsize', 'compact')
        if outputsize not in ['compact', 'full']:
            return make_response(jsonify({
                'error': 'outputsize must be either compact or full'
            }), 400)

        history = stock_api.get_historical_data(symbol, outputsize=outputsize)
        return make_response(jsonify({
            'status': 'success',
            'history': history
        }), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@stock_bp.route('/api/stock/company/<symbol>', methods=['GET'])
def get_company_info(symbol: str) -> Response:
    """Get detailed company information"""
    try:
        company_info = stock_api.get_company_info(symbol)
        return make_response(jsonify({
            'status': 'success',
            'company_info': company_info
        }), 200)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)