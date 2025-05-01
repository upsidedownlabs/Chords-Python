from flask import Flask, render_template, request, jsonify
import asyncio
from connection import Connection
from threading import Thread
import webbrowser
from pylsl import resolve_streams
import time
from chords_ble import Chords_BLE

app = Flask(__name__)
connection_manager = None
ble_devices = []
active_connection = None
lsl_stream_active = False
csv_logging_enabled = False  # Global CSV logging state

@app.route('/set_csv', methods=['POST'])
def set_csv():
    global csv_logging_enabled
    data = request.get_json()
    csv_logging_enabled = data.get('enabled', False)
    return jsonify({'status': 'success', 'csv_logging': csv_logging_enabled})

@app.route('/')
def index():
    colors_list = ['#a855f7', '#93c5fd', '#a7f3d0', '#10b981', '#b91c1c', '#1d4ed8']
    return render_template('index.html', colors=colors_list)

def check_lsl_stream():
    global lsl_stream_active
    while True:
        streams = resolve_streams()
        if any(s.name() == "BioAmpDataStream" for s in streams):
            lsl_stream_active = True
            break
        time.sleep(0.5)

@app.route('/connect', methods=['POST'])
def connect():
    global active_connection, lsl_stream_active
    protocol = request.form.get('protocol')
    
    if active_connection:
        return jsonify({'status': 'error', 'message': 'A connection is already active'})
    
    lsl_stream_active = False
    Thread(target=check_lsl_stream).start()
    
    if protocol == 'usb':
        thread = Thread(target=connect_usb)
        thread.start()
        return jsonify({'status': 'connecting', 'message': 'Connecting via USB...'})
    
    elif protocol == 'wifi':
        thread = Thread(target=connect_wifi)
        thread.start()
        return jsonify({'status': 'connecting', 'message': 'Connecting via WiFi...'})
    
    elif protocol == 'ble':
        return jsonify({'status': 'scanning', 'message': 'Scanning for BLE devices...'})
    
    return jsonify({'status': 'error', 'message': 'Invalid protocol'})

@app.route('/check_connection', methods=['GET'])
def check_connection():
    global lsl_stream_active
    if lsl_stream_active:
        return jsonify({'status': 'success', 'message': 'Connection established! LSL stream started.'})
    return jsonify({'status': 'connecting', 'message': 'Connecting...'})

@app.route('/scan_ble', methods=['GET'])
def scan_ble():
    global ble_devices
    try:
        ble_scanner = Chords_BLE()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        devices = loop.run_until_complete(ble_scanner.scan_devices())
        loop.close()
        
        if not devices:
            return jsonify({'status': 'error', 'message': 'No BLE devices found'})
        
        ble_devices = devices
        devices_list = [{'name': device.name, 'address': device.address} for device in devices]
        return jsonify({'status': 'success', 'devices': devices_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/connect_ble', methods=['POST'])
def connect_ble_device():
    device_address = request.form.get('address')
    if not device_address:
        return jsonify({'status': 'error', 'message': 'No device address provided'})
    
    thread = Thread(target=connect_ble, args=(device_address,))
    thread.start()
    return jsonify({'status': 'connecting', 'message': f'Connecting to BLE device {device_address}...'})

def connect_usb():
    global active_connection, lsl_stream_active, csv_logging_enabled
    active_connection = Connection(csv_logging=csv_logging_enabled)
    active_connection.connect_usb()

def connect_wifi():
    global active_connection, lsl_stream_active, csv_logging_enabled
    active_connection = Connection(csv_logging=csv_logging_enabled)
    active_connection.connect_wifi()

def connect_ble(address):
    global active_connection, lsl_stream_active, csv_logging_enabled
    active_connection = Connection(csv_logging=csv_logging_enabled)
    active_connection.connect_ble(address)  # No duplicate device selection

if __name__ == "__main__":
    app.run(debug=True)