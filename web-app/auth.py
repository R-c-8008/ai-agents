import sqlite3
import bcrypt
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
import re
import os

# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
DATABASE = 'users.db'
TOKEN_EXPIRATION_HOURS = 24

# Database initialization
def init_db():
    """Initialize the user database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# Database connection helper
def get_db():
    """Get database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Password validation
def validate_password(password):
    """Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Email is valid"
    return False, "Invalid email format"

# Password hashing
def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# JWT token generation
def generate_token(user_id, username):
    """Generate a JWT token for a user."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': expiration,
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token, expiration

def verify_token(token):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return False, {'error': 'Invalid token'}

# User registration
def register_user(username, email, password):
    """Register a new user.
    
    Returns:
        tuple: (success: bool, message: str, user_id: int or None)
    """
    # Validate inputs
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long", None
    
    email_valid, email_msg = validate_email(email)
    if not email_valid:
        return False, email_msg, None
    
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        return False, password_msg, None
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if username or email already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            return False, "Username or email already exists", None
        
        # Hash password and insert user
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        db.commit()
        user_id = cursor.lastrowid
        
        return True, "User registered successfully", user_id
    
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}", None

# User login
def login_user(username_or_email, password):
    """Authenticate a user and create a session.
    
    Returns:
        tuple: (success: bool, message: str, token: str or None, user_data: dict or None)
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Find user by username or email
        cursor.execute(
            'SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?',
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()
        
        if not user:
            return False, "Invalid credentials", None, None
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return False, "Invalid credentials", None, None
        
        # Generate token
        token, expiration = generate_token(user['id'], user['username'])
        
        # Store session in database
        cursor.execute(
            'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user['id'], token, expiration)
        )
        
        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (user['id'],)
        )
        
        db.commit()
        
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }
        
        return True, "Login successful", token, user_data
    
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}", None, None

# Session management
def validate_session(token):
    """Validate a session token.
    
    Returns:
        tuple: (valid: bool, user_data: dict or None)
    """
    # First verify JWT token
    valid, payload = verify_token(token)
    if not valid:
        return False, None
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if session exists and is not expired
        cursor.execute(
            '''SELECT s.id, s.user_id, u.username, u.email 
               FROM sessions s
               JOIN users u ON s.user_id = u.id
               WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP''',
            (token,)
        )
        session = cursor.fetchone()
        
        if not session:
            return False, None
        
        user_data = {
            'id': session['user_id'],
            'username': session['username'],
            'email': session['email']
        }
        
        return True, user_data
    
    except sqlite3.Error:
        return False, None

def logout_user(token):
    """Logout a user by invalidating their session.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        db.commit()
        
        if cursor.rowcount > 0:
            return True, "Logout successful"
        return False, "Session not found"
    
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"

def cleanup_expired_sessions():
    """Remove expired sessions from the database."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP')
        db.commit()
        return True, f"Cleaned up {cursor.rowcount} expired sessions"
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"

# Login required decorator
def login_required(f):
    """Decorator to protect routes that require authentication.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            user = g.user
            return jsonify({'message': f'Hello {user["username"]}'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        # Extract token (format: "Bearer <token>")
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Validate session
        valid, user_data = validate_session(token)
        
        if not valid:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user data in g object for access in route
        g.user = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function

# Flask route examples (to be integrated with your Flask app)
def setup_auth_routes(app):
    """Setup authentication routes for Flask app.
    
    Usage:
        from auth import setup_auth_routes
        app = Flask(__name__)
        setup_auth_routes(app)
    """
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message, user_id = register_user(username, email, password)
        
        if success:
            return jsonify({'message': message, 'user_id': user_id}), 201
        return jsonify({'error': message}), 400
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        username_or_email = data.get('username')
        password = data.get('password')
        
        if not all([username_or_email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success, message, token, user_data = login_user(username_or_email, password)
        
        if success:
            return jsonify({
                'message': message,
                'token': token,
                'user': user_data
            }), 200
        return jsonify({'error': message}), 401
    
    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        
        success, message = logout_user(token)
        
        if success:
            return jsonify({'message': message}), 200
        return jsonify({'error': message}), 400
    
    @app.route('/api/auth/me', methods=['GET'])
    @login_required
    def get_current_user():
        return jsonify({'user': g.user}), 200
    
    @app.route('/api/auth/cleanup', methods=['POST'])
    @login_required
    def cleanup():
        # This could be restricted to admin users only
        success, message = cleanup_expired_sessions()
        return jsonify({'message': message}), 200 if success else 500
    
    # Register teardown function
    app.teardown_appcontext(close_db)

# Initialize database on module import
if __name__ == '__main__':
    init_db()
    print("Database initialized successfully")
