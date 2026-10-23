let isLogging = false;

function logError(error) {
    if (isLogging) return; // Prevent recursion
    
    isLogging = true;
    try {
        const errorMessage = `[${getTimestamp()}] ${error.stack || error.message || error}\n`;
        
        // Fallback to console if fetch fails
        fetch('/log_error', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ error: errorMessage })
        }).catch(() => {
            console.error('Failed to log error:', errorMessage);
        });
        
        console.error(errorMessage);
    } finally {
        isLogging = false;
    }
}

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
        logError('Error loading apps config:', error);
        
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
                <button onclick="window.location.reload()" class="mt-4 px-4 py-2 bg-cyan-600 dark:bg-cyan-700 text-white rounded-lg hover:bg-cyan-700 dark:hover:bg-cyan-800 transition-colors">
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
        logError('Application initialization failed:', error);
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
        card.className = `group bg-gradient-to-b from-white to-gray-50 dark:bg-none dark:bg-gray-850 rounded-xl shadow border hover:shadow-lg transition-all duration-300 dark:border-gray-700 overflow-hidden cursor-pointer`;
        card.id = `card-${app.script}`;
        
        card.innerHTML = `
            <div class="relative h-full flex flex-col">
                <div class="w-full h-32 bg-${app.color}-500/10 dark:bg-${app.color}-500/20 rounded-t-lg flex items-center justify-center transition-all duration-300 group-hover:opacity-90">
                    <i class="fas ${app.icon} text-4xl text-${app.color}-600 dark:text-${app.color}-400"></i>
                </div>
                <div class="p-4 flex-1 flex flex-col">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-1">${app.title}</h3>
                        <span id="status-${app.script}" class="text-green-500 hidden">
                            <i class="fas fa-check-circle"></i>
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 flex-1">${app.description}</p>
                    <button onclick="launchApp('${app.script}')" 
                            class="w-full py-2 bg-${app.color}-600/90 hover:bg-${app.color}-700 dark:bg-${app.color}-700/90 dark:hover:bg-${app.color}-800 text-white rounded-lg transition-colors">
                        Launch
                    </button>
                </div>
            </div>
        `;
        
        appGrid.appendChild(card);
    });
}

async function launchApp(appScript) {
    try {
        const response = await fetch('/launch_app', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ app: appScript })
        });
        
        const result = await response.json();
        
        if (result.status === 'error') {
            if (result.code === 'ALREADY_RUNNING') {
                showToast('info', 'Application is already running');
            } else {
                showToast('error', `Failed to launch application: ${result.message}`);
            }   
        } else {
            console.log(`Launched ${appScript}`);
        }
    } catch (error) {
        logError('Error launching app:', error);
    }
}

