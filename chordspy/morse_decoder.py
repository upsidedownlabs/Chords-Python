import numpy as np
import pylsl
import sys
import time
from collections import deque
import threading
import tkinter as tk

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
        # Coefficients from firmware
        self.stage = BiquadFilter(0.99136003, -1.98272007, 0.99136003, 
                                   -1.98264542, 0.98279472)
    
    def process(self, input_sample):
        return self.stage.process(input_sample)
    
    def reset(self):
        self.stage.reset()

class NotchFilter:
    """50Hz/60Hz Notch filter matching firmware"""
    def __init__(self):
        # Two-stage notch filter from firmware
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
    def __init__(self, gui_label=None, gui_root=None):
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
        
        # Morse buffer and configuration
        self.morse_buffer = ""
        self.MAX_MORSE_LENGTH = 5
        
        # GUI label and root for updating decoded character
        self.gui_label = gui_label
        self.gui_root = gui_root
        self.decoded_word = ""
        
        # Set up LSL stream inlet
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
        
        # Blink Detection Configuration (matching firmware)
        self.BLINK_DEBOUNCE_MS = 250
        self.DOUBLE_BLINK_MS = 600
        self.TRIPLE_BLINK_MS = 1000
        self.BLINK_THRESHOLD = 150.0
        
        self.last_blink_time = 0
        self.first_blink_time = 0
        self.second_blink_time = 0
        self.blink_count = 0
        self.blink_active = False
        
        # Eye Movement Detection Configuration (matching firmware)
        self.EYE_MOVEMENT_DEBOUNCE_MS = 500
        self.EYE_MOVEMENT_THRESHOLD = 350.0
        self.last_eye_movement_time = 0
        self.eye_movement_active = False
        
        # Initialize filters for vertical EOG (blink detection)
        self.eog_filter_vertical = EOGFilter()
        self.notch_filter_vertical = NotchFilter()
        
        # Initialize filters for horizontal EOG (left/right detection)
        self.eog_filter_horizontal = EOGFilter()
        self.notch_filter_horizontal = NotchFilter()
        
        # Envelope detector for blink detection (100ms window)
        envelope_window_ms = 100
        envelope_window_size = (envelope_window_ms * self.sampling_rate) // 1000
        self.envelope_detector = EnvelopeDetector(envelope_window_size)
        
        # Baseline tracker for horizontal EOG
        self.horizontal_baseline = BaselineTracker(window_size=512)
        
        # Current signal values
        self.current_envelope = 0.0
        self.horizontal_signal = 0.0
        
        # Stream state
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
        """Add dot to morse buffer"""
        if len(self.morse_buffer) >= self.MAX_MORSE_LENGTH:
            print("\nBuffer full! Resetting...")
            self.morse_buffer = ""
        
        self.morse_buffer += "."
        print(".", end="", flush=True)
    
    def add_dash(self):
        """Add dash to morse buffer"""
        if len(self.morse_buffer) >= self.MAX_MORSE_LENGTH:
            print("\nBuffer full! Resetting...")
            self.morse_buffer = ""
        
        self.morse_buffer += "-"
        print("-", end="", flush=True)
    
    def send_morse_as_letter(self):
        """Send accumulated morse code as letter"""
        if len(self.morse_buffer) == 0:
            print("\nBuffer empty")
            return
        
        if self.morse_buffer in self.morse_code:
            decoded = self.morse_code[self.morse_buffer]
            print(f" -> {decoded}")
            self.decoded_word += decoded
            self.update_gui(self.decoded_word)
        else:
            print(f"\nInvalid: {self.morse_buffer}")
        
        self.morse_buffer = ""
    
    def send_backspace(self):
        """Send backspace - clear buffer and remove last character"""
        print("\n>>> BACKSPACE")
        self.morse_buffer = ""
        if len(self.decoded_word) > 0:
            self.decoded_word = self.decoded_word[:-1]
            self.update_gui(self.decoded_word)
    
    def update_gui(self, text):
        """Update the label in the tkinter window with the decoded word"""
        if self.gui_label and self.gui_root:
            def set_label():
                self.gui_label.config(text=text)
            self.gui_root.after(0, set_label)
    
    def detect_blinks(self, now_ms):
        """Detect blinks using envelope detector matching firmware logic"""
        envelope_high = self.current_envelope > self.BLINK_THRESHOLD
        
        if not self.blink_active and envelope_high and (now_ms - self.last_blink_time) >= self.BLINK_DEBOUNCE_MS:
            self.last_blink_time = now_ms
            
            if self.blink_count == 0:
                self.first_blink_time = now_ms
                self.blink_count = 1
            elif self.blink_count == 1 and (now_ms - self.first_blink_time) <= self.DOUBLE_BLINK_MS and \
                 (now_ms - self.first_blink_time) >= self.BLINK_DEBOUNCE_MS:
                self.second_blink_time = now_ms
                self.blink_count = 2
            elif self.blink_count == 2 and (now_ms - self.second_blink_time) <= self.TRIPLE_BLINK_MS and \
                 (now_ms - self.second_blink_time) >= self.BLINK_DEBOUNCE_MS:
                print("\n>>> TRIPLE BLINK <<<")
                self.send_backspace()
                self.blink_count = 0
            else:
                self.first_blink_time = now_ms
                self.blink_count = 1
            
            self.blink_active = True
        
        if not envelope_high:
            self.blink_active = False
        
        # Check for double blink timeout
        if self.blink_count == 2 and (now_ms - self.second_blink_time) > self.TRIPLE_BLINK_MS:
            print("\n>>> DOUBLE BLINK <<<")
            self.send_morse_as_letter()
            self.blink_count = 0
        
        # Check for single blink timeout
        if self.blink_count == 1 and (now_ms - self.first_blink_time) > self.DOUBLE_BLINK_MS:
            self.blink_count = 0
    
    def detect_eye_movement(self, now_ms):
        """Detect eye movement (left/right) matching firmware logic"""
        baseline = self.horizontal_baseline.get_baseline()
        deviation = self.horizontal_signal - baseline
        abs_deviation = abs(deviation)
        
        if not self.eye_movement_active and abs_deviation > self.EYE_MOVEMENT_THRESHOLD and \
           (now_ms - self.last_eye_movement_time) >= self.EYE_MOVEMENT_DEBOUNCE_MS:
            
            self.eye_movement_active = True
            self.last_eye_movement_time = now_ms
            
            if deviation < 0:
                print("\n>>> LEFT <<<")
                self.add_dot()
            else:
                print("\n>>> RIGHT <<<")
                self.add_dash()
        
        if self.eye_movement_active and abs_deviation < (self.EYE_MOVEMENT_THRESHOLD * 0.5):
            self.eye_movement_active = False

    def run(self):
        """Main loop matching firmware processing"""
        try:
            while self.stream_active:
                samples, _ = self.inlet.pull_chunk(timeout=0.1, max_samples=10)
                
                if samples:
                    self.last_data_time = time.time()
                    now_ms = int(time.time() * 1000)
                    
                    for sample in samples:
                        # Process vertical EOG (channel 1) for blink detection
                        raw_ch1 = sample[1]
                        filt_ch1 = self.notch_filter_vertical.process(raw_ch1)
                        filt_ch1 = self.eog_filter_vertical.process(filt_ch1)
                        self.current_envelope = self.envelope_detector.update(filt_ch1)
                        
                        # Process horizontal EOG (channel 0) for left/right detection
                        raw_ch0 = sample[0]
                        filt_ch0 = self.notch_filter_horizontal.process(raw_ch0)
                        filt_ch0 = self.eog_filter_horizontal.process(filt_ch0)
                        self.horizontal_signal = filt_ch0
                        self.horizontal_baseline.update(filt_ch0)
                    
                    # Detect blinks and eye movements
                    self.detect_blinks(now_ms)
                    self.detect_eye_movement(now_ms)
                
                else:
                    if self.last_data_time and (time.time() - self.last_data_time) > 2:
                        self.stream_active = False
                        print("\nLSL stream disconnected!")
                        
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    gui_root = tk.Tk()
    gui_root.title("Morse Output")
    gui_root.configure(bg="white")
    gui_root.geometry("500x300+220+280")
    gui_label = tk.Label(gui_root, text="", font=("Arial", 48), bg="white", fg="black")
    gui_label.pack(expand=True)

    system = MorseCodeEOGSystem(gui_label=gui_label, gui_root=gui_root)
    system_thread = threading.Thread(target=system.run, daemon=True)
    system_thread.start()

    gui_root.mainloop()