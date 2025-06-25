from flask import Flask, render_template, request, jsonify
from chordspy.connection import Connection
import threading
import asyncio
import logging
from bleak import BleakScanner
from flask import Response
import queue
import yaml
from pathlib import Path
import os
import webbrowser
import logging

console_queue = queue.Queue()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Only show errors

# Global variables
connection_manager = None
connection_thread = None
ble_devices = []
stream_active = False
running_apps = {}  # Dictionary to track running apps

@app.route('/log_error', methods=['POST'])
def log_error():
    try:
        error_data = request.get_json()
        if not error_data or 'error' not in error_data or 'log_error' in str(error_data):
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
        
        os.makedirs('logs', exist_ok=True)
        
        with open('logs/logging.txt', 'a') as f:
            f.write(error_data['error'])
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Logging failed'}), 500

def run_async(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_apps_config')
def get_apps_config():
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

@app.route('/scan_ble')
@run_async
async def scan_ble_devices():
    global ble_devices
    try:
        devices = await BleakScanner.discover(timeout=5)
        ble_devices = [{'name': d.name or 'Unknown', 'address': d.address} 
                      for d in devices if d.name and d.name.startswith(('NPG', 'npg'))]
        return jsonify({'status': 'success', 'devices': ble_devices})
    except Exception as e:
        logging.error(f"BLE scan error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/check_stream')
def check_stream():
    is_connected = connection_manager.stream_active if hasattr(connection_manager, 'stream_active') else False
    return jsonify({'connected': is_connected})

@app.route('/check_connection')
def check_connection():
    if connection_manager and connection_manager.stream_active:
        return jsonify({'status': 'connected'})
    return jsonify({'status': 'connecting'})

def post_console_message(message):
    global stream_active
    if "LSL stream started" in message:
        stream_active = True
    elif "disconnected" in message:
        stream_active = False
    console_queue.put(message)

@app.route('/console_updates')
def console_updates():
    def event_stream():
        while True:
            message = console_queue.get()
            yield f"data: {message}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/launch_app', methods=['POST'])
def launch_application():
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
        
        running_apps[module_name] = process
        
        return jsonify({'status': 'success', 'message': f'Launched {module_name}'})
    except Exception as e:
        logging.error(f"Error launching {module_name}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/check_app_status/<app_name>')
def check_app_status(app_name):
    if app_name in running_apps:
        if running_apps[app_name].poll() is None:  # Still running
            return jsonify({'status': 'running'})
        else:  # Process has terminated
            del running_apps[app_name]
            return jsonify({'status': 'not_running'})
    return jsonify({'status': 'not_running'})

@app.route('/connect', methods=['POST'])
def connect_device():
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

@app.route('/disconnect', methods=['POST'])
def disconnect_device():
    global connection_manager, stream_active
    if connection_manager:
        connection_manager.cleanup()
        stream_active = False
        post_console_message("disconnected")
        return jsonify({'status': 'disconnected'})
    return jsonify({'status': 'no active connection'})

@app.route('/start_recording', methods=['POST'])
def start_recording():
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

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
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

def main():
    def open_browser():
        webbrowser.open("http://localhost:5000")

    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()