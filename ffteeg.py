import numpy as np
from collections import deque
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QGridLayout, QScrollArea, QPushButton, QDialog, QCheckBox, QLabel, QComboBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import sys
from scipy.signal import butter, iirnotch, lfilter, lfilter_zi
import time

# Constants
FFT_WINDOW_SIZE = 512  # Data points we are using for fft analysis
# On increase this value - Frequency analysis becomes more accurate but updates slower
# On decrease this value - Updates faster but frequency details become less precise

SMOOTHING_WINDOW_SIZE = 10  # How many FFT results we average to make the display smoother
# On increase this value - Graph looks smoother but reacts slower to changes
# On decrease this value - Reacts faster but graph looks more jumpy

DISPLAY_DURATION = 4  # How many seconds of EEG data to show at once (in seconds)

class DataProcessor:
    def __init__(self, num_channels, sampling_rate):
        self.num_channels = num_channels
        self.sampling_rate = sampling_rate
        
        # Filters - 1. A notch filter to remove electrical interference (50Hz noise) and A bandpass filter (0.5-45Hz)
        self.b_notch, self.a_notch = iirnotch(50, 30, self.sampling_rate)
        self.b_band, self.a_band = butter(4, [0.5 / (self.sampling_rate / 2), 45.0 / (self.sampling_rate / 2)], btype='band')
        self.zi_notch = [lfilter_zi(self.b_notch, self.a_notch) * 0 for _ in range(num_channels)]
        self.zi_band = [lfilter_zi(self.b_band, self.a_band) * 0 for _ in range(num_channels)]
        
        # Circular buffers to store the last few seconds of EEG data
        self.eeg_data = [np.zeros(DISPLAY_DURATION * sampling_rate) for _ in range(num_channels)]
        self.current_indices = [0 for _ in range(num_channels)]    # Pointers to know where to put new data
        self.moving_windows = [deque(maxlen=FFT_WINDOW_SIZE) for _ in range(num_channels)]   # 3. Moving windows for FFT calculation
        
    def process_sample(self, sample):
        filtered_data = []
        for ch in range(self.num_channels):
            raw_point = sample[ch]  # Get the raw EEG value
            
            # Apply filters
            notch_filtered, self.zi_notch[ch] = lfilter(self.b_notch, self.a_notch, [raw_point], zi=self.zi_notch[ch])
            band_filtered, self.zi_band[ch] = lfilter(self.b_band, self.a_band, notch_filtered, zi=self.zi_band[ch])
            band_filtered = band_filtered[-1]  # Get the final filtered value
            
            # Update EEG data buffer
            self.eeg_data[ch][self.current_indices[ch]] = band_filtered
            self.current_indices[ch] = (self.current_indices[ch] + 1) % len(self.eeg_data[ch])
            
            # Update moving window for FFT
            self.moving_windows[ch].append(band_filtered)
            filtered_data.append(band_filtered)
        
        return filtered_data
    
    def get_display_data(self, channel):
        idx = self.current_indices[channel]
        return np.concatenate([self.eeg_data[channel][idx:], self.eeg_data[channel][:idx]])

