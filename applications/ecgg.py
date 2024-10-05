# import sys
# import numpy as np
# import time
# from pylsl import StreamInlet, resolve_stream
# from scipy.signal import butter, lfilter, find_peaks
# import pyqtgraph as pg  # For real-time plotting
# from pyqtgraph.Qt import QtWidgets, QtCore  # PyQt components for GUI
# import signal  # For handling Ctrl+C
# from collections import deque  # For creating a ring buffer

# # Initialize global variables
# inlet = None
# data_buffer = np.zeros(2000)  # Buffer to hold the last 2000 samples for ECG data

# # Function to design a Butterworth filter
# def butter_filter(cutoff, fs, order=4, btype='low'):
#     nyquist = 0.5 * fs  # Nyquist frequency
#     normal_cutoff = cutoff / nyquist
#     b, a = butter(order, normal_cutoff, btype=btype, analog=False)
#     return b, a

# # Apply the Butterworth filter to the data
# def apply_filter(data, b, a):
#     return lfilter(b, a, data)

# # Function to detect heartbeats using peak detection
# def detect_heartbeats(ecg_data, sampling_rate):
#     peaks, _ = find_peaks(ecg_data, distance=sampling_rate * 0.6, prominence=0.5)  # Adjust as necessary
#     return peaks

# class DataCollector(QtCore.QThread):
#     data_ready = QtCore.pyqtSignal(np.ndarray)

#     def __init__(self):
#         super().__init__()
#         self.running = True
#         self.sampling_rate = None

#     def run(self):
#         global inlet
#         print("Looking for LSL stream...")
#         streams = resolve_stream('name', 'BioAmpDataStream')
        
#         if not streams:
#             print("No LSL Stream found! Exiting...")
#             sys.exit(0)

#         inlet = StreamInlet(streams[0])
#         self.sampling_rate = inlet.info().nominal_srate()
#         print(f"Detected sampling rate: {self.sampling_rate} Hz")

#         # Create and design filters
#         low_cutoff = 20.0  # 20 Hz low-pass filter
#         self.low_b, self.low_a = butter_filter(low_cutoff, self.sampling_rate, order=4, btype='low')

#         while self.running:
#             # Pull multiple samples at once
#             samples, _ = inlet.pull_chunk(timeout=0.0, max_samples=10)  # Pull up to 10 samples
#             if samples:
#                 global data_buffer
#                 data_buffer = np.roll(data_buffer, -len(samples))  # Shift data left
#                 data_buffer[-len(samples):] = [sample[0] for sample in samples]  # Add new samples to the end

#                 filtered_data = apply_filter(data_buffer, self.low_b, self.low_a)   # Low-pass Filter
#                 self.data_ready.emit(filtered_data)  # Emit the filtered data for plotting

#             time.sleep(0.01)

#     def stop(self):
#         self.running = False

# class ECGApp(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # Create a plot widget
#         self.plot_widget = pg.PlotWidget(title="ECG Signal")
#         self.setCentralWidget(self.plot_widget)
#         self.plot_widget.setBackground('w')

#         # Create a label to display heart rate
#         self.heart_rate_label = QtWidgets.QLabel("Heart rate: - bpm", self)
#         self.heart_rate_label.setStyleSheet("font-size: 20px; font-weight: bold;")
#         self.heart_rate_label.setAlignment(QtCore.Qt.AlignCenter)

#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(self.plot_widget)
#         layout.addWidget(self.heart_rate_label)

#         container = QtWidgets.QWidget()
#         container.setLayout(layout)
#         self.setCentralWidget(container)

#         self.ecg_buffer = []    # Buffer to hold the ECG data
#         self.r_peak_times = deque(maxlen=10)  # Store up to 20 R-peaks 
#         self.last_update_time = time.time()

#         self.data_collector = DataCollector()  # Data collector thread
#         self.data_collector.data_ready.connect(self.update_plot)
#         self.data_collector.start()

#         self.time_axis = np.linspace(0, 2000 / 200, 2000)  # Store the x-axis time window
#         self.plot_widget.setYRange(0, 700)  # Set fixed y-axis limits 

#     def update_plot(self, ecg_data):
#         self.ecg_buffer = ecg_data  # Update buffer
#         self.plot_widget.clear()
#         # Set a fixed window (time axis) to ensure stable plotting
#         self.plot_widget.plot(self.time_axis, self.ecg_buffer, pen='#000000')  # Plot ECG data with black line
#         self.plot_widget.setXRange(self.time_axis[0], self.time_axis[-1], padding=0)

