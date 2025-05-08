import serial
import time
import numpy as np
import serial.tools.list_ports
import sys
import signal
import threading

class Chords_USB:
    SYNC_BYTE1 = 0xc7
    SYNC_BYTE2 = 0x7c
    END_BYTE = 0x01
    HEADER_LENGTH = 3

    supported_boards = {
        "UNO-R3": {"sampling_rate": 250, "Num_channels": 6},
        "UNO-CLONE": {"sampling_rate": 250, "Num_channels": 6},
        "GENUINO-UNO": {"sampling_rate": 250, "Num_channels": 6},
        "UNO-R4": {"sampling_rate": 500, "Num_channels": 6},
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
        self.data = None
        self.board = ""

        # Only install signal handler in the main thread
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, self.signal_handler)

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
                    sampling_rate = self.supported_boards[self.board]["sampling_rate"]
                    self.packet_length = (2 * self.num_channels) + self.HEADER_LENGTH + 1
                    self.data = np.zeros((self.num_channels, 2000))
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

                if len(self.buffer) >= sync_index + self.packet_length:
                    packet = self.buffer[sync_index:sync_index + self.packet_length]
                    if packet[0] == self.SYNC_BYTE1 and packet[1] == self.SYNC_BYTE2 and packet[-1] == self.END_BYTE:
                        channel_data = []

                        for ch in range(self.num_channels):
                            high_byte = packet[2 * ch + self.HEADER_LENGTH]
                            low_byte = packet[2 * ch + self.HEADER_LENGTH + 1]
                            value = (high_byte << 8) | low_byte
                            channel_data.append(float(value))

                        self.data = np.roll(self.data, -1, axis=1)
                        self.data[:, -1] = channel_data
                        del self.buffer[:sync_index + self.packet_length]
                    else:
                        del self.buffer[:sync_index + 1]
        except serial.SerialException:
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

if __name__ == "__main__":
    client = Chords_USB()
    client.detect_hardware()
    client.start_streaming()