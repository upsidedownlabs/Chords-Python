import numpy as np
import time
from pylsl import StreamInlet, resolve_stream
from scipy.signal import find_peaks

# Resolve the LSL stream
print("Looking for an LSL stream...")
streams = resolve_stream('name', 'BioAmpDataStream')  # Assuming the stream type is ECG

# Create an inlet to read from the stream
inlet = StreamInlet(streams[0])

# Function to filter ECG signal (simple bandpass filter)
def filter_signal(signal):
    return signal

# Function to detect heartbeats using peak detection
def detect_heartbeats(ecg_data, sampling_rate):
    filtered_signal = filter_signal(ecg_data)
    
    # Detect peaks (R-peaks in ECG)
    peaks, _ = find_peaks(filtered_signal, distance=sampling_rate * 0.6)  # Assuming minimum 600 ms between heartbeats
    
    return peaks

# Sampling frequency (adjust to your actual stream)
sampling_rate = 250  # Hz (example: 250 samples per second)

# Collect ECG data and detect heartbeats
window_size = sampling_rate * 5  # 5 seconds of data
ecg_buffer = []

while True:
    # Get a new sample from the stream
    sample, timestamp = inlet.pull_sample()
    
    # Append the sample to the buffer
    ecg_buffer.append(sample[0])  # Assuming ECG data is in the first channel
    
    # Keep buffer size fixed
    if len(ecg_buffer) > window_size:
        ecg_buffer = ecg_buffer[-window_size:]
    
    # Detect heartbeats every window
    if len(ecg_buffer) == window_size:
        heartbeats = detect_heartbeats(ecg_buffer, sampling_rate)
        if heartbeats.size > 0:
            print(f"Heartbeats detected at positions: {heartbeats}")
            # Calculate heartbeat rate (bpm)
            rr_intervals = np.diff(heartbeats) / sampling_rate
            bpm = 60 / np.mean(rr_intervals)
            print(f"Heart rate: {bpm:.2f} bpm")
    
    time.sleep(0.01)  # Adjust to control the data rate