async function handleAppClick(app, card) {
    const statusElement = document.getElementById(`status-${app.script}`);
    if (statusElement && !statusElement.classList.contains('hidden')) {
        return;
    }
    
    if (!isConnected) {
        showToast('info', 'Connect your device first');
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
        logError('Error launching app:', error);
        showToast('error', `Failed to launch ${app.title}: ${error.message}`);
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
        logError('Error checking app status:', error);
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
    const dropdown = document.getElementById('category-dropdown');
    const button = document.getElementById('category-btn');
    const menu = document.getElementById('category-menu');
    const label = document.getElementById('category-label');

    const fixedCategories = ['All', 'ECG', 'EMG', 'EOG', 'EEG', 'Tools']; // Fixed filter options
    menu.innerHTML = '';        // Clear existing options
    const items = [];

    const closeMenu = (returnFocus = false) => {
        menu.classList.add('hidden');
        button.setAttribute('aria-expanded', 'false');
        if (returnFocus) button.focus();
    };
    const openMenu = () => {
        menu.classList.remove('hidden');
        button.setAttribute('aria-expanded', 'true');
    };
    const choose = (category, userAction = true) => {
        label.textContent = category;
        items.forEach(item => {
            const selected = item.dataset.value === category;
            item.setAttribute('aria-selected', String(selected));
            item.querySelector('i').classList.toggle('invisible', !selected);
        });
        if (userAction) {    // Not on the initial setup: the grid is already showing all apps
            closeMenu(true);
            filterAppsByCategory(category, apps);
        }
    };

    fixedCategories.forEach(category => {
        const item = document.createElement('li');
        item.setAttribute('role', 'option');
        item.dataset.value = category;
        item.tabIndex = -1;
        item.className = 'flex items-center justify-between gap-4 px-3 py-2 text-sm rounded-lg text-gray-700 dark:text-gray-200 outline-none';

        // Disable the option if no apps exist for this category (except 'All')
        const hasApps = category === 'All' || apps.some(app => app.category === category);
        item.innerHTML = `<span>${category}${hasApps ? '' : ' (0)'}</span><i class="fas fa-check text-xs text-cyan-600 dark:text-cyan-400 invisible"></i>`;
        if (hasApps) {
            item.classList.add('cursor-pointer', 'hover:bg-gray-100', 'dark:hover:bg-gray-700', 'focus:bg-gray-100', 'dark:focus:bg-gray-700');
            item.addEventListener('click', () => choose(category));
        } else {
            item.setAttribute('aria-disabled', 'true');
            item.classList.add('opacity-40', 'cursor-not-allowed');
        }
        menu.appendChild(item);
        items.push(item);
    });
    choose('All', false);    // Mark 'All' as selected
    closeMenu();

    // Open/close the menu, keyboard navigation (arrows, Enter, Escape) and click outside to close
    button.addEventListener('click', () => menu.classList.contains('hidden') ? openMenu() : closeMenu());
    button.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            openMenu();
            const enabled = items.filter(item => !item.hasAttribute('aria-disabled'));
            (e.key === 'ArrowDown' ? enabled[0] : enabled[enabled.length - 1]).focus();
        }
    });
    menu.addEventListener('keydown', (e) => {
        const enabled = items.filter(item => !item.hasAttribute('aria-disabled'));
        const index = enabled.indexOf(document.activeElement);
        if (e.key === 'ArrowDown') { e.preventDefault(); enabled[(index + 1) % enabled.length].focus(); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); enabled[(index - 1 + enabled.length) % enabled.length].focus(); }
        else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (index >= 0) choose(enabled[index].dataset.value); }
        else if (e.key === 'Escape') { closeMenu(true); }
    });
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) closeMenu();
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
                btn.classList.remove('bg-cyan-600', 'dark:bg-cyan-700', 'text-white');
                // Set to original colors (dark mode aware)
                btn.classList.add('text-gray-700', 'dark:text-gray-200');
                btn.classList.remove('hover:bg-cyan-600', 'dark:hover:bg-cyan-700', 'hover:text-white');
            } else {
                // Make connected protocol button darker
                btn.classList.remove('bg-cyan-600', 'dark:bg-cyan-700');
                btn.classList.add('bg-cyan-700', 'dark:bg-cyan-800');
            }
        } else {
            btn.classList.remove('cursor-not-allowed');
            btn.classList.add('hover:bg-cyan-600', 'dark:hover:bg-cyan-700', 'hover:text-white');
            btn.classList.remove('bg-cyan-700', 'dark:bg-cyan-800');
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
        connectionBtns.forEach(b => b.classList.remove('bg-cyan-600', 'dark:bg-cyan-700', 'text-white'));
        btn.classList.add('bg-cyan-600', 'dark:bg-cyan-700', 'text-white');
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
            logError('BLE scan error:', error);
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
    connectionBtns.forEach(b => b.classList.remove('bg-cyan-600', 'dark:bg-cyan-700', 'text-white'));
    selectedProtocol = null;
    selectedBleDevice = null;
    connectBtn.disabled = true;
});

// Rescan BLE devices
rescanBle.addEventListener('click', scanBleDevices);

