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
import threading

class Connection:
    def __init__(self):
        self.ble_connection = None
        self.wifi_connection = None
        self.usb_connection = None
        self.lsl_connection = None
        self.stream_name = "BioAmpDataStream"
        self.stream_type = "EXG"
        self.stream_format = "float32"
        self.stream_id = "UDL"
        self.last_sample = None
        self.ble_samples_received = 0
        self.ble_start_time = time.time()
        self.csv_file = None
        self.csv_writer = None
        self.sample_counter = 0
        self.num_channels = 0
        self.stream_active = False
        self.recording_active = False
        self.usb_thread = None
        self.usb_running = False

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
        self.num_channels = num_channels

    def start_csv_recording(self, filename=None):
        if self.recording_active:
            return False
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ChordsPy_{timestamp}.csv"
            elif not filename.endswith('.csv'):
                filename += '.csv'
                
            self.csv_file = open(filename, 'w', newline='')
            headers = ['Counter'] + [f'Channel{i+1}' for i in range(self.num_channels)]
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(headers)
            self.recording_active = True
            self.sample_counter = 0
            print(f"CSV recording started: {filename}")
            return True
        except Exception as e:
            print(f"Error starting CSV recording: {str(e)}")
            return False

    def stop_csv_recording(self):
        if not self.recording_active:
            return False
        
        try:
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
                self.csv_writer = None
            self.recording_active = False
            print("CSV recording stopped")
            return True
        except Exception as e:
            print(f"Error stopping CSV recording: {str(e)}")
            return False

    def log_to_csv(self, sample_data):
        if not self.recording_active or not self.csv_writer:
            return
            
        try:
            self.sample_counter += 1
            row = [self.sample_counter] + sample_data
            self.csv_writer.writerow(row)
        except Exception as e:
            print(f"Error writing to CSV: {str(e)}")
            self.stop_csv_recording()

    def connect_ble(self, device_address=None):
        self.ble_connection = Chords_BLE()
        original_notification_handler = self.ble_connection.notification_handler
            
        def notification_handler(sender, data):
            if len(data) == self.ble_connection.NEW_PACKET_LEN:
                if not self.lsl_connection:
                    self.setup_lsl(num_channels=3, sampling_rate=500)
                
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
                        if self.recording_active:
                            self.log_to_csv(channels)
            
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
            return True
        except Exception as e:
            print(f"BLE connection failed: {str(e)}")
            return False

    def usb_data_handler(self):
        while self.usb_running:
            try:
                if self.usb_connection and hasattr(self.usb_connection, 'ser') and self.usb_connection.ser.is_open:
                    self.usb_connection.read_data()
                    
                    if hasattr(self.usb_connection, 'data'):
                        sample = self.usb_connection.data[:, -1]
                        if self.lsl_connection:
                            self.lsl_connection.push_sample(sample)
                        if self.recording_active:
                            self.log_to_csv(sample.tolist())
                    time.sleep(0.001)  # Small delay to prevent CPU overload
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"USB data handler error: {str(e)}")
                break

    def connect_usb(self):
        self.usb_connection = Chords_USB()
        if self.usb_connection.detect_hardware():
            self.num_channels = self.usb_connection.num_channels
            sampling_rate = self.usb_connection.supported_boards[self.usb_connection.board]["sampling_rate"]
            
            self.setup_lsl(self.num_channels, sampling_rate)
            
            # Start the USB streaming command
            response = self.usb_connection.send_command('START')
            
            # Start the data handler thread
            self.usb_running = True
            self.usb_thread = threading.Thread(target=self.usb_data_handler)
            self.usb_thread.daemon = True
            self.usb_thread.start()
            
            print(f"USB connection established to {self.usb_connection.board}. Waiting for data...")
            return True
        return False

    def connect_wifi(self):
        self.wifi_connection = Chords_WIFI()
        self.wifi_connection.connect()
        
        self.num_channels = self.wifi_connection.channels
        sampling_rate = self.wifi_connection.sampling_rate

        if not self.lsl_connection:
            self.setup_lsl(self.num_channels, sampling_rate)
        
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
                        if self.recording_active:
                            self.log_to_csv(channel_data)
                    
        except KeyboardInterrupt:
            self.wifi_connection.cleanup()
            print("\nDisconnected")
        finally:
            self.stop_csv_recording()

    def cleanup(self):
        self.stop_csv_recording()

        if self.lsl_connection:
            self.lsl_connection = None
            print("LSL stream stopped")
        
        if self.usb_connection:
            try:
                self.usb_running = False  # Signal the thread to stop
                if self.usb_thread and self.usb_thread.is_alive():
                    self.usb_thread.join(timeout=1)
                
                if hasattr(self.usb_connection, 'ser') and self.usb_connection.ser.is_open:
                    self.usb_connection.send_command('STOP')
                    self.usb_connection.ser.close()
                print("USB connection closed")
            except Exception as e:
                print(f"Error closing USB connection: {str(e)}")
            finally:
                self.usb_connection = None
        
        if self.ble_connection:
            try:
                self.ble_connection.stop()
                print("BLE connection closed")
            except Exception as e:
                print(f"Error closing BLE connection: {str(e)}")
            finally:
                self.ble_connection = None
        
        if self.wifi_connection:
            try:
                self.wifi_connection.cleanup()
                print("WiFi connection closed")
            except Exception as e:
                print(f"Error closing WiFi connection: {str(e)}")
            finally:
                self.wifi_connection = None
        
        self.stream_active = False
        self.recording_active = False

    def __del__(self):
        self.cleanup()

def main():
    parser = argparse.ArgumentParser(description='Connect to device')
    parser.add_argument('--protocol', choices=['usb', 'wifi', 'ble'], required=True, help='Connection protocol')
    parser.add_argument('--ble-address', help='Direct BLE device address')
    args = parser.parse_args()

    manager = Connection()

    try:
        if args.protocol == 'usb':
            if manager.connect_usb():
                # Keep the main thread alive while USB is running
                while manager.usb_running:
                    time.sleep(1)
        elif args.protocol == 'wifi':
            manager.connect_wifi()
        elif args.protocol == 'ble':
            manager.connect_ble(args.ble_address)
    except KeyboardInterrupt:
        print("\nCleanup Completed.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        manager.cleanup()

if __name__ == '__main__':
    main()