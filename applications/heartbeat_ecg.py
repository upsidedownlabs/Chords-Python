# import numpy as np
# from scipy.signal import butter, filtfilt
# from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QMainWindow, QWidget
# from PyQt5.QtCore import Qt
# from pyqtgraph import PlotWidget
# import pyqtgraph as pg
# import pylsl
# import neurokit2 as nk
# from collections import deque
# import sys

# class ECGMonitor(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # Set up GUI window
#         self.setWindowTitle("Real-Time ECG Monitor")
#         self.setGeometry(100, 100, 800, 600)
        
#         self.plot_widget = PlotWidget(self)
#         self.plot_widget.setBackground('w')
#         self.plot_widget.showGrid(x=True, y=True)
        
#         # Add a label to display the heart rate in bold at the bottom center
#         self.heart_rate_label = QLabel(self)
#         self.heart_rate_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
#         self.heart_rate_label.setAlignment(Qt.AlignCenter)
        
#         layout = QVBoxLayout()
#         layout.addWidget(self.plot_widget)
#         layout.addWidget(self.heart_rate_label)

#         central_widget = QWidget()
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#         # Set up LSL stream inlet
#         print("Looking for an ECG stream...")
#         streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
#         if not streams:
#             print("No LSL stream found!")
#             sys.exit(0)
#         self.inlet = pylsl.StreamInlet(streams[0])

#         # Sampling rate
#         self.sampling_rate = self.inlet.info().nominal_srate()
#         if self.sampling_rate == pylsl.IRREGULAR_RATE:
#             print("Irregular sampling rate detected!")
#             sys.exit(0)
#         print(f"Sampling rate: {self.sampling_rate} Hz")

#         self.sampling_rate = int(self.sampling_rate)     #Conversion into int
#         # Data and buffers
#         self.ecg_data = deque(maxlen=self.sampling_rate * 10)   # 10 seconds of data at 250/500 Hz
#         self.time_data = deque(maxlen=self.sampling_rate * 10)  #Sampling rate - 250/500
#         self.r_peaks = []
#         self.heart_rate = None

#         # Timer for updating the GUI
#         self.timer = pg.QtCore.QTimer()
#         self.timer.timeout.connect(self.update_plot)
#         self.timer.start(10)  # Update every 10 ms

#         # Low-pass filter coefficients
#         self.b, self.a = butter(4, 20.0 / (0.5 * self.sampling_rate), btype='low')

#         # Plot configuration
#         self.plot_window = 10  # Plot window of 10 seconds
#         self.buffer_size = self.plot_window * self.sampling_rate  # 10 seconds at 250/500 Hz sampling rate

#         # Set y-axis limits based on sampling rate
#         if self.sampling_rate == 250:  
#             self.plot_widget.setYRange(0, 2**10)  #for R3
#         elif self.sampling_rate == 500:  
#             self.plot_widget.setYRange(0, 2**14)  #for R4

#     def update_plot(self):
#         samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=32)
#         if samples:
#             for sample, timestamp in zip(samples, timestamps):
#                 self.ecg_data.append(sample[0])
#                 self.time_data.append(timestamp)

#             # Convert deque to numpy array for processing
#             ecg_array = np.array(self.ecg_data)
#             filtered_ecg = filtfilt(self.b, self.a, ecg_array)   # Apply low-pass filter
#             self.r_peaks = self.detect_r_peaks(filtered_ecg)     # Detect R-peaks using NeuroKit2
#             self.calculate_heart_rate()                          # Calculate heart rate

#             # Update plot immediately with whatever data is available
#             self.plot_widget.clear()
#             current_time = np.linspace(0, len(ecg_array)/self.sampling_rate, len(ecg_array))
#             self.plot_widget.setXRange(0, self.plot_window)  # Fixed x-axis range
#             self.plot_widget.plot(current_time, filtered_ecg, pen=pg.mkPen('k', width=1))

#             # Mark R-peaks on the plot
#             if len(self.r_peaks) > 0:
#                 self.plot_widget.plot(current_time[self.r_peaks], filtered_ecg[self.r_peaks], pen=None, symbol='o', symbolBrush='r')

#             # Update heart rate display
#             if self.heart_rate:
#                 self.heart_rate_label.setText(f"Heart Rate: {int(self.heart_rate)} BPM")
#             else:
#                 self.heart_rate_label.setText("Heart Rate: Calculating...")
#         else:
#             self.heart_rate_label.setText("Heart Rate: Collecting data...")

#     def detect_r_peaks(self, ecg_signal):
#         # Using NeuroKit2 to detect R-peaks
#         r_peaks = nk.ecg_findpeaks(ecg_signal, sampling_rate=self.sampling_rate)

#         if 'ECG_R_Peaks' in r_peaks:
#             return r_peaks['ECG_R_Peaks']
#         else:
#             print("No R-peaks detected. Please check the input ECG signal.")
#             return []

