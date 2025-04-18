import numpy as np
from scipy.signal import butter, filtfilt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import neurokit2 as nk
import sys
import time

class ECGMonitor(QMainWindow):
    def __init__(self): 
        super().__init__()

        self.setWindowTitle("Real-Time ECG Monitor")  # Set up GUI window
        self.setGeometry(100, 100, 800, 600)

        self.stream_active = True                     # Flag to check if the stream is active
        self.last_data_time = None                    # Variable to store the last data time

        self.plot_widget = PlotWidget(self)           # Create the plotting widget
        self.plot_widget.setBackground('w')           # Set background color to white
        self.plot_widget.showGrid(x=True, y=True)     # Show grid lines

        # Heart rate label at the bottom
        self.heart_rate_label = QLabel(self)
        self.heart_rate_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        self.heart_rate_label.setAlignment(Qt.AlignCenter)

        # Layout setup - vertical layout for plot and label
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.heart_rate_label)

        # Set the central widget that holds all other widgets
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set up LSL stream inlet
        print("Searching for available LSL streams...")
        available_streams = pylsl.resolve_streams()

        # Exit if no streams are found
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

        # Get Sampling rate from the stream info.
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")
        
        # Data and buffers
        self.buffer_size = self.sampling_rate * 10  # Fixed-size buffer for 10 seconds
        self.ecg_data = np.zeros(self.buffer_size)  # Fixed-size array for circular buffer
        self.time_data = np.linspace(0, 10, self.buffer_size)  # Fixed time array for plotting
        self.r_peaks = []       # Store the indices of R-peaks
        self.heart_rate = None  # Initialize heart rate variable
        self.current_index = 0  # Index for overwriting data

        self.b, self.a = butter(4, 20.0 / (0.5 * self.sampling_rate), btype='low')   # Low-pass filter coefficients

        self.timer = pg.QtCore.QTimer()   # Timer for updating the plot (every 10 ms)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)

        # Set y-axis limits based on sampling rate
        if self.sampling_rate == 250:  
            self.plot_widget.setYRange(0, 2**10,padding=0)  # for R3 & ensuring no extra spaces at end
        elif self.sampling_rate == 500:  
            self.plot_widget.setYRange(0, 2**14,padding=0)  # for R4 & ensuring no extra spaces at end

        # Set fixed x-axis range
        self.plot_widget.setXRange(0, 10,padding=0)  # ensure no extra spaces

        self.ecg_curve = self.plot_widget.plot(self.time_data, self.ecg_data, pen=pg.mkPen('k', width=1))
        self.r_peak_curve = self.plot_widget.plot([], [], pen=None, symbol='o', symbolBrush='r', symbolSize=10)  # R-peaks in red
        
        self.moving_average_window_size = 5   # Initialize moving average buffer
        self.heart_rate_history = []          # Buffer to store heart rates for moving average

        # Connect double-click event for zoom reset
        self.plot_widget.scene().sigMouseClicked.connect(self.on_double_click)

    def on_double_click(self, event):
        if event.double():
            self.reset_zoom()

    def reset_zoom(self):
        # Reset to default y-axis limits based on the sampling rate
        if self.sampling_rate == 250:  
            self.plot_widget.setYRange(0, 2**10, padding=0)
        elif self.sampling_rate == 500:  
            self.plot_widget.setYRange(0, 2**14, padding=0)
        self.plot_widget.setXRange(0, 10, padding=0)

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
        if samples:
            self.last_data_time = time.time()         # Update last data time
            for sample in samples:
                # Overwrite the oldest data point in the buffer
                self.ecg_data[self.current_index] = sample[0]
                self.current_index = (self.current_index + 1) % self.buffer_size  # Circular increment

            filtered_ecg = filtfilt(self.b, self.a, self.ecg_data) # Filter the signal

            self.ecg_curve.setData(self.time_data, filtered_ecg)  # Use current buffer for plotting

            # Detect R-peaks and update heart rate
            self.r_peaks = self.detect_r_peaks(filtered_ecg)
            self.calculate_heart_rate()
            self.plot_r_peaks(filtered_ecg)
        else:
            if self.last_data_time and (time.time() - self.last_data_time) > 2:
                self.stream_active = False           # Set stream active to false
                print("LSL stream disconnected!")
                self.timer.stop()                    # Stop the timer
                self.close()                         # Close the application

    def detect_r_peaks(self, ecg_signal):
        r_peaks = nk.ecg_findpeaks(ecg_signal, sampling_rate=self.sampling_rate)
        return r_peaks['ECG_R_Peaks'] if 'ECG_R_Peaks' in r_peaks else []

    def calculate_heart_rate(self):
        if len(self.r_peaks) >= 10:  # Check if we have 10 or more R-peaks
            recent_r_peaks = self.r_peaks[-10:]  # Use the last 10 R-peaks for heart rate calculation
            rr_intervals = np.diff([self.time_data[i] for i in recent_r_peaks])  # Calculate RR intervals (time differences between consecutive R-peaks)
            if len(rr_intervals) > 0:
                avg_rr = np.mean(rr_intervals)  # Average RR interval
                self.heart_rate = 60.0 / avg_rr  # Convert to heart rate (BPM)
                self.heart_rate_history.append(self.heart_rate)   # Update moving average
                if len(self.heart_rate_history) > self.moving_average_window_size:
                    self.heart_rate_history.pop(0)  # Remove the oldest heart rate 
                
                # Calculate the moving average heart rate
                moving_average_hr = np.mean(self.heart_rate_history)
                
                # Update heart rate label with moving average & convert into int
                self.heart_rate_label.setText(f"Heart Rate: {int(moving_average_hr)} BPM")
        else:
            self.heart_rate_label.setText("Heart Rate: Calculating...")   # Display message if not enough R-peaks detected

    def plot_r_peaks(self, filtered_ecg):
        r_peak_times = self.time_data[self.r_peaks]             # Extract the time of detected R-peaks
        r_peak_values = filtered_ecg[self.r_peaks]              # Get corresponding ECG values
        self.r_peak_curve.setData(r_peak_times, r_peak_values)  # Plot R-peaks as red dots

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ECGMonitor()  
    window.show()
    sys.exit(app.exec_())    