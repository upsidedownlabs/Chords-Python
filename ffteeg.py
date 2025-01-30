import numpy as np
from collections import deque
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import sys
from scipy.signal import butter, iirnotch, lfilter, lfilter_zi
from scipy.fft import fft
import math

class EEGMonitor(QMainWindow):
    def __init__(self): 
        super().__init__()

        self.setWindowTitle("Real-Time EEG Monitor with FFT and Brainwave Power")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout split into two halves: top for EEG, bottom for FFT and Brainwaves
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        # First half for EEG signal plot
        self.eeg_plot_widget = PlotWidget(self)
        self.eeg_plot_widget.setBackground('w')
        self.eeg_plot_widget.showGrid(x=True, y=True)
        self.eeg_plot_widget.setLabel('bottom', 'EEG Plot')
        self.eeg_plot_widget.setYRange(-5000, 5000, padding=0)
        self.eeg_plot_widget.setXRange(0, 4, padding=0)
        self.eeg_plot_widget.setMouseEnabled(x=False, y=True)  # Disable zoom
        self.main_layout.addWidget(self.eeg_plot_widget)

        # Second half for FFT and Brainwave Power, aligned horizontally
        self.bottom_layout = QHBoxLayout()

        # FFT Plot (left side of the second half)
        self.fft_plot = PlotWidget(self)
        self.fft_plot.setBackground('w')
        self.fft_plot.showGrid(x=True, y=True)
        self.fft_plot.setLabel('bottom', 'FFT')
        # self.fft_plot.setYRange(0, 500, padding=0)
        self.fft_plot.setXRange(0, 50, padding=0)  # Set x-axis to 0 to 50 Hz
        # self.fft_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
        self.fft_plot.setAutoVisible(y=True)  # Allow y-axis to autoscale
        self.bottom_layout.addWidget(self.fft_plot)

        # Bar graph for brainwave power bands (right side of the second half)
        self.bar_chart_widget = pg.PlotWidget(self)
        self.bar_chart_widget.setBackground('w')
        self.bar_chart_widget.setLabel('bottom', 'Brainpower Bands')
        self.bar_chart_widget.setXRange(-0.5, 4.5)
        self.bar_chart_widget.setMouseEnabled(x=False, y=False)  # Disable zoom
        # Add brainwave power bars
        self.brainwave_bars = pg.BarGraphItem(x=[0, 1, 2, 3, 4], height=[0, 0, 0, 0, 0], width=0.5, brush='g')
        self.bar_chart_widget.addItem(self.brainwave_bars)
        # Set x-ticks for brainwave types
        self.bar_chart_widget.getAxis('bottom').setTicks([[(0, 'Delta'), (1, 'Theta'), (2, 'Alpha'), (3, 'Beta'), (4, 'Gamma')]])
        self.bottom_layout.addWidget(self.bar_chart_widget)

        # Add the bottom layout to the main layout
        self.main_layout.addLayout(self.bottom_layout)
        self.setCentralWidget(self.central_widget)

        # Set up LSL stream inlet
        streams = pylsl.resolve_stream('name', 'BioAmpDataStream')
        if not streams:
            print("No LSL stream found!")
            sys.exit(0)
        self.inlet = pylsl.StreamInlet(streams[0])

        # Sampling rate
        self.sampling_rate = int(self.inlet.info().nominal_srate())
        print(f"Sampling rate: {self.sampling_rate} Hz")

        # Data and Buffers
        self.eeg_data = deque(maxlen=500)       # Initialize moving window with 500 samples
        self.moving_window = deque(maxlen=500)  # 500 samples for FFT and power calculation (sliding window)

        self.b_notch, self.a_notch = iirnotch(50, 30, self.sampling_rate)
        self.b_band, self.a_band = butter(4, [0.5 / (self.sampling_rate / 2), 48.0 / (self.sampling_rate / 2)], btype='band')

        self.zi_notch = lfilter_zi(self.b_notch, self.a_notch) * 0
        self.zi_band = lfilter_zi(self.b_band, self.a_band) * 0

        # Timer for updating the plot
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20) 

        self.eeg_curve = self.eeg_plot_widget.plot(pen=pg.mkPen('b', width=1))
        self.fft_curve = self.fft_plot.plot(pen=pg.mkPen('r', width=1))  # FFT Colour is red

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0)
        if samples:
            for sample in samples:
                raw_point = sample[0]

                notch_filtered, self.zi_notch = lfilter(self.b_notch, self.a_notch, [raw_point], zi=self.zi_notch)
                band_filtered, self.zi_band = lfilter(self.b_band, self.a_band, notch_filtered, zi=self.zi_band)
                band_filtered = band_filtered[-1]  # Get the current filtered point

                # Update EEG data buffer
                self.eeg_data.append(band_filtered)

                if len(self.moving_window) < 500:
                    self.moving_window.append(band_filtered)
                else:
                    self.process_fft_and_brainpower()

                    self.moving_window = deque(list(self.moving_window)[50:] + [band_filtered], maxlen=500)

            plot_data = np.array(self.eeg_data)
            time_axis = np.linspace(0, 4, len(plot_data))
            self.eeg_curve.setData(time_axis, plot_data)

    def process_fft_and_brainpower(self):
        window = np.hanning(len(self.moving_window))
        buffer_windowed = np.array(self.moving_window) * window
        fft_result = np.abs(np.fft.rfft(buffer_windowed))
        fft_result /= len(buffer_windowed)
        freqs = np.fft.rfftfreq(len(buffer_windowed), 1 / self.sampling_rate)
        self.fft_curve.setData(freqs, fft_result)

        brainwave_power = self.calculate_brainwave_power(fft_result, freqs)
        self.brainwave_bars.setOpts(height=brainwave_power)

    def calculate_brainwave_power(self, fft_data, freqs):
        delta_power = math.sqrt(np.sum(((fft_data[(freqs >= 0.5) & (freqs <= 4)])**2)/4))
        theta_power = math.sqrt(np.sum(((fft_data[(freqs >= 4) & (freqs <= 8)])**2)/5))
        alpha_power = math.sqrt(np.sum(((fft_data[(freqs >= 8) & (freqs <= 13)])**2)/6))
        beta_power = math.sqrt(np.sum(((fft_data[(freqs >= 13) & (freqs <=30)])**2)/18))
        gamma_power = math.sqrt(np.sum(((fft_data[(freqs >= 30) & (freqs <= 45)])**2)/16))
        print("Delta Power", delta_power)
        print("Theta Power", theta_power)
        print("Alpha Power", alpha_power)
        print("Beta Power", beta_power)
        print("Gamma Power", gamma_power)
        return [delta_power, theta_power, alpha_power, beta_power, gamma_power]
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EEGMonitor()  
    window.show()
    sys.exit(app.exec_())