# ey blink detection is ok but the issue is with that the peaks are there on the plain line when no signal are there.
# import numpy as np
# from scipy.signal import butter, filtfilt, find_peaks
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
#     #   self.blink_plot.setMouseEnabled(x=False,y=False)  # Disable zoom
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

#         # Sampling rate
#         self.sampling_rate = int(self.inlet.info().nominal_srate())
#         print(f"Sampling rate: {self.sampling_rate} Hz")

#         # Data and buffer
#         self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
#         self.eog_data = np.zeros(self.buffer_size)
#         self.time_data = np.linspace(0, 5, self.buffer_size)
#         self.blink_data = np.zeros(self.buffer_size)  # Blink data array
#         self.current_index = 0

#         # Low-pass filter coefficients for EOG (10 Hz)
#         self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')

#         # Set fixed axis ranges
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

#             self.detect_blinks(filtered_eog)    # Blink detection using peak detection on the filtered signal

#     def detect_blinks(self, filtered_eog):
#         # Set the blink threshold as 60% of the max
#         threshold = np.max(np.abs(filtered_eog)) * 0.8   #try for 80%
#         peaks, _ = find_peaks(filtered_eog, height=threshold, distance=self.sampling_rate // 5)

#         self.blink_data[:] = 0  # Reset blink data to zero

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

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = EOGMonitor()
#     window.show()
#     sys.exit(app.exec_())


# Algorithm - reduce to mean baseling then find local minima wiht constraints then corresponding local maxima  and then filter
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
        self.blink_plot.setMouseEnabled(x=False, y=False)
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
        
        # Blink peak scatter plot
        self.blink_scatter = pg.ScatterPlotItem(pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0), size=8)
        self.eog_plot.addItem(self.blink_scatter)

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

            filtered_eog = filtfilt(self.b, self.a, self.eog_data)  # Apply filtering
            self.eog_curve.setData(self.time_data, filtered_eog)    # Update curve with the filtered EOG signal
            self.detect_blinks(filtered_eog)                        # Detect blinks based on the preprocessed filtered data

    def detect_blinks(self, filtered_eog):
        # Step 1: Normalize signal to zero mean
        normalized_eog = filtered_eog - np.mean(filtered_eog)

        # Step 2: Find local minima with constraints
        min_distance_samples = int(0.1 * self.sampling_rate)
        minima_indices = []

        # Always check for the first peak if it's the first update
        for i in range(min_distance_samples, len(normalized_eog) - min_distance_samples):  # Loop through data to find local minima
            if normalized_eog[i] < normalized_eog[i - 1] and normalized_eog[i] < normalized_eog[i + 1]:
                if normalized_eog[i] < -70:  # Check if it is at least 70µV below baseline or not
                    if len(minima_indices) == 0 or (i - minima_indices[-1] >= min_distance_samples):
                        minima_indices.append(i)

        # Reset blink data and clear blink scatter points
        self.blink_data[:] = 0   
        blink_points = []

        # Step 3: Match minima with maxima within 0.5s windows
        for i, min_idx in enumerate(minima_indices):
            # Define window to find the maximum
            next_min_idx = minima_indices[i + 1] if i + 1 < len(minima_indices) else len(normalized_eog)
            window_size = min(next_min_idx - min_idx, int(0.5 * self.sampling_rate))
            max_idx = min_idx + np.argmax(normalized_eog[min_idx:min_idx + window_size])

            if normalized_eog[max_idx] < 10:  # Maximum threshold
                continue

            # Step 4: Identify start and end of the blink
            start_idx = min_idx
            while start_idx > 0 and normalized_eog[start_idx] > -5:
                start_idx -= 1

            end_idx = max_idx
            while end_idx < len(normalized_eog) and normalized_eog[end_idx] < 5:
                end_idx += 1

            self.blink_data[start_idx:end_idx] = 1   # Mark blink in blink data array

            # Add blink point for scatter plot
            blink_points.append({'pos': (self.time_data[max_idx], filtered_eog[max_idx])})

        self.blink_curve.setData(self.time_data, self.blink_data)   # Update the blink plot
        self.blink_scatter.setData(blink_points)  # Plot red dots at detected blinks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EOGMonitor()
    window.show()
    sys.exit(app.exec_())

#The start of a blink is identified by moving backward from the minimum point until the signal returns to a baseline of -5µV.
#The end of the blink is found by moving forward from the maximum point until the signal reaches +5µV, marking the end of the blink.

#Moving Window
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
        self.blink_plot.setMouseEnabled(x=False, y=False)
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
        
        # Blink peak scatter plot
        self.blink_scatter = pg.ScatterPlotItem(pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0), size=8)
        self.eog_plot.addItem(self.blink_scatter)

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

            filtered_eog = filtfilt(self.b, self.a, self.eog_data)  # Apply filtering
            self.eog_curve.setData(self.time_data, filtered_eog)    # Update curve with the filtered EOG signal
            self.detect_blinks(filtered_eog)                        # Detect blinks based on the preprocessed filtered data

    def detect_blinks(self, filtered_eog):
        # Step 1: Normalize signal to zero mean
        normalized_eog = filtered_eog - np.mean(filtered_eog)

        # Step 2: Moving window approach for peak detection
        window_samples = int(0.25 * self.sampling_rate)  # 250 ms window
        blink_points = []  # List to store blink scatter points
        self.blink_data[:] = 0  # Reset blink data array

        for i in range(window_samples, len(normalized_eog) - window_samples):
            window_data = normalized_eog[i - window_samples // 2: i + window_samples // 2]
            min_idx = i - window_samples // 2 + np.argmin(window_data)
            max_idx = i - window_samples // 2 + np.argmax(window_data)

            # Check if peak qualifies as a blink
            if normalized_eog[min_idx] < -70 and normalized_eog[max_idx] > 5:
                self.blink_data[min_idx:max_idx] = 1  # Mark the blink in blink data

                # Add blink point for scatter plot
                blink_points.append({'pos': (self.time_data[max_idx], filtered_eog[max_idx])})

        self.blink_curve.setData(self.time_data, self.blink_data)   # Update the blink plot
        self.blink_scatter.setData(blink_points)  # Plot red dots at detected blinks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EOGMonitor()
    window.show()
    sys.exit(app.exec_())

#Issue : first peak not detected, peaks detected on straight line as well, 