import tkinter as tk
from tkinter import PhotoImage
import threading
import pyautogui
import numpy as np
from scipy.signal import butter, lfilter
import pylsl
import time
import os

class EOGPeakDetector:
    def __init__(self, blink_button, keystroke_action, connect_button):
        self.inlet = None                         # LSL inlet for receiving data
        self.sampling_rate = None                 # Sampling rate of the data stream
        self.buffer_size = None                   # Size of the buffer for storing EOG data
        self.eog_data = None                      # Buffer for EOG data
        self.current_index = 0                    # Current index in the buffer
        self.b, self.a = None, None               # Filter coefficients for low-pass filter
        self.blink_button = blink_button          # Button to trigger blink action
        self.keystroke_action = keystroke_action  # Action to perform on blink detection
        self.connect_button = connect_button      # Button to connect to LSL stream
        self.blink_detected = False               # Flag to indicate if a blink has been detected
        self.running = False                      # Flag to control the detection loop
        self.connected = False                    # Flag to indicate if connected to LSL stream
        self.last_blink_time = 0                  # Last time a blink was detected
        self.refractory_period = 0.2              # Refractory period to prevent multiple eye blink detections
        self.stop_threads = False                 # Flag to stop threads
        self.stream_active = False                # Flag to indicate if the stream is active
        self.last_data_time = None                # Last time data was received from the stream

    def initialize_stream(self):
        """Initialize the LSL stream connection and set up the buffer and filter coefficients."""
        print("Searching for available LSL streams...")
        available_streams = pylsl.resolve_streams()
        
        if not available_streams:
            print("No LSL streams found! Connection failed.")
            self.connected = False
            return False

        for stream in available_streams:
            try:
                self.inlet = pylsl.StreamInlet(stream)
                print(f"Connected to LSL stream: {stream.name()}")
                self.sampling_rate = int(self.inlet.info().nominal_srate())
                print(f"Sampling rate: {self.sampling_rate} Hz")

                # Set buffer size and filter coefficients
                self.buffer_size = self.sampling_rate * 1      # Buffer size for 1 second of data
                self.eog_data = np.zeros(self.buffer_size)     # Initialize buffer for EOG data
                self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')  # Low-pass filter coefficients
                self.connected = True                          # Set connected flag to True(LSL Stream connected)
                print("LSL stream connected successfully.")
                return True  # Stop trying after first successful connection

            except Exception as e:
                print(f"Failed to connect to stream {stream.name()}: {e}")

        print("Unable to connect to any available LSL stream.")
        self.connected = False
        return False

    def start_detection(self):
        """Start the peak detection process"""
        print("Starting peak detection...")
        self.running = True    # Flag to control the detection loop
        while self.running:
            try:
                samples, _ = self.inlet.pull_chunk(timeout=1.0, max_samples=1)
                if samples:
                    self.last_data_time = time.time()
                    for sample in samples:
                        self.eog_data[self.current_index] = sample[0]                     # Store sample in circular buffer at current position
                        self.current_index = (self.current_index + 1) % self.buffer_size  # Update index with wrap-around using modulo

                    filtered_eog = lfilter(self.b, self.a, self.eog_data)
                    self.detect_blinks(filtered_eog)             # Run blink detection on the filtered signal
                else:
                    if self.last_data_time and (time.time() - self.last_data_time) > 2:
                        print("LSL Status: Stream disconnected. Stopping detection.")
                        self.stop_detection()
                        popup.after(0, popup.quit)  # Schedule quit on main thread
                        break  # Exit the loop
            except Exception as e:
                print(f"Error in detection: {e}")
                self.stop_detection()
                popup.after(0, popup.quit)
                break

    def stop_detection(self):
        """Stop the peak detection process"""
        print("Stopping peak detection...")
        self.running = False               # Set running flag to False to stop the detection loop

    def detect_blinks(self, filtered_eog):
        """Detect blinks in the filtered EOG signal using a threshold-based method."""
        # Calculate dynamic threshold based on signal statistics
        mean_signal = np.mean(filtered_eog)
        stdev_signal = np.std(filtered_eog)
        threshold = mean_signal + (1.7 * stdev_signal)

        window_size = self.sampling_rate
        start_index = self.current_index - window_size
        if start_index < 0:
            start_index = 0

        filtered_window = filtered_eog[start_index:self.current_index]  # Get the current window of filtered EOG data
        peaks = self.detect_peaks(filtered_window, threshold)           # Detect peaks above threshold in the current window

        current_time = time.time()
        if peaks and (current_time - self.last_blink_time > self.refractory_period):
            self.last_blink_time = current_time
            print(f"Blink detected at index {peaks[0]}. Time: {current_time}")
            self.trigger_action()

    def detect_peaks(self, signal, threshold):
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
                if not peaks or (i - peaks[-1] > self.sampling_rate * self.refractory_period):
                    peaks.append(i)
        return peaks

    def trigger_action(self):
        """Trigger the keystroke action when a blink is detected."""
        if not self.blink_detected:
            self.blink_detected = True
            print("Triggering action...")
            self.keystroke_action()  # Press spacebar
            self.update_button_color()
            threading.Timer(self.refractory_period, self.reset_blink_detected).start()

    def reset_blink_detected(self):
        self.blink_detected = False

    def update_button_color(self):
        self.blink_button.config(bg="#ADD8E6")
        self.blink_button.update()

    def reset_button_color(self):
        # Use a cross-platform default color for button background
        self.blink_button.after(100, lambda: self.blink_button.config(bg=self.blink_button.cget("bg")))

