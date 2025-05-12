async function loadApps() {
    try {
        const appGrid = document.getElementById('app-grid');
        appGrid.innerHTML = `
            <div class="col-span-full flex flex-col items-center justify-center py-12">
                <i class="fas fa-circle-notch fa-spin text-cyan-500 text-4xl mb-4"></i>
                <p class="text-gray-600 dark:text-gray-400">Loading applications...</p>
            </div>
        `;
        const response = await fetch('/get_apps_config');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const config = await response.json();
        
        if (!config?.apps || !Array.isArray(config.apps)) {
            throw new Error('Invalid apps configuration format');
        }

        return config.apps;
    } catch (error) {
        console.error('Error loading apps config:', error);
        
        // Show error state to user
        const appGrid = document.getElementById('app-grid');
        appGrid.innerHTML = `
            <div class="col-span-full flex flex-col items-center justify-center py-12 text-center">
                <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                <h3 class="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">
                    Failed to load applications
                </h3>
                <p class="text-gray-600 dark:text-gray-400 max-w-md">
                    Could not load application configuration. Please try refreshing the page.
                </p>
                <button onclick="window.location.reload()" class="mt-4 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors">
                    <i class="fas fa-sync-alt mr-2"></i> Refresh
                </button>
            </div>
        `;
    }
}

// Initialize the application with proper error handling
async function initializeApplication() {
    try {
        const apps = await loadApps();
        renderApps(apps);
        setupCategoryFilter(apps);
        startAppStatusChecker();
    } catch (error) {
        console.error('Application initialization failed:', error);
    }
}

// Render apps to the grid with improved card design
function renderApps(apps) {
    const appGrid = document.getElementById('app-grid');
    
    if (!apps || apps.length === 0) {
        appGrid.innerHTML = `
            <div class="col-span-full flex flex-col items-center justify-center py-12">
                <i class="fas fa-folder-open text-gray-400 text-4xl mb-4"></i>
                <p class="text-gray-600 dark:text-gray-400">No applications available</p>
            </div>
        `;
        return;
    }

    appGrid.innerHTML = '';
    
    apps.forEach(app => {
        const card = document.createElement('div');
        card.className = `group bg-gradient-to-b from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-xl shadow border hover:shadow-lg transition-all duration-300 dark:border-gray-700 overflow-hidden cursor-pointer`;
        card.id = `card-${app.script}`;
        
        card.innerHTML = `
            <div class="relative h-full flex flex-col">
                <div class="w-full h-32 bg-${app.color}-100 dark:bg-${app.color}-900 rounded-t-lg flex items-center justify-center transition-all duration-300 group-hover:opacity-90">
                    <i class="fas ${app.icon} text-4xl text-${app.color}-600 dark:text-${app.color}-300"></i>
                </div>
                <div class="p-4 flex-1 flex flex-col">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-1">${app.title}</h3>
                        <span id="status-${app.script}" class="text-green-500 hidden">
                            <i class="fas fa-check-circle"></i>
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 flex-1">${app.description}</p>
                </div>
            </div>
        `;
        
        updateAppStatus(app.script);
        card.addEventListener('click', async () => {
            await handleAppClick(app, card);
        });
        
        appGrid.appendChild(card);
    });
}

async function handleAppClick(app, card) {
    const statusElement = document.getElementById(`status-${app.script}`);
    if (statusElement && !statusElement.classList.contains('hidden')) {
        return;
    }
    
    if (!isConnected) {
        showAlert('Please connect to a device first using USB, WiFi or Bluetooth');
        return;
    }
    
    const originalContent = card.innerHTML;            // Add loading state to the clicked card
    card.innerHTML = `
        <div class="h-full flex items-center justify-center p-4">
            <i class="fas fa-circle-notch fa-spin text-${app.color}-500 text-xl mr-2"></i>
            <span>Launching ${app.title}...</span>
        </div>
    `;
    
    try {
        const response = await fetch(`/check_app_status/${app.script}`);
        
        if (!response.ok) {
            throw new Error('Failed to check app status');
        }
        
        const data = await response.json();
        
        await launchApplication(app.script);
        card.innerHTML = originalContent;
        updateAppStatus(app.script); // Update status after launch
    } catch (error) {
        console.error('Error launching app:', error);
        showAlert(`Failed to launch ${app.title}: ${error.message}`);
        card.innerHTML = originalContent;
    }
}

