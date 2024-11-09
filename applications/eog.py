# # import numpy as np
# # from scipy.signal import butter, filtfilt
# # from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout
# # import pyqtgraph as pg
# # import pylsl
# # import sys

# # class EOGMonitor(QMainWindow):
# #     def __init__(self):
# #         super().__init__()

# #         self.setWindowTitle("Real-Time EOG Monitor - Eye Blink Detection")
# #         self.setGeometry(100, 100, 800, 400)

# #         # Create layout
# #         layout = QVBoxLayout()
# #         central_widget = QWidget()
# #         central_widget.setLayout(layout)
# #         self.setCentralWidget(central_widget)

# #         # Create plot widget for EOG
# #         self.eog_plot = pg.PlotWidget(self)
# #         self.eog_plot.setBackground('w')
# #         self.eog_plot.showGrid(x=True, y=True)
# #         self.eog_plot.setTitle("Filtered EOG Signal (Low Pass: 10 Hz)")

# #         # Bottom layout for Blink Detection
# #         self.bottom_layout = QHBoxLayout()

# #         # Blink detection plot
# #         self.blink_plot = pg.PlotWidget(self)
# #         self.blink_plot.setBackground('w')
# #         self.blink_plot.showGrid(x=True, y=True)
# #         self.blink_plot.setYRange(0, 1, padding=0)
# #         self.blink_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
# #         self.blink_plot.setTitle("Blink Detection")

# #         # Add both plots to the layout
# #         layout.addWidget(self.eog_plot)
# #         layout.addWidget(self.blink_plot)

# #         # Set up LSL stream inlet
# #         streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
# #         if not streams:
# #             print("No LSL stream found!")
# #             sys.exit(0)
# #         self.inlet = pylsl.StreamInlet(streams[0])

# #         self.sampling_rate = int(self.inlet.info().nominal_srate())
# #         print(f"Sampling rate: {self.sampling_rate} Hz")

# #         self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
# #         self.eog_data = np.zeros(self.buffer_size)
# #         self.time_data = np.linspace(0, 5, self.buffer_size)
# #         self.blink_data = np.zeros(self.buffer_size)  # Blink data array
# #         self.current_index = 0

# #         # Low-pass filter for EOG (10 Hz)
# #         self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')

# #         self.eog_plot.setXRange(0, 5, padding=0)
# #         if self.sampling_rate == 250:
# #             self.eog_plot.setYRange(-((2**10)/2), ((2**10)/2), padding=0)
# #         elif self.sampling_rate == 500:
# #             self.eog_plot.setYRange(-((2**14)/2), ((2**14)/2), padding=0)

# #         # Plot curves
# #         self.eog_curve = self.eog_plot.plot(self.time_data, self.eog_data, pen=pg.mkPen('b', width=1))
# #         self.blink_curve = self.blink_plot.plot(self.time_data, self.blink_data, pen=pg.mkPen('r', width=2))

# #         # Timer for plot update
# #         self.timer = pg.QtCore.QTimer()
# #         self.timer.timeout.connect(self.update_plot)
# #         self.timer.start(15)

# #     def update_plot(self):
# #         samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
# #         if samples:
# #             for sample in samples:
# #                 # Overwrite the oldest data point in the buffer
# #                 self.eog_data[self.current_index] = sample[0]
# #                 self.current_index = (self.current_index + 1) % self.buffer_size

# #             filtered_eog = filtfilt(self.b, self.a, self.eog_data)

# #             self.eog_plot.clear()    # Clear the previous peaks from the plot

# #             # Update curve with the filtered EOG signal
# #             self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

# #             self.detect_blinks(filtered_eog)    # Blink detection

# #     def detect_blinks(self, filtered_eog):
# #         # Set the blink threshold as 60% of the max
# #         threshold = np.max(np.abs(filtered_eog)) * 0.8
# #         peaks = self.detect_peaks(filtered_eog, threshold)

# #         # Reset blink data to zero
# #         self.blink_data[:] = 0

# #         # Set a short window to 1 around each detected blink peak
# #         for peak in peaks:
# #             # Ensure the peak window doesn’t exceed the array bounds
# #             start = max(0, peak - 5)  # Start a few samples before the peak
# #             end = min(self.buffer_size, peak + 5)  # End a few samples after the peak
# #             self.blink_data[start:end] = 1

# #         # Mark peaks with red dots on the EOG plot
# #         self.eog_plot.plot(self.time_data[peaks], filtered_eog[peaks], pen=None, symbol='o', symbolPen='r', symbolSize=6)

# #         # Update the blink plot with the current blink data
# #         self.blink_curve.setData(self.time_data, self.blink_data)

# #     def detect_peaks(self, signal, threshold):
# #         # List to store detected peak indices
# #         peaks = []
# #         prev_peak_time = None  # Variable to store the timestamp of the previous peak
# #         min_peak_gap = 0.1  # Minimum time gap between two peaks in seconds

# #         # Loop over the signal (starting from the second point and ending at the second to last)
# #         for i in range(1, len(signal) - 1):
# #             # Check if the current point is greater than the previous and next point (local maximum)
# #             if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
# #                 current_peak_time = i / self.sampling_rate  # Time in seconds based on the sampling rate

