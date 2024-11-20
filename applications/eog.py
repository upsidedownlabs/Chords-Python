# import numpy as np
# from scipy.signal import butter, filtfilt
# from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout
# import pyqtgraph as pg
# import pylsl
# import sys

# class EOGMonitor(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Real-Time EOG Monitor - Eye Blink Detection")
#         self.setGeometry(100, 100, 800, 400)

#         # Create layout
#         layout = QVBoxLayout()
#         central_widget = QWidget()
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#         # Create plot widget for EOG
#         self.eog_plot = pg.PlotWidget(self)
#         self.eog_plot.setBackground('w')
#         self.eog_plot.showGrid(x=True, y=True)
#         self.eog_plot.setTitle("Filtered EOG Signal (Low Pass: 10 Hz)")

#         # Bottom layout for Blink Detection
#         self.bottom_layout = QHBoxLayout()

#         # Blink detection plot
#         self.blink_plot = pg.PlotWidget(self)
#         self.blink_plot.setBackground('w')
#         self.blink_plot.showGrid(x=True, y=True)
#         self.blink_plot.setYRange(0, 1, padding=0)
#         self.blink_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
#         self.blink_plot.setTitle("Blink Detection")

#         # Add both plots to the layout
#         layout.addWidget(self.eog_plot)
#         layout.addWidget(self.blink_plot)

#         # Set up LSL stream inlet
#         streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
#         if not streams:
#             print("No LSL stream found!")
#             sys.exit(0)
#         self.inlet = pylsl.StreamInlet(streams[0])

#         self.sampling_rate = int(self.inlet.info().nominal_srate())
#         print(f"Sampling rate: {self.sampling_rate} Hz")

#         self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
#         self.eog_data = np.zeros(self.buffer_size)
#         self.time_data = np.linspace(0, 5, self.buffer_size)
#         self.blink_data = np.zeros(self.buffer_size)  # Blink data array
#         self.current_index = 0

#         # Low-pass filter for EOG (10 Hz)
#         self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')

#         self.eog_plot.setXRange(0, 5, padding=0)
#         if self.sampling_rate == 250:
#             self.eog_plot.setYRange(-((2**10)/2), ((2**10)/2), padding=0)
#         elif self.sampling_rate == 500:
#             self.eog_plot.setYRange(-((2**14)/2), ((2**14)/2), padding=0)

#         # Plot curves
#         self.eog_curve = self.eog_plot.plot(self.time_data, self.eog_data, pen=pg.mkPen('b', width=1))
#         self.blink_curve = self.blink_plot.plot(self.time_data, self.blink_data, pen=pg.mkPen('r', width=2))

#         # Timer for plot update
#         self.timer = pg.QtCore.QTimer()
#         self.timer.timeout.connect(self.update_plot)
#         self.timer.start(15)

#     def update_plot(self):
#         samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
#         if samples:
#             for sample in samples:
#                 # Overwrite the oldest data point in the buffer
#                 self.eog_data[self.current_index] = sample[0]
#                 self.current_index = (self.current_index + 1) % self.buffer_size

#             filtered_eog = filtfilt(self.b, self.a, self.eog_data)

#             # Update curve with the filtered EOG signal (5-second window)
#             self.eog_plot.clear()    # Clear the previous peaks from the plot
#             self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

#             # Peak detection (1-second moving window)
#             self.detect_blinks(filtered_eog)

#     def detect_blinks(self, filtered_eog):
#         mean_signal = np.mean(filtered_eog)
#         stdev_signal = np.std(filtered_eog)
 
#         threshold = mean_signal + (2 * stdev_signal)

#         # Calculate the start and end indices for the 1-second window
#         window_size = 1 * self.sampling_rate  # 1 seconds in samples
#         start_index = self.current_index - window_size
#         if start_index < 0:
#             start_index = 0
#         end_index = self.current_index

#         # Use a 1-second window for peak detection
#         filtered_window = filtered_eog[start_index:end_index]
#         peaks = self.detect_peaks(filtered_window, threshold)

#         # Reset blink data to zero
#         self.blink_data[:] = 0

