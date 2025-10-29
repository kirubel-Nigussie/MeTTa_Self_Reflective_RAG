import secrets
import base64
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import User, db, SessionLocal
import re

# JWT Configuration
JWT_SECRET_KEY = 'your-secret-key-change-in-production'
JWT_EXPIRATION_HOURS = 24

def generate_token(user_id):
    """Generate JWT-like token for user"""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + (JWT_EXPIRATION_HOURS * 3600),
        'iat': int(time.time())
    }
    
    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # Create signature
    message = f"{header_encoded}.{payload_encoded}"
    signature = secrets.token_urlsafe(32)  # Simple signature for demo
    
    return f"{message}.{signature}"

def verify_token(token):
    """Verify JWT-like token and return user_id"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_encoded, payload_encoded, signature = parts
        
        # Decode payload
        payload_padded = payload_encoded + '=' * (4 - len(payload_encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padded))
        
        # Check expiration
        if time.time() > payload['exp']:
            return None
        
        return payload['user_id']
    except Exception:
        return None

def token_required(f):
    """Decorator to require token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if user_id is None:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        session = SessionLocal()
        try:
            user = session.query(User).get(user_id)
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
        finally:
            session.close()
        
        # Add user_id to kwargs for use in route
        kwargs['current_user_id'] = user_id
        return f(*args, **kwargs)
    
    return decorated

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def register_user(username, email, password):
    """Register a new user"""
    # Validate input
    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters long"
    
    if not validate_email(email):
        return None, "Invalid email format"
    
    is_valid, password_msg = validate_password(password)
    if not is_valid:
        return None, password_msg
    
    # Check if user already exists
    session = SessionLocal()
    try:
        if session.query(User).filter_by(username=username).first():
            return None, "Username already exists"
        
        if session.query(User).filter_by(email=email).first():
            return None, "Email already registered"
        
        # Create new user
        user = User(username=username, email=email, password=password)
        session.add(user)
        session.commit()
        
        # Get the user ID before closing the session
        user_id = user.id
        session.close()
        
        return user_id, "User registered successfully"
    except Exception as e:
        session.rollback()
        return None, f"Registration failed: {str(e)}"
    finally:
        session.close()

def authenticate_user(username_or_email, password):
    """Authenticate user with username/email and password"""
    if not username_or_email or not password:
        return None, "Username/email and password are required"
    
    # Find user by username or email
    session = SessionLocal()
    try:
        user = session.query(User).filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user:
            return None, "Invalid credentials"
        
        if not user.is_active:
            return None, "Account is deactivated"
        
        if not user.check_password(password):
            return None, "Invalid credentials"
        
        # Get the user ID before closing the session
        user_id = user.id
        session.close()
        
        return user_id, "Authentication successful"
    finally:
        session.close()

def get_user_by_id(user_id):
    """Get user data by ID"""
    session = SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active
            }
        return None
    finally:
        session.close()