// Handle connect button
connectBtn.addEventListener('click', async () => {
    if (!selectedProtocol) {
        showToast('info', 'Select a protocol before connecting');
        return;
    }

    // For BLE, ensure a device is selected
    if (selectedProtocol === 'ble' && !selectedBleDevice) {
        showToast('info', 'Select a Bluetooth device before connecting');
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
        logError('Connection error:', error);
        showToast('error', `Connection failed: ${error.message}`);
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
            logError('Connection polling error:', error);
            showToast('error', 'Connection failed: Try again');
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
            btn.classList.remove('bg-cyan-600', 'dark:bg-cyan-700', 'hover:bg-cyan-600', 'dark:hover:bg-cyan-700');
            btn.classList.add('bg-cyan-700', 'dark:bg-cyan-800', 'cursor-default');
            btn.classList.add('text-white');
        } else {
            // Other protocols - disable and make less prominent
            btn.classList.remove('bg-cyan-600', 'dark:bg-cyan-700', 'text-white', 'hover:bg-cyan-600', 'dark:hover:bg-cyan-700', 'hover:text-white');
            btn.classList.add('cursor-not-allowed', 'text-gray-400', 'dark:text-gray-500');
        }
        btn.disabled = true;
    });
    
    showToast('success', `Connected via ${selectedProtocol.toUpperCase()}`);
    
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
            showToast('info', data.message);
        } else {
            showToast('error', `Failed to launch ${appName}: ${data.message}`);
        }
    })
    .catch(error => {
        showToast('error', `Error launching ${appName}: ${error.message}`);
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
            showToast('message', 'Disconnected!');
            
            // Reset all protocol buttons
            connectionBtns.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove(
                    'bg-cyan-600', 'dark:bg-cyan-700', 'bg-cyan-700', 'dark:bg-cyan-800', 
                    'text-white', 'cursor-not-allowed', 'cursor-default',
                    'text-gray-400', 'dark:text-gray-500'
                );
                btn.classList.add(
                    'hover:bg-cyan-600', 'dark:hover:bg-cyan-700', 'hover:text-white',
                    'text-gray-700', 'dark:text-gray-200',
                    'cursor-pointer'
                );
            });

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
        logError('Disconnection error:', error);
        // Return to disconnect state if disconnection failed
        disconnectingBtn.classList.add('hidden');
        disconnectBtn.classList.remove('hidden');
        showToast('error', `Disconnection failed: ${error.message}`);
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
        logError('EventSource failed');
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
        showToast('info', 'Connect your device first');
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
                    showToast('message', 'Recording stopped');
                }
            })
            .catch(error => {
                logError('Error stopping recording:', error);
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
                    showToast('success', 'Recording started');
                }
            })
            .catch(error => {
                logError('Error starting recording:', error);
                showToast('error', 'Failed to start recording: ' + error.message);
            });
    }
}

// Initial setup
connectBtn.disabled = true; // Disable connect button until protocol is selected
initializeFilename(); // Set default filename with timestamp

// Toast notifications, matching Chords-Web (Sonner with rich colours, see the styles in index.html).
// The newest toast is in front, older ones are tucked behind it and spread out while hovered.
// Success, info and message toasts close after 4 s (paused while hovered); only error and warning toasts (failures)
// stay until closed and show how long ago they appeared. A repeat of a toast that is showing replaces it.
const TOAST_LIFETIME = 4000;    // ms before a success/message toast closes
const TOAST_GAP = 14;           // px between toasts when the stack is spread out
const VISIBLE_TOASTS = 3;       // Toasts shown in the stack at once
const TOAST_ICONS = {           // Sonner's icons (a message toast has none)
    success: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" height="20" width="20"><path fill-rule="evenodd" clip-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"/></svg>',
    warning: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" height="20" width="20"><path fill-rule="evenodd" clip-rule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z"/></svg>',
    error: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" height="20" width="20"><path fill-rule="evenodd" clip-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z"/></svg>',
};
TOAST_ICONS.info = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" height="20" width="20"><path fill-rule="evenodd" clip-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z"/></svg>';
const TOAST_CLOSE_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