#     def calculate_heart_rate(self):
#         if len(self.r_peaks) > 1:
#             peak_times = np.array([self.time_data[i] for i in self.r_peaks])
#             rr_intervals = np.diff(peak_times)
#             avg_rr_interval = np.mean(rr_intervals)
#             self.heart_rate = 60.0 / avg_rr_interval
#         else:
#             self.heart_rate = None

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ECGMonitor()
#     window.show()
#     sys.exit(app.exec_())



# Updated Holter monitor
import numpy as np
from scipy.signal import butter, filtfilt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import neurokit2 as nk
import sys

class ECGMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up GUI window
        self.setWindowTitle("Real-Time ECG Monitor")
        self.setGeometry(100, 100, 800, 600)

        self.plot_widget = PlotWidget(self)
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)

        # Heart rate label at the bottom
        self.heart_rate_label = QLabel(self)
        self.heart_rate_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        self.heart_rate_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.heart_rate_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set up LSL stream inlet
        streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
        if not streams:
            print("No LSL stream found!")
            sys.exit(0)
        self.inlet = pylsl.StreamInlet(streams[0])

        # Sampling rate
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")
        
        # Data and buffers
        self.buffer_size = self.sampling_rate * 10  # Fixed-size buffer for 10 seconds
        self.ecg_data = np.zeros(self.buffer_size)  # Fixed-size array for circular buffer
        self.time_data = np.linspace(0, 10, self.buffer_size)  # Fixed time array for plotting
        self.r_peaks = []  # Store the indices of R-peaks
        self.heart_rate = None
        self.current_index = 0  # Index for overwriting data

        # Low-pass filter coefficients
        self.b, self.a = butter(4, 20.0 / (0.5 * self.sampling_rate), btype='low')

        # Timer for updating the plot
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)

        # Set y-axis limits based on sampling rate
        if self.sampling_rate == 250:  
            self.plot_widget.setYRange(0, 2**10)  # for R3
        elif self.sampling_rate == 500:  
            self.plot_widget.setYRange(0, 2**14)  # for R4 

        # Set fixed x-axis range
        self.plot_widget.setXRange(0, 10)  # 10 seconds

        # Initialize the plot curves
        self.ecg_curve = self.plot_widget.plot(self.time_data, self.ecg_data, pen=pg.mkPen('k', width=1))
        self.r_peak_curve = self.plot_widget.plot([], [], pen=None, symbol='o', symbolBrush='r', symbolSize=10)  # R-peaks in red

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=32)
        if samples:
            for sample in samples:
                # Overwrite the oldest data point in the buffer
                self.ecg_data[self.current_index] = sample[0]
                self.current_index = (self.current_index + 1) % self.buffer_size  # Circular increment

            # Filter the signal
            filtered_ecg = filtfilt(self.b, self.a, self.ecg_data)

            # Update the plot data
            self.ecg_curve.setData(self.time_data, filtered_ecg)  # Use current buffer for plotting

            # Detect R-peaks and update heart rate
            self.r_peaks = self.detect_r_peaks(filtered_ecg)
            self.calculate_heart_rate()
            self.plot_r_peaks(filtered_ecg)

    def detect_r_peaks(self, ecg_signal):
        r_peaks = nk.ecg_findpeaks(ecg_signal, sampling_rate=self.sampling_rate)
        return r_peaks['ECG_R_Peaks'] if 'ECG_R_Peaks' in r_peaks else []

    def calculate_heart_rate(self):
        # Ensure there are enough R-peaks and at least 10 seconds of data before calculating heart rate
        if len(self.r_peaks) > 1 and self.current_index == 0:  # Buffer is full (10 seconds)
            rr_intervals = np.diff([self.time_data[i] for i in self.r_peaks])
            if len(rr_intervals) > 0:
                avg_rr = np.mean(rr_intervals)
                self.heart_rate = 60.0 / avg_rr
                self.heart_rate_label.setText(f"Heart Rate: {int(self.heart_rate)} BPM")
            else:
                self.heart_rate_label.setText("Heart Rate: Calculating...")
        elif len(self.r_peaks) > 1:  # After initial 10 seconds, keep updating with new R-peaks
            rr_intervals = np.diff([self.time_data[i] for i in self.r_peaks[-2:]])  # Last two R-peaks for instant HR
            if len(rr_intervals) > 0:
                avg_rr = np.mean(rr_intervals)
                self.heart_rate = 60.0 / avg_rr
                self.heart_rate_label.setText(f"Heart Rate: {int(self.heart_rate)} BPM")
            else:
                self.heart_rate_label.setText("Heart Rate: Calculating...")
        else:
            self.heart_rate_label.setText("Heart Rate: Calculating...")

    def plot_r_peaks(self, filtered_ecg):
        # Extract the time of detected R-peaks
        r_peak_times = self.time_data[self.r_peaks]
        r_peak_values = filtered_ecg[self.r_peaks]
        self.r_peak_curve.setData(r_peak_times, r_peak_values)  # Plot R-peaks as red dots

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ECGMonitor()
    window.show()
    sys.exit(app.exec_())