async function updateAppStatus(appName) {
    try {
        const response = await fetch(`/check_app_status/${appName}`);
        if (!response.ok) return;
        
        const data = await response.json();
        const statusElement = document.getElementById(`status-${appName}`);
        const cardElement = document.getElementById(`card-${appName}`);
        
        if (statusElement && cardElement) {
            if (data.status === 'running') {
                statusElement.classList.remove('hidden');
                cardElement.classList.add('cursor-not-allowed');
                cardElement.classList.remove('cursor-pointer');
                cardElement.classList.remove('hover:shadow-lg');
                cardElement.classList.add('opacity-60');
            } else {
                statusElement.classList.add('hidden');
                cardElement.style.pointerEvents = 'auto';
                cardElement.classList.remove('cursor-not-allowed');
                cardElement.classList.add('cursor-pointer');
                cardElement.classList.add('hover:shadow-lg');
                cardElement.classList.remove('opacity-60');
            }
        }
    } catch (error) {
        console.error('Error checking app status:', error);
    }
}

// Periodically check all app statuses
function startAppStatusChecker() {
    checkAllAppStatuses();
    setInterval(checkAllAppStatuses, 200);
}

// Check status of all apps
function checkAllAppStatuses() {
    const appGrid = document.getElementById('app-grid');
    if (!appGrid) return;
    
    const apps = appGrid.querySelectorAll('[id^="status-"]');
    apps.forEach(statusElement => {
        const appName = statusElement.id.replace('status-', '');
        updateAppStatus(appName);
    });
}

// Set up category filter with fixed options
function setupCategoryFilter(apps) {
    const categorySelect = document.querySelector('select');
    
    const fixedCategories = ['All', 'ECG', 'EMG', 'EOG', 'EEG', 'Tools']; // Fixed filter options
    categorySelect.innerHTML = '';        // Clear existing options
    
    // Add fixed options
    fixedCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        
        // Disable option if no apps exist for this category (except 'All')
        if (category !== 'All') {
            const hasApps = apps.some(app => app.category === category);
            option.disabled = !hasApps;
            if (!hasApps) {
                option.textContent += ' (0)';
            }
        }
        
        categorySelect.appendChild(option);
    });

    // Add event listener for filtering
    categorySelect.addEventListener('change', (e) => {
        const selectedCategory = e.target.value;
        filterAppsByCategory(selectedCategory, apps);
    });
}

// Filter apps by category with smooth transition
function filterAppsByCategory(category, allApps) {
    const appGrid = document.getElementById('app-grid');
    
    // Add fade-out effect
    appGrid.style.opacity = '0.5';
    appGrid.style.transition = 'opacity 0.3s ease';
    
    setTimeout(() => {
        const filteredApps = category === 'All' ? 
            allApps : 
            allApps.filter(app => app.category === category);
        
        renderApps(filteredApps);
        
        // Add fade-in effect
        appGrid.style.opacity = '0';
        setTimeout(() => {
            appGrid.style.opacity = '1';
            checkAllAppStatuses();
        }, 10);
    }, 300);
}

// Theme toggle
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = themeToggle.querySelector('i');

function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    themeIcon.className = isDark ? 'fas fa-sun text-xl' : 'fas fa-moon text-xl';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

themeToggle.addEventListener('click', toggleTheme);

// Initialize theme
const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark');
    themeIcon.className = 'fas fa-sun text-xl';
} else {
    document.documentElement.classList.remove('dark');
    themeIcon.className = 'fas fa-moon text-xl';
}

// Connection management
const connectionBtns = document.querySelectorAll('.connection-btn');
const connectBtn = document.getElementById('connect-btn');
const connectingBtn = document.getElementById('connecting-btn');
const disconnectBtn = document.getElementById('disconnect-btn');
const disconnectingBtn = document.getElementById('disconnecting-btn');
const recordBtn = document.getElementById('record-btn');
const filenameInput = document.getElementById('filename');
const recordingStatus = document.getElementById('recording-status');
const statusDiv = document.getElementById('connection-status');
const statusText = document.getElementById('status-text');
const statusIcon = document.getElementById('status-icon');
const bleModal = document.getElementById('ble-modal');
const bleDevicesList = document.getElementById('ble-devices-list');
const closeBleModal = document.getElementById('close-ble-modal');
const rescanBle = document.getElementById('rescan-ble');

