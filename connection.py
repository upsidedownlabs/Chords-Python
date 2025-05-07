from chords_serial import Chords_USB
from chords_wifi import Chords_WIFI
from chords_ble import Chords_BLE
from pylsl import StreamInfo, StreamOutlet
import argparse
import time
import sys
import asyncio
import csv
from datetime import datetime

class Connection:
    def __init__(self, csv_logging=False):
        self.ble_connection = None
        self.wifi_connection = None
        self.lsl_connection = None
        self.stream_name = "BioAmpDataStream"
        self.stream_type = "EXG"
        self.stream_format = "float32"
        self.stream_id = "UDL"
        self.last_sample = None
        self.ble_samples_received = 0
        self.ble_start_time = time.time()
        self.csv_logging = csv_logging
        self.csv_file = None
        self.csv_writer = None
        self.sample_counter = 0
        self.num_channels = 0
        self.stream_active = False

    async def get_ble_device(self):
        devices = await Chords_BLE.scan_devices()
        if not devices:
            print("No NPG devices found!")
            return None
        
        print("\nFound NPG Devices:")
        for i, device in enumerate(devices):
            print(f"[{i}] {device.name} - {device.address}")
        
        try:
            selection = int(input("\nEnter device number to connect: "))
            if 0 <= selection < len(devices):
                return devices[selection]
            print("Invalid selection!")
            return None
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return None

    def setup_lsl(self, num_channels, sampling_rate):
        info = StreamInfo(self.stream_name, self.stream_type, num_channels, sampling_rate, self.stream_format, self.stream_id)
        self.lsl_connection = StreamOutlet(info)
        print(f"LSL stream started: {num_channels} channels at {sampling_rate}Hz")
        self.stream_active = True
        print("Flag is set to True")
        self.num_channels = num_channels

    def setup_csv(self):
        if not self.csv_logging or self.csv_file:
            return  # Already set up or logging disabled
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ChordsPy_{timestamp}.csv"
            self.csv_file = open(filename, 'w', newline='')
            headers = ['Counter'] + [f'Channel{i+1}' for i in range(self.num_channels)]
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(headers)
            print(f"CSV logging started: {filename}")
        except Exception as e:
            print(f"Error setting up CSV logging: {str(e)}")
            self.csv_logging = False

    def log_to_csv(self, sample_data):
        if not self.csv_logging or not self.csv_writer:
            return
            
        try:
            self.sample_counter += 1
            row = [self.sample_counter] + sample_data
            self.csv_writer.writerow(row)
        except Exception as e:
            print(f"Error writing to CSV: {str(e)}")
            self.csv_logging = False

    def connect_ble(self, device_address=None):
        self.ble_connection = Chords_BLE()
        original_notification_handler = self.ble_connection.notification_handler
            
        def notification_handler(sender, data):
            if len(data) == self.ble_connection.NEW_PACKET_LEN:
                if not self.lsl_connection:
                    self.setup_lsl(num_channels=3, sampling_rate=500)
                    self.setup_csv()
                
                original_notification_handler(sender, data)
                
                for i in range(0, self.ble_connection.NEW_PACKET_LEN, self.ble_connection.SINGLE_SAMPLE_LEN):
                    sample_data = data[i:i+self.ble_connection.SINGLE_SAMPLE_LEN]
                    if len(sample_data) == self.ble_connection.SINGLE_SAMPLE_LEN:
                        channels = [
                            int.from_bytes(sample_data[1:3], byteorder='big', signed=True),
                            int.from_bytes(sample_data[3:5], byteorder='big', signed=True),
                            int.from_bytes(sample_data[5:7], byteorder='big', signed=True)
                        ]
                        self.last_sample = channels
                        self.ble_samples_received += 1
                
                        if self.lsl_connection:             # Push to LSL
                            self.lsl_connection.push_sample(channels)
                        self.log_to_csv(channels)           # Log to CSV
            
        self.ble_connection.notification_handler = notification_handler
            
        try:
            if device_address:
                print(f"Connecting to BLE device: {device_address}")
                self.ble_connection.connect(device_address)
            else:
                selected_device = asyncio.run(self.get_ble_device())
                if not selected_device:
                    return
                print(f"Connecting to BLE device: {selected_device.name}")
                self.ble_connection.connect(selected_device.address)
            
            print("BLE connection established. Waiting for data...")
        except Exception as e:
            print(f"BLE connection failed: {str(e)}")

    def connect_usb(self):
        serial_connection = Chords_USB()
        if serial_connection.detect_hardware():
            self.num_channels = serial_connection.num_channels
            sampling_rate = serial_connection.supported_boards[serial_connection.board]["sampling_rate"]
            
            self.setup_lsl(self.num_channels, sampling_rate)
            self.setup_csv()
            
            original_read_data = serial_connection.read_data
            def wrapped_read_data():
                original_read_data()
                if hasattr(serial_connection, 'data') and self.lsl_connection:
                    sample = serial_connection.data[:, -1]
                    self.lsl_connection.push_sample(sample)
                    self.log_to_csv(sample.tolist())
            
            serial_connection.read_data = wrapped_read_data
            serial_connection.start_streaming()

    def connect_wifi(self):
        self.wifi_connection = Chords_WIFI()
        self.wifi_connection.connect()
        
        self.num_channels = self.wifi_connection.channels
        sampling_rate = self.wifi_connection.sampling_rate

        if not self.lsl_connection:
            self.setup_lsl(self.num_channels, sampling_rate)
            if self.csv_logging:
                self.setup_csv()
        
        try:
            print("\nConnected! (Press Ctrl+C to stop)")
            while True:
                data = self.wifi_connection.ws.recv()
                
                if isinstance(data, (bytes, list)):
                    for i in range(0, len(data), self.wifi_connection.block_size):
                        block = data[i:i + self.wifi_connection.block_size]
                        if len(block) < self.wifi_connection.block_size:
                            continue
                        
                        channel_data = []
                        for ch in range(self.wifi_connection.channels):
                            offset = 1 + ch * 2
                            sample = int.from_bytes(block[offset:offset + 2], byteorder='big', signed=True)
                            channel_data.append(sample)
                        
                        if self.lsl_connection:                   # Push to LSL
                            self.lsl_connection.push_sample(channel_data)
                        if self.csv_logging and self.csv_writer:  # Only log if CSV is set up
                            self.log_to_csv(channel_data)
                    
        except KeyboardInterrupt:
            self.wifi_connection.disconnect()
            print("\nDisconnected")
        finally:
            if self.csv_file:
                self.csv_file.close()

    def __del__(self):
        if self.csv_file:
            self.csv_file.close()

def main():
    parser = argparse.ArgumentParser(description='Connect to device')
    parser.add_argument('--protocol', choices=['usb', 'wifi', 'ble'], required=True, help='Connection protocol')
    parser.add_argument('--ble-address', help='Direct BLE device address')
    parser.add_argument('--csv', action='store_true', help='Enable CSV logging')
    args = parser.parse_args()

    manager = Connection(csv_logging=args.csv)

    try:
        if args.protocol == 'usb':
            manager.connect_usb()
        elif args.protocol == 'wifi':
            manager.connect_wifi()
        elif args.protocol == 'ble':
            manager.connect_ble(args.ble_address)
    except KeyboardInterrupt:
        print("\nCleanup Completed.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()