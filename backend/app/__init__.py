from flask import Flask, send_from_directory, send_file, request, make_response, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from .models import User, db
from logging_config import setup_logger

# Load environment variables
load_dotenv()

# Initialize Flask extensions

jwt = JWTManager()
socketio = SocketIO()
logger = None

def create_app():
    try:
        # Initialize Flask app with static folder
        app = Flask(__name__, static_folder='../../frontend/build', static_url_path='')
        
        # Configure logging
        logger = setup_logger(app)

        # Configure the Flask application
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:hemingqin@localhost/lab_tasks')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging
        
        # JWT Configuration
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire
        app.config['JWT_TOKEN_LOCATION'] = ['headers']
        app.config['JWT_HEADER_NAME'] = 'Authorization'
        app.config['JWT_HEADER_TYPE'] = 'Bearer'
        app.config['JWT_JSON_KEY'] = 'access_token'
        app.config['JWT_IDENTITY_CLAIM'] = 'sub'
        app.config['JWT_DECODE_ALGORITHMS'] = ['HS256']
        app.config['JWT_ERROR_MESSAGE_KEY'] = 'msg'
        app.config['JWT_ENCODE_ISSUER'] = 'lab_tasks'
        app.config['JWT_DECODE_ISSUER'] = 'lab_tasks'
        app.config['JWT_ENCODE_AUDIENCE'] = 'lab_tasks_client'
        app.config['JWT_DECODE_AUDIENCE'] = 'lab_tasks_client'
        
        # Initialize extensions
        db.init_app(app)
        jwt.init_app(app)
        socketio.init_app(app, cors_allowed_origins="*")
        Migrate(app, db)
        
        # Debug logging for requests
        @app.before_request
        def log_request_info():
            logger.debug('Headers: %s', dict(request.headers))
            logger.debug('Method: %s, Path: %s', request.method, request.path)
            if request.is_json:
                logger.debug('Request JSON: %s', request.get_json())

        # Register blueprints first
        from .routes.auth import auth_bp
        from .routes.tasks import tasks_bp
        from .routes.projects import projects_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
        app.register_blueprint(projects_bp, url_prefix='/api/projects')

        # Configure CORS
        CORS(app, resources={
            r"/api/*": {
                "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Authorization"]
            }
        })
        
        @app.before_request
        def handle_preflight():
            if request.method == "OPTIONS":
                response = make_response()
                response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                response.headers.add('Access-Control-Allow-Credentials', 'true')
                response.headers.add('Access-Control-Max-Age', '3600')
                return response

        @app.after_request
        def after_request(response):
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Max-Age'] = '3600'
            return response

        # Define the build directory path
        build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/build'))
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path.startswith('api/'):
                return {"error": "Not Found"}, 404
            
            try:
                # First try to serve the exact file
                file_path = os.path.join(build_dir, path)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return send_from_directory(build_dir, path)
                
                # If not found, serve index.html for client-side routing
                return send_from_directory(build_dir, 'index.html')
            except Exception as e:
                logger.error(f"Error serving file {path}: {str(e)}")
                return send_from_directory(build_dir, 'index.html')

        # Test database connection
        with app.app_context():
            try:
                db.engine.connect()
                logger.info("Database connection successful!")
            except Exception as e:
                logger.error(f"Database connection failed: {str(e)}")
                raise e
        
        # JWT token handlers
        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            logger.debug(f'Token payload: {jwt_payload}')
            return False
            
        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            identity = str(jwt_data["sub"])
            logger.debug(f'Looking up user with identity: {identity} (type: {type(identity)})')
            return User.query.get(int(identity))
            
        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            logger.error(f'Invalid token error: {error}')
            return jsonify({
                'error': 'Invalid token',
                'message': str(error)
            }), 401
            
        @jwt.unauthorized_loader
        def unauthorized_callback(error):
            logger.error(f'Unauthorized error: {error}')
            return jsonify({
                'error': 'No token provided',
                'message': str(error)
            }), 401
            
        @jwt.needs_fresh_token_loader
        def token_not_fresh_callback(jwt_header, jwt_payload):
            logger.error('Token is not fresh')
            return jsonify({
                'error': 'Fresh token required',
                'message': 'The token has expired'
            }), 401
            
        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            logger.error('Token has been revoked')
            return jsonify({
                'error': 'Token has been revoked',
                'message': 'The token is no longer valid'
            }), 401
        
        return app
    except Exception as e:
        logger.error(f"Error creating Flask app: {str(e)}")
        raise e 