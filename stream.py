import serial
import time
import numpy as np
import serial.tools.list_ports
import sys
import threading
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from scipy.fft import rfft, rfftfreq

class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = np.zeros(size, dtype=np.float32)
        self.write_index = 0
        self.read_index = 0
        self.count = 0
        self.lock = threading.Lock()
    
    def write(self, data):
        with self.lock:
            if isinstance(data, (list, np.ndarray)):
                for value in data:
                    self.buffer[self.write_index] = value
                    self.write_index = (self.write_index + 1) % self.size
                    if self.count < self.size:
                        self.count += 1
            else:
                self.buffer[self.write_index] = data
                self.write_index = (self.write_index + 1) % self.size
                if self.count < self.size:
                    self.count += 1
    
    def read_block(self, block_size, start_offset=0):
        with self.lock:
            if self.count < block_size:
                return None
            
            # Calculate the actual read start position
            read_start = (self.read_index + start_offset) % self.size
            # Read the block
            if read_start + block_size <= self.size:
                return self.buffer[read_start:read_start + block_size].copy()
            else:
                first_part = self.buffer[read_start:].copy()
                second_part = self.buffer[:block_size - len(first_part)].copy()
                return np.concatenate([first_part, second_part])
    
    def advance_read_pointer(self, count=1):
        with self.lock:
            self.read_index = (self.read_index + count) % self.size
            self.count = max(0, self.count - count)
    
    def get_count(self):
        with self.lock:
            return self.count
    
    def is_full(self):
        with self.lock:
            return self.count >= self.size

