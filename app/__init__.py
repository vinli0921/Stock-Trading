from flask import Flask, jsonify, make_response
from app.routes.auth import auth_bp
from app.routes.portfolio import portfolio_bp
from app.routes.stock import stock_bp
from app.utils.sql_utils import check_database_connection, check_tables_exist

# Create Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(stock_bp)

# Health check routes
@app.route('/api/health')
def healthcheck():
    """Basic health check"""
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check')
def db_check():
    """Check database connection and tables"""
    try:
        check_database_connection()
        check_tables_exist()
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)