const toaster = document.getElementById('toaster');
let toasts = [];                // Toasts showing, newest first
let toastsExpanded = false;     // True while the mouse is over the stack

// type: 'success' | 'info' | 'error' | 'warning' | 'message'
function showToast(type, title) {
    const persistent = type === 'error' || type === 'warning';
    const id = `${type}:${title}`;
    let toast = toasts.find(t => t.id === id);
    if (toast) {
        // Repeat: bring the showing toast to the front and restart its time instead of adding a copy
        toasts = [toast, ...toasts.filter(t => t !== toast)];
        toast.since = Date.now();
        if (!persistent) startToastTimer(toast);
        updateToastTimes();
        layoutToasts();
        return;
    }

    const el = document.createElement('li');
    el.className = `toast toast-${type}`;
    el.setAttribute('role', persistent ? 'alert' : 'status');
    el.innerHTML = (TOAST_ICONS[type] ? `<div class="toast-icon">${TOAST_ICONS[type]}</div>` : '') +
        `<div class="toast-content"><div class="toast-title"></div>${persistent ? '<time class="toast-time"></time>' : ''}</div>` +
        (persistent ? `<button type="button" class="toast-close" aria-label="Close notification">${TOAST_CLOSE_ICON}</button>` : '');
    el.querySelector('.toast-title').textContent = title;

    toast = { id, el, persistent, since: Date.now(), timer: null, remaining: 0, startedAt: 0 };
    if (persistent) el.querySelector('.toast-close').addEventListener('click', () => removeToast(toast));
    toaster.appendChild(el);
    toast.height = el.offsetHeight;    // Natural height, measured before the toast is stacked
    toasts.unshift(toast);
    if (!persistent) startToastTimer(toast);
    updateToastTimes();
    requestAnimationFrame(() => {      // Start from below, then slide up into place
        el.dataset.mounted = '';
        layoutToasts();
    });
}

// Position every toast: collapsed (older toasts tucked behind the front one) or spread out while hovered
function layoutToasts() {
    const frontHeight = toasts.length ? toasts[0].height : 0;
    let offset = 0;    // Distance from the bottom when spread out: heights of the newer toasts plus gaps
    toasts.forEach((toast, i) => {
        const el = toast.el;
        if (!('mounted' in el.dataset)) return;    // Still waiting for its slide-in
        el.style.zIndex = toasts.length - i;
        el.style.opacity = i < VISIBLE_TOASTS ? '' : '0';
        el.style.pointerEvents = i < VISIBLE_TOASTS ? '' : 'none';
        if (toastsExpanded) {
            el.style.transform = `translateY(${-offset}px)`;
            el.style.height = `${toast.height}px`;
            el.dataset.expanded = '';
            delete el.dataset.behind;
        } else {
            el.style.transform = i === 0 ? 'translateY(0)' : `translateY(${-TOAST_GAP * i}px) scale(${1 - 0.05 * i})`;
            el.style.height = `${i === 0 ? toast.height : frontHeight}px`;
            delete el.dataset.expanded;
            if (i === 0) delete el.dataset.behind; else el.dataset.behind = '';
        }
        offset += toast.height + TOAST_GAP;
    });
}

function removeToast(toast) {
    if (!toasts.includes(toast)) return;
    clearTimeout(toast.timer);
    const wasFront = toasts[0] === toast;
    toasts = toasts.filter(t => t !== toast);
    const el = toast.el;
    el.style.pointerEvents = 'none';
    el.style.opacity = '0';
    el.style.transform = wasFront || toastsExpanded ? `${el.style.transform} translateY(100%)` : 'translateY(40%)';
    setTimeout(() => el.remove(), 400);
    layoutToasts();
}

function startToastTimer(toast) {
    clearTimeout(toast.timer);
    toast.timer = null;
    toast.remaining = TOAST_LIFETIME;
    if (!toastsExpanded) runToastTimer(toast);    // While hovered, the timer starts when the mouse leaves
}

