import numpy as np
from numpy import hamming
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import sys
from scipy.signal import butter, filtfilt
from scipy.fft import fft

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
        self.eeg_plot_widget.setYRange(0, 15000, padding=0)
        self.eeg_plot_widget.setXRange(0, 10, padding=0)
        self.eeg_plot_widget.setMouseEnabled(x=False, y=False)  # Disable zoom
        self.main_layout.addWidget(self.eeg_plot_widget)

        # Second half for FFT and Brainwave Power, aligned horizontally
        self.bottom_layout = QHBoxLayout()

        # FFT Plot (left side of the second half)
        self.fft_plot = PlotWidget(self)
        self.fft_plot.setBackground('w')
        self.fft_plot.showGrid(x=True, y=True)
        self.fft_plot.setLabel('bottom', 'FFT')
        self.fft_plot.setYRange(0, 25000, padding=0)
        self.fft_plot.setXRange(0, 50, padding=0)  # Set x-axis to 0 to 50 Hz
        self.fft_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
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

        # Data and buffers
        self.buffer_size = self.sampling_rate * 10  # Fixed-size buffer for 10 seconds
        self.eeg_data = np.zeros(self.buffer_size)  # Fixed-size array for circular buffer
        self.time_data = np.linspace(0, 10, self.buffer_size)  # Fixed time array for plotting
        self.current_index = 0  # Index for overwriting data

        # Low-pass filter (4th order, cutoff at 45 Hz)
        self.b_lowpass, self.a_lowpass = butter(4, 45 / (0.5 * self.sampling_rate), btype='low')

        # Timer for updating the plot
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20) 

        self.eeg_curve = self.eeg_plot_widget.plot(self.time_data, self.eeg_data, pen=pg.mkPen('b', width=1))  #EEG Colour is blue
        self.fft_curve = self.fft_plot.plot(pen=pg.mkPen('r', width=1))  # FFT Colour is red

    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
        if samples:
            for sample in samples:
                # Overwrite the oldest data point in the buffer
                self.eeg_data[self.current_index] = sample[0]
                self.current_index = (self.current_index + 1) % self.buffer_size  # Circular increment

            # Apply low-pass filter
            filtered_eeg = filtfilt(self.b_lowpass, self.a_lowpass, self.eeg_data)

            # Update the EEG plot with the filtered data
            self.eeg_curve.setData(self.time_data, filtered_eeg)

            # Perform FFT with windowing (Hamming window)
            window = hamming(len(filtered_eeg))  # Apply Hamming window to reduce spectral leakage
            filtered_eeg_windowed = filtered_eeg * window  # Element-wise multiply

            eeg_fft = np.abs(fft(filtered_eeg_windowed))[:len(filtered_eeg_windowed) // 2]  # Positive frequencies only
            freqs = np.fft.fftfreq(len(filtered_eeg_windowed), 1 / self.sampling_rate)[:len(filtered_eeg_windowed) // 2]

            # Update FFT plot
            self.fft_curve.setData(freqs, eeg_fft)

            # Calculate brainwave power
            brainwave_power = self.calculate_brainwave_power(eeg_fft, freqs)
            self.brainwave_bars.setOpts(height=brainwave_power)

    def calculate_brainwave_power(self, fft_data, freqs):
        delta_power = np.sum(fft_data[(freqs >= 0.5) & (freqs <= 4)])
        theta_power = np.sum(fft_data[(freqs >= 4) & (freqs <= 8)])
        alpha_power = np.sum(fft_data[(freqs >= 8) & (freqs <= 13)])
        beta_power = np.sum(fft_data[(freqs >= 13) & (freqs <= 30)])
        gamma_power = np.sum(fft_data[(freqs >= 30) & (freqs <= 45)])

        return [delta_power, theta_power, alpha_power, beta_power, gamma_power]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EEGMonitor()  
    window.show()
    sys.exit(app.exec_())