"""
Flask-based web interface for managing connections to devices and applications.
This module provides a web-based GUI for:
- Scanning and connecting to devices via USB, WiFi, or BLE
- Managing data streaming and recording
- Launching and monitoring Chords-Python applications
- Displaying real-time console updates
- Handling error logging
The application uses Server-Sent Events (SSE) for real-time updates to the frontend.
"""

# Importing Necessary Libraries
from flask import Flask, render_template, request, jsonify  # Flask web framework
from chordspy.connection import Connection                  # Connection management module
import threading                                            # For running connection management in a separate thread
import asyncio                                              # For asynchronous operations, especially with BLE           
import logging                                              # For logging errors and information        
from bleak import BleakScanner                              # BLE device scanner from Bleak library
from flask import Response                                  # For handling server-sent events (SSE)
import queue                                                # Queue for managing console messages
import yaml                                                 # For loading application configuration from YAML files     
from pathlib import Path                                    # For handling file paths in a platform-independent way
import os                                                   # For file and directory operations
import webbrowser                                           # For opening the web interface in a browser

console_queue = queue.Queue()            # Global queue for console messages to be displayed in the web interface
app = Flask(__name__)                    # Initialize Flask application
logging.basicConfig(level=logging.INFO)  # Configure logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)              # Only show errors from Werkzeug (Flask's WSGI)

# Global variables
connection_manager = None  # Manages the device connection
connection_thread = None   # Thread for connection management
ble_devices = []           # List of discovered BLE devices
stream_active = False      # Flag indicating if data stream is active
running_apps = {}          # Dictionary to track running applications

# Error logging endpoint. This allows the frontend to send error messages to be logged.
@app.route('/log_error', methods=['POST'])
def log_error():
    """
    Endpoint for logging errors from the frontend. It receives error data via POST request and writes it to a log file.
    Returns:
        JSON response with status and optional error message.
    """
    try:
        error_data = request.get_json()
        if not error_data or 'error' not in error_data or 'log_error' in str(error_data):
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
        
        os.makedirs('logs', exist_ok=True)        # Ensure logs directory exists
        
        with open('logs/logging.txt', 'a') as f:  # Append error to log file
            f.write(error_data['error'])
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Logging failed'}), 500

# Decorator to run async functions in a synchronous context. It allows us to call async functions from Flask routes.
def run_async(coro):
    """
    Decorator to run async functions in a synchronous context.
    Args:
        coro: The coroutine to be executed.
    Returns:
        A wrapper function that runs the coroutine in a new event loop.
    """
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# Main route for the web interface. It renders the index.html template.
@app.route('/')
def index():
    """Render the main index page of the web interface."""
    return render_template('index.html')

# Route to retrieve the configuration for available Chord-Python applications.
@app.route('/get_apps_config')
def get_apps_config():
    """
    Retrieve the configuration for available applications.It looks for apps.yaml in either the package config directory or a local config directory.
    Returns:
        JSON response containing the application configuration or an empty list if not found.
    """
    try:
        config_path = Path(__file__).parent / 'config' / 'apps.yaml' # Try package-relative path first
        if not config_path.exists():
            config_path = Path('chordspy.config') / 'apps.yaml'      # Fallback to local path
            
        if config_path.exists():
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return jsonify(config)
        return jsonify({'apps': []})
    
    except Exception as e:
        logging.error(f"Error loading apps config: {str(e)}")
        return jsonify({'apps': [], 'error': str(e)})