#         # Detect heartbeats in real time
#         heartbeats = detect_heartbeats(np.array(self.ecg_buffer), self.data_collector.sampling_rate)

#         # Mark detected R-peaks
#         for index in heartbeats:
#             time_point = index / self.data_collector.sampling_rate  # Convert index to time
#             self.r_peak_times.append(time_point)  # Store the time of the detected R-peak

#             # Plot a red circle at the R-peak position
#             self.plot_widget.plot([self.time_axis[index]], [self.ecg_buffer[index]], pen=None, symbol='o', symbolBrush='r', symbolSize=8)

#         self.calculate_heart_rate()  # Calculate heart rate after detecting R-peaks

#     def calculate_heart_rate(self):
#         current_time = time.time()
#         if current_time - self.last_update_time >= 10:  # Update every 10 seconds
#             if len(self.r_peak_times) > 1:
#                 # Calculate the time intervals between successive R-peaks
#                 intervals = np.diff(self.r_peak_times)
#                 valid_intervals = intervals[intervals > 0]  # Filter positive intervals

#                 if len(valid_intervals) > 0:
#                     bpm = 60 / np.mean(valid_intervals)  # Mean interval is in seconds, converting to bpm
#                     self.heart_rate_label.setText(f"Heart rate: {bpm:.2f} bpm")
#                 else:
#                     self.heart_rate_label.setText("Heart rate: 0 bpm")
#             else:
#                 self.heart_rate_label.setText("Heart rate: 0 bpm")
            
#             self.r_peak_times.clear()  # Clear the deque after calculation
#             self.last_update_time = current_time  # Update last update time

#     def closeEvent(self, event):
#         self.data_collector.stop()   # Stop the data collector thread on close
#         self.data_collector.wait()  # Wait for the thread to finish
#         event.accept()  # Accept the close event

# def signal_handler(sig, frame):
#     print("Exiting...")
#     QtWidgets.QApplication.quit()

# if __name__ == "__main__":
#     signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

#     streams = resolve_stream('name', 'BioAmpDataStream')
#     if not streams:
#         print("No LSL Stream found! Exiting...")
#         sys.exit(0)

#     app = QtWidgets.QApplication(sys.argv)
    
#     window = ECGApp()
#     window.setWindowTitle("Real-Time ECG Monitoring")
#     window.resize(800, 600)
#     window.show()

#     sys.exit(app.exec_())

import sys
import numpy as np
import time
from pylsl import StreamInlet, resolve_stream
from scipy.signal import butter, lfilter, find_peaks
import pyqtgraph as pg  # For real-time plotting
from pyqtgraph.Qt import QtWidgets, QtCore  # PyQt components for GUI
import signal  # For handling Ctrl+C
from collections import deque  # For creating a ring buffer

# Initialize global variables
inlet = None
data_buffer = np.zeros(2000)  # Buffer to hold the last 2000 samples for ECG data

# Function to design a Butterworth filter
def butter_filter(cutoff, fs, order=4, btype='low'):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return b, a

# Apply the Butterworth filter to the data
def apply_filter(data, b, a):
    return lfilter(b, a, data)

# Function to detect heartbeats using peak detection
def detect_heartbeats(ecg_data, sampling_rate):
    peaks, _ = find_peaks(ecg_data, distance=sampling_rate * 0.6, prominence=0.5)  # Adjust as necessary
    return peaks

