from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from ..models import User, db
import logging
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        logger.info('Registration request received')
        data = request.get_json()
        logger.info(f'Registration data received: {data}')
        
        # Validate required fields
        if not data:
            logger.error('No data received in request')
            return jsonify({'error': 'No data provided'}), 400
            
        if not all(key in data for key in ['username', 'email', 'password']):
            logger.error(f'Missing required fields. Received fields: {list(data.keys())}')
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f'Email already registered: {data["email"]}')
            return jsonify({'error': 'Email already registered'}), 400
            
        if User.query.filter_by(username=data['username']).first():
            logger.warning(f'Username already taken: {data["username"]}')
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'team_member')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        logger.info(f'User registered successfully: {user.username}')
        
        # Create access token with additional claims
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'type': 'access'
            }
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201
    except Exception as e:
        logger.error(f'Error during registration: {str(e)}')
        return jsonify({'error': 'An error occurred during registration'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        if not all(key in data for key in ['email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token with additional claims
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'type': 'access'
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error during login: {str(e)}')
        return jsonify({'error': 'An error occurred during login'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        # Get the current user ID using get_jwt_identity()
        current_user_id = int(get_jwt_identity())
        logger.debug(f'Current user ID: {current_user_id} (type: {type(current_user_id)})')
        
        user = User.query.get(int(current_user_id))
        if not user:
            logger.error(f'User not found with ID: {current_user_id}')
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }), 200
    except Exception as e:
        logger.error(f'Error getting current user: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    data = request.get_json()
    
    # Check if username is already taken
    if 'username' in data and data['username'] != user.username:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'Username already taken'}), 400
    
    # Check if email is already taken
    if 'email' in data and data['email'] != user.email:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
    
    # Update user information
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }), 200

@auth_bp.route('/debug/users', methods=['GET'])
def debug_users():
    try:
        users = User.query.all()
        return jsonify({
            'users': [{
                'username': user.username,
                'email': user.email,
                'id': user.id
            } for user in users]
        }), 200
    except Exception as e:
        logger.error(f'Error getting users: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500

@auth_bp.route('/debug/delete-user', methods=['POST'])
def debug_delete_user():
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
            
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        logger.error(f'Error deleting user: {str(e)}')
        return jsonify({'error': 'An error occurred'}), 500 