# Route to scan for nearby BLE devices. It uses BleakScanner to discover devices.
@app.route('/scan_ble')
@run_async
async def scan_ble_devices():
    """
    Scan for nearby BLE devices. It uses BleakScanner to discover devices for 5 seconds and filters for devices with names starting with 'NPG' or 'npg'.
    Returns:
        JSON response with list of discovered devices or error message.
    """
    global ble_devices
    try:
        devices = await BleakScanner.discover(timeout=5)
        ble_devices = [{'name': d.name or 'Unknown', 'address': d.address} 
                      for d in devices if d.name and d.name.startswith(('NPG', 'npg'))]
        return jsonify({'status': 'success', 'devices': ble_devices})
    except Exception as e:
        logging.error(f"BLE scan error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route to check if the data stream is currently active. It checks the connection manager's stream_active flag.
@app.route('/check_stream')
def check_stream():
    """
    Check if data stream is currently active.
    Returns:
        JSON response with connection status.
    """
    is_connected = connection_manager.stream_active if hasattr(connection_manager, 'stream_active') else False
    return jsonify({'connected': is_connected})

# Route to check the current connection status with the device. It returns 'connected' if the stream is active, otherwise 'connecting'.
@app.route('/check_connection')
def check_connection():
    """
    Check the current connection status with the device.
    Returns:
        JSON response with connection status ('connected' or 'connecting').
    """
    if connection_manager and connection_manager.stream_active:
        return jsonify({'status': 'connected'})
    return jsonify({'status': 'connecting'})

# Function to post messages to the console queue. It updates the stream_active flag based on the message content. This function is used to send messages to the web interface for display in real-time.
def post_console_message(message):
    """
    Post a message to the console queue for display in the web interface and updates the stream_active flag based on message content.
    Args:
        message: The message to be displayed in the console.
    """
    global stream_active
    if "LSL stream started" in message:
        stream_active = True
    elif "disconnected" in message:
        stream_active = False
    console_queue.put(message)

# Route for Server-Sent Events (SSE) to provide real-time console updates to the web interface.
@app.route('/console_updates')
def console_updates():
    """
    Server-Sent Events (SSE) endpoint for real-time console updates.
    Returns:
        SSE formatted messages from the console queue.
    """
    def event_stream():
        """Generator function that yields messages from the console queue as SSE formatted messages."""
        while True:
            message = console_queue.get()
            yield f"data: {message}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

# Route to launch Chord-Python application as a subprocess. It receives the application name via POST request and starts it as a Python module.
@app.route('/launch_app', methods=['POST'])
def launch_application():
    """
    Launch a Chord-Python application as a subprocess.It receives the application name via POST request and starts it as a Python module.
    Returns:
        JSON response indicating success or failure of application launch.
    """
    if not connection_manager or not connection_manager.stream_active:
        return jsonify({'status': 'error', 'message': 'No active stream'}), 400
    
    data = request.get_json()
    module_name = data.get('app')
    
    if not module_name:
        return jsonify({'status': 'error', 'message': 'No application specified'}), 400
    
    # Check if app is already running
    if module_name in running_apps and running_apps[module_name].poll() is None:
        return jsonify({'status': 'error', 'message': f'{module_name} is already running','code': 'ALREADY_RUNNING'}), 400
    
    try:
        import subprocess
        import sys
        
        # Run the module using Python's -m flag
        process = subprocess.Popen([sys.executable, "-m", f"chordspy.{module_name}"])
        running_apps[module_name] = process    # Track running application
        
        return jsonify({'status': 'success', 'message': f'Launched {module_name}'})
    except Exception as e:
        logging.error(f"Error launching {module_name}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route to check the status of a running application. It checks if the application is in the running_apps dictionary and whether its process is still active.
@app.route('/check_app_status/<app_name>')
def check_app_status(app_name):
    """
    Check the status of a running application.
    Args:
        app_name: Name of the application to check.
    Returns:
        JSON response indicating if the application is running or not.
    """
    if app_name in running_apps:
        if running_apps[app_name].poll() is None:  # Still running
            return jsonify({'status': 'running'})
        else:  # Process has terminated
            del running_apps[app_name]
            return jsonify({'status': 'not_running'})
    return jsonify({'status': 'not_running'})

# Route to connect to a device using the specified protocol. It supports USB, WiFi, and BLE connections. Starts connection in a separate thread.
@app.route('/connect', methods=['POST'])
def connect_device():
    """
    Establish connection to a device using the specified protocol.It supports USB, WiFi, and BLE connections. Starts connection in a separate thread.
    Returns:
        JSON response indicating connection status.
    """
    global connection_manager, connection_thread, stream_active
    
    data = request.get_json()
    protocol = data.get('protocol')
    device_address = data.get('device_address')
    
    # Reset stream status
    stream_active = False
    
    # Clean up any existing connection
    if connection_manager:
        connection_manager.cleanup()
        if connection_thread and connection_thread.is_alive():
            connection_thread.join()
    
    # Create new connection
    connection_manager = Connection()
    
    def run_connection():
        """
        Internal function to handle the connection process in a thread.
        """
        try:
            if protocol == 'usb':
                success = connection_manager.connect_usb()
            elif protocol == 'wifi':
                success = connection_manager.connect_wifi()
            elif protocol == 'ble':
                if not device_address:
                    logging.error("No BLE device address provided")
                    return
                
                # For BLE, we need to run in an event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = connection_manager.connect_ble(device_address)
            
            if success:
                post_console_message("LSL stream started")
            else:
                post_console_message("Connection failed")
        except Exception as e:
            logging.error(f"Connection error: {str(e)}")
            post_console_message(f"Connection error: {str(e)}")
    
    # Start connection in a separate thread
    connection_thread = threading.Thread(target=run_connection, daemon=True)
    connection_thread.start()
    
    return jsonify({'status': 'connecting', 'protocol': protocol})

# Route to disconnect from the currently connected device. It cleans up the connection manager and resets the stream status.
@app.route('/disconnect', methods=['POST'])
def disconnect_device():
    """
    Disconnect from the currently connected device.
    Returns:
        JSON response indicating disconnection status.
    """
    global connection_manager, stream_active
    if connection_manager:
        connection_manager.cleanup()
        stream_active = False
        post_console_message("disconnected")
        return jsonify({'status': 'disconnected'})
    return jsonify({'status': 'no active connection'})

# Route to start recording data from the connected device to a CSV file.
@app.route('/start_recording', methods=['POST'])
def start_recording():
    """
    Start recording data from the connected device to a CSV file.
    Returns:
        JSON response indicating recording status.
    """
    global connection_manager
    if not connection_manager:
        return jsonify({'status': 'error', 'message': 'No active connection'}), 400
    
    data = request.get_json()
    filename = data.get('filename')
    
    # If filename is empty or None, let connection_manager use default
    if filename == "":
        filename = None
    
    try:
        if connection_manager.start_csv_recording(filename):
            post_console_message(f"Recording started: {filename or 'default filename'}")
            return jsonify({'status': 'recording_started'})
        return jsonify({'status': 'error', 'message': 'Failed to start recording'}), 500
    except Exception as e:
        logging.error(f"Recording error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route to stop the current recording session. It calls the stop_csv_recording method of the connection manager.
@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    """
    Stop the current recording session.
    Returns:
        JSON response indicating recording stop status.
    """
    global connection_manager
    if connection_manager:
        try:
            if connection_manager.stop_csv_recording():
                post_console_message("Recording stopped")
                return jsonify({'status': 'recording_stopped'})
            return jsonify({'status': 'error', 'message': 'Failed to stop recording'}), 500
        except Exception as e:
            logging.error(f"Stop recording error: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'No active connection'}), 400

# Route to check if a specific application is running. It checks the running_apps dictionary for the application's process.
def main():
    """
    Main entry point for the application. It starts the Flask server and opens the web browser to the application.
    """
    def open_browser():
        """Open the default web browser to the application URL."""
        webbrowser.open("http://localhost:5000")

    threading.Timer(1, open_browser).start()  # Open browser after 1 seconds to allow server to start
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)   # Start Flask application

if __name__ == "__main__":
    main()