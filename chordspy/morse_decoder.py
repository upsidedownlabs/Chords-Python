import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi, iirnotch
import pylsl
import sys
import time
from collections import deque
import threading
import tkinter as tk

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
    
        self.morse_buffer = ""            # Output buffer for morse code
        self.min_interblink_gap = 0.1     # 100ms minimum between blinks in a double blink
        self.max_interblink_gap = 0.4     # 400ms maximum between blinks in a double blink
        self.double_blink_cooldown = 1.0  # 1 second cooldown between double blink detections
        self.last_double_blink_time = 0
        self.last_data_time = None
        self.stream_active = True
        self.last_input_time = None       # Track last input time for inactivity
        self.inactivity_timeout = 3.0

        # GUI label and root for updating decoded character
        self.gui_label = gui_label
        self.gui_root = gui_root

        # Accumulated decoded word for GUI
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
        
        # Buffer for EOG data
        self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer
        self.eog_data = np.zeros(self.buffer_size)
        self.filtered_eog_data = np.zeros(self.buffer_size)  # Buffer for filtered EOG data
        self.current_index = 0
        
        # Low-pass filter for blink detection (10 Hz)
        self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')
        self.zi = lfilter_zi(self.b, self.a)
        
        # Circular buffer for detected peaks
        self.detected_peaks = deque(maxlen=self.sampling_rate * 5)
        self.start_time = time.time()
        
        # Left/Right detection parameters
        self.BUFFER_SIZE = 250
        self.BASELINE_SAMPLES = 100
        self.DEVIATION_SIGMA = 8
        self.MIN_MOVEMENT_SAMPLES = 8
        self.COOLDOWN_SAMPLES = 15
        
        # Left/Right data structures
        self.circular_buffer = deque(maxlen=self.BUFFER_SIZE)
        self.baseline = None
        self.baseline_std = None
        self.current_state = "NEUTRAL"
        self.movement_samples = 0
        self.cooldown_counter = 0
        self.last_movement = None
        self.movement_sequence = deque(maxlen=4)
        
        # Filter parameters for left/right detection
        self.NOTCH_FREQ = 50.0
        self.NOTCH_Q = 20.0
        self.BANDPASS_LOW = 1.0
        self.BANDPASS_HIGH = 20.0
        
        # Initialize filters for left/right detection
        self.initialize_filters()
        
        print("Right movement -> Dot (.)")
        print("Left movement -> Dash (-)")
        print("Double blink -> Process morse code and clear buffer")
        print("=" * 50)

    def initialize_filters(self):
        """Initialize filters for left/right detection"""
        self.notch_b, self.notch_a = iirnotch(self.NOTCH_FREQ, self.NOTCH_Q, self.sampling_rate)
        nyq = 0.5 * self.sampling_rate
        low = self.BANDPASS_LOW / nyq
        high = self.BANDPASS_HIGH / nyq
        self.bandpass_b, self.bandpass_a = butter(2, [low, high], btype='band')
        self.filter_state_notch = np.zeros(max(len(self.notch_a), len(self.notch_b)) - 1)
        self.filter_state_bandpass = np.zeros(max(len(self.bandpass_a), len(self.bandpass_b)) - 1)

    def apply_filters(self, sample):
        """Apply notch and bandpass filters to sample"""
        if self.filter_state_notch[0] == -1:
            filtered, self.filter_state_notch = lfilter(self.notch_b, self.notch_a, [sample], zi=None)
        else:
            filtered, self.filter_state_notch = lfilter(self.notch_b, self.notch_a, [sample], zi=self.filter_state_notch)
        
        if self.filter_state_bandpass[0] == -1:
            filtered, self.filter_state_bandpass = lfilter(self.bandpass_b, self.bandpass_a, filtered, zi=None)
        else:
            filtered, self.filter_state_bandpass = lfilter(self.bandpass_b, self.bandpass_a, filtered, zi=self.filter_state_bandpass)
        
        return filtered[0]

    def update_baseline_stats(self):
        """Update baseline statistics for left/right detection"""
        self.baseline = np.median(self.circular_buffer)
        self.baseline_std = np.std(self.circular_buffer)
        print(f"Baseline set: {self.baseline:.2f}μV")

    def get_movement_type(self, current_value):
        """Determine movement type based on current value"""
        deviation = current_value - self.baseline
        threshold = self.DEVIATION_SIGMA * self.baseline_std
        
        if deviation < -threshold:
            return "LEFT"
        elif deviation > threshold:
            return "RIGHT"
        else:
            return "NEUTRAL"

    def check_movement_completion(self):
        """Check if a complete movement sequence has been detected"""
        if len(self.movement_sequence) != 4:
            return False
        
        seq = tuple(self.movement_sequence)
        
        # Right movement -> Dot (.)
        if seq == ("RIGHT", "NEUTRAL", "LEFT", "NEUTRAL"):
            print(".", end="", flush=True)
            self.morse_buffer += "."
            self.movement_sequence.clear()
            self.last_input_time = time.time()  # Update last input time
            return True
        
        # Left movement -> Dash (-)
        if seq == ("LEFT", "NEUTRAL", "RIGHT", "NEUTRAL"):
            print("-", end="", flush=True)
            self.morse_buffer += "-"
            self.movement_sequence.clear()
            self.last_input_time = time.time()  # Update last input time
            return True
        
        self.movement_sequence.popleft()   # If we have 4 elements but no match, clear the oldest one
        return False

    def process_morse_code(self):
        """Process the current morse buffer and convert to character"""
        if self.morse_buffer in self.morse_code:
            character = self.morse_code[self.morse_buffer]
            print(f" -> {character}")
            # Append character to the decoded word and update GUI
            self.decoded_word += character
            self.update_gui(self.decoded_word)
            self.morse_buffer = ""
            self.last_input_time = None  # Reset last input time after decoding
        else:
            # print(f" -> Unknown morse code: {self.morse_buffer}")
            self.morse_buffer = ""
            self.last_input_time = None  # Reset last input time after decoding

    def update_gui(self, text):
        # Update the label in the tkinter window with the decoded word
        if self.gui_label and self.gui_root:
            def set_label():
                self.gui_label.config(text=text)
            self.gui_root.after(0, set_label)

    def detect_peaks(self, signal, threshold):
        """Detect peaks in the signal for blink detection"""
        peaks = []
        prev_peak_time = None
        min_peak_gap = 0.1  # Minimum time gap between two peaks in seconds
        
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
                current_peak_time = i / self.sampling_rate
                if prev_peak_time is not None:
                    time_gap = current_peak_time - prev_peak_time
                    if time_gap < min_peak_gap:
                        continue
                peaks.append(i)
                prev_peak_time = current_peak_time
        
        return peaks

    def detect_blinks(self, filtered_eog):
        """Detect blinks and check for double blinks"""
        mean_signal = np.mean(filtered_eog)
        stdev_signal = np.std(filtered_eog)
        threshold = mean_signal + (1.5 * stdev_signal)
        
        window_size = 1 * self.sampling_rate
        start_index = self.current_index - window_size
        if start_index < 0:
            start_index = 0
        
        end_index = self.current_index
        filtered_window = filtered_eog[start_index:end_index]
        peaks = self.detect_peaks(filtered_window, threshold)
        
        for peak in peaks:
            full_peak_index = start_index + peak
            peak_time = time.time() - (self.current_index - full_peak_index) / self.sampling_rate
            self.detected_peaks.append((full_peak_index, peak_time))
        
        # Double blink detection using actual peak times
        if len(self.detected_peaks) >= 2:
            last_peak_index, last_peak_time = self.detected_peaks[-1]
            prev_peak_index, prev_peak_time = self.detected_peaks[-2]
            time_diff = last_peak_time - prev_peak_time
            
            if (self.min_interblink_gap <= time_diff <= self.max_interblink_gap and 
                time.time() - self.last_double_blink_time > self.double_blink_cooldown):
            
                print("\nDOUBLE BLINK DETECTED!")
                self.process_morse_code()
                self.last_double_blink_time = time.time()

    def run(self):
        try:
            while self.stream_active:
                samples, _ = self.inlet.pull_chunk(timeout=0.1, max_samples=10)
                
                if samples:
                    self.last_data_time = time.time()
                    
                    for sample in samples:
                        # Store data for blink detection (channel 1)
                        self.eog_data[self.current_index] = sample[1]
                        # Filter only the new sample and update filtered_eog_data
                        filtered_sample, self.zi = lfilter(self.b, self.a, [sample[1]], zi=self.zi)
                        self.filtered_eog_data[self.current_index] = filtered_sample[0]
                        self.current_index = (self.current_index + 1) % self.buffer_size
                        
                        # Process for left/right detection (channel 0)
                        filtered_sample_lr = sample[0]  # Using raw signal for left/right
                        self.circular_buffer.append(filtered_sample_lr)
                        
                        # Set baseline for left/right detection
                        if len(self.circular_buffer) == self.BASELINE_SAMPLES and self.baseline is None:
                            self.update_baseline_stats()
                            continue
                        
                        if self.baseline is None:
                            continue
                        
                        # Left/Right movement detection
                        detected_state = self.get_movement_type(filtered_sample_lr)
                        
                        if self.cooldown_counter > 0:
                            self.cooldown_counter -= 1
                            continue
                        
                        # Movement validation
                        if detected_state != "NEUTRAL":
                            if detected_state == self.last_movement or self.last_movement is None:
                                self.movement_samples += 1
                            else:
                                self.movement_samples = 1
                            
                            if self.movement_samples >= self.MIN_MOVEMENT_SAMPLES:
                                if detected_state != self.current_state:
                                    self.movement_sequence.append(detected_state)
                                    self.current_state = detected_state
                                    self.last_movement = detected_state
                                    self.cooldown_counter = self.COOLDOWN_SAMPLES
                                    self.movement_samples = 0
                                    self.check_movement_completion()
                        else:
                            if self.current_state != "NEUTRAL":
                                self.movement_sequence.append("NEUTRAL")
                                self.current_state = "NEUTRAL"
                                self.check_movement_completion()
                            self.movement_samples = 0
                            self.last_movement = None
                    
                    # Blink detection
                    if time.time() - self.start_time >= 2:
                        # Use only the filtered_eog_data buffer
                        self.detect_blinks(self.filtered_eog_data)
                    
                    # Clear out old peaks from the circular buffer
                    current_time = time.time()
                    while self.detected_peaks and (current_time - self.detected_peaks[0][1] > 4):
                        self.detected_peaks.popleft()
                
                else:
                    if self.last_data_time and (time.time() - self.last_data_time) > 2:
                        self.stream_active = False
                        print("LSL stream disconnected!")
                if self.morse_buffer and self.last_input_time:
                    if time.time() - self.last_input_time > self.inactivity_timeout:
                        print(f"\nBuffer timeout. Clearing morse buffer: {self.morse_buffer}")
                        self.morse_buffer = ""
                        self.last_input_time = None
                        
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