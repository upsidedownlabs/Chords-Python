import numpy as np
from collections import deque
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QGridLayout, QScrollArea, QPushButton, QDialog, QCheckBox, QLabel, QComboBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import sys
from scipy.signal import butter, iirnotch, lfilter, lfilter_zi
from scipy.fft import fft
import math
import time

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

        self.stream_active = True   # Flag to check if the stream is active
        self.last_data_time = None  # Variable to store the last data time
        self.selected_eeg_channels = []
        self.selected_bp_channel = 0

        # Main layout
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
        self.fft_plot.setAutoVisible(y=True)
        self.right_layout.addWidget(self.fft_plot, stretch=1)
        
        # Brainpower Plot
        self.bar_chart_widget = pg.PlotWidget()
        self.bar_chart_widget.setBackground('black')
        self.bar_chart_widget.showGrid(x=True, y=True, alpha=0.3)
        self.bar_chart_widget.setLabel('bottom', 'Brainpower Bands')
        self.bar_chart_widget.setXRange(-0.5, 4.5)
        self.bar_chart_widget.setMouseEnabled(x=False, y=False)
        self.brainwave_bars = pg.BarGraphItem(x=[0, 1, 2, 3, 4], height=[0, 0, 0, 0, 0], width=0.5)
        self.bar_chart_widget.addItem(self.brainwave_bars)
        self.bar_chart_widget.getAxis('bottom').setTicks([[(0, 'Delta'), (1, 'Theta'), (2, 'Alpha'), (3, 'Beta'), (4, 'Gamma')]])
        self.right_layout.addWidget(self.bar_chart_widget, stretch=1)
        
        self.main_layout.addWidget(self.right_container, stretch=1)
        self.setCentralWidget(self.central_widget)

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

        # Get stream info
        self.stream_info = self.inlet.info()
        self.sampling_rate = int(self.stream_info.nominal_srate())
        self.num_channels = self.stream_info.channel_count()
        print(f"Sampling rate: {self.sampling_rate} Hz")

        # Data and Buffers
        self.display_duration = 4  # seconds
        self.buffer_size = self.display_duration * self.sampling_rate
        self.eeg_data = [np.zeros(self.buffer_size) for _ in range(self.num_channels)]
        self.current_indices = [0 for _ in range(self.num_channels)]
        
        # Moving window for FFT (separate from display buffer)
        self.fft_window_size = 500  # samples for FFT calculation
        self.moving_windows = [deque(maxlen=self.fft_window_size) for _ in range(self.num_channels)]
        
        # Initialize filters
        self.b_notch, self.a_notch = iirnotch(50, 30, self.sampling_rate)
        self.b_band, self.a_band = butter(4, [0.5 / (self.sampling_rate / 2), 48.0 / (self.sampling_rate / 2)], btype='band')
        self.zi_notch = [lfilter_zi(self.b_notch, self.a_notch) * 0 for _ in range(self.num_channels)]
        self.zi_band = [lfilter_zi(self.b_band, self.a_band) * 0 for _ in range(self.num_channels)]

        self.colors = ['#FF0054', '#00FF8C', '#00FF47', '#AA42FF','#FF8C19','#FF00FF','#00FFFF','#FFFF00']
        
        # Initialize plots
        self.eeg_plots = []
        self.eeg_curves = []
        self.fft_curves = []
        
        self.selected_eeg_channels = list(range(self.num_channels))  # By default, select all channels
        self.selected_bp_channel = 0
        
        self.initialize_plots()
        
        # Timer for updating plots
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20) 
    
    def initialize_plots(self):
        for i in reversed(range(self.eeg_layout.count())): 
            widget = self.eeg_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        self.eeg_plots = []
        self.eeg_curves = []
        
        # Create EEG plots for all channels
        for ch in range(self.num_channels):
            plot = PlotWidget()
            plot.setBackground('black')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.setLabel('left', f'Ch {ch+1}', color='white')
            plot.getAxis('left').setTextPen('white')
            plot.getAxis('bottom').setTextPen('white')
            plot.setYRange(-5000, 5000, padding=0)
            plot.setXRange(0, self.display_duration, padding=0)
            plot.setMouseEnabled(x=False, y=True)
            plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            color = self.colors[ch % len(self.colors)]
            pen = pg.mkPen(color=color, width=2)
            curve = plot.plot(pen=pen)
            
            self.eeg_layout.addWidget(plot)
            self.eeg_plots.append(plot)
            self.eeg_curves.append((ch, curve))
        
            plot.setVisible(False)     # Initially hide all plots
        
        # Clear FFT plot and create curves for all channels
        self.fft_plot.clear()
        self.fft_curves = []
        
        for ch in range(self.num_channels):
            color = self.colors[ch % len(self.colors)]
            pen = pg.mkPen(color=color, width=2)
            self.fft_curves.append((ch, self.fft_plot.plot(pen=pen)))
        
        self.update_brainpower_colors()   # Update brainpower bar colors
        self.update_plot_visibility()     # Now show only the selected channels
    
    def update_plot_visibility(self):
        for plot in self.eeg_plots:
            plot.setVisible(False)
        
        # Show only selected channels and set stretch factors
        visible_count = len(self.selected_eeg_channels)
        for idx, (ch, curve) in enumerate(self.eeg_curves):
            if ch in self.selected_eeg_channels:
                self.eeg_plots[idx].setVisible(True)
                self.eeg_layout.setStretch(self.eeg_layout.indexOf(self.eeg_plots[idx]), 1)  # Set stretch factor to distribute space equally
        
        # Update FFT curve visibility
        for ch, curve in self.fft_curves:
            curve.setVisible(ch in self.selected_eeg_channels)
    
    def update_brainpower_colors(self):
        colors = [self.colors[0], self.colors[1], self.colors[2], self.colors[3], self.colors[4]]
        self.brainwave_bars.setOpts(brushes=[pg.mkBrush(color) for color in colors])
    
    def show_settings(self):
        dialog = SettingBox(self.num_channels, self.selected_eeg_channels, self.selected_bp_channel, self)
        if dialog.exec_():
            new_eeg_selection = [i for i, cb in enumerate(dialog.eeg_checkboxes) if cb.isChecked()]
            new_bp_channel = dialog.bp_combobox.currentIndex()
            
            # Only update if selections actually changed
            if (set(new_eeg_selection) != set(self.selected_eeg_channels) or (new_bp_channel != self.selected_bp_channel)):
                self.selected_eeg_channels = new_eeg_selection
                self.selected_bp_channel = new_bp_channel
                self.update_plot_visibility()      # Update plot visibility without recreating plots
                
                # Reset data buffers for the brainpower channel if it changed
                if new_bp_channel != self.selected_bp_channel:
                    self.reset_brainpower_buffer()
    
    def reset_brainpower_buffer(self):
        self.moving_windows[self.selected_bp_channel] = deque(maxlen=self.fft_window_size)
        self.zi_notch[self.selected_bp_channel] = lfilter_zi(self.b_notch, self.a_notch) * 0
        self.zi_band[self.selected_bp_channel] = lfilter_zi(self.b_band, self.a_band) * 0
    
    def update_plot(self):
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=50)
        if samples:
            self.last_data_time = time.time()
            
            for sample in samples:
                for ch in range(self.num_channels):
                    raw_point = sample[ch]
                    
                    # Apply filters
                    notch_filtered, self.zi_notch[ch] = lfilter(self.b_notch, self.a_notch, [raw_point], zi=self.zi_notch[ch])
                    band_filtered, self.zi_band[ch] = lfilter(self.b_band, self.a_band, notch_filtered, zi=self.zi_band[ch])
                    band_filtered = band_filtered[-1]
                    
                    # Update EEG data buffer (circular buffer)
                    self.eeg_data[ch][self.current_indices[ch]] = band_filtered
                    self.current_indices[ch] = (self.current_indices[ch] + 1) % self.buffer_size
                    
                    # Update moving window for FFT
                    self.moving_windows[ch].append(band_filtered)
            
            # Update EEG plots for visible channels
            time_axis = np.linspace(0, self.display_duration, self.buffer_size)
            for ch, curve in self.eeg_curves:
                if ch in self.selected_eeg_channels:
                    # Create properly ordered data from circular buffer
                    ordered_data = np.concatenate([
                        self.eeg_data[ch][self.current_indices[ch]:],  # From current index to end
                        self.eeg_data[ch][:self.current_indices[ch]]   # From start to current index
                    ])
                    curve.setData(time_axis, ordered_data)
            
            # Process FFT if we have enough data
            if len(self.moving_windows[0]) == self.fft_window_size:
                self.process_fft_and_brainpower()
        else:
            if self.last_data_time and (time.time() - self.last_data_time) > 2:
                self.stream_active = False
                print("LSL stream disconnected!")
                self.timer.stop()
                self.close()
    
    def process_fft_and_brainpower(self):
        # Calculate FFT for visible channels
        all_fft_results = []
        freqs = None
        
        for ch, curve in self.fft_curves:
            if ch not in self.selected_eeg_channels:
                continue
            if len(self.moving_windows[ch]) < 10:
                continue
                
            window = np.hanning(len(self.moving_windows[ch]))
            buffer_windowed = np.array(self.moving_windows[ch]) * window
            fft_result = np.abs(np.fft.rfft(buffer_windowed))
            fft_result /= len(buffer_windowed)
            
            if freqs is None:
                freqs = np.fft.rfftfreq(len(buffer_windowed), 1 / self.sampling_rate)
            
            min_len = min(len(freqs), len(fft_result))
            freqs = freqs[:min_len]
            fft_result = fft_result[:min_len]
            all_fft_results.append((ch, fft_result))
        
        # Update FFT plots for visible channels
        for ch, curve in self.fft_curves:
            if ch in self.selected_eeg_channels:
                fft_result = next((res for c, res in all_fft_results if c == ch), None)
                if fft_result is not None:
                    curve.setData(freqs, fft_result)
        
        # Calculate brainpower for selected channel
        if 0 <= self.selected_bp_channel < len(self.moving_windows):
            ch = self.selected_bp_channel
            if len(self.moving_windows[ch]) >= 10:
                window = np.hanning(len(self.moving_windows[ch]))
                buffer_windowed = np.array(self.moving_windows[ch]) * window
                fft_result = np.abs(np.fft.rfft(buffer_windowed))
                fft_result /= len(buffer_windowed)
                
                if freqs is None:
                    freqs = np.fft.rfftfreq(len(buffer_windowed), 1 / self.sampling_rate)
                
                min_len = min(len(freqs), len(fft_result))
                freqs = freqs[:min_len]
                fft_result = fft_result[:min_len]
                
                brainwave_power = self.calculate_brainwave_power(fft_result, freqs)
                self.brainwave_bars.setOpts(height=brainwave_power)
    
    def calculate_brainwave_power(self, fft_data, freqs):
        delta_range = (freqs >= 0.5) & (freqs <= 4)
        theta_range = (freqs >= 4) & (freqs <= 8)
        alpha_range = (freqs >= 8) & (freqs <= 13)
        beta_range = (freqs >= 13) & (freqs <= 30)
        gamma_range = (freqs >= 30) & (freqs <= 45)
        
        delta_power = math.sqrt(np.sum(fft_data[delta_range]**2)/4) if np.any(delta_range) else 0
        theta_power = math.sqrt(np.sum(fft_data[theta_range]**2)/5) if np.any(theta_range) else 0
        alpha_power = math.sqrt(np.sum(fft_data[alpha_range]**2)/6) if np.any(alpha_range) else 0
        beta_power = math.sqrt(np.sum(fft_data[beta_range]**2)/18) if np.any(beta_range) else 0
        gamma_power = math.sqrt(np.sum(fft_data[gamma_range]**2)/16) if np.any(gamma_range) else 0
        
        print(f"Brainpower (Ch {self.selected_bp_channel+1}): Delta: {delta_power:.2f} Theta: {theta_power:.2f} Alpha: {alpha_power:.2f} Beta: {beta_power:.2f} Gamma: {gamma_power:.2f}")
        return [delta_power, theta_power, alpha_power, beta_power, gamma_power]
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EEGMonitor()  
    window.show()
    sys.exit(app.exec_())