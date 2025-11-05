from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

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

def monitoring_worker():
    """Background worker for continuous monitoring"""
    global monitoring_active, threat_log, status_data
    
    while monitoring_active:
        # Simulate threat detection (integrate with actual security monitor)
        timestamp = datetime.now().isoformat()
        status_data['last_scan'] = timestamp
        
        # Check for potential threats
        # This is a placeholder - integrate with actual Python Security Monitor Agent
        if len(threat_log) > 0:
            status_data['system_health'] = 'Warning'
        
        time.sleep(5)  # Check every 5 seconds

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Security Monitor API'
    }), 200

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start the security monitoring process"""
    global monitoring_active, monitoring_thread, status_data
    
    if monitoring_active:
        return jsonify({
            'success': False,
            'message': 'Monitoring is already active'
        }), 400
    
    monitoring_active = True
    monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
    monitoring_thread.start()
    status_data['monitoring'] = True
    
    return jsonify({
        'success': True,
        'message': 'Monitoring started successfully',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop the security monitoring process"""
    global monitoring_active, status_data
    
    if not monitoring_active:
        return jsonify({
            'success': False,
            'message': 'Monitoring is not active'
        }), 400
    
    monitoring_active = False
    status_data['monitoring'] = False
    
    return jsonify({
        'success': True,
        'message': 'Monitoring stopped successfully',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/threats/analyze', methods=['POST'])
def analyze_threats():
    """Analyze potential security threats"""
    global threat_log, status_data
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided for analysis'
        }), 400
    
    # Perform threat analysis
    threat_info = {
        'id': len(threat_log) + 1,
        'timestamp': datetime.now().isoformat(),
        'type': data.get('type', 'unknown'),
        'severity': data.get('severity', 'medium'),
        'description': data.get('description', 'Potential security threat detected'),
        'source': data.get('source', 'system'),
        'status': 'active'
    }
    
    threat_log.append(threat_info)
    status_data['threats_detected'] += 1
    
    return jsonify({
        'success': True,
        'message': 'Threat analyzed and logged',
        'threat': threat_info
    }), 200

@app.route('/api/threats', methods=['GET'])
def get_threats():
    """Get all detected threats"""
    return jsonify({
        'success': True,
        'count': len(threat_log),
        'threats': threat_log
    }), 200

@app.route('/api/alerts/send', methods=['POST'])
def send_alert():
    """Send security alert"""
    global status_data
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'No alert data provided'
        }), 400
    
    alert_info = {
        'id': status_data['alerts_sent'] + 1,
        'timestamp': datetime.now().isoformat(),
        'recipient': data.get('recipient', 'admin'),
        'message': data.get('message', 'Security alert'),
        'priority': data.get('priority', 'high'),
        'channel': data.get('channel', 'email')
    }
    
    # Simulate sending alert (integrate with actual notification system)
    status_data['alerts_sent'] += 1
    
    return jsonify({
        'success': True,
        'message': 'Alert sent successfully',
        'alert': alert_info
    }), 200

@app.route('/api/emergency/call', methods=['POST'])
def initiate_emergency_call():
    """Initiate emergency call"""
    data = request.get_json()
    
    emergency_info = {
        'timestamp': datetime.now().isoformat(),
        'type': data.get('type', 'security_breach') if data else 'security_breach',
        'location': data.get('location', 'unknown') if data else 'unknown',
        'severity': data.get('severity', 'critical') if data else 'critical',
        'status': 'initiated'
    }
    
    # Simulate emergency call (integrate with actual emergency system)
    # In production, this would connect to emergency services or security team
    
    return jsonify({
        'success': True,
        'message': 'Emergency call initiated',
        'emergency': emergency_info
    }), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify({
        'success': True,
        'status': status_data,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update configuration"""
    if request.method == 'GET':
        config = {
            'scan_interval': 5,
            'alert_threshold': 3,
            'auto_response': False,
            'logging_enabled': True
        }
        return jsonify({
            'success': True,
            'config': config
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        # Update configuration (integrate with actual config management)
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'config': data
        }), 200

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get system logs"""
    limit = request.args.get('limit', 50, type=int)
    
    # Return recent logs (integrate with actual logging system)
    logs = [
        {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'System operational',
            'component': 'security_monitor'
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(logs),
        'logs': logs[:limit]
    }), 200

@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Reset system state"""
    global threat_log, status_data, monitoring_active
    
    monitoring_active = False
    threat_log.clear()
    status_data = {
        'monitoring': False,
        'threats_detected': 0,
        'alerts_sent': 0,
        'last_scan': None,
        'system_health': 'Good'
    }
    
    return jsonify({
        'success': True,
        'message': 'System reset successfully',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print('Starting Security Monitor API...')
    print('API will be available at http://localhost:5000')
    print('\nAvailable endpoints:')
    print('  GET  /api/health - Health check')
    print('  POST /api/monitoring/start - Start monitoring')
    print('  POST /api/monitoring/stop - Stop monitoring')
    print('  POST /api/threats/analyze - Analyze threats')
    print('  GET  /api/threats - Get all threats')
    print('  POST /api/alerts/send - Send alert')
    print('  POST /api/emergency/call - Initiate emergency call')
    print('  GET  /api/status - Get system status')
    print('  GET/POST /api/config - Manage configuration')
    print('  GET  /api/logs - Get system logs')
    print('  POST /api/reset - Reset system')
    print('\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
