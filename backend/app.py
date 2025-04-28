from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db
from models import User, Listing, ListingImage
from routes.auth_routes import auth_bp
from routes.marketplace_routes import marketplace_bp
import os
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS Configuration
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],  # Vite dev server port
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours in seconds
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for development

# Database Configuration - Using absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "college_market.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints with proper URL prefixes
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(marketplace_bp, url_prefix='/api/marketplace')

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: {error}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
    return jsonify({"error": "An unexpected error occurred"}), 500

def init_db():
    """Initialize the database."""
    with app.app_context():
        try:
            db_file = os.path.join(basedir, "college_market.db")
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    logger.info("Removed existing database file")
                except PermissionError:
                    logger.warning("Could not remove existing database file - it may be in use")
                    # Continue anyway - SQLite will handle this case
            
            # Create new database
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

# Initialize database
init_db()

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