#final one -- need to be tested
# import numpy as np
# from scipy.signal import butter, filtfilt
# from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QMainWindow, QWidget
# from PyQt5.QtCore import Qt
# from pyqtgraph import PlotWidget
# import pyqtgraph as pg
# import pylsl
# import neurokit2 as nk
# import sys

# class ECGMonitor(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # Set up GUI window
#         self.setWindowTitle("Real-Time ECG Monitor")
#         self.setGeometry(100, 100, 800, 600)

#         self.plot_widget = PlotWidget(self)
#         self.plot_widget.setBackground('w')
#         self.plot_widget.showGrid(x=True, y=True)

#         # Heart rate label at the bottom
#         self.heart_rate_label = QLabel(self)
#         self.heart_rate_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
#         self.heart_rate_label.setAlignment(Qt.AlignCenter)

#         layout = QVBoxLayout()
#         layout.addWidget(self.plot_widget)
#         layout.addWidget(self.heart_rate_label)

#         central_widget = QWidget()
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#         # Set up LSL stream inlet
#         streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
#         if not streams:
#             print("No LSL stream found!")
#             sys.exit(0)
#         self.inlet = pylsl.StreamInlet(streams[0])

#         # Sampling rate
#         self.sampling_rate = int(self.inlet.info().nominal_srate())
#         print(f"Sampling rate: {self.sampling_rate} Hz")
        
#         # Data and buffers
#         self.buffer_size = self.sampling_rate * 10  # Fixed-size buffer for 10 seconds
#         self.ecg_data = np.zeros(self.buffer_size)  # Fixed-size array for circular buffer
#         self.time_data = np.linspace(0, 10, self.buffer_size)  # Fixed time array for plotting
#         self.r_peaks = []  # Store the indices of R-peaks
#         self.heart_rate = None
#         self.current_index = 0  # Index for overwriting data

#         # Low-pass filter coefficients
#         self.b, self.a = butter(4, 20.0 / (0.5 * self.sampling_rate), btype='low')

#         # Timer for updating the plot
#         self.timer = pg.QtCore.QTimer()
#         self.timer.timeout.connect(self.update_plot)
#         self.timer.start(10)

#         # Set y-axis limits based on sampling rate
#         if self.sampling_rate == 250:  
#             self.plot_widget.setYRange(0, 2**10)  # for R3
#         elif self.sampling_rate == 500:  
#             self.plot_widget.setYRange(0, 2**14)  # for R4 

#         # Set fixed x-axis range
#         self.plot_widget.setXRange(0, 10)  # 10 seconds

#         # Initialize the plot curves
#         self.ecg_curve = self.plot_widget.plot(self.time_data, self.ecg_data, pen=pg.mkPen('k', width=1))
#         self.r_peak_curve = self.plot_widget.plot([], [], pen=None, symbol='o', symbolBrush='r', symbolSize=10)  # R-peaks in red

    #  def update_plot(self):
    #     samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=32)
    #     if samples:
    #         for sample in samples:
    #             # Overwrite the oldest data point in the buffer
    #             self.ecg_data[self.current_index] = sample[0]
    #             self.current_index = (self.current_index + 1) % self.buffer_size  # Circular increment

    #         # Filter the signal
    #         filtered_ecg = filtfilt(self.b, self.a, self.ecg_data)

    #         # Update the plot data
    #         self.ecg_curve.setData(self.time_data, filtered_ecg)  # Use current buffer for plotting

    #         # Detect R-peaks and update heart rate
    #         self.r_peaks = self.detect_r_peaks(filtered_ecg)

    #         # Only calculate heart rate after the first 10 seconds
    #         if self.current_index >= self.buffer_size - self.sampling_rate * 10:
    #             self.calculate_heart_rate()

    #         # Plot R-peaks
    #         self.plot_r_peaks(filtered_ecg)

#     def detect_r_peaks(self, ecg_signal):
#         r_peaks = nk.ecg_findpeaks(ecg_signal, sampling_rate=self.sampling_rate)
#         return r_peaks['ECG_R_Peaks'] if 'ECG_R_Peaks' in r_peaks else []

    # def calculate_heart_rate(self):
    #     # Calculate heart rate only if there are enough R-peaks
    #     if len(self.r_peaks) > 1:
    #         rr_intervals = np.diff([self.time_data[i] for i in self.r_peaks])
    #         avg_rr = np.mean(rr_intervals)
    #         self.heart_rate = 60.0 / avg_rr
    #         self.heart_rate_label.setText(f"Heart Rate: {int(self.heart_rate)} BPM")
    #     else:
    #         self.heart_rate_label.setText("Heart Rate: Calculating...")

#     def plot_r_peaks(self, filtered_ecg):
#         # Extract the time of detected R-peaks
#         r_peak_times = self.time_data[self.r_peaks]
#         r_peak_values = filtered_ecg[self.r_peaks]
#         self.r_peak_curve.setData(r_peak_times, r_peak_values)  # Plot R-peaks as red dots

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ECGMonitor()
#     window.show()
#     sys.exit(app.exec_())