class FFTAnalyzer:
    def __init__(self, num_channels, sampling_rate):
        self.num_channels = num_channels
        self.sampling_rate = sampling_rate
        
        # Calculate all the frequency bins
        self.freqs = np.fft.rfftfreq(FFT_WINDOW_SIZE, d=1.0/self.sampling_rate)
        self.freq_resolution = self.sampling_rate / FFT_WINDOW_SIZE
        self.fft_window = np.hanning(FFT_WINDOW_SIZE)     # Create a window function to make the FFT more accurate
        self.window_correction = np.sum(self.fft_window)  # For amplitude scaling
        
        # Smoothing buffers
        self.smoothing_buffers = [deque(maxlen=SMOOTHING_WINDOW_SIZE) for _ in range(num_channels)]
        
        print(f"[FFT Setup] Sampling Rate: {self.sampling_rate} Hz")
        print(f"[FFT Setup] Freq Resolution: {self.freq_resolution:.2f} Hz/bin")
        print(f"[FFT Setup] FFT Window Size: {FFT_WINDOW_SIZE} samples")
        
    def compute_fft(self, channel, time_data):
        if len(time_data) < FFT_WINDOW_SIZE:
            return None, None

        # Extract the most recent EEG Data (FFT_WINDOW_SIZE samples)
        signal_chunk = np.array(time_data[-FFT_WINDOW_SIZE:], dtype=np.float64)
        windowed_signal = signal_chunk * self.fft_window
        fft_result = np.fft.rfft(windowed_signal)
        fft_magnitude = np.abs(fft_result[1:]) * (2.0 / self.window_correction)  # Skip first value
        adjusted_freqs = self.freqs[1:]  # Skip DC frequency (0 Hz)
        
        # DEBUG: Print detected peak frequency
        if channel == 0:
            start_idx = int(2.0 * len(fft_magnitude) / (self.sampling_rate / 2))                       
            sorted_indices = np.argsort(fft_magnitude[start_idx:])[::-1] + start_idx
            peak1_idx = sorted_indices[0]
            peak1_freq = adjusted_freqs[peak1_idx]
            print(f"Peak Frequency: {peak1_freq:.2f} Hz")
        
        # Update smoothing buffer
        self.smoothing_buffers[channel].append(fft_magnitude)
        
        # Return smoothed FFT
        smoothed_fft = np.mean(self.smoothing_buffers[channel], axis=0) if self.smoothing_buffers[channel] else fft_magnitude
        return adjusted_freqs, smoothed_fft

    def calculate_band_power(self, fft_magnitudes, freq_range):
        low, high = freq_range
        mask = (self.freqs[1:] >= low) & (self.freqs[1:] <= high)   # Find which frequencies are in our desired range
        return np.sum(fft_magnitudes[mask] ** 2)  # Sum up the power in this range

    def compute_band_powers(self, channel, time_data):
        freqs, fft_mag = self.compute_fft(channel, time_data)
        if fft_mag is None:
            return None

        # Compute band powers (absolute)
        delta = self.calculate_band_power(fft_mag, (0.5, 4))
        theta = self.calculate_band_power(fft_mag, (4, 8))
        alpha = self.calculate_band_power(fft_mag, (8, 12))
        beta = self.calculate_band_power(fft_mag, (12, 30))
        gamma = self.calculate_band_power(fft_mag, (30, 45))
        
        total_power = delta + theta + alpha + beta + gamma
        
        # Return relative powers
        return {'delta': delta / total_power,'theta': theta / total_power,'alpha': alpha / total_power,'beta': beta / total_power,'gamma': gamma / total_power}