let selectedProtocol = null;
let selectedBleDevice = null;
let isConnected = false;
let isRecording = false;
let eventSource = null;
let isScanning = false;

// Function to update the filename timestamp periodically
function startTimestampUpdater() {
    updateFilenameTimestamp();
    setInterval(updateFilenameTimestamp, 1000);
}

// Update the filename timestamp in the input field
function updateFilenameTimestamp() {
    // Only update if recording is stop
    if (!isRecording) {
        const defaultName = `ChordsPy_${getTimestamp()}`;
        filenameInput.placeholder = defaultName;
        
        // If the input is empty or has the default pattern, update the value too
        if (!filenameInput.value || filenameInput.value.startsWith('ChordsPy_')) {
            filenameInput.value = defaultName;
        }
    }
}

// Function to generate timestamp for filename
function getTimestamp() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}${month}${day}_${hours}${minutes}${seconds}`;
}

function setProtocolButtonsDisabled(disabled) {
    connectionBtns.forEach(btn => {
        btn.disabled = disabled;
        // Add/remove cursor-not-allowed class based on disabled state
        if (disabled) {
            btn.classList.add('cursor-not-allowed');
            // Only keep the connected protocol button highlighted
            if (btn.dataset.protocol !== selectedProtocol) {
                btn.classList.remove('bg-cyan-500', 'text-white');
                // Set to original colors (dark mode aware)
                btn.classList.add('text-gray-700', 'dark:text-gray-200');
                btn.classList.remove('hover:bg-cyan-500', 'hover:text-white');
            } else {
                // Make connected protocol button darker
                btn.classList.remove('bg-cyan-500');
                btn.classList.add('bg-cyan-600', 'dark:bg-cyan-700');
            }
        } else {
            btn.classList.remove('cursor-not-allowed');
            btn.classList.add('hover:bg-cyan-500', 'hover:text-white');
            btn.classList.remove('bg-cyan-600', 'dark:bg-cyan-700');
        }
    });
}

// Initialize filename with default value
function initializeFilename() {
    const defaultName = `ChordsPy_${getTimestamp()}`;
    filenameInput.value = defaultName;
    filenameInput.placeholder = defaultName;
    filenameInput.disabled = false;              // Ensure input is enabled initially
    filenameInput.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
    filenameInput.classList.add('dark:bg-gray-800');
    startTimestampUpdater();
}

// Sanitize filename input - replace spaces and dots with underscores
function sanitizeFilename(filename) {
    // Remove leading/trailing whitespace
    filename = filename.trim();
    // Replace spaces and dots with underscores
    filename = filename.replace(/[^A-Za-z0-9_-]/g, '_');
    return filename;
}

// Handle filename input changes
filenameInput.addEventListener('input', function() {
    // Only sanitize for display (don't modify the actual value)
    const cursorPos = this.selectionStart;
    const displayValue = sanitizeFilename(this.value);
    this.value = displayValue;
    // Restore cursor position after display update
    this.setSelectionRange(cursorPos, cursorPos);
});

// Handle protocol selection
connectionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        connectionBtns.forEach(b => b.classList.remove('bg-cyan-500', 'text-white'));
        btn.classList.add('bg-cyan-500', 'text-white');
        selectedProtocol = btn.dataset.protocol;
        
        // For BLE, show device selection modal
        if (selectedProtocol === 'ble') {
            showBleDeviceModal();
        } else {
            connectBtn.disabled = false;   // For other protocols, enable connect button immediately
        }
    });
});

// Show BLE device selection modal
function showBleDeviceModal() {
    bleModal.classList.remove('hidden');
    scanBleDevices();
}

// Scan for BLE devices
function scanBleDevices() {
    if (isScanning) return;
    
    isScanning = true;
    bleDevicesList.innerHTML = `
        <div class="flex items-center justify-center py-4">
            <i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i>
            <span>Scanning for devices...</span>
        </div>
    `;
    
    fetch('/scan_ble')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            isScanning = false;
            if (data.status === 'success' && data.devices.length > 0) {
                renderBleDevices(data.devices);
            } else {
                bleDevicesList.innerHTML = `
                    <div class="text-center py-4 text-gray-500">
                        ${data.message || 'No NPG devices found. Make sure your device is powered on and in range.'}
                    </div>
                `;
            }
        })
        .catch(error => {
            isScanning = false;
            console.error('BLE scan error:', error);
            bleDevicesList.innerHTML = `
                <div class="text-center py-4 text-red-500">
                    Error scanning for devices. Please try again.
                </div>
            `;
        });
}

// Render BLE devices list
function renderBleDevices(devices) {
    bleDevicesList.innerHTML = '';
    
    if (devices.length === 0) {
        bleDevicesList.innerHTML = `
            <div class="text-center py-4 text-gray-500">
                No NPG devices found.
            </div>
        `;
        return;
    }
    
    devices.forEach(device => {
        const deviceElement = document.createElement('div');
        deviceElement.className = 'p-3 border-b dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer flex items-center';
        deviceElement.innerHTML = `
            <i class="fab fa-bluetooth-b text-blue-500 mr-3 text-lg"></i>
            <div class="flex-1">
                <div class="font-medium text-gray-800 dark:text-gray-200">${device.name}</div>
                <div class="text-xs text-gray-500">${device.address}</div>
            </div>
            ${selectedBleDevice?.address === device.address ? 
                '<i class="fas fa-check text-green-500 ml-2"></i>' : ''}
        `;
        
        deviceElement.addEventListener('click', () => {
            selectedBleDevice = device;
            bleModal.classList.add('hidden');
            connectBtn.disabled = false; // Enable connect button after selection
        });
        
        bleDevicesList.appendChild(deviceElement);
    });
}

// Close BLE modal
closeBleModal.addEventListener('click', () => {
    bleModal.classList.add('hidden');
    connectionBtns.forEach(b => b.classList.remove('bg-cyan-500', 'text-white'));
    selectedProtocol = null;
    selectedBleDevice = null;
    connectBtn.disabled = true;
});

// Rescan BLE devices
rescanBle.addEventListener('click', scanBleDevices);

// Handle connect button
connectBtn.addEventListener('click', async () => {
    if (!selectedProtocol) {
        showAlert('Please select a protocol before connecting.');
        return;
    }

    // For BLE, ensure a device is selected
    if (selectedProtocol === 'ble' && !selectedBleDevice) {
        showAlert('Please select a BLE device before connecting.');
        return;
    }

    // Transition to connecting state
    connectBtn.classList.add('hidden');
    connectingBtn.classList.remove('hidden');
    connectionBtns.forEach(btn => btn.disabled = true);

    try {
        let postData = { protocol: selectedProtocol };
        if (selectedProtocol === 'ble' && selectedBleDevice) {
            postData.device_address = selectedBleDevice.address;
        }

        const response = await fetch('/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data.status === 'connecting') {
            // Start polling connection status
            await pollConnectionStatus();
        } else {
            throw new Error(data.message || 'Connection failed');
        }
    } catch (error) {
        console.error('Connection error:', error);
        showStatus(`Connection failed: ${error.message}`, 'fa-times-circle', 'text-red-500');
        // Return to connect state
        connectingBtn.classList.add('hidden');
        connectBtn.classList.remove('hidden');
        connectBtn.disabled = false;
        connectionBtns.forEach(btn => btn.disabled = false);
    }
});

// Poll connection status
async function pollConnectionStatus() {
    let attempts = 0;
    const maxAttempts = 15; // 15 seconds timeout
    
    const checkStatus = async () => {
        attempts++;
        
        try {
            const response = await fetch('/check_connection');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.status === 'connected') {
                handleConnectionSuccess();
                return true;
            } else if (attempts >= maxAttempts) {
                throw new Error('Connection timeout');
            } else {
                // Continue polling
                return new Promise(resolve => {
                    setTimeout(async () => {
                        const result = await checkStatus();
                        resolve(result);
                    }, 1000);
                });
            }
        } catch (error) {
            console.error('Connection polling error:', error);
            showStatus(`Connection failed: Try again`, 'fa-times-circle', 'text-red-500');
            // Return to connect state
            connectingBtn.classList.add('hidden');
            connectBtn.classList.remove('hidden');
            connectBtn.disabled = false;
            connectionBtns.forEach(btn => btn.disabled = false);
            return false;
        }
    };
    
    return await checkStatus();
}

function handleConnectionSuccess() {
    isConnected = true;
    // Transition to disconnect state
    connectingBtn.classList.add('hidden');
    disconnectBtn.classList.remove('hidden');
    
    // Highlight the connected protocol and disable others
    connectionBtns.forEach(btn => {
        if (btn.dataset.protocol === selectedProtocol) {
            // Connected protocol - make it darker
            btn.classList.remove('bg-cyan-500', 'hover:bg-cyan-500');
            btn.classList.add('bg-cyan-600', 'dark:bg-cyan-700', 'cursor-default');
            btn.classList.add('text-white');
        } else {
            // Other protocols - disable and make less prominent
            btn.classList.remove('bg-cyan-500', 'text-white', 'hover:bg-cyan-500', 'hover:text-white');
            btn.classList.add('cursor-not-allowed', 'text-gray-400', 'dark:text-gray-500');
        }
        btn.disabled = true;
    });
    
    showStatus(`Connected via ${selectedProtocol.toUpperCase()}`, 'fa-check-circle');
    
    // Start console updates
    startConsoleUpdates();
}

function launchApplication(appName) {
    fetch('/launch_app', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app: appName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
        } else if (data.code === 'ALREADY_RUNNING') {
            showAlert(data.message);
        } else {
            showAlert(`Failed to launch ${appName}: ${data.message}`);
        }
    })
    .catch(error => {
        showAlert(`Error launching ${appName}: ${error.message}`);
    });
}

// Handle disconnect button
disconnectBtn.addEventListener('click', async () => {
    try {
        // Show connecting state during disconnection
        disconnectBtn.classList.add('hidden');
        disconnectingBtn.classList.remove('hidden');
        
        const response = await fetch('/disconnect', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'disconnected') {
            isConnected = false;
            // Return to connect state
            disconnectingBtn.classList.add('hidden');
            connectBtn.classList.remove('hidden');
            showStatus('Disconnected!', 'fa-times-circle', 'text-red-500');
            
            // Reset all protocol buttons
            connectionBtns.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove(
                    'bg-cyan-500', 'bg-cyan-600', 'dark:bg-cyan-700', 
                    'text-white', 'cursor-not-allowed', 'cursor-default',
                    'text-gray-400', 'dark:text-gray-500'
                );
                btn.classList.add(
                    'hover:bg-cyan-500', 'hover:text-white',
                    'text-gray-700', 'dark:text-gray-200',
                    'cursor-pointer'
                );
            });
            
            statusDiv.classList.add('hidden');
            selectedProtocol = null;
            selectedBleDevice = null;
            
            // Stop recording if active
            if (isRecording) {
                isRecording = false; // Force set to false since we're disconnecting
                recordBtn.innerHTML = 'Start Recording';
                recordBtn.classList.remove('bg-gray-500');
                recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
                recordingStatus.classList.add('hidden');
            }
            
            // Stop console updates
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
        }
    } catch (error) {
        console.error('Disconnection error:', error);
        // Return to disconnect state if disconnection failed
        disconnectingBtn.classList.add('hidden');
        disconnectBtn.classList.remove('hidden');
        showStatus(`Disconnection failed: ${error.message}`, 'fa-times-circle', 'text-red-500');
    }
});

// Start console updates via SSE
function startConsoleUpdates() {
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource('/console_updates');
    
    eventSource.onmessage = function(e) {
        console.log('Console update:', e.data);
    };
    
    eventSource.onerror = function() {
        console.error('EventSource failed');
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    };
}

// Handle record button
recordBtn.addEventListener('click', toggleRecording);

// In the toggleRecording function
function toggleRecording() {
    if (!isConnected) {
        showAlert('Please Start a stream before recording.');
        return;
    }

    // Get the filename (already sanitized in the display)
    let filename = filenameInput.value.trim();
    
    // If empty, use default (pass null to let server generate default)
    if (filename === '') {
        filename = null;
    }

    if (isRecording) {
        // Stop recording
        fetch('/stop_recording', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'recording_stopped') {
                    isRecording = false;
                    recordBtn.innerHTML = 'Start Recording';
                    recordBtn.classList.remove('bg-gray-500');
                    recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
                    recordingStatus.classList.add('hidden');
                    
                    // Enable filename input
                    filenameInput.disabled = false;
                    filenameInput.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
                    filenameInput.classList.add('dark:bg-gray-800');
                    updateFilenameTimestamp()
                    showStatus('Recording stopped', 'fa-stop-circle', 'text-red-500');
                }
            })
            .catch(error => {
                console.error('Error stopping recording:', error);
            });
    } else {
        // Start recording - send the filename (or null for default)
        fetch('/start_recording', { 
            method: 'POST',
            headers: {'Content-Type': 'application/json', },
            body: JSON.stringify({ filename: filename })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'recording_started') {
                    isRecording = true;
                    recordBtn.innerHTML = 'Stop Recording';
                    recordBtn.classList.remove('bg-red-500', 'hover:bg-red-600');
                    recordBtn.classList.add('bg-gray-500');
                    recordingStatus.classList.remove('hidden');
                    
                    // Disable filename input
                    filenameInput.disabled = true;
                    filenameInput.classList.add('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
                    filenameInput.classList.remove('dark:bg-gray-800');
                    showStatus('Recording started', 'fa-record-vinyl', 'text-green-500');
                }
            })
            .catch(error => {
                console.error('Error starting recording:', error);
                showAlert('Failed to start recording: ' + error.message);
            });
    }
}

// Initial setup
connectBtn.disabled = true; // Disable connect button until protocol is selected
initializeFilename(); // Set default filename with timestamp

function showStatus(text, icon, colorClass) {
    const statusDiv = document.getElementById('connection-status');
    statusText.textContent = text;
    statusIcon.innerHTML = `<i class="fas ${icon} text-white"></i>`; 
    statusDiv.classList.remove('hidden');
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 3000);
}

function showAlert(message) {
    alert(message);
}

function checkStreamStatus() {
    fetch('/check_stream')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                // If connected, update the frontend
                if (!isConnected) {
                    handleConnectionSuccess();
                    isConnected = true;
                    connectBtn.classList.add('hidden');
                    connectingBtn.classList.add('hidden');
                    disconnectBtn.classList.remove('hidden');
                    // Disable all protocol buttons
                    setProtocolButtonsDisabled(true);
                    startConsoleUpdates();
                }
            } else {
                // If not connected, update the frontend
                if (isConnected) {
                    handleDisconnection();
                    isConnected = false;
                    disconnectBtn.classList.add('hidden');
                    disconnectingBtn.classList.add('hidden');
                    connectingBtn.classList.add('hidden');
                    connectBtn.classList.remove('hidden');
                    showStatus('Disconnected!', 'fa-times-circle', 'text-red-500');
                    
                    // Re-enable protocol buttons
                    setProtocolButtonsDisabled(false);
                    
                    // Stop recording if active and update button
                    if (isRecording) {
                        isRecording = false;
                        recordBtn.innerHTML = 'Start Recording';
                        recordBtn.classList.remove('bg-gray-500');
                        recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
                        recordingStatus.classList.add('hidden');
                        
                        // Enable filename input if recording was stopped due to disconnection
                        filenameInput.disabled = false;
                        filenameInput.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
                        filenameInput.classList.add('dark:bg-gray-800');
                        showStatus('Recording stopped (connection lost)', 'fa-stop-circle', 'text-red-500');
                    }
                    
                    // Stop console updates
                    if (eventSource) {
                        eventSource.close();
                        eventSource = null;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error fetching stream status:', error);
        });
}

function handleDisconnection() {
    isConnected = false;
    disconnectBtn.classList.add('hidden');
    disconnectingBtn.classList.add('hidden');
    connectingBtn.classList.add('hidden');
    connectBtn.classList.remove('hidden');
    showStatus('Stream disconnected!', 'fa-times-circle', 'text-red-500');
    
    // Reset protocol buttons
    connectionBtns.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('bg-cyan-600', 'dark:bg-cyan-700', 'cursor-default');
        btn.classList.add('hover:bg-cyan-500', 'hover:text-white');
    });
    
    // Handle recording state
    if (isRecording) {
        isRecording = false;
        recordBtn.innerHTML = 'Start Recording';
        recordBtn.classList.remove('bg-gray-500');
        recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
        recordingStatus.classList.add('hidden');
        filenameInput.disabled = false;
        showStatus('Recording stopped (stream lost)', 'fa-stop-circle', 'text-red-500');
    }
    
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }
}

// Call the checkStreamStatus function every 1 second
setInterval(checkStreamStatus, 1000);

// Call it initially when the page loads
checkStreamStatus();

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
initializeApplication();

document.getElementById('github-btn').addEventListener('click', () => {
    window.open('https://github.com/upsidedownlabs/Chords-Python', '_blank');
});

document.getElementById('info-btn').addEventListener('click', () => {
    alert('Chords Python - Biopotential Data Acquisition System\nVersion 2.1.0');
});
});