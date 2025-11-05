// Security Monitor Agent - Background Service Worker

// Configuration
const API_BASE_URL = 'http://localhost:5000';
const CHECK_INTERVAL = 30000; // 30 seconds
const NOTIFICATION_SOUND_URL = 'notification.mp3';

// State management
let monitoringStatus = 'unknown';
let lastCheckTime = null;
let alarmId = 'securityMonitorCheck';

// Initialize service worker
chrome.runtime.onInstalled.addListener((details) => {
    console.log('Security Monitor Agent installed:', details.reason);
    initializeExtension();
});

chrome.runtime.onStartup.addListener(() => {
    console.log('Security Monitor Agent started');
    initializeExtension();
});

// Initialize extension
function initializeExtension() {
    // Set default settings
    chrome.storage.sync.get(['apiUrl', 'checkInterval'], (items) => {
        if (!items.apiUrl) {
            chrome.storage.sync.set({ apiUrl: API_BASE_URL });
        }
        if (!items.checkInterval) {
            chrome.storage.sync.set({ checkInterval: CHECK_INTERVAL });
        }
    });
    
    // Start monitoring
    startMonitoring();
}

// Start monitoring
function startMonitoring() {
    // Create alarm for periodic checks
    chrome.alarms.create(alarmId, {
        periodInMinutes: 0.5 // Check every 30 seconds
    });
    
    // Initial check
    checkSecurityStatus();
}

// Handle alarm events
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === alarmId) {
        checkSecurityStatus();
    }
});

// Check security status
async function checkSecurityStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        const data = await response.json();
        
        lastCheckTime = Date.now();
        updateMonitoringStatus(data.status);
        
        // Check for new alerts
        if (data.alerts && data.alerts.length > 0) {
            handleNewAlerts(data.alerts);
        }
    } catch (error) {
        console.error('Failed to check security status:', error);
        updateMonitoringStatus('offline');
    }
}

// Update monitoring status
function updateMonitoringStatus(status) {
    const previousStatus = monitoringStatus;
    monitoringStatus = status;
    
    // Update badge
    updateBadge(status);
    
    // Send status change notification if critical
    if (status === 'alert' && previousStatus !== 'alert') {
        showNotification({
            title: 'Security Alert!',
            message: 'Security system has detected an alert',
            priority: 2
        });
    }
    
    // Store status
    chrome.storage.local.set({ monitoringStatus: status, lastCheckTime });
}

// Update badge
function updateBadge(status) {
    const badges = {
        'active': { text: '✓', color: '#4CAF50' },
        'monitoring': { text: '✓', color: '#4CAF50' },
        'alert': { text: '!', color: '#F44336' },
        'offline': { text: 'X', color: '#9E9E9E' },
        'unknown': { text: '?', color: '#FFC107' }
    };
    
    const badge = badges[status] || badges.unknown;
    
    chrome.action.setBadgeText({ text: badge.text });
    chrome.action.setBadgeBackgroundColor({ color: badge.color });
}

// Handle new alerts
function handleNewAlerts(alerts) {
    alerts.forEach(alert => {
        // Check if alert is new (not shown before)
        chrome.storage.local.get(['shownAlerts'], (items) => {
            const shownAlerts = items.shownAlerts || [];
            
            if (!shownAlerts.includes(alert.id)) {
                // Show notification
                showNotification({
                    title: `Security Alert: ${alert.type}`,
                    message: alert.message,
                    priority: alert.severity === 'critical' ? 2 : 1
                });
                
                // Mark as shown
                shownAlerts.push(alert.id);
                chrome.storage.local.set({ shownAlerts });
            }
        });
    });
}

// Show notification
function showNotification(options) {
    const notificationOptions = {
        type: 'basic',
        iconUrl: 'icon-128.png',
        title: options.title,
        message: options.message,
        priority: options.priority || 1,
        requireInteraction: options.priority === 2
    };
    
    chrome.notifications.create('', notificationOptions, (notificationId) => {
        console.log('Notification shown:', notificationId);
    });
}

// Handle notification clicks
chrome.notifications.onClicked.addListener((notificationId) => {
    // Open popup or specific page
    chrome.action.openPopup();
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getStatus') {
        sendResponse({ 
            status: monitoringStatus, 
            lastCheckTime 
        });
    } else if (request.action === 'refreshStatus') {
        checkSecurityStatus();
        sendResponse({ success: true });
    }
    return true;
});

// Keep service worker alive
setInterval(() => {
    chrome.storage.local.get(['heartbeat'], () => {
        chrome.storage.local.set({ heartbeat: Date.now() });
    });
}, 20000);