# #                 if prev_peak_time is not None:
# #                     time_gap = current_peak_time - prev_peak_time
# #                     if time_gap < min_peak_gap:  # Ignore if the time gap is less than the threshold
# #                         continue

# #                 peaks.append(i)
# #                 prev_peak_time = current_peak_time  # Update previous peak time

# #         return peaks

# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     window = EOGMonitor()
# #     window.show()
# #     sys.exit(app.exec_())




# #Blink is ok but moving window remains.
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

#             self.eog_plot.clear()    # Clear the previous peaks from the plot

#             # Update curve with the filtered EOG signal
#             self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

#             self.detect_blinks(filtered_eog)    # Blink detection

#     def detect_blinks(self, filtered_eog):
#         # Calculate dynamic threshold based on the mean and standard deviation of the signal
#         mean_signal = np.mean(filtered_eog)
#         stdev_signal = np.std(filtered_eog)

#         # Set the threshold 
#         threshold = mean_signal + (2 * stdev_signal)
        
#         peaks = self.detect_peaks(filtered_eog, threshold)

#         # Reset blink data to zero
#         self.blink_data[:] = 0

#         # Set a short window to 1 around each detected blink peak
#         for peak in peaks:
#             # Ensure the peak window doesn’t exceed the array bounds
#             start = max(0, peak - 5)  # Start a few samples before the peak
#             end = min(self.buffer_size, peak + 5)  # End a few samples after the peak
#             self.blink_data[start:end] = 1

#         # Mark peaks with red dots on the EOG plot
#         self.eog_plot.plot(self.time_data[peaks], filtered_eog[peaks], pen=None, symbol='o', symbolPen='r', symbolSize=6)

#         # Update the blink plot with the current blink data
#         self.blink_curve.setData(self.time_data, self.blink_data)

#     def detect_peaks(self, signal, threshold):
#         # List to store detected peak indices
#         peaks = []
#         prev_peak_time = None  # Variable to store the timestamp of the previous peak
#         min_peak_gap = 0.1  # Minimum time gap between two peaks in seconds

#         # Loop over the signal (starting from the second point and ending at the second to last)
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




#Working Now but now the issue is with the blink detection plot
import numpy as np
from scipy.signal import butter, filtfilt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout
import pyqtgraph as pg
import pylsl
import sys

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

        # Timer for plot update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(15)

        # Define window size and shift size (in samples)
        self.window_size = self.sampling_rate * 3   # 3 seconds window
        self.shift_size = self.sampling_rate * 0.5  # 500 ms shift

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
        if samples:
            for sample in samples:
                # Overwrite the oldest data point in the buffer
                self.eog_data[self.current_index] = sample[0]
                self.current_index = (self.current_index + 1) % self.buffer_size

            filtered_eog = filtfilt(self.b, self.a, self.eog_data)

            self.eog_plot.clear()  # Clear the previous peaks from the plot

            # Update curve with the filtered EOG signal
            self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

            # Detect peaks within the current moving window
            self.detect_blinks(filtered_eog)  # Blink detection

    def detect_blinks(self, filtered_eog):
        # Calculate dynamic threshold based on the mean and standard deviation of the signal
        mean_signal = np.mean(filtered_eog)
        stdev_signal = np.std(filtered_eog)
        # print(stdev_signal)

        # Set the threshold 
        # threshold = mean_signal + (2 * stdev_signal)
        threshold = 500

        # Process the signal in windows
        start_idx = self.current_index - self.window_size
        if start_idx < 0:
            start_idx = 0

        window_eog = filtered_eog[start_idx:start_idx + self.window_size]
        peaks = self.detect_peaks(window_eog, threshold)

        # Reset blink data to zero
        self.blink_data[:] = 0

        # Set a short window to 1 around each detected blink peak
        for peak in peaks:
            # Ensure the peak window doesn’t exceed the array bounds
            start = max(0, peak - 5)  # Start a few samples before the peak
            end = min(self.buffer_size, peak + 5)  # End a few samples after the peak
            self.blink_data[start:end] = 1

        # Ensure peak indices are integers for plotting
        peak_indices = np.array(peaks, dtype=int)

        # Mark peaks with red dots on the EOG plot
        self.eog_plot.plot(self.time_data[start_idx + peak_indices], window_eog[peak_indices], pen=None, symbol='o', symbolPen='r', symbolSize=6)

        # Update the blink plot with the current blink data
        self.blink_curve.setData(self.time_data, self.blink_data)

    def detect_peaks(self, signal, threshold):
        # List to store detected peak indices
        peaks = []
        prev_peak_time = None  # Variable to store the timestamp of the previous peak
        min_peak_gap = 0.1  # Minimum time gap between two peaks in seconds

        # Loop over the signal (starting from the second point and ending at the second to last)
        for i in range(1, len(signal) - 1):
            # Check if the current point is greater than the previous and next point (local maximum)
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1] and signal[i] > threshold:
                current_peak_time = i / self.sampling_rate  # Time in seconds based on the sampling rate
                peaks.append(i)

                if prev_peak_time is not None:
                    time_gap = current_peak_time - prev_peak_time
                    if time_gap < min_peak_gap:  # Ignore if the time gap is less than the threshold
                        continue

        return peaks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EOGMonitor()
    window.show()
    sys.exit(app.exec_())