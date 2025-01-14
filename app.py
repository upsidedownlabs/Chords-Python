from flask import Flask, render_template, jsonify, request
import subprocess
import psutil
import os
import signal
import sys

app = Flask(__name__)
lsl_process = None
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
    global lsl_process
    if lsl_process and lsl_process.poll() is None:
        return jsonify({"status": "LSL stream already running", "lsl_started": True})
    try:
        # Start the LSL stream as a subprocess
        if sys.platform == "win32":
            lsl_process = subprocess.Popen(["python", "chords.py", "--lsl"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            lsl_process = subprocess.Popen(["python", "chords.py", "--lsl"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = lsl_process.stderr.readline().decode().strip()  # Read the initial stderr line

        print(output)
        if output == "No":
            return render_template("index.html", lsl_started=False, lsl_status="Failed to Start", lsl_color="red")
        else:
            return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green")
    except subprocess.TimeoutExpired:
        return render_template(
            "index.html", lsl_started=False, lsl_status="Timeout Error", lsl_color="red"
        )
    except Exception as e:
        return render_template("index.html", lsl_started=False, lsl_status=f"Error: {e}", lsl_color="red")

@app.route("/run_app", methods=["POST"])
def run_app():
    app_name = request.form.get("app_name")

    # Check if the app is already running
    if app_name in app_processes and app_processes[app_name].poll() is None:
        return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green", message=f"{app_name} is already Running", running_apps=app_processes.keys())

    try:
        # Start the app subprocess
        if sys.platform == "win32":
            process = subprocess.Popen(["python", f"{app_name}.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            process = subprocess.Popen(["python", f"{app_name}.py"])

        app_processes[app_name] = process
        return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green", running_apps=app_processes.keys(), message=None)
        
    except Exception as e:
        return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green", message=f"Error starting {app_name}: {e}", running_apps=app_processes.keys())

@app.route("/app_status", methods=["GET"])
def app_status():
    # Check the status of all apps
    try:
        statuses = {
            app_name: (process.poll() is None)  # True if running, False if not
            for app_name, process in app_processes.items()
        }
        return jsonify(statuses)
    except Exception as e:
       return jsonify({"error": str(e)}), 500
 
@app.route("/stop_lsl", methods=['POST'])
def stop_lsl():
    stop_all_processes()
    return jsonify({'status': 'LSL Stream and applications stopped and server is shutting down.'})

def stop_all_processes():
    global lsl_process, app_processes

    # Terminate LSL process
    if lsl_process and lsl_process.poll() is None:
        lsl_process.terminate()
        try:
            lsl_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            lsl_process.kill()

    # Terminate all app processes
    for app_name, process in app_processes.items():
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()

    app_processes.clear()
    print("All processes terminated.")

def handle_sigint(signal_num, frame):
    print("\nCtrl+C pressed! Stopping all processes...")
    stop_all_processes()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)   # Register signal handler for Ctrl+C

if __name__ == "__main__":
    app.run(debug=True)