class Chords_USB:
    SYNC_BYTE1 = 0xc7
    SYNC_BYTE2 = 0x7c
    END_BYTE = 0x01
    HEADER_LENGTH = 3

    supported_boards = {
        "UNO-R3": {"sampling_rate": 250, "Num_channels": 6},
        "UNO-CLONE": {"sampling_rate": 250, "Num_channels": 6},
        "GENUINO-UNO": {"sampling_rate": 250, "Num_channels": 6},
        "UNO-R4": {"sampling_rate": 512, "Num_channels": 6},
        "RPI-PICO-RP2040": {"sampling_rate": 500, "Num_channels": 3},
        "NANO-CLONE": {"sampling_rate": 250, "Num_channels": 8},
        "NANO-CLASSIC": {"sampling_rate": 250, "Num_channels": 8},
        "STM32F4-BLACK-PILL": {"sampling_rate": 500, "Num_channels": 8},
        "STM32G4-CORE-BOARD": {"sampling_rate": 500, "Num_channels": 16},
        "MEGA-2560-R3": {"sampling_rate": 250, "Num_channels": 16},
        "MEGA-2560-CLONE": {"sampling_rate": 250, "Num_channels": 16},
        "GIGA-R1": {"sampling_rate": 500, "Num_channels": 6},
        "NPG-LITE": {"sampling_rate": 500, "Num_channels": 3},
    }

    def __init__(self):
        self.ser = None
        self.buffer = bytearray()
        self.retry_limit = 4
        self.packet_length = None
        self.num_channels = None
        self.board = ""
        self.streaming_active = False
        self.sampling_rate = 512
        
        # Circular buffers
        self.serial_buffer = CircularBuffer(512)  # 512 samples for serial data
        self.fft_ready = threading.Event()
        self.fft_counter = 0
        self.overlap_samples = 16  # Overlap for smoother FFT updates

    def connect_hardware(self, port, baudrate, timeout=1):
        try:
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            retry_counter = 0
            response = None

            while retry_counter < self.retry_limit:
                self.ser.write(b'WHORU\n')
                try:
                    response = self.ser.readline().strip().decode()
                except UnicodeDecodeError:
                    response = None

                if response in self.supported_boards:
                    self.board = response
                    print(f"{response} detected at {port} with baudrate {baudrate}")
                    self.num_channels = self.supported_boards[self.board]["Num_channels"]
                    self.sampling_rate = self.supported_boards[self.board]["sampling_rate"]
                    self.packet_length = (2 * self.num_channels) + self.HEADER_LENGTH + 1
                    return True

                retry_counter += 1

            self.ser.close()
        except Exception as e:
            print(f"Connection Error: {e}")
        return False

    def detect_hardware(self, timeout=1):
        baudrates = [230400, 115200]
        ports = serial.tools.list_ports.comports()

        for port in ports:
            for baud in baudrates:
                print(f"Trying {port.device} at {baud}...")
                if self.connect_hardware(port.device, baud, timeout):
                    return True

        print("Unable to detect supported hardware.")
        return False

    def send_command(self, command):
        if self.ser and self.ser.is_open:
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(f"{command}\n".encode())
            time.sleep(0.1)
            response = self.ser.readline().decode('utf-8', errors='ignore').strip()
            return response
        return None

    def read_data(self):
        try:
            raw_data = self.ser.read(self.ser.in_waiting or 1)
            if raw_data == b'':
                raise serial.SerialException("Serial port disconnected or No data received.")
            self.buffer.extend(raw_data)

            while len(self.buffer) >= self.packet_length:
                sync_index = self.buffer.find(bytes([self.SYNC_BYTE1, self.SYNC_BYTE2]))
                if sync_index == -1:
                    self.buffer.clear()
                    continue

                if len(self.buffer) >= (sync_index + self.packet_length):
                    packet = self.buffer[sync_index:sync_index + self.packet_length]
                    if packet[0] == self.SYNC_BYTE1 and packet[1] == self.SYNC_BYTE2 and packet[-1] == self.END_BYTE:
                        channel_data = []

                        for ch in range(self.num_channels):
                            high_byte = packet[2 * ch + self.HEADER_LENGTH]
                            low_byte = packet[2 * ch + self.HEADER_LENGTH + 1]
                            value = (high_byte << 8) | low_byte
                            channel_data.append(float(value))

                        self.serial_buffer.write(channel_data[0])
                        
                        if self.serial_buffer.get_count() >= 512: # Set FFT ready flag when we have enough data
                            self.fft_ready.set()
                        
                        del self.buffer[:sync_index + self.packet_length]
                    else:
                        del self.buffer[:sync_index + 1]
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.cleanup()

    def start_streaming(self):
        self.send_command('START')
        self.streaming_active = True
        try:
            while self.streaming_active:
                self.read_data()
        except KeyboardInterrupt:
            print("KeyboardInterrupt received.")
            self.cleanup()

    def stop_streaming(self):
        self.streaming_active = False
        self.send_command('STOP')
        
    def cleanup(self):
        self.stop_streaming()
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def signal_handler(self, sig, frame):
        self.cleanup()
        sys.exit(0)

class FFTProcessor:
    def __init__(self, serial_reader):
        self.serial_reader = serial_reader
        self.fft_buffer_size = 512
        self.overlap_samples = 16
        self.latest_fft_data = None
        self.latest_freqs = None
        self.latest_raw_data = None
        self.processing_active = False
        self.data_lock = threading.Lock()
        
    def start_processing(self):
        self.processing_active = True
        processing_thread = threading.Thread(target=self._process_fft)
        processing_thread.daemon = True
        processing_thread.start()
        
    def stop_processing(self):
        self.processing_active = False
        
    def _process_fft(self):
        fft_counter = 0
        
        while self.processing_active:
            if self.serial_reader.serial_buffer.get_count() >= self.fft_buffer_size:
                offset = (fft_counter * self.overlap_samples) % self.fft_buffer_size
                fft_data = self.serial_reader.serial_buffer.read_block(self.fft_buffer_size, start_offset=offset)
                
                if fft_data is not None:
                    fft_data = fft_data - np.mean(fft_data)
                    window = np.hanning(len(fft_data))
                    windowed_signal = fft_data * window
                    fft_result = rfft(windowed_signal)
                    freqs = rfftfreq(len(fft_data), 1.0/self.serial_reader.sampling_rate)
                    power_spectrum = np.abs(fft_result)**2
                    power_spectrum = power_spectrum / (self.serial_reader.sampling_rate * np.sum(window**2))
                    
                    with self.data_lock:
                        self.latest_fft_data = power_spectrum
                        self.latest_freqs = freqs
                        self.latest_raw_data = fft_data
                    
                    fft_counter += 1
                    if len(power_spectrum) > 5:
                        start_idx = int(2.0 * len(power_spectrum) / (self.serial_reader.sampling_rate / 2))
                        
                        sorted_indices = np.argsort(power_spectrum[start_idx:])[::-1] + start_idx
                        peak1_idx = sorted_indices[0]
                        peak1_freq = freqs[peak1_idx]
                        print(f"Peak Frequency: {peak1_freq:.2f} Hz")
                
                self.serial_reader.serial_buffer.advance_read_pointer(self.overlap_samples)
                
            else:
                time.sleep(0.01)
    
    def get_latest_data(self):
        with self.data_lock:
            return (
                self.latest_raw_data.copy() if self.latest_raw_data is not None else None,
                self.latest_fft_data.copy() if self.latest_fft_data is not None else None,
                self.latest_freqs.copy() if self.latest_freqs is not None else None
            )

