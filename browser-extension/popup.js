// Security Monitor Agent - Popup Script

// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const alertsList = document.getElementById('alertsList');
const lastUpdate = document.getElementById('lastUpdate');
const callPolice = document.getElementById('callPolice');
const callAmbulance = document.getElementById('callAmbulance');
const callFire = document.getElementById('callFire');
const refreshBtn = document.getElementById('refreshBtn');
const settingsBtn = document.getElementById('settingsBtn');

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    loadRecentAlerts();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    callPolice.addEventListener('click', () => initiateEmergencyCall('police'));
    callAmbulance.addEventListener('click', () => initiateEmergencyCall('ambulance'));
    callFire.addEventListener('click', () => initiateEmergencyCall('fire'));
    refreshBtn.addEventListener('click', () => {
        loadStatus();
        loadRecentAlerts();
    });
    settingsBtn.addEventListener('click', openSettings);
}

// Load monitoring status
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        const data = await response.json();
        
        updateStatus(data.status);
        updateLastUpdate();
    } catch (error) {
        console.error('Failed to load status:', error);
        updateStatus('offline');
    }
}

// Update status indicator
function updateStatus(status) {
    statusDot.className = 'status-dot';
    
    switch(status) {
        case 'active':
        case 'monitoring':
            statusDot.classList.add('active');
            statusText.textContent = 'Monitoring Active';
            break;
        case 'alert':
            statusDot.classList.add('alert');
            statusText.textContent = 'Alert Detected!';
            break;
        case 'offline':
        default:
            statusDot.classList.add('offline');
            statusText.textContent = 'Offline';
    }
}

// Load recent alerts
async function loadRecentAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/alerts/recent`);
        const alerts = await response.json();
        
        displayAlerts(alerts);
    } catch (error) {
        console.error('Failed to load alerts:', error);
        alertsList.innerHTML = '<div class="alert-item error">Failed to load alerts</div>';
    }
}

// Display alerts in the list
function displayAlerts(alerts) {
    if (!alerts || alerts.length === 0) {
        alertsList.innerHTML = '<div class="alert-item no-alerts">No recent alerts</div>';
        return;
    }
    
    alertsList.innerHTML = alerts.slice(0, 5).map(alert => `
        <div class="alert-item ${alert.severity}">
            <div class="alert-header">
                <span class="alert-type">${getAlertIcon(alert.type)} ${alert.type}</span>
                <span class="alert-time">${formatTime(alert.timestamp)}</span>
            </div>
            <div class="alert-message">${alert.message}</div>
        </div>
    `).join('');
}

// Get icon for alert type
function getAlertIcon(type) {
    const icons = {
        'intrusion': '⚠️',
        'fire': '🔥',
        'medical': '❤️',
        'security': '🛡️',
        'system': '⚙️'
    };
    return icons[type.toLowerCase()] || 'ℹ️';
}

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
}

// Update last update time
function updateLastUpdate() {
    const now = new Date();
    lastUpdate.textContent = now.toLocaleTimeString();
}

// Initiate emergency call
async function initiateEmergencyCall(type) {
    const confirmMessages = {
        'police': 'Call Police (Emergency)?',
        'ambulance': 'Call Ambulance (Medical Emergency)?',
        'fire': 'Call Fire Department (Fire Emergency)?'
    };
    
    if (!confirm(confirmMessages[type])) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/emergency/${type}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Emergency call initiated: ${type}\nCall ID: ${result.call_id}`);
        } else {
            alert('Failed to initiate emergency call');
        }
    } catch (error) {
        console.error('Emergency call failed:', error);
        alert('Error: Could not connect to security system');
    }
}

// Open settings
function openSettings() {
    chrome.runtime.openOptionsPage();
}