class SettingBox(QDialog):
    def __init__(self, num_channels, selected_eeg, selected_bp, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Channel Selection Settings")
        self.setGeometry(200, 200, 400, 400)
        
        self.layout = QVBoxLayout()
        
        # EEG Channel Selection
        self.eeg_label = QLabel("Select EEG Channels to Display:")
        self.layout.addWidget(self.eeg_label)
        
        self.eeg_checkboxes = []
        for i in range(num_channels):
            cb = QCheckBox(f"Channel {i+1}")
            cb.setChecked(i in selected_eeg)
            self.eeg_checkboxes.append(cb)
            self.layout.addWidget(cb)
        
        # Brainpower Channel Selection
        self.bp_label = QLabel("\nSelect Brainpower Channel:")
        self.layout.addWidget(self.bp_label)
        
        self.bp_combobox = QComboBox()
        for i in range(num_channels):
            self.bp_combobox.addItem(f"Channel {i+1}")
        self.bp_combobox.setCurrentIndex(selected_bp)
        self.layout.addWidget(self.bp_combobox)
        
        # OK Button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.layout.addWidget(self.ok_button)
        
        self.setLayout(self.layout)
    
    def validate_and_accept(self):
        # Ensure at least one EEG channel is selected
        eeg_selected = any(cb.isChecked() for cb in self.eeg_checkboxes)
        
        if not eeg_selected:
            self.eeg_checkboxes[0].setChecked(True)
        
        self.accept()

class EEGMonitor(QMainWindow):
    def __init__(self): 
        super().__init__()

        self.setWindowTitle("Real-Time EEG Monitor with FFT and Brainwave Power")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize LSL stream
        self.inlet = self.connect_to_lsl()
        if not self.inlet:
            sys.exit(0)
            
        self.stream_info = self.inlet.info()
        self.sampling_rate = int(self.stream_info.nominal_srate())
        self.num_channels = self.stream_info.channel_count()
        
        # Data processing components
        self.data_processor = DataProcessor(self.num_channels, self.sampling_rate)
        self.fft_analyzer = FFTAnalyzer(self.num_channels, self.sampling_rate)
        
        self.selected_eeg_channels = list(range(self.num_channels))
        self.selected_bp_channel = 0
        self.last_data_time = None
        self.stream_active = True
        
        self.colors = ['#FF0054', '#00FF8C', '#AA42FF', '#00FF47', '#FF8C19', '#FF00FF', '#00FFFF', '#FFFF00']
        
        self.init_ui()
        
        # Start update timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)
    
    def connect_to_lsl(self):
        print("Searching for available LSL streams...")
        available_streams = pylsl.resolve_streams()

        if not available_streams:
            print("No LSL streams found! Exiting...")
            return None

        inlet = None
        for stream in available_streams:
            try:
                inlet = pylsl.StreamInlet(stream)
                print(f"Connected to LSL stream: {stream.name()}")
                print(f"Sampling rate: {inlet.info().nominal_srate()} Hz")
                print(f"Number of channels: {inlet.info().channel_count()}")
                break
            except Exception as e:
                print(f"Failed to connect to {stream.name()}: {e}")

        if inlet is None:
            print("Unable to connect to any LSL stream!")
        
        return inlet
    
    def init_ui(self):
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left side: EEG plots with settings button
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        
        # Scroll area for EEG channels
        self.eeg_scroll = QScrollArea()
        self.eeg_scroll.setWidgetResizable(True)
        self.eeg_container = QWidget()
        self.eeg_layout = QVBoxLayout(self.eeg_container)
        self.eeg_layout.setSpacing(0)  # Remove spacing between plots
        self.eeg_scroll.setWidget(self.eeg_container)
        self.left_layout.addWidget(self.eeg_scroll)
        
        # Add a frame for the settings button in bottom right
        self.settings_frame = QFrame()
        self.settings_frame.setStyleSheet("QFrame { background-color: rgba(50, 50, 50, 150); border: 1px solid #888; border-radius: 5px; }")
        self.settings_frame_layout = QHBoxLayout(self.settings_frame)
        self.settings_frame_layout.setContentsMargins(5, 5, 5, 5)
        
        # Settings button with improved styling
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)

        self.settings_button.clicked.connect(self.show_settings)
        self.settings_frame_layout.addWidget(self.settings_button, alignment=Qt.AlignRight)
        
        self.left_layout.addWidget(self.settings_frame, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.left_container, stretch=1)

        # Right side: FFT and Brainpower
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        
        # FFT Plot
        self.fft_plot = PlotWidget()
        self.fft_plot.setBackground('black')
        self.fft_plot.showGrid(x=True, y=True, alpha=0.3)
        self.fft_plot.setLabel('bottom', 'Frequency (Hz)')
        self.fft_plot.setXRange(0, 50, padding=0)
        self.fft_plot.setYRange(0, 10000)
        self.right_layout.addWidget(self.fft_plot, stretch=1)
        
        # Brainpower Plot
        self.bar_chart_widget = pg.PlotWidget()
        self.bar_chart_widget.setBackground('black')
        self.bar_chart_widget.showGrid(x=True, y=True, alpha=0.3)
        self.bar_chart_widget.setLabel('bottom', 'Brainpower Bands')
        self.bar_chart_widget.setLabel('left', 'Relative Power')
        self.bar_chart_widget.setXRange(-0.5, 4.5)
        self.bar_chart_widget.setYRange(0, 1)
        self.bar_chart_widget.setMouseEnabled(x=False, y=False)
        self.brainwave_bars = pg.BarGraphItem(x=[0, 1, 2, 3, 4], height=[0, 0, 0, 0, 0], width=0.5, brushes=[pg.mkBrush(color) for color in self.colors[:5]])
        self.bar_chart_widget.addItem(self.brainwave_bars)
        self.bar_chart_widget.getAxis('bottom').setTicks([[(0, 'Delta'), (1, 'Theta'), (2, 'Alpha'), (3, 'Beta'), (4, 'Gamma')]])
        self.right_layout.addWidget(self.bar_chart_widget, stretch=1)
        
        self.main_layout.addWidget(self.right_container, stretch=1)
        self.setCentralWidget(self.central_widget)

        # Initialize plots
        self.eeg_plots = []
        self.eeg_curves = []
        self.fft_curves = []
        self.init_plots()
    
    def init_plots(self):
        # Clear existing plots
        for i in reversed(range(self.eeg_layout.count())): 
            widget = self.eeg_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        self.eeg_plots = []
        self.eeg_curves = []
        self.fft_plot.clear()
        self.fft_curves = []
        
        # Create EEG plots for all channels
        for ch in range(self.num_channels):
            plot = PlotWidget()
            plot.setBackground('black')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.setLabel('left', f'Ch {ch+1}', color='white')
            plot.getAxis('left').setTextPen('white')
            plot.getAxis('bottom').setTextPen('white')
            plot.setYRange(-5000, 5000, padding=0)
            plot.setXRange(0, DISPLAY_DURATION, padding=0)
            plot.setMouseEnabled(x=False, y=True)
            plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            color = self.colors[ch % len(self.colors)]
            pen = pg.mkPen(color=color, width=2)
            curve = plot.plot(pen=pen)
            
            self.eeg_layout.addWidget(plot)
            self.eeg_plots.append(plot)
            self.eeg_curves.append((ch, curve))
        
            plot.setVisible(False)     # Initially hide all plots
        
        # Create FFT curves for all channels
        for ch in range(self.num_channels):
            color = self.colors[ch % len(self.colors)]
            pen = pg.mkPen(color=color, width=2)
            self.fft_curves.append((ch, self.fft_plot.plot(pen=pen)))
        
        self.update_plot_visibility()
    
    def update_plot_visibility(self):
        for idx, (ch, curve) in enumerate(self.eeg_curves):
            visible = ch in self.selected_eeg_channels
            self.eeg_plots[idx].setVisible(visible)
            if visible:
                self.eeg_layout.setStretch(self.eeg_layout.indexOf(self.eeg_plots[idx]), 1)
        
        # Update FFT curve visibility
        for ch, curve in self.fft_curves:
            curve.setVisible(ch in self.selected_eeg_channels)
    
    def show_settings(self):
        dialog = SettingBox(self.num_channels, self.selected_eeg_channels, self.selected_bp_channel, self)
        if dialog.exec_():
            new_eeg_selection = [i for i, cb in enumerate(dialog.eeg_checkboxes) if cb.isChecked()]
            new_bp_channel = dialog.bp_combobox.currentIndex()
            
            if (set(new_eeg_selection) != set(self.selected_eeg_channels) or 
                (new_bp_channel != self.selected_bp_channel)):
                self.selected_eeg_channels = new_eeg_selection
                self.selected_bp_channel = new_bp_channel
                self.update_plot_visibility()
    
    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=50)
        if samples:
            self.last_data_time = time.time()
            
            for sample in samples:
                self.data_processor.process_sample(sample)
            
            self.update_eeg_plots()
            self.update_fft_plots()
            self.update_brainpower_plot()
        else:
            if self.last_data_time and (time.time() - self.last_data_time) > 2:
                self.stream_active = False
                print("LSL stream disconnected!")
                self.timer.stop()
                self.close()
    
    def update_eeg_plots(self):
        time_axis = np.linspace(0, DISPLAY_DURATION, len(self.data_processor.eeg_data[0]))
        for ch, curve in self.eeg_curves:
            if ch in self.selected_eeg_channels:
                display_data = self.data_processor.get_display_data(ch)
                curve.setData(time_axis, display_data)
    
    def update_fft_plots(self):
        for ch, curve in self.fft_curves:
            if ch in self.selected_eeg_channels:
                time_data = list(self.data_processor.moving_windows[ch])
                freqs, fft_result = self.fft_analyzer.compute_fft(ch, time_data)
                if fft_result is not None and freqs is not None:
                    curve.setData(freqs, fft_result)
    
    def update_brainpower_plot(self):
        ch = self.selected_bp_channel
        time_data = list(self.data_processor.moving_windows[ch])
        band_powers = self.fft_analyzer.compute_band_powers(ch, time_data)
        
        if band_powers is not None:
            relative_powers = [band_powers['delta'], band_powers['theta'], band_powers['alpha'], band_powers['beta'], band_powers['gamma']]
            self.brainwave_bars.setOpts(height=relative_powers)

def main():
    app = QApplication(sys.argv)
    window = EEGMonitor()  
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()