import tkinter as tk
from tkinter import PhotoImage
import threading
import pyautogui
import numpy as np
from scipy.signal import butter, lfilter
import pylsl
import time

class EOGPeakDetector:
    def __init__(self, blink_button, keystroke_action, connect_button):
        self.inlet = None
        self.sampling_rate = None
        self.buffer_size = None
        self.eog_data = None
        self.current_index = 0
        self.b, self.a = None, None
        self.blink_button = blink_button
        self.keystroke_action = keystroke_action
        self.connect_button = connect_button
        self.blink_detected = False
        self.running = False
        self.connected = False
        self.last_blink_time = 0
        self.refractory_period = 0.2
        self.stop_threads = False

    def initialize_stream(self):
        print("Attempting to connect to LSL stream...")
        streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
        if not streams:
            print("No LSL stream found!")
            self.connected = False
            return False

        self.inlet = pylsl.StreamInlet(streams[0])
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")

        self.buffer_size = self.sampling_rate * 1
        self.eog_data = np.zeros(self.buffer_size)
        self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')
        self.connected = True
        print("LSL stream connected successfully.")
        return True

    def start_detection(self):
        print("Starting peak detection...")
        self.running = True
        while self.running:
            try:
                samples, _ = self.inlet.pull_chunk(timeout=1.0, max_samples=1)
                if samples:
                    for sample in samples:
                        self.eog_data[self.current_index] = sample[0]
                        self.current_index = (self.current_index + 1) % self.buffer_size

                    filtered_eog = lfilter(self.b, self.a, self.eog_data)
                    self.detect_blinks(filtered_eog)
            except Exception as e:
                print(f"Error in detection: {e}")
                break

    def stop_detection(self):
        print("Stopping peak detection...")
        self.running = False

    def detect_blinks(self, filtered_eog):
        mean_signal = np.mean(filtered_eog)
        stdev_signal = np.std(filtered_eog)
        threshold = mean_signal + (1.7 * stdev_signal)

        window_size = self.sampling_rate
        start_index = self.current_index - window_size
        if start_index < 0:
            start_index = 0

        filtered_window = filtered_eog[start_index:self.current_index]
        peaks = self.detect_peaks(filtered_window, threshold)

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
        self.blink_button.after(100, lambda: self.blink_button.config(bg="SystemButtonFace"))

def quit_action(detector):
    print("Quit button pressed. Exiting program.")
    detector.stop_threads = True
    detector.stop_detection()
    popup.quit()
    popup.destroy()

def keystroke_action():
    print("Spacebar pressed!")
    pyautogui.press('space')

def connect_start_stop_action(detector, connect_button):
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

    eye_icon = PhotoImage(file="media\\icons8-eye-30.png")

    blink_button = tk.Button(horizontal_frame, image=eye_icon, width=70, height=38, bg="#FFFFFF")
    blink_button.image = eye_icon
    blink_button.pack(side=tk.LEFT, padx=10)

    connect_button = tk.Button(horizontal_frame, text="Connect", width=7, bg="#CBC3E3")
    connect_button.pack(side=tk.LEFT, padx=10)

    quit_button = tk.Button(horizontal_frame, text="Quit", width=7, bg="#71797E", fg="#FFFFFF")
    quit_button.pack(side=tk.LEFT, padx=10)

    detector = EOGPeakDetector(blink_button, keystroke_action, connect_button)

    connect_button.config(command=lambda: connect_start_stop_action(detector, connect_button))
    quit_button.config(command=lambda: quit_action(detector))

    popup.mainloop()

create_popup()