class DataCollector(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = True
        self.sampling_rate = None

    def run(self):
        global inlet
        print("Looking for LSL stream...")
        streams = resolve_stream('name', 'BioAmpDataStream')
        
        if not streams:
            print("No LSL Stream found! Exiting...")
            sys.exit(0)

        inlet = StreamInlet(streams[0])
        self.sampling_rate = inlet.info().nominal_srate()
        print(f"Detected sampling rate: {self.sampling_rate} Hz")

        # Create and design filters
        low_cutoff = 20.0  # 20 Hz low-pass filter
        self.low_b, self.low_a = butter_filter(low_cutoff, self.sampling_rate, order=4, btype='low')

        while self.running:
            # Pull multiple samples at once
            samples, _ = inlet.pull_chunk(timeout=0.0, max_samples=10)  # Pull up to 10 samples
            if samples:
                global data_buffer
                data_buffer = np.roll(data_buffer, -len(samples))  # Shift data left
                data_buffer[-len(samples):] = [sample[0] for sample in samples]  # Add new samples to the end

                filtered_data = apply_filter(data_buffer, self.low_b, self.low_a)   # Low-pass Filter
                self.data_ready.emit(filtered_data)  # Emit the filtered data for plotting

            time.sleep(0.01)

    def stop(self):
        self.running = False

class HeartRateCalculator(QtCore.QThread):
    heart_rate_ready = QtCore.pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.running = True
        self.r_peak_times = deque(maxlen=20)  # Store R-peaks times
        self.last_update_time = time.time()

    def run(self):
        while self.running:
            time.sleep(1)  # Check every second
            current_time = time.time()

            if current_time - self.last_update_time >= 10:  # Calculate heart rate every 10 seconds
                if len(self.r_peak_times) > 1:
                    # Calculate the time intervals between successive R-peaks
                    intervals = np.diff(self.r_peak_times)
                    valid_intervals = intervals[intervals > 0]  # Filter positive intervals

                    if len(valid_intervals) > 0:
                        bpm = 60 / np.mean(valid_intervals)  # Mean interval is in seconds, converting to bpm
                        self.heart_rate_ready.emit(bpm)
                    else:
                        self.heart_rate_ready.emit(0)  # No valid intervals, heart rate is 0
                else:
                    self.heart_rate_ready.emit(0)  # Not enough R-peaks to calculate heart rate
                
                self.r_peak_times.clear()  # Clear R-peaks after calculation
                self.last_update_time = current_time  # Update last update time

    def add_r_peak_time(self, time):
        self.r_peak_times.append(time)  # Add R-peak time to the deque

    def stop(self):
        self.running = False

class ECGApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a plot widget
        self.plot_widget = pg.PlotWidget(title="ECG Signal")
        self.setCentralWidget(self.plot_widget)
        self.plot_widget.setBackground('w')

        # Create a label to display heart rate
        self.heart_rate_label = QtWidgets.QLabel("Heart rate: - bpm", self)
        self.heart_rate_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.heart_rate_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.heart_rate_label)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.ecg_buffer = []    # Buffer to hold the ECG data

        self.data_collector = DataCollector()  # Data collector thread
        self.data_collector.data_ready.connect(self.update_plot)
        self.data_collector.start()

        self.heart_rate_calculator = HeartRateCalculator()  # Heart rate calculation thread
        self.heart_rate_calculator.start()
        self.heart_rate_calculator.heart_rate_ready.connect(self.update_heart_rate)

        self.time_axis = np.linspace(0, 2000 / 200, 2000)  # Store the x-axis time window
        self.plot_widget.setYRange(0, 700)  # Set fixed y-axis limits 

    def update_plot(self, ecg_data):
        self.ecg_buffer = ecg_data  # Update buffer
        self.plot_widget.clear()
        # Set a fixed window (time axis) to ensure stable plotting
        self.plot_widget.plot(self.time_axis, self.ecg_buffer, pen='#000000')  # Plot ECG data with black line
        self.plot_widget.setXRange(self.time_axis[0], self.time_axis[-1], padding=0)

        # Detect heartbeats in real time
        heartbeats = detect_heartbeats(np.array(self.ecg_buffer), self.data_collector.sampling_rate)

        # Mark detected R-peaks and store in HeartRateCalculator
        for index in heartbeats:
            time_point = index / self.data_collector.sampling_rate  # Convert index to time
            self.heart_rate_calculator.add_r_peak_time(time_point)  # Store the time of the detected R-peak

            # Plot a red circle at the R-peak position
            self.plot_widget.plot([self.time_axis[index]], [self.ecg_buffer[index]], pen=None, symbol='o', symbolBrush='r', symbolSize=8)

    def update_heart_rate(self, bpm):
        if bpm > 0:
            self.heart_rate_label.setText(f"Heart rate: {bpm:.2f} bpm")
        else:
            self.heart_rate_label.setText("Heart rate: 0 bpm")

    def closeEvent(self, event):
        self.data_collector.stop()   # Stop the data collector thread on close
        self.data_collector.wait()  # Wait for the thread to finish
        self.heart_rate_calculator.stop()  # Stop the heart rate calculator
        self.heart_rate_calculator.wait()  # Wait for the thread to finish
        event.accept()  # Accept the close event

def signal_handler(sig, frame):
    print("Exiting...")
    QtWidgets.QApplication.quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

    streams = resolve_stream('name', 'BioAmpDataStream')
    if not streams:
        print("No LSL Stream found! Exiting...")
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    
    window = ECGApp()
    window.setWindowTitle("Real-Time ECG Monitoring")
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec_())