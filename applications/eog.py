import numpy as np
from scipy.signal import butter, filtfilt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget
from pyqtgraph import PlotWidget
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

        # Create plot widget for EOG
        self.eog_plot = PlotWidget(self)
        self.eog_plot.setBackground('w')
        self.eog_plot.showGrid(x=True, y=True)
        self.eog_plot.setTitle("Filtered EOG Signal (Low Pass: 10 Hz)")

        # Add plot to layout
        layout.addWidget(self.eog_plot)

        # Central widget
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
        
        # Data and buffer
        self.buffer_size = self.sampling_rate * 5  # 5 seconds buffer for recent data
        self.eog_data = np.zeros(self.buffer_size)
        self.time_data = np.linspace(0, 5, self.buffer_size)
        self.current_index = 0

        # Low-pass filter for EOG (10 Hz)
        self.b, self.a = butter(4, 10.0 / (0.5 * self.sampling_rate), btype='low')

        # Set fixed axis ranges
        self.eog_plot.setXRange(0, 5, padding=0)
        if self.sampling_rate == 250:
            self.eog_plot.setYRange(-((2**10)/2), ((2**10)/2), padding=0)
        elif self.sampling_rate == 500:
            self.eog_plot.setYRange(-((2**14)/2), ((2**14)/2), padding=0)

        # Plot curve for EOG data
        self.eog_curve = self.eog_plot.plot(self.time_data, self.eog_data, pen=pg.mkPen('b', width=1))

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

            # Apply only the low-pass filter to the EOG data
            filtered_eog = filtfilt(self.b, self.a, self.eog_data)

            # Update curve with the low-pass filtered EOG signal
            self.eog_curve.setData(self.time_data, filtered_eog)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EOGMonitor()
    window.show()
    sys.exit(app.exec_())