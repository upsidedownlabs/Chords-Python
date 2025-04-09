from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import subprocess
import psutil
import signal
import sys
import atexit
import time
import os
import json
from threading import Thread
from flask import Response

app = Flask(__name__)
app.secret_key = '--'

lsl_process = None            # Process for LSL
lsl_running = False           # Flag to check if LSL is running
npg_running = False           # Flag to check if NPG is running
npg_process = None            # Process for NPG
app_processes = {}            # Dictionary to hold other app processes
current_message = None        # Message to display in the UI
discovered_devices = []       # List for all discovered devices
npg_connection_thread = None  # Thread for NPG connection

def is_process_running(name):
    """Function to check if a process is running by name."""
    for proc in psutil.process_iter(['pid', 'name']): # Iterate through all processes 
        if name in proc.info['name']:                 # Check if the process name matches
            return True                               # Returns True if process found
    return False                                      # Returns False if process not found

@app.route("/")
def home():
    """Render the home page with the current status of LSL Stream , NPG stream, running applications, messages."""
    return render_template("index.html", lsl_started=lsl_running, npg_started=npg_running, running_apps=[k for k,v in app_processes.items() if v.poll() is None], message=current_message, devices=session.get('devices', []), selected_device=session.get('selected_device'))

@app.route("/scan_devices", methods=["POST"])
def scan_devices():
    """Scan for available devices using the npg-ble.py --scan script."""
    global discovered_devices
    
    try:
        # Run the scanning in a separate process
        scan_process = subprocess.Popen([sys.executable, "npg-ble.py", "--scan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for scan to complete (with timeout)
        try:
            stdout, stderr = scan_process.communicate(timeout=10)
            if scan_process.returncode != 0:
                raise Exception(f"Scan failed: {stderr}")
            
            # Parse the output to get devices
            devices = []
            for line in stdout.split('\n'):
                if line.startswith("DEVICE:"):
                    parts = line[len("DEVICE:"):].strip().split('|')
                    if len(parts) >= 2:
                        devices.append({
                            "name": parts[0],
                            "address": parts[1]
                        })
            
            session['devices'] = devices       # Store devices in session
            discovered_devices = devices       # Update devices list to global variable
            return jsonify({"status": "success", "devices": devices})
            
        except subprocess.TimeoutExpired:
            scan_process.kill()
            return jsonify({"status": "error", "message": "Device scan timed out"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/connect_device", methods=["POST"])
def connect_device():
    """Handle POST request to connect to a Bluetooth device"""
    global npg_process, npg_running, npg_connection_thread, current_message
    
    device_address = request.form.get("device_address")    # Get device address from the POST form data
    if not device_address:                                 # Check if device address was provided
        return jsonify({"status": "error", "message": "No device selected"})
    
    session['selected_device'] = device_address            # Store selected device in session
    
    if npg_connection_thread and npg_connection_thread.is_alive(): # Check if there's an existing connection thread running
        if npg_process and npg_process.poll() is None:             # If any active NPG process, terminate it
            npg_process.terminate()
            try:
                npg_process.wait(timeout=2)                        # Wait for process to terminate (with timeout)
            except subprocess.TimeoutExpired:
                npg_process.kill()                                 # Force kill if process doesn't terminate smoothly within timeout
    
    def connect_and_monitor():
        """Connect to the device and monitor the output."""
        global npg_process, npg_running, current_message
        
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "npg-ble.py")    # Get the path of the npg.ble script to run
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            npg_process = subprocess.Popen([sys.executable, script_path, "--connect", device_address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, creationflags=creation_flags)    # Start the process with no window
            time.sleep(1)
            
            # Monitor the output for connection status
            connected = False
            for line in iter(npg_process.stdout.readline, ''):  # Read lines from the process output
                if "Connected to" in line:                      # Check for the required message showing successful connection
                    connected = True                            # Set connected flag to True         
                if npg_process.poll() is not None:              # If process has terminated, break the loop
                    break
            
            if connected:            # If connected successfully, update the global variables
                current_message = f"Connected to {device_address}"
                npg_running = True   # Set npg_running to True
                monitor_thread = Thread(target=monitor_process_output, args=(npg_process, "npg"), daemon=True)     # Create a new thread to monitor the process output
                monitor_thread.start()       # Start the monitoring thread that will handle the output of the process
            else:
                current_message = f"Failed to connect to {device_address}"      # If not connected, update the message
                npg_running = False      # Set npg_running to False
                if npg_process.poll() is None:   # If process is still running, terminate it
                    npg_process.terminate()
        
        except Exception as e:
            current_message = f"Connection error: {str(e)}"
            npg_running = False
            if npg_process and npg_process.poll() is None:
                npg_process.terminate()
    
    # Start the connection in a new thread
    npg_connection_thread = Thread(target=connect_and_monitor, daemon=True)
    npg_connection_thread.start()
    
    return jsonify({"status": "pending"})

@app.route("/check_connection", methods=["GET"])
def check_connection():
    """Check the connection status of the NPG process"""
    global npg_running, current_message, npg_process

    if npg_process is None or npg_process.poll() is not None:
        npg_running = False
        if npg_process:
            output = npg_process.stdout.read()
            current_message = f"Connection terminated: {output}"
        else:
            current_message = "No active connection"
        return jsonify({"connected": False, "message": current_message})
    
    while True:
        line = npg_process.stdout.readline()
        if not line:
            break
        
        if "Connected to" in line:
            npg_running = True
            current_message = line.strip()
            return jsonify({"connected": True, "message": current_message})
        elif "Data Interrupted" in line or "Data Interrupted (Bluetooth disconnected)" in line:
            npg_running = False
            stop_dependent_apps("npg")
            current_message = line.strip()
            return jsonify({"connected": False, "message": current_message})
    
    return jsonify({"connected": npg_running, "message": current_message or "Connecting..."})

def monitor_process_output(process, process_type):
    """Monitor the output of a subprocess(LSL/NPG) and handle termination events."""
    global lsl_running, npg_running, current_message, app_processes
    
    while True:      # Infinite loop to keep checking the process output
        if process.poll() is not None:  # Process has terminated
            if process_type == "lsl":
                lsl_running = False
                current_message = "LSL stream terminated"
            elif process_type == "npg":
                npg_running = False
                current_message = "NPG stream terminated"
            break
            
        line = process.stdout.readline()   # Read a line from the process output
        if not line:
            time.sleep(0.1)
            continue
            
        print(f"{process_type} output:", line.strip())  # Debug logging
            
        if process_type == "npg" and ("Data Interrupted" in line or "Data Interrupted (Bluetooth disconnected)" in line.lower()): # Handle NPG data interruption
            current_message = "NPG connection lost - stopping all applications"
            npg_running = False           # Set npg_running to False
            stop_dependent_apps("npg")    # Stop all dependent applications
            
            if process.poll() is None:    # If process is still running, terminate it
                process.terminate()
                try:
                    process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    process.kill()
            break
            
        elif process_type == "lsl" and ("Error while closing serial connection" in line or "disconnected" in line.lower()):     # Handle LSL stream interruption
            current_message = "LSL stream error - connection closed"
            lsl_running = False
            stop_dependent_apps("lsl")
            if process.poll() is None:
                process.terminate()
            break

def stop_dependent_apps(stream_type):
    """Stop all dependent applications based on the stream type(LSL/NPG)"""
    global app_processes, current_message, lsl_running, npg_running
    
    apps_to_stop = []       # Track which apps we're stopping for status message
    for app_name, process in list(app_processes.items()):
        if process.poll() is None:          # If process is running
            apps_to_stop.append(app_name)   # Add to stopped apps list
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            del app_processes[app_name]
    
    if stream_type == "lsl":
        lsl_running = False
    elif stream_type == "npg":
        npg_running = False
    elif stream_type == "all":
        lsl_running = False
        npg_running = False
    
    if apps_to_stop:
        current_message = f"Stopped {', '.join(apps_to_stop)} due to {stream_type.upper()} stream termination"
    elif stream_type in ["lsl", "npg"]:
        current_message = f"{stream_type.upper()} stream terminated - dependent apps stopped"

@app.route("/start_lsl", methods=["POST"])
def start_lsl():
    """Start the LSL stream and handle CSV saving option."""
    global lsl_process, lsl_running, current_message
    save_csv = request.form.get('csv', 'false').lower() == 'true'

    if npg_running:             # Check for conflicting NPG stream
        current_message = "Please stop NPG stream first"
        return redirect(url_for('home'))

    if lsl_running:              # Prevent duplicate LSL streams
        current_message = "LSL stream already running"
        return redirect(url_for('home'))

    try:
        command = ["python", "chords.py", "--lsl"]  # Command to start chords.py with LSL streaming
        if save_csv:                                # Check if CSV saving is requested
            command.append("--csv")

        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        lsl_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=creation_flags, text=True, bufsize=1)

        output = lsl_process.stdout.readline().strip()
        if "No" in output:      # Check for failure messages in output
            current_message = "Failed to start LSL stream"
            lsl_running = False
        else:
            current_message = "LSL stream started successfully"
            lsl_running = True

        if not lsl_running:
            current_message = "Failed to start LSL stream - no data detected"
            if lsl_process.poll() is None:
                lsl_process.terminate()
            return redirect(url_for('home'))

        monitor_thread = Thread(target=monitor_process_output, args=(lsl_process, "lsl"), daemon=True)      # Create a new thread to monitor the LSL process output
        monitor_thread.start()

    except Exception as e:
        current_message = f"Error starting LSL: {str(e)}"
        lsl_running = False

    return redirect(url_for('home'))

@app.route("/start_npg", methods=["POST"])
def start_npg():
    """ Start the NPG stream and handle connection to the selected device."""
    global npg_process, npg_running, current_message

    if lsl_running:        # Check for conflicting LSL stream
        current_message = "Please stop LSL stream first"
        return jsonify({"status": "error", "message": current_message})

    device_address = session.get('selected_device')
    if not device_address: # Check if a device is selected
        current_message = "No device selected"
        return jsonify({"status": "error", "message": current_message})

    if npg_running:        # Prevent duplicate NPG streams
        current_message = "NPG already running"
        return jsonify({"status": "error", "message": current_message})

    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "npg-ble.py")
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        
        npg_process = subprocess.Popen([sys.executable, script_path, "--connect", device_address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=creation_flags, text=True, bufsize=1)

        monitor_thread = Thread(target=monitor_process_output, args=(npg_process, "npg"), daemon=True)
        monitor_thread.start()
        return jsonify({"status": "pending", "message": "Attempting to connect to NPG device..."})
        
    except Exception as e:
        current_message = f"Error starting NPG: {str(e)}"
        npg_running = False
        return jsonify({"status": "error", "message": current_message})
    
@app.route("/run_app", methods=["POST"])
def run_app():
    """Start a specified application process."""
    global current_message
    app_name = request.form.get("app_name")
    valid_apps = ["heartbeat_ecg", "emgenvelope", "eog", "ffteeg", "game", "beetle", "gui", "keystroke", "csvplotter"]

    if not (lsl_running or npg_running):  # Verify either one of the streams is running
        current_message = "Start LSL or NPG first!"
        return redirect(url_for('home'))

    if app_name not in valid_apps:
        current_message = "Invalid application"
        return redirect(url_for('home'))

    if app_name in app_processes and app_processes[app_name].poll() is None:   # Check if application is already running
        current_message = f"{app_name} is already running"
        return redirect(url_for('home'))

    try:
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        process = subprocess.Popen(["python", f"{app_name}.py"], creationflags=creation_flags)   # Start the application process
        
        app_processes[app_name] = process   # Track running process in global dictionary
        current_message = f"{app_name} started successfully"
    except Exception as e:
        current_message = f"Error starting {app_name}: {str(e)}"

    return redirect(url_for('home'))

@app.route("/stream_events")
def stream_events():
    """Stream events to the client using Server-Sent Events (SSE)."""
    def event_stream():
        """Generator function that yields system state updates when changes occur."""
        last_state = None    # Initialize last_state to None
        
        while True:
            current_state = {"lsl_running": lsl_running, "npg_running": npg_running, "running_apps": [k for k,v in app_processes.items() if v.poll() is None], "message": current_message, "stream_interrupted": (("Data Interrupted (Bluetooth Disconnected)" or "Error while closing serial connection" in current_message) if current_message else False)}
            if current_state != last_state:
                yield f"data: {json.dumps(current_state)}\n\n"
                last_state = current_state.copy()
            
            time.sleep(0.5)
    
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/stop_all", methods=['POST'])
def stop_all():
    """ Stop all running processes and clear the current message."""
    global current_message
    stop_all_processes()
    current_message = "All processes stopped"
    return redirect(url_for('home'))

def cleanup_processes():
    """ Remove finished processes from the app_processes dictionary."""
    global app_processes
    app_processes = {
        k: v for k, v in app_processes.items()
        if v.poll() is None  # Only keep running processes
    }

@app.route("/check_app_status", methods=["GET"])
def check_app_status():
    """ Check the status of running applications and return a JSON response."""
    cleanup_processes()  # Remove finished processes
    return jsonify({"running_apps": list(app_processes.keys())})

def stop_all_processes():
    """Stop all running processes and clear the current message."""
    global lsl_process, npg_process, app_processes, lsl_running, npg_running, current_message

    # Terminate LSL process
    if lsl_process and lsl_process.poll() is None:
        lsl_process.terminate()
        try:
            lsl_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            lsl_process.kill()
        lsl_running = False
        stop_dependent_apps("lsl")

    if npg_process and npg_process.poll() is None:
        npg_process.terminate()
        try:
            npg_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            npg_process.kill()
        npg_running = False
        stop_dependent_apps("npg")

    stop_dependent_apps("all")
    current_message = "All processes stopped"
    print("All processes terminated.")

def handle_sigint(signal_num, frame):
    """Handle Ctrl+C signal to stop all processes gracefully."""
    print("\nCtrl+C pressed! Stopping all processes...")
    stop_all_processes()
    sys.exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, handle_sigint)
atexit.register(stop_all_processes)

if __name__ == "__main__":
    app.run(debug=True)