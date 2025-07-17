"""
CHORDS USB Data Acquisition Script - This script supports detecting, connecting to, and reading data from
supported development boards via USB. It handles device identification, serial communication,
data packet parsing, and streaming management. The system supports multiple microcontroller
boards with different sampling rates and channel configurations.
"""

# Importing necessary libraries
import serial
import time
import numpy as np
import serial.tools.list_ports
import sys
import signal
import threading

class Chords_USB:
    """
    A class to interface with microcontroller development hardware for data acquisition.
    This class handles communication with various supported microcontroller boards, data streaming, and packet parsing. It provides methods for hardware detection, connection, and data acquisition.
    Attributes:
        SYNC_BYTE1 (int): First synchronization byte for packet identification
        SYNC_BYTE2 (int): Second synchronization byte for packet identification
        END_BYTE (int): End byte marking the end of a packet
        HEADER_LENGTH (int): Length of the packet header (sync bytes + counter)
        supported_boards (dict): Dictionary of supported boards with their specifications
        ser (serial.Serial): Serial connection object
        buffer (bytearray): Buffer for incoming data
        retry_limit (int): Maximum connection retries
        packet_length (int): Expected packet length for current board
        num_channels (int): Number of channels for current board
        data (numpy.ndarray): Array for storing channel data
        board (str): Detected board name
        streaming_active (bool): Streaming state flag
    """
    # Packet protocol constants
    SYNC_BYTE1 = 0xc7   # First synchronization byte
    SYNC_BYTE2 = 0x7c   # Second synchronization byte
    END_BYTE = 0x01     # End of packet marker
    HEADER_LENGTH = 3   # Length of packet header (sync bytes + counter)

    # Supported boards with their sampling rate and Number of Channels
    supported_boards = {
        "UNO-R3": {"sampling_rate": 250, "Num_channels": 6, "resolution": 10},
        "UNO-CLONE": {"sampling_rate": 250, "Num_channels": 6, "resolution": 10},
        "GENUINO-UNO": {"sampling_rate": 250, "Num_channels": 6, "resolution": 10},
        "UNO-R4": {"sampling_rate": 500, "Num_channels": 6, "resolution": 14},
        "RPI-PICO-RP2040": {"sampling_rate": 500, "Num_channels": 3, "resolution": 12},
        "NANO-CLONE": {"sampling_rate": 250, "Num_channels": 8, "resolution": 10},
        "NANO-CLASSIC": {"sampling_rate": 250, "Num_channels": 8, "resolution": 10},
        "STM32F4-BLACK-PILL": {"sampling_rate": 500, "Num_channels": 8, "resolution": 12},
        "STM32G4-CORE-BOARD": {"sampling_rate": 500, "Num_channels": 16, "resolution": 12},
        "MEGA-2560-R3": {"sampling_rate": 250, "Num_channels": 16, "resolution": 10},
        "MEGA-2560-CLONE": {"sampling_rate": 250, "Num_channels": 16, "resolution": 10},
        "GIGA-R1": {"sampling_rate": 500, "Num_channels": 6, "resolution": 16},
        "NPG-LITE": {"sampling_rate": 500, "Num_channels": 3, "resolution": 12},
    }

    def __init__(self):
        """
        Initialize the Chords_USB client and sets up serial connection attributes, data buffer, and installs signal handler for clean exit on interrupt signals.
        """
        self.ser = None               # Serial connection object
        self.buffer = bytearray()     # Buffer for incoming data
        self.retry_limit = 4          # Maximum connection retries
        self.packet_length = None     # Expected packet length for current board
        self.num_channels = None      # Number of data channels for current board
        self.data = None              # Numpy array for storing channel data
        self.board = ""               # Detected board name
        self.streaming_active = False # Streaming state flag

        # Only install signal handler in the main thread
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, self.signal_handler)

    def connect_hardware(self, port, baudrate, timeout=1):
        """
        Attempt to connect to hardware at the specified port and baudrate.
        Args:
            port (str): Serial port to connect to (e.g., 'COM3' or '/dev/ttyUSB0')
            baudrate (int): Baud rate for serial communication
            timeout (float, optional): Serial timeout in seconds. Defaults to 1.
        Returns:
            bool: True if connection and board identification succeeded, False otherwise
            
        The method performs the following steps:
        1. Establishes serial connection
        2. Sends 'WHORU' command
        3. Validates response against supported boards
        4. Configures parameters based on detected board
        """
        try:
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)   # Initialize serial connection
            retry_counter = 0
            response = None

            while retry_counter < self.retry_limit:   # Try to identify the board with retries
                self.ser.write(b'WHORU\n')            # Send identification command
                try:
                    response = self.ser.readline().strip().decode()
                except UnicodeDecodeError:
                    response = None

                if response in self.supported_boards:  # Board identified successfully
                    self.board = response
                    print(f"{response} detected at {port} with baudrate {baudrate}")
                    self.num_channels = self.supported_boards[self.board]["Num_channels"]
                    sampling_rate = self.supported_boards[self.board]["sampling_rate"]
                    self.packet_length = (2 * self.num_channels) + self.HEADER_LENGTH + 1    # Calculate expected packet length: 2 bytes per channel + header + end byte
                    self.data = np.zeros((self.num_channels, 2000))    # Initialize data buffer with 2000 samples per channel
                    return True

                retry_counter += 1

            # Connection failed after retries
            self.ser.close()
        except Exception as e:
            print(f"Connection Error: {e}")
        return False

    def detect_hardware(self, timeout=1):
        """
        Automatically detect and connect to supported hardware.        
        Scans available serial ports and tries common baud rates to find a supported CHORDS USB device.
        Args:
            timeout (float, optional): Serial timeout in seconds. Defaults to 1.
        Returns:
            bool: True if hardware was detected and connected, False otherwise
        """
        baudrates = [230400, 115200]                # Common baud rates to try with
        ports = serial.tools.list_ports.comports()  # Get list of available serial ports

        # Try all ports and baud rates
        for port in ports:
            for baud in baudrates:
                print(f"Trying {port.device} at {baud}...")
                if self.connect_hardware(port.device, baud, timeout):
                    return True

        print("Unable to detect supported hardware.")
        return False

    def send_command(self, command):
        """
        Send a command to the connected hardware.
        Args:
            command (str): Command to send (e.g., 'START', 'STOP')
        Returns:
            str: Response from hardware if available, None otherwise
        Note: Flushes input/output buffers before sending command to ensure clean communication
        """
        if self.ser and self.ser.is_open:
            self.ser.flushInput()   # Clear buffers to avoid stale data
            self.ser.flushOutput()  # Clear buffers to avoid stale data
            self.ser.write(f"{command}\n".encode())   # Send command with newline terminator
            time.sleep(0.1)         # Small delay to allow hardware response
            response = self.ser.readline().decode('utf-8', errors='ignore').strip()   # Read and decode response
            return response
        return None

    def read_data(self):
        """
        Read and process incoming data from the serial connection. Parses packets, validates them, and stores channel data in the data buffer.
        serial.SerialException raised: If serial port is disconnected or no data received
        """
        try:
            # Read available data or wait for at least 1 byte
            raw_data = self.ser.read(self.ser.in_waiting or 1)
            if raw_data == b'':
                raise serial.SerialException("Serial port disconnected or No data received.")
            self.buffer.extend(raw_data)

            # Process complete packets in the buffer
            while len(self.buffer) >= self.packet_length:
                sync_index = self.buffer.find(bytes([self.SYNC_BYTE1, self.SYNC_BYTE2]))   # Find synchronization bytes in buffer
                if sync_index == -1:
                    self.buffer.clear()    # No sync found, clear buffer
                    continue

                # Check if we have a complete packet
                if len(self.buffer) >= sync_index + self.packet_length:
                    packet = self.buffer[sync_index:sync_index + self.packet_length]
                    # Validate packet structure
                    if (packet[0] == self.SYNC_BYTE1 and packet[1] == self.SYNC_BYTE2 and packet[-1] == self.END_BYTE):
                        channel_data = []    # Extract channel data

                        for ch in range(self.num_channels):
                            # Combine high and low bytes for each channel
                            high_byte = packet[2 * ch + self.HEADER_LENGTH]
                            low_byte = packet[2 * ch + self.HEADER_LENGTH + 1]
                            value = (high_byte << 8) | low_byte
                            channel_data.append(float(value))

                        self.data = np.roll(self.data, -1, axis=1)    # Update data buffer (rolling window)
                        self.data[:, -1] = channel_data
                        del self.buffer[:sync_index + self.packet_length]    # Remove processed packet from buffer
                    else:
                        del self.buffer[:sync_index + 1]    # Invalid packet, skip the first sync byte
        except serial.SerialException:
            self.cleanup()

    def start_streaming(self):
        """
        Start continuous data streaming from the hardware by sending the 'START' command and enters a loop to continuously read and process incoming data until stopped or interrupted.
        """
        self.send_command('START')
        self.streaming_active = True
        try:
            while self.streaming_active:
                self.read_data()
        except KeyboardInterrupt:
            print("KeyboardInterrupt received.")
            self.cleanup()

    def stop_streaming(self):
        """
        Stop data streaming by sending 'STOP' Command to the hardware and sets the streaming flag to False.
        """
        self.streaming_active = False
        self.send_command('STOP')
        
    def cleanup(self):
        """
        Clean up resources and ensure proper shutdown.It stops streaming, closes serial connection, and handles any cleanup errors.
        """
        self.stop_streaming()
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def signal_handler(self, sig, frame):
        """
        Signal handler for interrupt signals (Ctrl+C).It ensures clean shutdown when the program is interrupted.
        """
        print("\nInterrupt received, shutting down...")
        self.cleanup()
        sys.exit(0)

    def start_timer(self):
        """
        Start the timer for packet counting and logging.
        """
        global start_time, last_ten_minute_time, total_packet_count, cumulative_packet_count
        current_time = time.time()
        start_time = current_time            # Session start time
        last_ten_minute_time = current_time  # 10-minute interval start time
        total_packet_count = 0               # Counter for packets in current second
        cumulative_packet_count = 0          # Counter for all packets

    def log_one_second_data(self):
        """
        Log data for one second intervals and displays: Number of packets received in the last second, Number of missing samples (if any)
        """
        global total_packet_count, samples_per_second, missing_samples
        samples_per_second = total_packet_count
        print(f"Data count for the last second: {total_packet_count} samples, "f"Missing samples: {missing_samples}")
        total_packet_count = 0  # Reset for next interval

    def log_ten_minute_data(self):
        """
        Log data for 10-minute intervals and displays: Total packets received, Actual sampling rate, Drift from expected rate
        """
        global cumulative_packet_count, last_ten_minute_time, supported_boards, board
        print(f"Total data count after 10 minutes: {cumulative_packet_count}")
        sampling_rate = cumulative_packet_count / (10 * 60)    # Calculate actual sampling rate
        print(f"Sampling rate: {sampling_rate:.2f} samples/second")
        expected_sampling_rate = supported_boards[board]["sampling_rate"]
        drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600    # Calculate drift from expected rate
        print(f"Drift: {drift:.2f} seconds/hour")
        
        # Reset counters
        cumulative_packet_count = 0
        last_ten_minute_time = time.time()

if __name__ == "__main__":
    client = Chords_USB()     # Create and run the USB client
    client.detect_hardware()  # Detect and connect to hardware
    client.start_streaming()  # Start streaming data