function runToastTimer(toast) {
    toast.startedAt = Date.now();
    toast.timer = setTimeout(() => removeToast(toast), toast.remaining);
}

// "just now", "2 min ago", ... like Chords-Web; the exact time shows on hover
function formatTimeAgo(since) {
    const s = Math.max(0, Math.round((Date.now() - since) / 1000));
    if (s < 45) return 'just now';
    const m = Math.round(s / 60);
    if (m < 60) return `${m} min ago`;
    const h = Math.round(m / 60);
    if (h < 24) return `${h} h ago`;
    return new Date(since).toLocaleString();
}

function updateToastTimes() {
    toasts.forEach(toast => {
        const time = toast.el.querySelector('.toast-time');
        if (time) {
            time.textContent = formatTimeAgo(toast.since);
            time.dateTime = new Date(toast.since).toISOString();
            time.title = new Date(toast.since).toLocaleString();
        }
    });
}
setInterval(updateToastTimes, 15000);

// Spread the stack out and pause the close timers while hovered
toaster.addEventListener('mouseenter', () => {
    toastsExpanded = true;
    toasts.filter(t => t.timer).forEach(t => {
        clearTimeout(t.timer);
        t.timer = null;
        t.remaining -= Date.now() - t.startedAt;
    });
    layoutToasts();
});
toaster.addEventListener('mouseleave', () => {
    toastsExpanded = false;
    toasts.filter(t => !t.persistent && !t.timer).forEach(runToastTimer);
    layoutToasts();
});

// In-app popup, only for information or very important warnings that must not be missed (everything else is a toast)
function showPopup(title, messageHtml) {
    document.getElementById('popup-title').textContent = title;
    document.getElementById('popup-message').innerHTML = messageHtml;
    document.getElementById('popup-modal').classList.remove('hidden');
}
document.getElementById('popup-close').addEventListener('click', () => document.getElementById('popup-modal').classList.add('hidden'));
document.getElementById('popup-modal').addEventListener('click', e => {
    if (e.target.id === 'popup-modal') e.target.classList.add('hidden');    // Click outside to close
});
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.getElementById('popup-modal').classList.add('hidden');
});

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
                        showToast('warning', 'Recording stopped (connection lost)');
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
            logError('Error fetching stream status:', error);
        });
}

function handleDisconnection() {
    isConnected = false;
    disconnectBtn.classList.add('hidden');
    disconnectingBtn.classList.add('hidden');
    connectingBtn.classList.add('hidden');
    connectBtn.classList.remove('hidden');
    showToast('error', 'Stream disconnected!');
    
    // Reset protocol buttons
    connectionBtns.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('bg-cyan-700', 'dark:bg-cyan-800', 'cursor-default');
        btn.classList.add('hover:bg-cyan-600', 'dark:hover:bg-cyan-700', 'hover:text-white');
    });
    
    // Handle recording state
    if (isRecording) {
        isRecording = false;
        recordBtn.innerHTML = 'Start Recording';
        recordBtn.classList.remove('bg-gray-500');
        recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
        recordingStatus.classList.add('hidden');
        filenameInput.disabled = false;
        showToast('warning', 'Recording stopped (stream lost)');
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
    checkStreamStatus();
    setInterval(checkStreamStatus, 1000);
    startTimestampUpdater();
    
    // Error handling
    window.onerror = function(message, source, lineno, colno, error) {
        logError(error || message);
        return true; };

document.getElementById('github-btn').addEventListener('click', () => {
    window.open('https://github.com/upsidedownlabs/Chords-Python', '_blank');
});

document.getElementById('info-btn').addEventListener('click', async () => {
    let version = 'unknown';
    try {
        version = (await (await fetch('/version')).json()).version;    // Installed chordspy version
    } catch (error) {
        logError('Version fetch error:', error);
    }
    showPopup('Chords Python', `Bio-potential Data Acquisition System<br>Version ${version}`);
});
});