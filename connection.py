from chords_serial import Serial_USB
from chords_wifi import NPG_Wifi
from chords_ble import NPG_Ble
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
        self.lsl_outlet = None
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

    async def get_ble_device(self):
        devices = await NPG_Ble.scan_devices()
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
        self.lsl_outlet = StreamOutlet(info)
        print(f"LSL stream started: {num_channels} channels at {sampling_rate}Hz")
        self.num_channels = num_channels

    def setup_csv(self):
        if not self.csv_logging:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ChordsPy{timestamp}.csv"
        self.csv_file = open(filename, 'w', newline='')
        headers = ['Counter'] + [f'Channel{i+1}' for i in range(self.num_channels)]
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(headers)
        print(f"CSV logging started: {filename}")

    def log_to_csv(self, sample_data):
        if not self.csv_logging or not self.csv_writer:
            return
            
        self.sample_counter += 1
        row = [self.sample_counter] + sample_data
        self.csv_writer.writerow(row)

    def connect_ble(self, device_address=None):
        self.ble_connection = NPG_Ble()
        original_notification_handler = self.ble_connection.notification_handler
        
        def wrapped_notification_handler(sender, data):
            if len(data) == self.ble_connection.NEW_PACKET_LEN:
                if not self.lsl_outlet:
                    self.setup_lsl(num_channels=3, sampling_rate=500)
                    self.setup_csv()
                    print("BLE LSL stream started")
                
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
            
                        if self.lsl_outlet:             # Push to LSL
                            self.lsl_outlet.push_sample(channels)
                        self.log_to_csv(channels)       # Log to CSV
        
        self.ble_connection.notification_handler = wrapped_notification_handler
        
        if device_address:
            self.ble_connection.connect(device_address)
        else:
            selected_device = asyncio.run(self.get_ble_device())
            if not selected_device:
                return
            self.ble_connection.connect(selected_device.address)
        
        print("BLE connection established. Waiting for data...")

    def connect_usb(self):
        serial_connection = Serial_USB()
        if serial_connection.detect_hardware():
            self.num_channels = serial_connection.num_channels
            sampling_rate = serial_connection.supported_boards[serial_connection.board]["sampling_rate"]
            
            self.setup_lsl(self.num_channels, sampling_rate)
            self.setup_csv()
            
            original_read_data = serial_connection.read_data
            def wrapped_read_data():
                original_read_data()
                if hasattr(serial_connection, 'data') and self.lsl_outlet:
                    sample = serial_connection.data[:, -1]
                    self.lsl_outlet.push_sample(sample)
                    self.log_to_csv(sample.tolist())
            
            serial_connection.read_data = wrapped_read_data
            serial_connection.start_streaming()

    def connect_wifi(self):
        self.wifi_connection = NPG_Wifi()
        self.wifi_connection.connect()
        
        self.num_channels = self.wifi_connection.channels
        self.setup_lsl(self.num_channels, self.wifi_connection.sampling_rate)
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
                        
                        if self.lsl_outlet:           # Push to LSL
                            self.lsl_outlet.push_sample(channel_data)
                        self.log_to_csv(channel_data) # Log to CSV
                
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
        print("\nDisconnecting...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()