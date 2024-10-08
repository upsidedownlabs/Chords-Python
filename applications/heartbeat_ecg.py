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

        self.ecg_buffer = []
        self.r_peak_times = deque(maxlen=10)  # Deque to store recent R-peak times
        self.peak_intervals = deque(maxlen=9)  # Deque to store intervals between R-peaks

        self.data_collector = DataCollector() # Data collector thread
        self.data_collector.data_ready.connect(self.update_plot)
        self.data_collector.start()

        self.time_axis = np.linspace(0, 2000/200, 2000)       # Store the x-axis time window
        self.plot_widget.setYRange(0,1000)                     # Set fixed y-axis limits 

        # Time to start heart rate calculation after 10 seconds
        self.start_time = time.time()
        self.initial_period = 10  # First 10 seconds to gather enough R-peaks

        self.total_interval_sum = 0  # To track the sum of intervals for efficient heart rate calculation

    def update_plot(self, ecg_data):
        self.ecg_buffer = ecg_data  # Update buffer
        self.plot_widget.clear()

        # Set a fixed window (time axis) to ensure stable plotting
        self.plot_widget.plot(self.time_axis, self.ecg_buffer, pen='#000000')  # Plot ECG data with black line
        self.plot_widget.setXRange(self.time_axis[0], self.time_axis[-1], padding=0)

        heartbeats = detect_heartbeats(np.array(self.ecg_buffer), self.data_collector.sampling_rate)

        for index in heartbeats:
            r_time = index / self.data_collector.sampling_rate
            self.r_peak_times.append(r_time)

            if len(self.r_peak_times) > 1:
                # Calculate the interval between consecutive R-peaks
                new_interval = self.r_peak_times[-1] - self.r_peak_times[-2]

                if len(self.peak_intervals) == self.peak_intervals.maxlen:
                    # Remove the oldest interval from the sum
                    oldest_interval = self.peak_intervals.popleft()
                    self.total_interval_sum -= oldest_interval    #Minus the oldest

                # Add the new interval to the deque and update the sum
                self.peak_intervals.append(new_interval)
                self.total_interval_sum += new_interval     #   Plus the new

        # Plot detected R-peaks
        r_peak_times = self.time_axis[heartbeats]
        r_peak_scatter = pg.ScatterPlotItem(x=r_peak_times, y=self.ecg_buffer[heartbeats],
                                            symbol='o', size=10, pen='r', brush='r')
        self.plot_widget.addItem(r_peak_scatter)

        # Start heart rate calculation after 10 seconds
        if time.time() - self.start_time >= self.initial_period:
            self.update_heart_rate()

    def update_heart_rate(self):
        if len(self.peak_intervals) > 0:
            # Efficiently calculate the heart rate using the sum of intervals
            avg_interval = self.total_interval_sum / len(self.peak_intervals)
            bpm = 60 / avg_interval  # Convert to beats per minute
            self.heart_rate_label.setText(f"Heart rate: {bpm:.2f} bpm")
        else:
            self.heart_rate_label.setText("Heart rate: 0 bpm")

    def closeEvent(self, event):
        self.data_collector.stop()   # Stop the data collector thread on close
        self.data_collector.wait()  # Wait for the thread to finish
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