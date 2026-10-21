"""
EMG Weighing Scale - Estimate the weight of a held object from the EMG envelope after a quick calibration.

Calibration records the envelope with an empty hand or empty container (E_rest), then while holding 1 to 5 objects
of known mass M_i (E_i). The model
    W = A * (E - E_rest) ** p
is fitted to those points (fixed p = WEIGHT_EXPONENT for one weight, least-squares log-log fit for two or more),
and a held object is weighed by recording its envelope level E.

Filtering and the envelope method are the same as the "EMG with Envelope" app (emgenvelope.py), plus a mains notch.
Everything is applied causally (lfilter with stored state), so recorded envelope values never change retroactively.
"""
import math
import numpy as np
from scipy.signal import butter, iirnotch, lfilter, lfilter_zi
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QLineEdit, QProgressBar, QFrame)
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import pylsl
import sys
import time
from chordspy.emgenvelope import EMGMonitor

# Constants
WEIGHT_EXPONENT = 0.8          # Default exponent p (used for one known weight, or when the fit is unreliable)
P_MIN = 0.5                    # Smallest fitted exponent accepted
P_MAX = 1.5                    # Largest fitted exponent accepted
COUNTDOWN_SECONDS = 3          # Countdown before each recording so the user can get into position
RECORD_SECONDS = 20            # Seconds of envelope recorded for each calibration/weighing step
SETTLE_SECONDS = 5             # First seconds of each recording discarded (pickup and settling)
MOVING_AVERAGE_SECONDS = 2     # Window of the live moving average drawn over the envelope
STABILITY_LIMIT = 0.25         # Maximum std/mean of the analysed segment before asking the user to repeat
MIN_KNOWN_RATIO = 1.5          # Every E_i must be at least this many times E_rest
MIN_KNOWN_MASS_KG = 0.5        # Smallest accepted known calibration mass
MAX_KNOWN_WEIGHTS = 5          # Most known weights used in one calibration
ABOVE_RANGE_FACTOR = 1.5       # Warn when a prediction exceeds this many times the largest calibrated mass
DISPLAY_DURATION = 10          # Seconds of signal shown in the plots (same as EMG with Envelope)
HIGH_PASS_CUTOFF = 70.0        # High-pass cutoff in Hz (same as EMG with Envelope)
NOTCH_QUALITY = 30             # Notch quality factor (same as EEG with FFT)

# Session phases
PHASE_IDLE = "idle"            # Nothing in progress
PHASE_READY = "ready"          # Instructions/inputs shown, waiting for Start/Continue/Retry
PHASE_COUNTDOWN = "countdown"  # Countdown before recording
PHASE_RECORDING = "recording"  # Envelope is being recorded

# Session steps
STEP_SETUP = "setup"           # Calibration setup: entering the known weights
STEP_REST = "rest"             # Calibration: empty hand / empty container
STEP_KNOWN = "known"           # Calibration: one known weight
STEP_WEIGH = "weigh"           # Weighing an unknown object

INSTRUCTIONS = [
    "Keep the same electrode placement for calibration and weighing. Do not remove or adjust electrodes.",
    "Hold the object in your palm with the same grip every time.",
    "Keep the same arm posture: upper arm by your side, elbow at about 120 degrees.",
    "Keep your hand and arm still while recording.",
    "Do not rest your arm on anything. If you must use support, use the exact same support for calibration and all objects.",
    "Rest about 1 minute between holds to avoid fatigue.",
    "Breathe normally and avoid talking or tensing other muscles.",
]

CONTAINER_NOTE = ("You can hold an empty container or bag during this step. Then place each known weight, and later the "
                  "unknown object, inside the same container so the grip stays identical. All masses you enter and all "
                  "results will be the contents only, since the container is part of the baseline.")

COLOR_TEXT = "#222222"
COLOR_OK = "#1e8449"
COLOR_WARN = "#c0392b"

