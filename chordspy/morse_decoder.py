import numpy as np
import pylsl
import sys
import time
from collections import deque
import threading
import tkinter as tk
from tkinter import ttk

class BiquadFilter:
    """Biquad filter implementation matching the firmware"""
    def __init__(self, b0, b1, b2, a1, a2):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a1 = a1
        self.a2 = a2
        self.z1 = 0.0
        self.z2 = 0.0
    
    def process(self, input_sample):
        x0 = input_sample - (self.a1 * self.z1) - (self.a2 * self.z2)
        output = self.b0 * x0 + self.b1 * self.z1 + self.b2 * self.z2
        self.z2 = self.z1
        self.z1 = x0
        return output
    
    def reset(self):
        self.z1 = 0.0
        self.z2 = 0.0

class EOGFilter:
    """EOG High-pass filter (0.5Hz) matching firmware"""
    def __init__(self):
        self.stage = BiquadFilter(0.99136003, -1.98272007, 0.99136003, 
                                   -1.98264542, 0.98279472)
    
    def process(self, input_sample):
        return self.stage.process(input_sample)
    
    def reset(self):
        self.stage.reset()

class NotchFilter:
    """50Hz/60Hz Notch filter matching firmware"""
    def __init__(self):
        self.stage0 = BiquadFilter(0.96588529, -1.57986211, 0.96588529,
                                    -1.58696045, 0.96505858)
        self.stage1 = BiquadFilter(1.00000000, -1.63566226, 1.00000000,
                                    -1.62761184, 0.96671306)
    
    def process(self, input_sample):
        output = self.stage0.process(input_sample)
        output = self.stage1.process(output)
        return output
    
    def reset(self):
        self.stage0.reset()
        self.stage1.reset()

class EnvelopeDetector:
    """Envelope detector for blink detection matching firmware"""
    def __init__(self, window_size):
        self.window_size = window_size
        self.buffer = np.zeros(window_size)
        self.index = 0
        self.sum = 0.0
    
    def update(self, sample):
        abs_sample = abs(sample)
        self.sum -= self.buffer[self.index]
        self.sum += abs_sample
        self.buffer[self.index] = abs_sample
        self.index = (self.index + 1) % self.window_size
        envelope = self.sum / self.window_size
        return envelope

class BaselineTracker:
    """Baseline tracker for horizontal EOG matching firmware"""
    def __init__(self, window_size=512):
        self.window_size = window_size
        self.buffer = np.zeros(window_size)
        self.index = 0
        self.sum = 0.0
        self.filled = False
    
    def update(self, sample):
        self.sum -= self.buffer[self.index]
        self.sum += sample
        self.buffer[self.index] = sample
        self.index += 1
        if self.index >= self.window_size:
            self.index = 0
            self.filled = True
    
    def get_baseline(self):
        if not self.filled and self.index == 0:
            return 0.0
        count = self.window_size if self.filled else self.index
        return self.sum / count if count > 0 else 0.0

