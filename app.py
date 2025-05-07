from flask import Flask, render_template, request, jsonify
from connection import Connection
import threading
import asyncio
import logging
from bleak import BleakScanner
from flask import Response
import queue
import threading
import time
from datetime import datetime

console_queue = queue.Queue()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global variables
connection_manager = None
connection_thread = None
ble_devices = []
stream_active = False

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
    if connection_manager and connection_manager.stream_active:
        return jsonify({'connected': True})
    return jsonify({'connected': False})

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
    app_name = data.get('app')
    
    if not app_name:
        return jsonify({'status': 'error', 'message': 'No application specified'}), 400
    
    try:
        # Here we'll use subprocess to launch the application script
        import subprocess
        import sys
        
        python_exec = sys.executable       # Determine the correct Python executable
        subprocess.Popen([python_exec, f"{app_name}.py"])   # Launch the application script in a separate process
        
        return jsonify({'status': 'success', 'message': f'Launched {app_name}'})
    except Exception as e:
        logging.error(f"Error launching {app_name}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

if __name__ == "__main__":
    app.run(debug=True)