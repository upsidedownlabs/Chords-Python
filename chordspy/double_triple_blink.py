import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QHBoxLayout
import pyqtgraph as pg
import pylsl
import sys
import time
from collections import deque

class EOGMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time EOG Monitor - Double & Triple Blink Detection")
        self.setGeometry(100, 100, 800, 400)

        self.stream_active = True
        self.last_data_time = None

        # Detection parameters (can be tuned)
        self.min_interblink_gap = 0.1    # 100ms minimum between blinks
        self.max_interblink_gap = 0.4    # 400ms maximum between blinks
        self.double_triple_window = 500  # ms to wait after 2nd blink for possible triple
        self.last_double_blink_time = 0
        self.last_triple_blink_time = 0

        # State for look-ahead logic
        self.blink_times = []  # list of (timestamp, index)
        self.waiting_for_triple = False
        self.triple_timer = None
        self.locked = False  # Prevents multiple detections per sequence

        # Create layout
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create plot widget for EOG
        self.eog_plot = pg.PlotWidget(self)
        self.eog_plot.setBackground('w')
        self.eog_plot.showGrid(x=True, y=True)
        self.eog_plot.setMouseEnabled(x=False, y=False)
        self.eog_plot.setTitle("Filtered EOG Signal (Low Pass: 10 Hz)")

        # Blink detection plot
        self.blink_plot = pg.PlotWidget(self)
        self.blink_plot.setBackground('w')
        self.blink_plot.showGrid(x=True, y=True)
        self.blink_plot.setYRange(0, 1)
        self.blink_plot.setMouseEnabled(x=False, y=False)
        self.blink_plot.setTitle("Blink Detection")

        # Add both plots to the layout
        layout.addWidget(self.eog_plot)
        layout.addWidget(self.blink_plot)

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

        self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
        self.eog_data = np.zeros(self.buffer_size)
        self.time_data = np.linspace(0, 5, self.buffer_size)
        self.blink_data = np.zeros(self.buffer_size)  # Blink data array
        self.current_index = 0

        # Low-pass filter for EOG (10 Hz)
        self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')
        self.zi = lfilter_zi(self.b, self.a)  # Initialize filter state

        self.eog_plot.setXRange(0, 5, padding=0)
        if self.sampling_rate == 250:
            self.eog_plot.setYRange(0, 2**10, padding=0)
        elif self.sampling_rate == 500:
            self.eog_plot.setYRange(0, 5000, padding=0)

        # Plot curves
        self.eog_curve = self.eog_plot.plot(self.time_data, self.eog_data, pen=pg.mkPen('b', width=1))
        self.blink_curve = self.blink_plot.plot(self.time_data, self.blink_data, pen=pg.mkPen('r', width=2))

        # Circular buffer for detected peaks (store (index, time))
        self.detected_peaks = deque(maxlen=self.sampling_rate * 5)

        # Timer for plot update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(15)
        self.start_time = time.time()

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
        if samples:
            self.last_data_time = time.time()
            for sample in samples:
                self.eog_data[self.current_index] = sample[0]
                self.current_index = (self.current_index + 1) % self.buffer_size

            # Filter only the new data
            filtered_eog, self.zi = lfilter(self.b, self.a, self.eog_data, zi=self.zi)

            # Update curve with the filtered EOG signal
            self.eog_plot.clear()
            self.eog_curve = self.eog_plot.plot(self.time_data, filtered_eog, pen=pg.mkPen('b', width=1))

            if time.time() - self.start_time >= 2:
                self.detect_blinks(filtered_eog)

            # Clear out old peaks from the circular buffer
            current_time = time.time()
            while self.detected_peaks and (current_time - self.detected_peaks[0][1] > 4):
                self.detected_peaks.popleft()

            # Update the blink plot based on stored peaks
            self.blink_data[:] = 0
            for index, _ in self.detected_peaks:
                if 0 <= index < self.buffer_size:
                    self.blink_data[index] = 1

            # Mark the stored peaks on the EOG plot
            peak_indices = [index for index, t in self.detected_peaks]
            peak_values = [filtered_eog[i] for i in peak_indices]
            self.eog_plot.plot(self.time_data[peak_indices], peak_values, pen=None, symbol='o', symbolPen='r', symbolSize=6)

            # Update the blink plot
            self.blink_curve.setData(self.time_data, self.blink_data)
        else:
            if self.last_data_time and (time.time() - self.last_data_time) > 2:
                self.stream_active = False
                print("LSL stream disconnected!")
                self.timer.stop()
                self.close()

    def detect_blinks(self, filtered_eog):
        if self.locked:
            return
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
            self.handle_new_blink(peak_time, full_peak_index, filtered_eog)

    def handle_new_blink(self, peak_time, peak_index, filtered_eog):
        if self.locked:
            return
        # Remove old blinks (older than 1.5s)
        self.blink_times = [(t, idx) for t, idx in self.blink_times if peak_time - t < 1.5]
        self.blink_times.append((peak_time, peak_index))

        if self.waiting_for_triple:
            # If already waiting for triple, check if this is the 3rd blink
            if len(self.blink_times) >= 3:
                t1, idx1 = self.blink_times[-3]
                t2, idx2 = self.blink_times[-2]
                t3, idx3 = self.blink_times[-1]
                gap1 = t2 - t1
                gap2 = t3 - t2
                if (self.min_interblink_gap <= gap1 <= self.max_interblink_gap and
                    self.min_interblink_gap <= gap2 <= self.max_interblink_gap):
                    # Triple blink detected
                    self.locked = True
                    print("TRIPLE BLINK DETECTED!")
                    self.last_triple_blink_time = time.time()
                    self.eog_plot.plot([self.time_data[idx1], self.time_data[idx2], self.time_data[idx3]],
                                      [filtered_eog[idx1], filtered_eog[idx2], filtered_eog[idx3]],
                                      pen=None, symbol='x', symbolPen='g', symbolSize=12)
                    self.reset_blink_state()
                    return
        else:
            # Not waiting for triple, check for double
            if len(self.blink_times) >= 2:
                t1, idx1 = self.blink_times[-2]
                t2, idx2 = self.blink_times[-1]
                gap = t2 - t1
                if self.min_interblink_gap <= gap <= self.max_interblink_gap:
                    # Start timer to wait for possible triple
                    self.waiting_for_triple = True
                    if self.triple_timer is not None:
                        self.triple_timer.stop()
                    self.triple_timer = pg.QtCore.QTimer()
                    self.triple_timer.setSingleShot(True)
                    self.triple_timer.timeout.connect(lambda: self.double_blink_timeout(filtered_eog))
                    self.triple_timer.start(self.double_triple_window)

    def double_blink_timeout(self, filtered_eog):
        if self.locked:
            return
        # Called if no 3rd blink appears in the window
        if len(self.blink_times) >= 2:
            t1, idx1 = self.blink_times[-2]
            t2, idx2 = self.blink_times[-1]
            gap = t2 - t1
            if self.min_interblink_gap <= gap <= self.max_interblink_gap:
                self.locked = True
                print("DOUBLE BLINK DETECTED!")
                self.last_double_blink_time = time.time()
                self.eog_plot.plot([self.time_data[idx1], self.time_data[idx2]], [filtered_eog[idx1], filtered_eog[idx2]], pen=None, symbol='x', symbolPen='b', symbolSize=10)
        self.reset_blink_state()

    def reset_blink_state(self):
        self.blink_times = []
        self.waiting_for_triple = False
        if self.triple_timer is not None:
            self.triple_timer.stop()
            self.triple_timer = None
        # Unlock after a short refractory period
        pg.QtCore.QTimer.singleShot(500, self.unlock)

    def unlock(self):
        self.locked = False

    def detect_peaks(self, signal, threshold):
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EOGMonitor()
    print("Note: There will be a 2s calibration delay before peak detection starts.")
    window.show()
    sys.exit(app.exec_()) 