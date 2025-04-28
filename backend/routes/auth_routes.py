from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from database import db  # Import db from database.py
from models import User
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({"message": "Missing required fields"}), 400
    
    username = data['name']  # Changed from 'username' to 'name' to match frontend
    email = data['email']
    password = data['password']
    
    # Validate email format
    if not validate_email(email):
        return jsonify({"message": "Invalid email format"}), 400
    
    # Validate password strength
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({"message": message}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 409
    
    try:
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role='student'  # Default role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token with expiration
        expires = timedelta(days=1)
        access_token = create_access_token(
            identity=new_user.id,
            expires_delta=expires
        )
        
        return jsonify({
            "message": "User registered successfully!",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role
            },
            "access_token": access_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({"message": "Missing email or password"}), 400
    
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"message": "User not found. Please register first."}), 404
    
    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid password"}), 401
    
    # Create access token with expiration
    expires = timedelta(days=1)
    access_token = create_access_token(
        identity=user.id,
        expires_delta=expires
    )
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }), 200