class EEGMonitor(QtWidgets.QMainWindow):
    def __init__(self, serial_reader, fft_processor):
        super().__init__()
        self.serial_reader = serial_reader
        self.fft_processor = fft_processor
        self.setWindowTitle("EEG Monitor")
        self.setGeometry(100, 100, 1200, 600)

        self.buffer_size = self.serial_reader.sampling_rate  # 1 second buffer
        self.chunk_size = 5  # Chunk of new samples to read each update
        self.raw_data_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.x_vals = np.arange(self.buffer_size)

        self.init_ui()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)  # Every 20 ms

    def init_ui(self):
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QHBoxLayout(self.central_widget)

        # Raw EEG plot
        self.raw_plot = pg.PlotWidget(title="Raw EEG Data")
        self.raw_plot.setLabel('left', 'Amplitude')
        self.raw_plot.setLabel('bottom', 'Sample')
        self.raw_plot.setYRange(0, 10000)
        self.raw_curve = self.raw_plot.plot(self.x_vals, self.raw_data_buffer, pen='y')

        # FFT plot
        self.fft_plot = pg.PlotWidget(title="Real-time FFT")
        self.fft_plot.setLabel('left', 'Power')
        self.fft_plot.setLabel('bottom', 'Frequency (Hz)')
        self.fft_plot.setXRange(0, 50)
        self.fft_plot.setYRange(0, 200000)
        self.fft_curve = self.fft_plot.plot(pen='c')

        self.layout.addWidget(self.raw_plot)
        self.layout.addWidget(self.fft_plot)

    def update(self):
        try:
            new_data = self.serial_reader.serial_buffer.read_block(self.chunk_size)
            if new_data is not None and len(new_data) == self.chunk_size:
                self.raw_data_buffer = np.roll(self.raw_data_buffer, -self.chunk_size)
                self.raw_data_buffer[-self.chunk_size:] = new_data
                self.raw_curve.setData(self.x_vals, self.raw_data_buffer)

            _, fft_data, freqs = self.fft_processor.get_latest_data()
            if fft_data is not None and freqs is not None:
                self.fft_curve.setData(freqs, fft_data)

        except Exception as e:
            print(f"Error in update: {e}")

def main():
    serial_reader = Chords_USB()
    if not serial_reader.detect_hardware():
        print("Failed to detect hardware. Exiting...")
        return
    
    fft_processor = FFTProcessor(serial_reader)
    
    serial_thread = threading.Thread(target=serial_reader.start_streaming)
    serial_thread.daemon = True
    serial_thread.start()
    
    fft_processor.start_processing()
    
    app = QtWidgets.QApplication(sys.argv)
    window = EEGMonitor(serial_reader, fft_processor)
    window.show()

    try:
        sys.exit(app.exec_())
    finally:
        fft_processor.stop_processing()
        serial_reader.cleanup()

if __name__ == "__main__":
    main()