#         # Mark detected peaks in blink_data
#         for peak in peaks:
#             full_peak_index = start_index + peak
#             self.blink_data[full_peak_index] = 1

#         # Mark peaks with red dots on the EOG plot
#         self.eog_plot.plot(self.time_data[start_index:end_index][peaks], filtered_window[peaks], pen=None, symbol='o', symbolPen='r', symbolSize=6)

#         # Update the blink plot with the current blink data
#         self.blink_curve.setData(self.time_data, self.blink_data)

#     def detect_peaks(self, signal, threshold):
#         # List to store detected peak indices
#         peaks = []
#         prev_peak_time = None  # Variable to store the timestamp of the previous peak
#         min_peak_gap = 0.1  # Minimum time gap between two peaks in seconds

#         for i in range(1, len(signal) - 1):
#             # Check if the current point is greater than the previous and next point (local maximum)
#             if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
#                 current_peak_time = i / self.sampling_rate  # Time in seconds based on the sampling rate

#                 if prev_peak_time is not None:
#                     time_gap = current_peak_time - prev_peak_time
#                     if time_gap < min_peak_gap:  # Ignore if the time gap is less than the threshold
#                         continue

#                 peaks.append(i)
#                 prev_peak_time = current_peak_time  # Update previous peak time

#         return peaks

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = EOGMonitor()
#     window.show()
#     sys.exit(app.exec_())





# import numpy as np
# from scipy.signal import butter, lfilter
# from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout
# import pyqtgraph as pg
# import pylsl
# import sys
# import time

# class EOGMonitor(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Real-Time EOG Monitor - Eye Blink Detection")
#         self.setGeometry(100, 100, 800, 400)

#         # Create layout
#         layout = QVBoxLayout()
#         central_widget = QWidget()
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#         # Create plot widget for EOG
#         self.eog_plot = pg.PlotWidget(self)
#         self.eog_plot.setBackground('w')
#         self.eog_plot.showGrid(x=True, y=True)
#         self.eog_plot.setTitle("Filtered EOG Signal (Low Pass: 10 Hz)")

#         # Bottom layout for Blink Detection
#         self.bottom_layout = QHBoxLayout()

#         # Blink detection plot
#         self.blink_plot = pg.PlotWidget(self)
#         self.blink_plot.setBackground('w')
#         self.blink_plot.showGrid(x=True, y=True)
#         self.blink_plot.setYRange(0, 1, padding=0)
#         self.blink_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
#         self.blink_plot.setTitle("Blink Detection")

#         # Add both plots to the layout
#         layout.addWidget(self.eog_plot)
#         layout.addWidget(self.blink_plot)

#         # Set up LSL stream inlet
#         streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
#         if not streams:
#             print("No LSL stream found!")
#             sys.exit(0)
#         self.inlet = pylsl.StreamInlet(streams[0])

#         self.sampling_rate = int(self.inlet.info().nominal_srate())
#         print(f"Sampling rate: {self.sampling_rate} Hz")

#         self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
#         self.eog_data = np.zeros(self.buffer_size)
#         self.time_data = np.linspace(0, 5, self.buffer_size)
#         self.blink_data = np.zeros(self.buffer_size)  # Blink data array
#         self.current_index = 0

#         # Low-pass filter for EOG (10 Hz)
#         self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')

#         self.eog_plot.setXRange(0, 5, padding=0)
#         if self.sampling_rate == 250:
#             self.eog_plot.setYRange(-((2**10)/2), ((2**10)/2), padding=0)
#         elif self.sampling_rate == 500:
#             self.eog_plot.setYRange(-((2**14)/2), ((2**14)/2), padding=0)

#         # Plot curves
#         self.eog_curve = self.eog_plot.plot(self.time_data, self.eog_data, pen=pg.mkPen('b', width=1))
#         self.blink_curve = self.blink_plot.plot(self.time_data, self.blink_data, pen=pg.mkPen('r', width=2))

#         # List to store detected peaks with timestamps
#         self.detected_peaks = []

#         # Timer for plot update
#         self.timer = pg.QtCore.QTimer()
#         self.timer.timeout.connect(self.update_plot)
#         self.timer.start(15)