class MorseCodeEOGSystem:
    def __init__(self, gui_label=None, gui_root=None, status_label=None, buffer_label=None):
        self.morse_code = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9'
        }
        
        self.morse_buffer = ""
        self.MAX_MORSE_LENGTH = 5
        
        self.gui_label = gui_label
        self.gui_root = gui_root
        self.status_label = status_label
        self.buffer_label = buffer_label
        self.decoded_word = ""
        
        print("Searching for available LSL streams...")
        available_streams = pylsl.resolve_streams()
        if not available_streams:
            print("No LSL streams found! Exiting...")
            sys.exit(0)
        
        self.inlet = None
        for stream in available_streams:
            try:
                self.inlet = pylsl.StreamInlet(stream)
                print(f"Connected to LSL stream: {stream.name()}")
                break
            except Exception as e:
                print(f"Failed to connect to {stream.name()}: {e}")
        
        if self.inlet is None:
            print("Unable to connect to any LSL stream! Exiting...")
            sys.exit(0)
        
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")
        
        # Detect ADC resolution from stream metadata or default to 12-bit
        self.adc_resolution = 12
        self.adc_max = (2 ** self.adc_resolution) - 1
        self.adc_mid = self.adc_max / 2.0
        
        print(f"ADC Resolution: {self.adc_resolution}-bit (0-{self.adc_max})")
        
        # Blink Detection Configuration - adjusted for filtered signal magnitude
        self.BLINK_DEBOUNCE_MS = 150  # Minimum time between detecting separate blinks
        self.DOUBLE_BLINK_MS = 700    # Window for intentional double blinks
        self.TRIPLE_BLINK_MS = 1200   # Window for intentional triple blinks
        self.BLINK_THRESHOLD = 120.0  # Threshold to detect blink start
        self.BLINK_RELEASE_THRESHOLD = 100.0  # Hysteresis: must drop below to allow next blink
        
        self.last_blink_time = 0
        self.first_blink_time = 0
        self.second_blink_time = 0
        self.blink_count = 0
        self.blink_active = False
        self.blink_released = True  # Track if blink has been released before next detection
        
        # Eye Movement Detection Configuration - adjusted for filtered signal
        self.EYE_MOVEMENT_DEBOUNCE_MS = 750  # Minimum time between detecting separate movements
        self.EYE_MOVEMENT_THRESHOLD = 200.0  # Threshold to detect movement
        self.EYE_MOVEMENT_RELEASE_THRESHOLD = 30.0  # Must drop below this to allow next movement
        self.last_eye_movement_time = 0
        self.eye_movement_active = False
        self.eye_movement_released = True  # Track if movement has been released
        
        # Initialize filters
        self.eog_filter_vertical = EOGFilter()
        self.notch_filter_vertical = NotchFilter()
        self.eog_filter_horizontal = EOGFilter()
        self.notch_filter_horizontal = NotchFilter()
        
        # Envelope detector (100ms window)
        envelope_window_ms = 100
        envelope_window_size = (envelope_window_ms * self.sampling_rate) // 1000
        self.envelope_detector = EnvelopeDetector(envelope_window_size)
        
        # Baseline tracker for horizontal EOG
        self.horizontal_baseline = BaselineTracker(window_size=512)
        
        self.current_envelope = 0.0
        self.horizontal_signal = 0.0
        
        self.stream_active = True
        self.last_data_time = None
        
        print("\n===================================")
        print("EOG Morse Code Decoder")
        print("===================================")
        print("Left Eye  = DOT (.)")
        print("Right Eye = DASH (-)")
        print("2x Blink  = SEND Letter")
        print("3x Blink  = BACKSPACE")
        print("===================================\n")

    def add_dot(self):
        if len(self.morse_buffer) >= self.MAX_MORSE_LENGTH:
            print("\nBuffer full! Resetting...")
            self.morse_buffer = ""
        
        self.morse_buffer += "."
        print(".", end="", flush=True)
        self.update_buffer_gui()
    
    def add_dash(self):
        if len(self.morse_buffer) >= self.MAX_MORSE_LENGTH:
            print("\nBuffer full! Resetting...")
            self.morse_buffer = ""
        
        self.morse_buffer += "-"
        print("-", end="", flush=True)
        self.update_buffer_gui()
    
    def send_morse_as_letter(self):
        if len(self.morse_buffer) == 0:
            print("\nBuffer empty")
            return
        
        if self.morse_buffer in self.morse_code:
            decoded = self.morse_code[self.morse_buffer]
            print(f" -> {decoded}")
            self.decoded_word += decoded
            self.update_word_gui(self.decoded_word)
        else:
            print(f"\nInvalid: {self.morse_buffer}")
        
        self.morse_buffer = ""
        self.update_buffer_gui()
    
    def send_backspace(self):
        print("\n>>> BACKSPACE")
        self.morse_buffer = ""
        if len(self.decoded_word) > 0:
            self.decoded_word = self.decoded_word[:-1]
            self.update_word_gui(self.decoded_word)
        self.update_buffer_gui()
    
    def update_word_gui(self, text):
        if self.gui_label and self.gui_root:
            def set_label():
                self.gui_label.config(text=text)
            self.gui_root.after(0, set_label)
    
    def update_status_gui(self, text):
        if self.status_label and self.gui_root:
            def set_status():
                self.status_label.config(text=text)
            self.gui_root.after(0, set_status)
    
    def update_buffer_gui(self):
        if self.buffer_label and self.gui_root:
            buffer_text = f"Buffer: {self.morse_buffer if self.morse_buffer else '(empty)'}"
            def set_buffer():
                self.buffer_label.config(text=buffer_text)
            self.gui_root.after(0, set_buffer)
    
    def detect_blinks(self, now_ms):
        envelope_high = self.current_envelope > self.BLINK_THRESHOLD
        envelope_low = self.current_envelope < self.BLINK_RELEASE_THRESHOLD
        
        # Track release state - envelope must drop below release threshold before next blink
        if envelope_low and self.blink_active:
            self.blink_released = True
            self.blink_active = False
        
        # Only detect new blink if:
        # 1. Envelope is high (crossing threshold upward)
        # 2. Previous blink has been released (envelope went low)
        # 3. Sufficient time has passed (debounce) OR blink was released
        # The key: allow quick blinks if they properly released, ignore bouncing if too fast
        time_since_last = now_ms - self.last_blink_time
        can_detect = self.blink_released and (time_since_last >= self.BLINK_DEBOUNCE_MS or time_since_last >= 150)
        
        if envelope_high and not self.blink_active and can_detect:
            self.last_blink_time = now_ms
            self.blink_released = False  # Mark as not released until envelope drops
            self.blink_active = True
            
            if self.blink_count == 0:
                self.first_blink_time = now_ms
                self.blink_count = 1
                self.update_status_gui("Blink detected (1)")
                print("\n[BLINK 1]", end="", flush=True)
            elif self.blink_count == 1 and (now_ms - self.first_blink_time) <= self.DOUBLE_BLINK_MS:
                self.second_blink_time = now_ms
                self.blink_count = 2
                self.update_status_gui("Double Blink detected (2)")
                print(" [BLINK 2]", end="", flush=True)
            elif self.blink_count == 2 and (now_ms - self.second_blink_time) <= self.TRIPLE_BLINK_MS:
                print("\n>>> TRIPLE BLINK <<<")
                self.update_status_gui(">>> TRIPLE BLINK - BACKSPACE <<<")
                self.send_backspace()
                self.blink_count = 0
            else:
                # Reset if timing doesn't match double/triple blink pattern
                self.first_blink_time = now_ms
                self.blink_count = 1
                self.update_status_gui("Blink detected (1)")
                print("\n[BLINK 1]", end="", flush=True)
        
        # Check for double blink timeout
        if self.blink_count == 2 and (now_ms - self.second_blink_time) > self.TRIPLE_BLINK_MS:
            print("\n>>> DOUBLE BLINK <<<")
            self.update_status_gui(">>> DOUBLE BLINK - SEND LETTER <<<")
            self.send_morse_as_letter()
            self.blink_count = 0
        
        # Check for single blink timeout
        if self.blink_count == 1 and (now_ms - self.first_blink_time) > self.DOUBLE_BLINK_MS:
            self.blink_count = 0
            self.update_status_gui("Ready")
    
    def detect_eye_movement(self, now_ms):
        baseline = self.horizontal_baseline.get_baseline()
        deviation = self.horizontal_signal - baseline
        abs_deviation = abs(deviation)
        
        # Track release state - must return to low deviation before next movement
        if abs_deviation < self.EYE_MOVEMENT_RELEASE_THRESHOLD and self.eye_movement_active:
            self.eye_movement_released = True
            self.eye_movement_active = False
        
        # Only detect new movement if:
        # 1. Deviation exceeds threshold
        # 2. Previous movement has been released
        # 3. Sufficient time has passed (debounce)
        if not self.eye_movement_active and abs_deviation > self.EYE_MOVEMENT_THRESHOLD and \
           self.eye_movement_released and (now_ms - self.last_eye_movement_time) >= self.EYE_MOVEMENT_DEBOUNCE_MS:
            
            self.eye_movement_active = True
            self.eye_movement_released = False  # Mark as not released
            self.last_eye_movement_time = now_ms
            
            if deviation < 0:
                print("\n>>> LEFT <<<")
                self.update_status_gui(">>> LEFT - DOT <<<")
                self.add_dot()
            else:
                print("\n>>> RIGHT <<<")
                self.update_status_gui(">>> RIGHT - DASH <<<")
                self.add_dash()

    def run(self):
        try:
            while self.stream_active:
                samples, _ = self.inlet.pull_chunk(timeout=0.1, max_samples=10)
                
                if samples:
                    self.last_data_time = time.time()
                    now_ms = int(time.time() * 1000)
                    
                    for sample in samples:
                        # Get raw ADC values and center them
                        # sample[0] = Vertical EOG (blinks)
                        # sample[1] = Horizontal EOG (left/right)
                        raw_vertical = sample[0] - self.adc_mid
                        raw_horizontal = sample[1] - self.adc_mid
                        
                        # Process vertical EOG (channel 0) for blink detection
                        filt_vertical = self.notch_filter_vertical.process(raw_vertical)
                        filt_vertical = self.eog_filter_vertical.process(filt_vertical)
                        self.current_envelope = self.envelope_detector.update(filt_vertical)
                        
                        # Process horizontal EOG (channel 1) for left/right detection
                        filt_horizontal = self.notch_filter_horizontal.process(raw_horizontal)
                        filt_horizontal = self.eog_filter_horizontal.process(filt_horizontal)
                        self.horizontal_signal = filt_horizontal
                        self.horizontal_baseline.update(filt_horizontal)
                    
                    self.detect_blinks(now_ms)
                    self.detect_eye_movement(now_ms)
                
                else:
                    if self.last_data_time and (time.time() - self.last_data_time) > 2:
                        self.stream_active = False
                        print("\nLSL stream disconnected!")
                        self.update_status_gui("Stream disconnected!")
                        
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    gui_root = tk.Tk()
    gui_root.title("EOG Morse Code Decoder")
    gui_root.configure(bg="white")
    gui_root.geometry("700x400+200+200")
    
    # Title
    title_label = tk.Label(gui_root, text="EOG Morse Code Decoder", 
                           font=("Arial", 20, "bold"), bg="white", fg="#2c3e50")
    title_label.pack(pady=10)
    
    # Instructions
    instructions = tk.Label(gui_root, 
                           text="Left Eye = DOT (.)  |  Right Eye = DASH (-)  |  2x Blink = SEND  |  3x Blink = BACKSPACE",
                           font=("Arial", 10), bg="white", fg="#7f8c8d")
    instructions.pack(pady=5)
    
    # Status label
    status_label = tk.Label(gui_root, text="Initializing...", 
                           font=("Arial", 14), bg="white", fg="#27ae60")
    status_label.pack(pady=10)
    
    # Buffer display
    buffer_label = tk.Label(gui_root, text="Buffer: (empty)", 
                           font=("Courier", 16, "bold"), bg="#ecf0f1", fg="#2980b9",
                           relief=tk.SUNKEN, padx=10, pady=5)
    buffer_label.pack(pady=10, padx=20, fill=tk.X)
    
    # Decoded word display
    word_frame = tk.Frame(gui_root, bg="white")
    word_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
    
    word_title = tk.Label(word_frame, text="Decoded Message:", 
                         font=("Arial", 12), bg="white", fg="#34495e")
    word_title.pack(anchor=tk.W)
    
    gui_label = tk.Label(word_frame, text="", font=("Arial", 36, "bold"), 
                        bg="#ffffff", fg="#2c3e50", relief=tk.GROOVE, 
                        padx=20, pady=20, anchor=tk.W, justify=tk.LEFT)
    gui_label.pack(fill=tk.BOTH, expand=True)

    system = MorseCodeEOGSystem(gui_label=gui_label, gui_root=gui_root, 
                                status_label=status_label, buffer_label=buffer_label)
    system_thread = threading.Thread(target=system.run, daemon=True)
    system_thread.start()

    gui_root.mainloop()