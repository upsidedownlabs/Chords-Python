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
            lsl_process = subprocess.Popen(["python", "chords.py", "--lsl"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            lsl_process = subprocess.Popen(["python", "chords.py", "--lsl"])
        
        if lsl_process.poll() is None:
            return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green")
        else:
            return render_template("index.html", lsl_started=False, lsl_status="Failed to Start", lsl_color="red")
    except Exception as e:
        return render_template("index.html", lsl_started=False, lsl_status=f"Error: {e}", lsl_color="red")

@app.route("/run_app", methods=["POST"])
def run_app():
    app_name = request.form.get("app_name")

    # Check if the app is already running
    if app_name in app_processes and app_processes[app_name].poll() is None:
        return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green", message=f"{app_name} is already Running")

    try:
        # Start the app subprocess
        if sys.platform == "win32":
            process = subprocess.Popen(["python", f"{app_name}.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            process = subprocess.Popen(["python", f"{app_name}.py"])

        app_processes[app_name] = process
        return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green", message=None)
    except Exception as e:
        return render_template("index.html", lsl_started=True, lsl_status="Running", lsl_color="green", message=f"Error starting {app_name}: {e}")

@app.route("/stop_lsl", methods=['POST'])
def stop_lsl():
    # Terminate LSL process
    if lsl_process and lsl_process.poll() is None:
        lsl_process.terminate()

    # Terminate all app processes
    for app_name, process in app_processes.items():
        if process.poll() is None:
            process.terminate()

    # Shutdown the server gracefully
    os._exit(0)
    return jsonify({'status': 'LSL Stream and applications stopped and server is shutting down.'})

if __name__ == "__main__":
    app.run(debug=True)