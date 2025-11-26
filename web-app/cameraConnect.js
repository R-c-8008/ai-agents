/**
 * Camera Connection Logic for Security Monitor Agent
 * Supports WiFi, Bluetooth, and Mobile Cam App connections
 */

// ==================== WiFi Connection ====================

/**
 * Connect camera via WiFi
 * Scans local network for WiFi-enabled cameras and establishes connection
 */
async function connectWithWiFi() {
  try {
    console.log('Scanning for WiFi cameras...');
    
    // Discover WiFi cameras on local network
    const devices = await discoverWiFiCameras();
    
    if (devices.length === 0) {
      throw new Error('No WiFi cameras found on network');
    }
    
    // Display available cameras to user
    const selectedDevice = await showDeviceSelectionModal(devices);
    
    if (!selectedDevice) {
      console.log('User cancelled device selection');
      return null;
    }
    
    // Establish connection with selected camera
    const connection = await connectToCamera({
      ip: selectedDevice.ip,
      port: selectedDevice.port || 8080,
      protocol: 'rtsp', // or 'http' depending on camera
      type: 'wifi'
    });
    
    if (connection.success) {
      // Store camera info in database
      await saveCameraToDatabase({
        name: selectedDevice.name || `Camera ${Date.now()}`,
        type: 'wifi',
        ip: selectedDevice.ip,
        streamUrl: connection.streamUrl,
        connected: true,
        connectedAt: new Date().toISOString()
      });
      
      console.log('✅ Camera connected via WiFi!');
      return connection;
    }
    
  } catch (error) {
    console.error('WiFi connection failed:', error.message);
    showErrorNotification('WiFi Connection Failed', error.message);
    return null;
  }
}

/**
 * Discover WiFi cameras on local network
 * Uses network scanning to find compatible cameras
 */
async function discoverWiFiCameras() {
  // Implementation options:
  // 1. mDNS/Bonjour discovery for cameras advertising services
  // 2. Network scan of common camera ports (554 for RTSP, 80/8080 for HTTP)
  // 3. UPnP discovery for network devices
  
  return new Promise((resolve, reject) => {
    // Simulate camera discovery
    // In production, use actual network scanning library
    
    fetch('/api/discover-cameras', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'wifi' })
    })
    .then(response => response.json())
    .then(data => resolve(data.cameras || []))
    .catch(error => reject(error));
  });
}

// ==================== Bluetooth Connection ====================

/**
 * Connect camera via Bluetooth
 * Uses Web Bluetooth API for pairing and connection
 */
async function connectWithBluetooth() {
  try {
    // Check if Bluetooth is supported
    if (!navigator.bluetooth) {
      throw new Error('Bluetooth not supported in this browser. Use Chrome, Edge, or Opera.');
    }
    
    console.log('Scanning for Bluetooth cameras...');
    
    // Request Bluetooth device with camera service
    const device = await navigator.bluetooth.requestDevice({
      filters: [
        { services: ['battery_service'] }, // Standard service
        { namePrefix: 'Cam' }, // Devices starting with "Cam"
        { namePrefix: 'Camera' }
      ],
      optionalServices: [
        '0000ffe0-0000-1000-8000-00805f9b34fb', // Custom camera service UUID
        'device_information'
      ]
    });
    
    console.log('Device selected:', device.name);
    
    // Connect to GATT server
    const server = await device.gatt.connect();
    console.log('Connected to GATT server');
    
    // Get camera service and characteristics
    const service = await server.getPrimaryService('0000ffe0-0000-1000-8000-00805f9b34fb');
    const characteristic = await service.getCharacteristic('0000ffe1-0000-1000-8000-00805f9b34fb');
    
    // Start notifications for camera data
    await characteristic.startNotifications();
    characteristic.addEventListener('characteristicvaluechanged', handleBluetoothData);
    
    // Save camera connection
    await saveCameraToDatabase({
      name: device.name || `Bluetooth Camera ${Date.now()}`,
      type: 'bluetooth',
      deviceId: device.id,
      connected: true,
      connectedAt: new Date().toISOString()
    });
    
    console.log('✅ Camera connected via Bluetooth!');
    showSuccessNotification('Bluetooth Connected', `${device.name} is now connected`);
    
    return { device, server, service, characteristic };
    
  } catch (error) {
    console.error('Bluetooth connection failed:', error.message);
    showErrorNotification('Bluetooth Connection Failed', error.message);
    return null;
  }
}

/**
 * Handle incoming Bluetooth data from camera
 */