#     def update_plot(self):
#         samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
#         if samples:
#             for sample in samples:
#                 # Overwrite the oldest data point in the buffer
#                 self.eog_data[self.current_index] = sample[0]
#                 self.current_index = (self.current_index + 1) % self.buffer_size

#             filtered_eog = lfilter(self.b, self.a, self.eog_data)

#             # Update curve with the filtered EOG signal (5-second window)
#             self.eog_plot.clear()    # Clear the previous peaks from the plot
#             self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

#             # Peak detection (1-second moving window)
#             self.detect_blinks(filtered_eog)

#             # Clear out old peaks from self.detected_peaks after 5 seconds
#             current_time = time.time()
#             self.detected_peaks = [(index, t) for index, t in self.detected_peaks if current_time - t < 5]

#             # Update the blink plot based on stored peaks
#             self.blink_data[:] = 0  # Reset blink data
#             for index, _ in self.detected_peaks:
#                 if 0 <= index < self.buffer_size:
#                     self.blink_data[index] = 1  # Keep blink data high at detected peaks

#             # Mark the stored peaks on the EOG plot
#             peak_indices = [index for index, t in self.detected_peaks]
#             peak_values = [filtered_eog[i] for i in peak_indices]
#             self.eog_plot.plot(self.time_data[peak_indices], peak_values, pen=None, symbol='o', symbolPen='r', symbolSize=6)

#             # Update the blink plot with the current blink data
#             self.blink_curve.setData(self.time_data, self.blink_data)

#     def detect_blinks(self, filtered_eog):
#         mean_signal = np.mean(filtered_eog)
#         stdev_signal = np.std(filtered_eog)
#         threshold = mean_signal + (2 * stdev_signal)

#         # Calculate the start and end indices for the 1-second window
#         window_size = 1 * self.sampling_rate
#         start_index = self.current_index - window_size
#         if start_index < 0:
#             start_index = 0
#         end_index = self.current_index

#         # Use a 1-second window for peak detection
#         filtered_window = filtered_eog[start_index:end_index]
#         peaks = self.detect_peaks(filtered_window, threshold)

#         # Mark detected peaks and store them with timestamps
#         for peak in peaks:
#             full_peak_index = start_index + peak
#             self.detected_peaks.append((full_peak_index, time.time()))  # Add detected peak with current timestamp

#     def detect_peaks(self, signal, threshold):
#         peaks = []
#         prev_peak_time = None  # Variable to store the timestamp of the previous peak
#         min_peak_gap = 0.1  # Minimum time gap between two peaks in seconds

#         for i in range(1, len(signal) - 1):
#             if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
#                 current_peak_time = i / self.sampling_rate  # Time in seconds based on the sampling rate

#                 if prev_peak_time is not None:
#                     time_gap = current_peak_time - prev_peak_time
#                     if time_gap < min_peak_gap:
#                         continue

#                 peaks.append(i)
#                 prev_peak_time = current_peak_time

#         return peaks

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = EOGMonitor()
#     window.show()
#     sys.exit(app.exec_())

#Use deque that remove the oldest peak after 5 seconds.
import numpy as np
from scipy.signal import butter, lfilter
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout
import pyqtgraph as pg
import pylsl
import sys
import time
from collections import deque

class EOGMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time EOG Monitor - Eye Blink Detection")
        self.setGeometry(100, 100, 800, 400)

        # Create layout
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create plot widget for EOG
        self.eog_plot = pg.PlotWidget(self)
        self.eog_plot.setBackground('w')
        self.eog_plot.showGrid(x=True, y=True)
        self.eog_plot.setTitle("Filtered EOG Signal (Low Pass: 10 Hz)")

        # Bottom layout for Blink Detection
        self.bottom_layout = QHBoxLayout()

        # Blink detection plot
        self.blink_plot = pg.PlotWidget(self)
        self.blink_plot.setBackground('w')
        self.blink_plot.showGrid(x=True, y=True)
        self.blink_plot.setYRange(0, 1, padding=0)
        self.blink_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
        self.blink_plot.setTitle("Blink Detection")

        # Add both plots to the layout
        layout.addWidget(self.eog_plot)
        layout.addWidget(self.blink_plot)

        # Set up LSL stream inlet
        streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
        if not streams:
            print("No LSL stream found!")
            sys.exit(0)
        self.inlet = pylsl.StreamInlet(streams[0])

        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")

        self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
        self.eog_data = np.zeros(self.buffer_size)
        self.time_data = np.linspace(0, 5, self.buffer_size)
        self.blink_data = np.zeros(self.buffer_size)  # Blink data array
        self.current_index = 0

        # Low-pass filter for EOG (10 Hz)
        self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')

        self.eog_plot.setXRange(0, 5, padding=0)
        if self.sampling_rate == 250:
            self.eog_plot.setYRange(-((2**10)/2), ((2**10)/2), padding=0)
        elif self.sampling_rate == 500:
            self.eog_plot.setYRange(-((2**14)/2), ((2**14)/2), padding=0)

        # Plot curves
        self.eog_curve = self.eog_plot.plot(self.time_data, self.eog_data, pen=pg.mkPen('b', width=1))
        self.blink_curve = self.blink_plot.plot(self.time_data, self.blink_data, pen=pg.mkPen('r', width=2))

        # Circular buffer for detected peaks
        self.detected_peaks = deque(maxlen=self.sampling_rate * 5)  # Store peaks with 5-second window

        # Timer for plot update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(15)

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
        if samples:
            for sample in samples:
                # Overwrite the oldest data point in the buffer
                self.eog_data[self.current_index] = sample[0]
                self.current_index = (self.current_index + 1) % self.buffer_size

            filtered_eog = lfilter(self.b, self.a, self.eog_data)

            # Update curve with the filtered EOG signal (5-second window)
            self.eog_plot.clear()    # Clear the previous peaks from the plot
            self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

            # Peak detection (1-second moving window)
            self.detect_blinks(filtered_eog)

            # Clear out old peaks from the circular buffer after 4 seconds(because we want to clear the peaks just after the data overwrite.)
            current_time = time.time()
            while self.detected_peaks and (current_time - self.detected_peaks[0][1] > 4):
                self.detected_peaks.popleft()  # Remove old peaks from the buffer

            # Update the blink plot based on stored peaks
            self.blink_data[:] = 0  # Reset blink data
            for index, _ in self.detected_peaks:
                if 0 <= index < self.buffer_size:
                    self.blink_data[index] = 1  # Keep blink data high at detected peaks

            # Mark the stored peaks on the EOG plot
            peak_indices = [index for index, t in self.detected_peaks]
            peak_values = [filtered_eog[i] for i in peak_indices]
            self.eog_plot.plot(self.time_data[peak_indices], peak_values, pen=None, symbol='o', symbolPen='r', symbolSize=6)

            # Update the blink plot with the current blink data
            self.blink_curve.setData(self.time_data, self.blink_data)

    def detect_blinks(self, filtered_eog):
        mean_signal = np.mean(filtered_eog)
        stdev_signal = np.std(filtered_eog)
        threshold = mean_signal + (1.5 * stdev_signal)

        # Calculate the start and end indices for the 1-second window
        window_size = 1 * self.sampling_rate
        start_index = self.current_index - window_size
        if start_index < 0:
            start_index = 0
        end_index = self.current_index

        # Use a 1-second window for peak detection
        filtered_window = filtered_eog[start_index:end_index]
        peaks = self.detect_peaks(filtered_window, threshold)

        # Mark detected peaks and store them with timestamps
        for peak in peaks:
            full_peak_index = start_index + peak
            self.detected_peaks.append((full_peak_index, time.time()))  # Add detected peak with current timestamp

    def detect_peaks(self, signal, threshold):
        peaks = []
        prev_peak_time = None  # Variable to store the timestamp of the previous peak
        min_peak_gap = 0.01 # Minimum time gap between two peaks in seconds

        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
                current_peak_time = i / self.sampling_rate  # Time in seconds based on the sampling rate

                if prev_peak_time is not None:
                    time_gap = current_peak_time - prev_peak_time
                    if time_gap < min_peak_gap:
                        continue

                peaks.append(i)
                prev_peak_time = current_peak_time

        return peaks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EOGMonitor()
    window.show()
    sys.exit(app.exec_())