class EMGWeighingScale(QMainWindow):
    # Reuse the moving RMS envelope from the EMG with Envelope app instead of duplicating it
    calculate_moving_rms = EMGMonitor.calculate_moving_rms

    def __init__(self):
        super().__init__()

        self.setWindowTitle("EMG Weighing Scale")
        self.setGeometry(100, 100, 1200, 700)

        self.stream_active = True   # Flag to check if the stream is active
        self.last_data_time = None  # Variable to store the last data time

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
        self.num_channels = self.inlet.info().channel_count()
        print(f"Sampling rate: {self.sampling_rate} Hz")
        print(f"Number of channels: {self.num_channels}")

        # Signal settings
        self.channel = 0       # Selected channel index (Channel 1)
        self.notch_freq = 50   # Selected mains frequency in Hz
        self.b_hp, self.a_hp = butter(4, HIGH_PASS_CUTOFF / (0.5 * self.sampling_rate), btype='high')
        self.design_notch()
        self.rms_window_size = int(0.1 * self.sampling_rate)  # Same envelope window as EMG with Envelope
        self.avg_window_size = MOVING_AVERAGE_SECONDS * self.sampling_rate

        # Display buffers (circular, like EMG with Envelope)
        self.buffer_size = self.sampling_rate * DISPLAY_DURATION
        self.time_data = np.linspace(0, DISPLAY_DURATION, self.buffer_size)
        self.emg_data = np.zeros(self.buffer_size)
        self.envelope_data = np.zeros(self.buffer_size)
        self.average_data = np.zeros(self.buffer_size)

        # Calibration result (set by complete_calibration)
        self.calibrated = False
        self.e_rest = None
        self.cal_masses = None         # Known masses in ascending order
        self.cal_envelopes = None      # Envelope value E_i for each known mass
        self.fit_p = None
        self.fit_a = None
        self.fit_reliable = True

        # Calibration in progress
        self.pending_rest = None
        self.pending_masses = []
        self.pending_envelopes = []
        self.known_index = 0           # Index into pending_masses of the weight being recorded

        # Session state
        self.phase = PHASE_IDLE
        self.step = None
        self.countdown_end = 0.0
        self.recorded = []             # Envelope chunks recorded in the current step
        self.recorded_count = 0
        self.record_target = RECORD_SECONDS * self.sampling_rate

        self.init_ui()
        self.reset_signal_state()
        self.show_idle("Press Calibrate to begin.")

        # Timer for plot update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(15)

    # UI
    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Top controls: channel, notch and session buttons
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Channel:"))
        self.channel_combo = QComboBox()
        for i in range(self.num_channels):
            self.channel_combo.addItem(f"Channel {i+1}")
        self.channel_combo.setCurrentIndex(self.channel)
        self.channel_combo.currentIndexChanged.connect(self.on_channel_changed)
        controls.addWidget(self.channel_combo)

        controls.addSpacing(20)
        controls.addWidget(QLabel("Mains notch:"))
        self.notch_combo = QComboBox()
        self.notch_combo.addItems(["50 Hz", "60 Hz"])
        self.notch_combo.currentIndexChanged.connect(self.on_notch_changed)
        controls.addWidget(self.notch_combo)
        controls.addStretch()

        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self.start_calibration)
        controls.addWidget(self.calibrate_button)

        self.weigh_button = QPushButton("Weigh")
        self.weigh_button.setEnabled(False)   # Enabled once calibration is done
        self.weigh_button.clicked.connect(self.start_weighing)
        controls.addWidget(self.weigh_button)

        self.reset_button = QPushButton("Reset calibration")
        self.reset_button.clicked.connect(self.reset_calibration)
        controls.addWidget(self.reset_button)
        main_layout.addLayout(controls)

        body = QHBoxLayout()

        # Left: plots (same styling as EMG with Envelope)
        plots_layout = QVBoxLayout()
        self.emg_plot = PlotWidget(self)
        self.emg_plot.setBackground('w')
        self.emg_plot.showGrid(x=True, y=True)
        self.emg_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
        self.update_emg_title()

        self.envelope_plot = PlotWidget(self)
        self.envelope_plot.setBackground('w')
        self.envelope_plot.showGrid(x=True, y=True)
        self.envelope_plot.setMouseEnabled(x=False, y=False)  # Disable zoom
        self.envelope_plot.setTitle(f"EMG Envelope (Samples Average:10%) with {MOVING_AVERAGE_SECONDS} s Moving Average")
        self.envelope_plot.addLegend(offset=(10, 10), labelTextColor='k', brush=pg.mkBrush(255, 255, 255, 200))

        # Set fixed axis ranges
        self.emg_plot.setXRange(0, DISPLAY_DURATION, padding=0)
        self.envelope_plot.setXRange(0, DISPLAY_DURATION, padding=0)

        # Set y-axis limits based on sampling rate (same as EMG with Envelope)
        if self.sampling_rate == 250:
            self.emg_plot.setYRange(-((2**10)/2), ((2**10)/2), padding=0)  # for R3
            self.envelope_plot.setYRange(0, ((2**10)/2), padding=0)       # for R3
        elif self.sampling_rate == 500:
            self.emg_plot.setYRange(-((2**14)/2), ((2**14)/2), padding=0)  # for R4
            self.envelope_plot.setYRange(0, ((2**14)/2), padding=0)       # for R4

        self.emg_curve = self.emg_plot.plot(self.time_data, self.emg_data, pen=pg.mkPen('b', width=1))
        self.envelope_curve = self.envelope_plot.plot(self.time_data, self.envelope_data, pen=pg.mkPen('r', width=2), name="Envelope")
        self.average_curve = self.envelope_plot.plot(self.time_data, self.average_data, pen=pg.mkPen('k', width=2), name=f"{MOVING_AVERAGE_SECONDS} s average")

        # Numeric readout of the current moving average
        self.average_label = QLabel()
        self.average_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.average_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        plots_layout.addWidget(self.emg_plot)
        plots_layout.addWidget(self.average_label)
        plots_layout.addWidget(self.envelope_plot)
        body.addLayout(plots_layout, stretch=3)

        # Right: status/instruction panel
        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.StyledPanel)
        status_layout = QVBoxLayout(self.status_frame)

        self.step_label = QLabel()
        self.step_label.setWordWrap(True)
        self.step_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        status_layout.addWidget(self.step_label)

        self.big_label = QLabel()
        self.big_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.big_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.record_target)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        status_layout.addWidget(self.progress_bar)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setTextFormat(Qt.RichText)
        self.info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info_label.setStyleSheet("font-size: 13px;")
        status_layout.addWidget(self.info_label)

        # Known weights setup (calibration setup only): list of mass entries + Add weight button
        self.weights_panel = QWidget()
        weights_layout = QVBoxLayout(self.weights_panel)
        weights_layout.setContentsMargins(0, 0, 0, 0)
        self.weights_list_layout = QVBoxLayout()
        weights_layout.addLayout(self.weights_list_layout)
        self.add_weight_button = QPushButton("Add weight")
        self.add_weight_button.clicked.connect(lambda: self.add_weight_row())
        weights_layout.addWidget(self.add_weight_button, alignment=Qt.AlignLeft)
        self.weights_error_label = QLabel()
        self.weights_error_label.setWordWrap(True)
        self.weights_error_label.setStyleSheet(f"color: {COLOR_WARN};")
        weights_layout.addWidget(self.weights_error_label)
        self.weights_panel.hide()
        status_layout.addWidget(self.weights_panel)

        self.weight_rows = []   # (row widget, label, mass input, error label) for each known weight entry
        self.add_weight_row()   # Start with exactly one entry

        # Start / Continue / Retry / Cancel button for the current step
        self.action_button = QPushButton("Start")
        self.action_button.setStyleSheet("font-size: 16px; padding: 6px;")
        self.action_button.clicked.connect(self.on_action_clicked)
        self.action_button.hide()
        status_layout.addWidget(self.action_button)
        status_layout.addStretch()

        body.addWidget(self.status_frame, stretch=2)
        main_layout.addLayout(body)
        self.setCentralWidget(central_widget)

    def add_weight_row(self):
        if len(self.weight_rows) >= MAX_KNOWN_WEIGHTS:
            return
        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        input_layout = QHBoxLayout()
        label = QLabel()
        mass_input = QLineEdit()
        mass_input.setPlaceholderText(f"kg (minimum {MIN_KNOWN_MASS_KG})")
        mass_input.textChanged.connect(self.validate_weight_entries)
        input_layout.addWidget(label)
        input_layout.addWidget(mass_input)
        if self.weight_rows:   # Every entry except the first can be removed
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda _, r=row: self.remove_weight_row(r))
            input_layout.addWidget(remove_button)
        row_layout.addLayout(input_layout)
        error_label = QLabel()   # Shows why this entry is invalid
        error_label.setStyleSheet(f"color: {COLOR_WARN};")
        error_label.hide()
        row_layout.addWidget(error_label)
        self.weights_list_layout.addWidget(row)
        self.weight_rows.append((row, label, mass_input, error_label))
        self.refresh_weight_rows()

    def remove_weight_row(self, row):
        self.weight_rows = [entry for entry in self.weight_rows if entry[0] is not row]
        self.weights_list_layout.removeWidget(row)
        row.deleteLater()
        self.refresh_weight_rows()

    def refresh_weight_rows(self):
        for i, (_, label, _, _) in enumerate(self.weight_rows):
            label.setText(f"Known weight {i+1} (kg):")
        self.add_weight_button.setEnabled(len(self.weight_rows) < MAX_KNOWN_WEIGHTS)
        self.validate_weight_entries()

    def validate_weight_entries(self):
        # Check every entry as it is typed: numbers >= MIN_KNOWN_MASS_KG and no duplicates.
        # Invalid entries are marked, and Start stays disabled until all entries are valid.
        # Returns the masses in ascending order, or None if any entry is missing or invalid.
        masses = []
        all_valid = True
        for _, _, mass_input, error_label in self.weight_rows:
            text = mass_input.text().strip()
            try:
                mass = float(text)
            except ValueError:
                mass = None
            if not text:
                message = ""   # Not filled in yet: block Start without flagging it
            elif mass is None or not math.isfinite(mass):
                message = f"Invalid: enter a number (minimum {MIN_KNOWN_MASS_KG} kg)"
            elif mass < MIN_KNOWN_MASS_KG:
                message = f"Invalid: minimum {MIN_KNOWN_MASS_KG} kg required"
            else:
                message = None
                masses.append(mass)
            if message is not None:
                all_valid = False
            error_label.setText(message or "")
            error_label.setVisible(bool(message))
            mass_input.setStyleSheet(f"border: 1px solid {COLOR_WARN};" if message else "")

        duplicates = all_valid and len({round(m, 3) for m in masses}) != len(masses)
        self.weights_error_label.setText("Known weights must all be different." if duplicates else "")
        valid = all_valid and not duplicates
        if self.step == STEP_SETUP:
            self.action_button.setEnabled(valid)
        return sorted(masses) if valid else None

    def update_emg_title(self):
        self.emg_plot.setTitle(f"Filtered EMG Signal (High Pass:{int(HIGH_PASS_CUTOFF)} Hz, Notch:{self.notch_freq} Hz)")

    def set_status(self, step_text, big_text="", info_html="", big_color=COLOR_TEXT):
        self.step_label.setText(step_text)
        self.big_label.setText(big_text)
        self.big_label.setStyleSheet(f"font-size: 44px; font-weight: bold; color: {big_color};")
        self.big_label.setVisible(bool(big_text))
        self.info_label.setText(info_html)

    def show_action(self, text):
        self.action_button.setText(text)
        self.action_button.setEnabled(True)
        self.action_button.show()

    def set_busy(self, busy):
        # Lock controls that would disturb a countdown/recording in progress
        self.calibrate_button.setEnabled(not busy)
        self.reset_button.setEnabled(not busy)
        self.channel_combo.setEnabled(not busy)
        self.notch_combo.setEnabled(not busy)
        self.weigh_button.setEnabled(not busy and self.calibrated)

    def instructions_html(self):
        items = "".join(f"<li>{text}</li>" for text in INSTRUCTIONS)
        return f"<p><b>Before you start:</b></p><ul>{items}</ul>"

    def calibration_html(self):
        # Short calibration summary for the idle and weighing screens
        masses = ", ".join(f"{m:.2f}" for m in self.cal_masses)
        return (f"<p>E_rest = {self.e_rest:.1f}<br>Known weights: {masses} kg<br>"
                f"p = {self.fit_p:.3f}, A = {self.fit_a:.4g}</p>")

    def results_html(self):
        # Results table shown after calibration: known mass, envelope, predicted mass and error
        rows = ""
        errors = []
        for mass, envelope in zip(self.cal_masses, self.cal_envelopes):
            predicted = self.predict_weight(envelope)
            error = (predicted - mass) / mass * 100
            errors.append(abs(error))
            rows += (f"<tr><td align='right'>{mass:.2f}</td><td align='right'>{envelope:.1f}</td>"
                     f"<td align='right'>{predicted:.2f}</td><td align='right'>{error:+.1f}%</td></tr>")
        html = ("<table border='1' cellspacing='0' cellpadding='3'>"
                "<tr><th>Mass (kg)</th><th>Envelope</th><th>Predicted (kg)</th><th>Error</th></tr>"
                f"{rows}</table>")
        html += f"<p>E_rest = {self.e_rest:.1f}<br>p = {self.fit_p:.3f}, A = {self.fit_a:.4g}"
        if len(self.cal_masses) >= 3:
            html += f"<br>Average error: {np.mean(errors):.1f}%"
        html += "</p>"
        if not self.fit_reliable:
            html += (f"<p style='color:{COLOR_WARN}'>The fit was unreliable (exponent outside {P_MIN} to {P_MAX}), "
                     f"so p = {WEIGHT_EXPONENT} was used and only A was fitted.</p>")
        return html

    def show_idle(self, message):
        # Return to the idle state, summarising the current calibration
        self.phase = PHASE_IDLE
        self.step = None
        self.action_button.hide()
        self.weights_panel.hide()
        self.progress_bar.hide()
        self.set_busy(False)
        if self.calibrated:
            self.set_status("Calibrated", "", f"<p>{message}</p>{self.calibration_html()}<p>Press <b>Weigh</b> to weigh an object.</p>")
        else:
            self.set_status("Not calibrated", "", f"<p>{message}</p>")

    def step_title(self):
        total = len(self.pending_masses) + 1
        if self.step == STEP_REST:
            return f"Calibration - Step 1 of {total}: Empty hand / empty container"
        if self.step == STEP_KNOWN:
            mass = self.pending_masses[self.known_index]
            return f"Calibration - Step {self.known_index + 2} of {total}: Known weight {mass:.2f} kg"
        if self.step == STEP_WEIGH:
            return "Weighing"
        return "Calibration"

    def step_prompt(self):
        if self.step == STEP_REST:
            return "Get into position, hand empty (or holding the empty container)"
        if self.step == STEP_KNOWN:
            mass = self.pending_masses[self.known_index]
            return f"Pick up the {mass:.2f} kg known weight and hold it in position"
        return "Pick up the object and hold it in position"

    # Signal processing
    def design_notch(self):
        self.b_notch, self.a_notch = iirnotch(self.notch_freq, NOTCH_QUALITY, self.sampling_rate)

    def reset_signal_state(self):
        # Filter states are primed from the first sample after a reset to avoid a start-up transient
        self.zi_notch = None
        self.zi_hp = None
        self.rms_tail = np.zeros(self.rms_window_size - 1)   # Last window-1 rectified samples for the causal envelope
        self.avg_history = np.zeros(0)                       # Last window-1 envelope samples for the moving average
        self.emg_data[:] = 0
        self.envelope_data[:] = 0
        self.average_data[:] = 0
        self.current_index = 0
        self.average_label.setText(f"{MOVING_AVERAGE_SECONDS} s average: --")

    def process_chunk(self, raw):
        if self.zi_notch is None:
            self.zi_notch = lfilter_zi(self.b_notch, self.a_notch) * raw[0]
            self.zi_hp = lfilter_zi(self.b_hp, self.a_hp) * raw[0]

        # Causal, stateful filtering: notch then the same high-pass as EMG with Envelope
        notched, self.zi_notch = lfilter(self.b_notch, self.a_notch, raw, zi=self.zi_notch)
        filtered, self.zi_hp = lfilter(self.b_hp, self.a_hp, notched, zi=self.zi_hp)

        # Envelope: same method as EMG with Envelope (absolute value + moving RMS).
        # Prepending the previous window-1 samples makes the 'valid' part line up exactly with the new samples.
        extended = np.concatenate([self.rms_tail, np.abs(filtered)])
        envelope = self.calculate_moving_rms(extended, self.rms_window_size)[-len(filtered):]
        self.rms_tail = extended[-(self.rms_window_size - 1):]

        # Causal moving average of the envelope (uses fewer samples until the window has filled)
        history = np.concatenate([self.avg_history, envelope])
        cumsum = np.concatenate([[0.0], np.cumsum(history)])
        ends = np.arange(len(self.avg_history) + 1, len(history) + 1)
        starts = np.maximum(ends - self.avg_window_size, 0)
        moving_avg = (cumsum[ends] - cumsum[starts]) / (ends - starts)
        self.avg_history = history[-(self.avg_window_size - 1):]

        return filtered, envelope, moving_avg

    def update_plot(self):
        if self.inlet is None or not self.stream_active:
            return
        samples, _ = self.inlet.pull_chunk(timeout=0.0, max_samples=30)
        if samples:
            self.last_data_time = time.time()
            raw = np.array([sample[self.channel] for sample in samples], dtype=float)
            filtered, envelope, moving_avg = self.process_chunk(raw)

            # Overwrite the oldest data points in the circular buffers
            indices = (self.current_index + np.arange(len(raw))) % self.buffer_size
            self.emg_data[indices] = filtered
            self.envelope_data[indices] = envelope
            self.average_data[indices] = moving_avg
            self.current_index = (self.current_index + len(raw)) % self.buffer_size

            if self.phase == PHASE_RECORDING:
                self.recorded.append(envelope)
                self.recorded_count += len(envelope)

            # Update curves and readout
            self.emg_curve.setData(self.time_data, self.emg_data)
            self.envelope_curve.setData(self.time_data, self.envelope_data)
            self.average_curve.setData(self.time_data, self.average_data)
            self.average_label.setText(f"{MOVING_AVERAGE_SECONDS} s average: {moving_avg[-1]:.1f}")
        else:
            if self.last_data_time and (time.time() - self.last_data_time) > 2:
                self.stream_active = False
                print("LSL stream disconnected!")
                self.timer.stop()
                self.close()
                return

        self.update_session()

    # Weight model
    @staticmethod
    def fit_model(masses, deltas):
        # Fit W = A * delta ** p, where delta = E - E_rest. Returns (p, A, reliable).
        if len(masses) == 1:
            return WEIGHT_EXPONENT, float(masses[0] / deltas[0] ** WEIGHT_EXPONENT), True
        p, log_a = np.polyfit(np.log(deltas), np.log(masses), 1)   # ln(W) = p * ln(delta) + ln(A)
        if P_MIN <= p <= P_MAX:
            return float(p), float(np.exp(log_a)), True
        # Fitted exponent is implausible: keep the default exponent and refit only A (geometric mean)
        a = np.exp(np.mean(np.log(masses / deltas ** WEIGHT_EXPONENT)))
        return WEIGHT_EXPONENT, float(a), False

    def predict_weight(self, envelope_value):
        if envelope_value <= self.e_rest:
            return 0.0
        return self.fit_a * (envelope_value - self.e_rest) ** self.fit_p

    # Session flow
    def start_calibration(self):
        self.step = STEP_SETUP
        self.phase = PHASE_READY
        self.weights_panel.show()
        self.set_status("Calibration", "", self.instructions_html() +
                        f"<p><b>Empty hand step:</b> {CONTAINER_NOTE}</p>"
                        f"<p>Enter 1 to {MAX_KNOWN_WEIGHTS} known weights below (at least {MIN_KNOWN_MASS_KG} kg each, all different), "
                        "then press <b>Start</b>. Starting discards any previous calibration.</p>")
        self.show_action("Start")
        self.validate_weight_entries()   # Start is enabled only when every entry is valid

    def start_weighing(self):
        if not self.calibrated:
            return
        self.step = STEP_WEIGH
        self.phase = PHASE_READY
        self.weights_panel.hide()
        self.set_status("Weighing", "", self.instructions_html() + "<p>Press <b>Start</b> when ready.</p>")
        self.show_action("Start")

    def on_action_clicked(self):
        if self.phase in (PHASE_COUNTDOWN, PHASE_RECORDING):
            self.show_idle("Cancelled.")
            return
        if self.phase != PHASE_READY:
            return
        if self.step == STEP_SETUP:
            masses = self.validate_weight_entries()
            if masses is None:
                return
            self.clear_calibration()
            self.pending_masses = masses
            self.weights_panel.hide()
            self.step = STEP_REST
        self.begin_countdown()

    def begin_countdown(self):
        self.phase = PHASE_COUNTDOWN
        self.countdown_end = time.time() + COUNTDOWN_SECONDS
        self.set_busy(True)
        self.show_action("Cancel")
        self.set_status(self.step_title(), str(COUNTDOWN_SECONDS), f"<p><b>{self.step_prompt()}</b></p>")

    def begin_recording(self):
        self.phase = PHASE_RECORDING
        self.recorded = []
        self.recorded_count = 0
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.set_status(self.step_title(), f"0.0 / {RECORD_SECONDS} s")

    def update_session(self):
        if self.phase == PHASE_COUNTDOWN:
            remaining = self.countdown_end - time.time()
            if remaining > 0:
                self.big_label.setText(str(math.ceil(remaining)))
            else:
                self.begin_recording()
        elif self.phase == PHASE_RECORDING:
            if self.recorded_count >= self.record_target:
                self.finish_recording()
                return
            elapsed = self.recorded_count / self.sampling_rate
            self.big_label.setText(f"{elapsed:.1f} / {RECORD_SECONDS} s")
            self.progress_bar.setValue(self.recorded_count)
            if elapsed < SETTLE_SECONDS:
                self.info_label.setText(f"<p>Recording, keep your hand and arm still.<br>Settling (first {SETTLE_SECONDS} s are not used)...</p>")
            else:
                self.info_label.setText("<p>Recording, keep your hand and arm still.<br>Measuring...</p>")

    def analyse_segment(self, envelope):
        # Discard the settling period, then use the median as the step value and std/mean as stability
        segment = envelope[SETTLE_SECONDS * self.sampling_rate:]
        value = float(np.median(segment))
        mean = float(np.mean(segment))
        stability = float(np.std(segment) / mean) if mean > 0 else float('inf')
        return value, stability

    def finish_recording(self):
        envelope = np.concatenate(self.recorded)[:self.record_target]
        value, stability = self.analyse_segment(envelope)
        self.phase = PHASE_READY
        self.progress_bar.hide()
        self.set_busy(False)

        if stability > STABILITY_LIMIT:
            # Let the user repeat the same step
            self.set_status(self.step_title(), "Unstable",
                            f"<p style='color:{COLOR_WARN}'><b>Signal unstable, keep your arm still and repeat.</b></p>"
                            f"<p>Envelope: {value:.1f}<br>Stability: {stability:.2f} (limit {STABILITY_LIMIT})</p>"
                            "<p>Rest about 1 minute, then press <b>Retry</b>.</p>", COLOR_WARN)
            self.show_action("Retry")
            return

        if self.step == STEP_REST:
            self.finish_rest(value, stability)
        elif self.step == STEP_KNOWN:
            self.finish_known(value, stability)
        elif self.step == STEP_WEIGH:
            self.finish_weigh(value, stability)

    def prompt_next_known(self, message):
        mass = self.pending_masses[self.known_index]
        self.set_status(self.step_title(), "",
                        f"<p>{message}</p><p>Next: known weight {mass:.2f} kg.</p>"
                        "<p><b>Rest your arm, then press Continue.</b></p>")
        self.show_action("Continue")

    def finish_rest(self, value, stability):
        self.pending_rest = value
        self.pending_envelopes = []
        self.known_index = 0
        self.step = STEP_KNOWN
        self.prompt_next_known(f"Baseline recorded: E_rest = {value:.1f} (stability {stability:.2f}).")

    def finish_known(self, value, stability):
        i = self.known_index
        mass = self.pending_masses[i]

        # Validate this weight: clearly above rest and increasing with mass
        problem = None
        if value <= self.pending_rest or value < MIN_KNOWN_RATIO * self.pending_rest:
            problem = (f"Known weight {mass:.2f} kg did not raise muscle activity enough: E = {value:.1f}, "
                       f"needs at least {MIN_KNOWN_RATIO}x E_rest ({MIN_KNOWN_RATIO * self.pending_rest:.1f}). "
                       "Use a heavier object or check electrodes.")
        elif i > 0 and value <= self.pending_envelopes[i - 1]:
            previous_mass = self.pending_masses[i - 1]
            problem = (f"Known weight {mass:.2f} kg gave E = {value:.1f}, which is not above the "
                       f"{previous_mass:.2f} kg weight (E = {self.pending_envelopes[i - 1]:.1f}). "
                       "The envelope must increase with mass.")
        if problem:
            self.set_status(self.step_title(), "Not calibrated",
                            f"<p style='color:{COLOR_WARN}'><b>{problem}</b></p>"
                            "<p>Rest your arm, then press <b>Retry</b> to redo this step, "
                            "or press <b>Calibrate</b> to start over.</p>", COLOR_WARN)
            self.show_action("Retry")
            return

        self.pending_envelopes.append(value)
        self.known_index += 1
        if self.known_index < len(self.pending_masses):
            self.prompt_next_known(f"Known weight {mass:.2f} kg recorded: E = {value:.1f} (stability {stability:.2f}).")
            return
        self.complete_calibration()

    def complete_calibration(self):
        self.e_rest = self.pending_rest
        self.cal_masses = np.array(self.pending_masses)
        self.cal_envelopes = np.array(self.pending_envelopes)
        self.fit_p, self.fit_a, self.fit_reliable = self.fit_model(self.cal_masses, self.cal_envelopes - self.e_rest)
        self.calibrated = True
        self.show_idle("")
        self.set_status("Calibration complete", "Calibrated",
                        self.results_html() + "<p>Press <b>Weigh</b> to weigh an object.</p>", COLOR_OK)

    def finish_weigh(self, value, stability):
        weight = self.predict_weight(value)
        info = f"<p>Measured envelope: {value:.1f}<br>Stability: {stability:.2f}</p>"
        if value <= self.e_rest:
            info += "<p><b>No load detected.</b></p>"
        elif weight > ABOVE_RANGE_FACTOR * self.cal_masses.max():
            info += f"<p style='color:{COLOR_WARN}'>Above calibration range, estimate less reliable.</p>"
        info += f"{self.calibration_html()}<p>Press <b>Weigh</b> to weigh another object.</p>"

        self.show_idle("")
        self.set_status("Estimated weight", f"{weight:.2f} kg", info, COLOR_OK)

    def clear_calibration(self):
        self.calibrated = False
        self.e_rest = None
        self.cal_masses = None
        self.cal_envelopes = None
        self.fit_p = None
        self.fit_a = None
        self.fit_reliable = True
        self.pending_rest = None
        self.pending_masses = []
        self.pending_envelopes = []
        self.known_index = 0
        self.weigh_button.setEnabled(False)

    def reset_calibration(self):
        self.clear_calibration()
        self.show_idle("Calibration reset. Press Calibrate to begin.")

    def on_channel_changed(self, index):
        self.channel = index
        self.reset_signal_state()
        self.clear_calibration()
        self.show_idle(f"Channel {index + 1} selected. Filters and calibration were reset. Press Calibrate to begin.")

    def on_notch_changed(self, index):
        # Calibration values depend on the exact filter chain, so they are invalidated as well
        self.notch_freq = 50 if index == 0 else 60
        self.design_notch()
        self.update_emg_title()
        self.reset_signal_state()
        self.clear_calibration()
        self.show_idle(f"Notch set to {self.notch_freq} Hz. Filters and calibration were reset. Press Calibrate to begin.")

def main():
    app = pg.mkQApp()    # Enables high-DPI scaling, so plots scale correctly when moved to another monitor
    window = EMGWeighingScale()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