function handleBluetoothData(event) {
  const value = event.target.value;
  // Parse and process camera data
  const data = new TextDecoder().decode(value);
  console.log('Bluetooth data received:', data);
  
  // Process camera stream data
  // This could be metadata, image chunks, or control responses
}

// ==================== Cam App Connection ====================

/**
 * Connect using mobile Cam App
 * Generates pairing QR code or deep link for mobile app connection
 */
async function connectWithCamApp() {
  try {
    console.log('Generating Cam App pairing...');
    
    // Generate unique session ID for pairing
    const sessionId = generateSessionId();
    
    // Create pairing link
    const pairLink = `${window.location.origin}/pair?session=${sessionId}`;
    const deepLink = `camapp://pair?session=${sessionId}&server=${encodeURIComponent(window.location.origin)}`;
    
    // Store session in backend for validation
    await fetch('/api/create-pairing-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId,
        createdAt: new Date().toISOString(),
        expiresIn: 300 // 5 minutes
      })
    });
    
    // Show QR code modal
    showQRCodeModal({
      link: pairLink,
      deepLink: deepLink,
      sessionId: sessionId
    });
    
    // Listen for successful pairing via WebSocket
    const connection = await waitForCamAppConnection(sessionId);
    
    if (connection.success) {
      await saveCameraToDatabase({
        name: connection.deviceName || `Mobile Camera ${Date.now()}`,
        type: 'camapp',
        sessionId: sessionId,
        deviceInfo: connection.deviceInfo,
        connected: true,
        connectedAt: new Date().toISOString()
      });
      
      console.log('✅ Camera connected via Cam App!');
      showSuccessNotification('Cam App Connected', 'Mobile camera is now streaming');
      return connection;
    }
    
  } catch (error) {
    console.error('Cam App connection failed:', error.message);
    showErrorNotification('Cam App Connection Failed', error.message);
    return null;
  }
}

/**
 * Generate unique session ID for pairing
 */
function generateSessionId() {
  return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

/**
 * Wait for mobile app to connect using WebSocket
 */
function waitForCamAppConnection(sessionId, timeout = 300000) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(`wss://${window.location.host}/ws/pairing`);
    
    const timeoutId = setTimeout(() => {
      ws.close();
      reject(new Error('Connection timeout. Please try again.'));
    }, timeout);
    
    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'pair', sessionId }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'connected' && data.sessionId === sessionId) {
        clearTimeout(timeoutId);
        ws.close();
        resolve({
          success: true,
          deviceName: data.deviceName,
          deviceInfo: data.deviceInfo,
          streamUrl: data.streamUrl
        });
      }
    };
    
    ws.onerror = (error) => {
      clearTimeout(timeoutId);
      reject(error);
    };
  });
}

// ==================== Helper Functions ====================

/**
 * Connect to camera using provided configuration
 */
async function connectToCamera(config) {
  const response = await fetch('/api/connect-camera', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  
  return await response.json();
}

/**
 * Save camera information to database
 */
async function saveCameraToDatabase(cameraData) {
  const response = await fetch('/api/cameras', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cameraData)
  });
  
  return await response.json();
}

/**
 * Show device selection modal
 */
function showDeviceSelectionModal(devices) {
  return new Promise((resolve) => {
    // Create and show modal with device list
    // User selects device, modal resolves with selection
    // Implementation depends on your UI framework
    console.log('Available devices:', devices);
    resolve(devices[0]); // Placeholder
  });
}

/**
 * Show QR code modal for Cam App pairing
 */
function showQRCodeModal({ link, deepLink, sessionId }) {
  // Create modal with QR code
  // Can use libraries like qrcode.js or qrcode.react
  console.log('Pairing link:', link);
  console.log('Deep link:', deepLink);
  console.log('Session ID:', sessionId);
  
  // Example implementation:
  const modal = document.createElement('div');
  modal.innerHTML = `
    <div class="qr-modal">
      <h3>Scan with Cam App</h3>
      <div id="qrcode"></div>
      <p>Or tap: <a href="${deepLink}">Open in Cam App</a></p>
      <button onclick="this.closest('.qr-modal').remove()">Cancel</button>
    </div>
  `;
  document.body.appendChild(modal);
}

/**
 * Show success notification
 */
function showSuccessNotification(title, message) {
  console.log(`✅ ${title}: ${message}`);
  // Implement toast notification or alert
}

/**
 * Show error notification
 */
function showErrorNotification(title, message) {
  console.error(`❌ ${title}: ${message}`);
  // Implement error toast or alert
}

// ==================== Export Functions ====================

export {
  connectWithWiFi,
  connectWithBluetooth,
  connectWithCamApp,
  discoverWiFiCameras
};
