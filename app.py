from flask import Flask, render_template, jsonify, request
import subprocess
import psutil
import os
import signal
import sys
import atexit
import threading

app = Flask(__name__)
lsl_process = None
lsl_running = False
npg_running = False
npg_process = None
app_processes = {}

def is_process_running(name):
    for proc in psutil.process_iter(['pid', 'name']):
        if name in proc.info['name']:
            return True
    return False

@app.route("/")
def home():
    return render_template("index.html", lsl_started=False, lsl_status="Stopped", lsl_color="red")

@app.route("/start_lsl", methods=["POST"])
def start_lsl():
    global lsl_process, lsl_running

    if lsl_running:
        return jsonify({"status": "LSL stream already running", "lsl_started": True})

    try:
        if sys.platform == "win32":
            lsl_process = subprocess.Popen(["python", "chords.py", "--lsl"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW, text=True, bufsize=1)
        else:
            lsl_process = subprocess.Popen(["python", "chords.py", "--lsl"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        output = lsl_process.stderr.readline().strip()
        print(output)

        if "No" in output:
            lsl_running = False
            return render_template("index.html", lsl_started= False, lsl_status= "Failed to Start", lsl_color= "red", apps_enabled=False)
        else:
            lsl_running = True
            return render_template("index.html", lsl_started= True, lsl_status= "Running", lsl_color= "green", apps_enabled=True)

    except Exception as e:
        return render_template("index.html", lsl_started= False, lsl_status= f"Error: {e}", lsl_color= "red")

def read_npg_output():
    global npg_process

    if npg_process:
        for line in iter(npg_process.stdout.readline, ''):
            print(line.strip())  # Print npg.py output to the terminal

@app.route("/start_npg", methods=["POST"])
def start_npg():
    global npg_process, npg_running

    if npg_running:
        return jsonify({"status": "NPG already running", "npg_started": True})

    try:
        if sys.platform == "win32":
            npg_process = subprocess.Popen(["python", "npg.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW, text=True, bufsize=1)
        else:
            npg_process = subprocess.Popen(["python3", "npg.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        # Start a separate thread to read npg.py output
        threading.Thread(target=read_npg_output, daemon=True).start()

        if "NPG WebSocket connected!" in npg_process.stdout.readline().strip():
            npg_running = True
            return render_template("index.html", npg_started=True, npg_status="Running", npg_color="green", apps_enabled=True)

    except Exception as e:
        npg_running = False
        return render_template("index.html", npg_started=False, npg_status=f"Error: {e}", npg_color="red", apps_enabled=False)

@app.route("/run_app", methods=["POST"])
def run_app():
    global lsl_running, npg_running
    app_name = request.form.get("app_name")

    if not (lsl_running or npg_running):
        return render_template("index.html", message="Start LSL or NPG first!", running_apps=app_processes.keys())

    if app_name in app_processes and app_processes[app_name].poll() is None:
        return render_template("index.html", message=f"{app_name} is already running", running_apps=app_processes.keys())

    try:
        # Start the app subprocess
        if sys.platform == "win32":
            process = subprocess.Popen(["python", f"{app_name}.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            process = subprocess.Popen(["python", f"{app_name}.py"])

        app_processes[app_name] = process
        return render_template("index.html", running_apps=app_processes.keys(), message=None)
    except Exception as e:
        return render_template("index.html", message=f"Error starting {app_name}: {e}", running_apps=app_processes.keys())

@app.route("/app_status", methods=["GET"])
def app_status():
    # Check the status of all apps
    try:
        statuses = {
            "lsl_started": lsl_running,
            "npg_started": npg_running
        }
        statuses.update({app_name: (process.poll() is None) for app_name, process in app_processes.items()})
        return jsonify(statuses)
    except Exception as e:
       return jsonify({"error": str(e)}), 500
 
@app.route("/stop_lsl", methods=['POST'])
def stop_lsl():
    stop_all_processes()
    return jsonify({'status': 'LSL Stream and applications stopped and server is shutting down.'})

def stop_all_processes():
    global lsl_process, npg_process, app_processes, lsl_running, npg_running

    # Terminate LSL process
    if lsl_process and lsl_process.poll() is None:
        lsl_process.terminate()
        try:
            lsl_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            lsl_process.kill()
        lsl_running = False

    if npg_process and npg_process.poll() is None:
        npg_process.terminate()
        try:
            npg_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            npg_process.kill()
        npg_running = False

    for app_name, process in list(app_processes.items()):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
        del app_processes[app_name]

    print("All processes terminated.")

def handle_sigint(signal_num, frame):
    print("\nCtrl+C pressed! Stopping all processes...")
    stop_all_processes()
    sys.exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, handle_sigint)
atexit.register(stop_all_processes)

if __name__ == "__main__":
    app.run(debug=True)