def quit_action(detector):
    """Handle the quit action for the GUI."""
    print("Quit button pressed. Exiting program.")
    detector.stop_threads = True
    detector.stop_detection()
    popup.quit()
    popup.destroy()

def keystroke_action():
    """Perform the keystroke action (press spacebar)."""
    print("Spacebar pressed!")
    pyautogui.press('space')

def connect_start_stop_action(detector, connect_button):
    """Handle the connect/start/stop action for the GUI."""
    if not detector.connected:
        print("Connect button pressed. Starting connection in a new thread.")
        threading.Thread(target=connect_to_stream, args=(detector, connect_button), daemon=True).start()
    elif not detector.running:
        print("Start button pressed. Starting blink detection.")
        connect_button.config(text="Stop", bg="#FF6961")
        detection_thread = threading.Thread(target=detector.start_detection, daemon=True)
        detection_thread.start()
    else:
        print("Stop button pressed. Stopping blink detection.")
        connect_button.config(text="Start", bg="#90EE90")
        detector.stop_detection()

def connect_to_stream(detector, connect_button):
    if detector.initialize_stream():
        connect_button.config(text="Start", bg="#90EE90")
    else:
        print("Failed to connect to LSL stream.")

def create_popup():
    """Create the popup window for the EOG keystroke emulator."""
    global popup
    popup = tk.Tk()
    popup.geometry("300x120")
    popup.overrideredirect(1)
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    title_bar = tk.Frame(popup, bg="#6082B6", relief="raised", bd=0, height=20)
    title_bar.pack(fill=tk.X, side=tk.TOP)

    title_label = tk.Label(title_bar, text="     EOG Keystroke Emulator", bg="#6082B6", fg="white", font=("Arial", 10))
    title_label.pack(side=tk.LEFT, padx=5)

    def start_move(event):
        popup.x = event.x
        popup.y = event.y

    def move(event):
        x = popup.winfo_pointerx() - popup.x
        y = popup.winfo_pointery() - popup.y
        popup.geometry(f"+{x}+{y}")

    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", move)
    title_label.bind("<Button-1>", start_move)
    title_label.bind("<B1-Motion>", move)

    horizontal_frame = tk.Frame(popup)
    horizontal_frame.pack(expand=True, pady=10)

    # Use a relative path for the icon
    icon_path = os.path.join(os.path.dirname(__file__), "media", "icons8-eye-30.png")
    eye_icon = PhotoImage(file=icon_path)

    blink_button = tk.Button(horizontal_frame, image=eye_icon, width=70, height=38, bg="#FFFFFF")
    blink_button.image = eye_icon
    blink_button.pack(side=tk.LEFT, padx=10)

    connect_button = tk.Button(horizontal_frame, text="Connect", width=7, bg="#CBC3E3")
    connect_button.pack(side=tk.LEFT, padx=10)

    quit_button = tk.Button(horizontal_frame, text="Quit", width=7, bg="#71797E", fg="#FFFFFF")
    quit_button.pack(side=tk.LEFT, padx=10)

    detector = EOGPeakDetector(blink_button, keystroke_action, connect_button)

    connect_button.config(command=lambda: connect_start_stop_action(detector, connect_button))   # Connect/Start/Stop action
    quit_button.config(command=lambda: quit_action(detector))    # Quit action

    popup.mainloop()

create_popup()