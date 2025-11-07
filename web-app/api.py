from flask import Flask, request, jsonify, session
from flask_cors import CORS
import threading
import time
from datetime import datetime
import json
import os
from functools import wraps
# Import auth module
from auth import authenticate_user, register_user, logout_user, is_authenticated

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)  # Enable CORS with credentials for session support

# Global state management
monitoring_active = False
monitoring_thread = None
threat_log = []
status_data = {
    'monitoring': False,
    'threats_detected': 0,
    'alerts_sent': 0,
    'last_scan': None,
    'system_health': 'Good'
}

# Decorator for protecting endpoints
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated(session):
            return jsonify({'error': 'Authentication required', 'authenticated': False}), 401
        return f(*args, **kwargs)
    return decorated_function

def monitoring_worker():
    """Background worker for continuous monitoring"""
    
    while monitoring_active:
        # Simulate threat detection (integrate with actual security monitor)
        timestamp = datetime.now().isoformat()
        status_data['last_scan'] = timestamp
        
        # Check for potential threats
        # This is a placeholder - integrate with actual Python Security Monitor Agent
        if len(threat_log) > 0:
            status_data['system_health'] = 'Warning'
        else:
            status_data['system_health'] = 'Good'
        
        time.sleep(10)  # Check every 10 seconds

# Authentication endpoints
@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required', 'success': False}), 400
    
    username = data['username']
    password = data['password']
    
    # Authenticate user
    result = authenticate_user(username, password)
    
    if result['success']:
        # Set session data
        session['user_id'] = result['user_id']
        session['username'] = username
        session['authenticated'] = True
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Invalid credentials')
        }), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Registration endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required', 'success': False}), 400
    
    username = data['username']
    password = data['password']
    email = data.get('email', '')
    
    # Register user
    result = register_user(username, password, email)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'username': username
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Registration failed')
        }), 400

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout endpoint"""
    username = session.get('username')
    
    # Clear session
    logout_user(session)
    session.clear()
    
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    if is_authenticated(session):
        return jsonify({
            'authenticated': True,
            'username': session.get('username')
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200

# Protected endpoints
@app.route('/api/start', methods=['POST'])
@login_required
def start_monitoring():
    """Start the security monitoring"""
    global monitoring_active, monitoring_thread
    
    if not monitoring_active:
        monitoring_active = True
        status_data['monitoring'] = True
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()
        return jsonify({'status': 'started', 'message': 'Monitoring activated'}), 200
    else:
        return jsonify({'status': 'already_running', 'message': 'Monitoring already active'}), 200

@app.route('/api/stop', methods=['POST'])
@login_required
def stop_monitoring():
    """Stop the security monitoring"""
    global monitoring_active
    
    if monitoring_active:
        monitoring_active = False
        status_data['monitoring'] = False
        return jsonify({'status': 'stopped', 'message': 'Monitoring deactivated'}), 200
    else:
        return jsonify({'status': 'not_running', 'message': 'Monitoring not active'}), 200

@app.route('/api/status', methods=['GET'])
@login_required
def get_status():
    """Get current system status"""
    return jsonify(status_data), 200

@app.route('/api/threats', methods=['GET'])
@login_required
def get_threats():
    """Get threat log"""
    return jsonify({'threats': threat_log}), 200

@app.route('/api/threats', methods=['POST'])
@login_required
def report_threat():
    """Report a new threat"""
    data = request.get_json()
    threat = {
        'id': len(threat_log) + 1,
        'timestamp': datetime.now().isoformat(),
        'type': data.get('type', 'Unknown'),
        'severity': data.get('severity', 'Medium'),
        'description': data.get('description', ''),
        'source': data.get('source', 'Manual Report')
    }
    
    threat_log.append(threat)
    status_data['threats_detected'] += 1
    
    return jsonify({'status': 'threat_logged', 'threat': threat}), 201

@app.route('/api/alerts/send', methods=['POST'])
@login_required
def send_alert():
    """Send security alert"""
    data = request.get_json()
    # Integrate with actual alert system (email, SMS, etc.)
    status_data['alerts_sent'] += 1
    
    return jsonify({
        'status': 'alert_sent',
        'message': 'Alert dispatched successfully',
        'recipient': data.get('recipient', 'admin')
    }), 200

# Health check endpoint (public)
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
        # Initialize database on startup
    from auth import init_db
    init_db()
    print('Database initialized successfully')
    app.run(debug=True, host='0.0.0.0', port=5000)
