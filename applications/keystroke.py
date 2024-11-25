import numpy as np
from scipy.signal import butter, lfilter
import pylsl
import tkinter as tk
import threading
import time
import pyautogui


class EOGPeakDetector:
    def __init__(self, blink_button, keystroke_action):
        self.inlet = None
        self.sampling_rate = None
        self.buffer_size = None
        self.eog_data = None
        self.current_index = 0
        self.b, self.a = None, None
        self.blink_button = blink_button
        self.keystroke_action = keystroke_action
        self.blink_detected = False
        self.running = False

    def initialize_stream(self):
        streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
        if not streams:
            print("No LSL stream found!")
            return False
        
        self.inlet = pylsl.StreamInlet(streams[0])
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")
        
        self.buffer_size = self.sampling_rate * 1
        self.eog_data = np.zeros(self.buffer_size)
        self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')
        return True

    def start_detection(self):
        if not self.initialize_stream():
            print("Failed to initialize LSL stream. Cannot start detection.")
            return

        print("Starting peak detection...")
        self.running = True
        while self.running:
            # Pull a chunk of data from the stream
            samples, _ = self.inlet.pull_chunk(timeout=1.0, max_samples=1)
            if samples:
                for sample in samples:
                    # Store the sample in the circular buffer
                    self.eog_data[self.current_index] = sample[0]
                    self.current_index = (self.current_index + 1) % self.buffer_size

                # Apply the low-pass filter
                filtered_eog = lfilter(self.b, self.a, self.eog_data)
                
                # Detect blinks in the filtered signal
                self.detect_blinks(filtered_eog)

    def stop_detection(self):
        # Stop the detection loop
        print("Stopping peak detection...")
        self.running = False

    def detect_blinks(self, filtered_eog):
        mean_signal = np.mean(filtered_eog)
        stdev_signal = np.std(filtered_eog)
        threshold = mean_signal + (2 * stdev_signal)  # Threshold for detecting blinks

        # Define the window size (1 second of data)
        window_size = self.sampling_rate
        start_index = self.current_index - window_size
        if start_index < 0:
            start_index = 0

        # Extract the window of data for peak detection
        filtered_window = filtered_eog[start_index:self.current_index]
        peaks = self.detect_peaks(filtered_window, threshold)

        if peaks and not self.blink_detected:
            # Blink detected, trigger actions
            print("Blink Detected!")
            self.update_button_color()
            self.keystroke_action()
            self.blink_detected = True
        elif not peaks:
            # Reset blink state when no peaks are detected
            self.blink_detected = False

    def detect_peaks(self, signal, threshold):
        # Detect peaks in the signal that exceed the threshold
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
                peaks.append(i)
        return peaks

    def update_button_color(self):
        # Temporarily change the button color to indicate a blink
        self.blink_button.config(bg="green")
        self.blink_button.update()
        time.sleep(0.1)
        self.blink_button.config(bg="SystemButtonFace")

def stop_action(detector):
    # Action for the Quit button
    print("Quit button pressed. Exiting program.")
    detector.stop_detection()
    exit()

def keystroke_action():
    # Action to simulate a spacebar key press
    print("Spacebar pressed.")
    pyautogui.press('space')

def start_action(detector):
    # Action for the Start button
    print("Start button pressed. Starting the program.")
    detection_thread = threading.Thread(target=detector.start_detection, daemon=True)
    detection_thread.start()

def create_popup():
    # Create the main GUI window
    popup = tk.Tk()
    popup.geometry("350x80")  # Set the window size
    popup.overrideredirect(1)  # Remove title bar
    popup.attributes("-topmost", True)  # Keep the window on top

    # Create a single horizontal frame for buttons
    horizontal_frame = tk.Frame(popup)
    horizontal_frame.pack(expand=True, pady=10)

    # Add Blink Detected button
    blink_button = tk.Button(horizontal_frame, text="Blink Detected", width=12)
    blink_button.pack(side=tk.LEFT, padx=10)

    # Add Start button
    start_button = tk.Button(horizontal_frame, text="Start", width=8)
    start_button.pack(side=tk.LEFT, padx=10)

    # Add Quit button
    stop_button = tk.Button(horizontal_frame, text="Quit", width=8)
    stop_button.pack(side=tk.LEFT, padx=10)

    # Initialize the EOG peak detector
    detector = EOGPeakDetector(blink_button, keystroke_action)

    # Link Start and Stop buttons to their respective actions
    start_button.config(command=lambda: start_action(detector))
    stop_button.config(command=lambda: stop_action(detector))

    popup.mainloop()

# Create the pop-up window and run the application
create_popup()