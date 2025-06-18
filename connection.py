from chords_serial import Chords_USB
from chords_wifi import Chords_WIFI
from chords_ble import Chords_BLE
from pylsl import StreamInfo, StreamOutlet
import argparse
import time
import asyncio
import csv
from datetime import datetime
import threading
from collections import deque
from pylsl import local_clock
from pylsl import StreamInlet, resolve_stream
import numpy as np

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
        self.samples_received = 0
        self.start_time = time.time()
        self.csv_file = None
        self.csv_writer = None
        self.sample_counter = 0
        self.num_channels = 0
        self.sampling_rate = 0
        self.stream_active = False
        self.recording_active = False
        self.usb_thread = None
        self.ble_thread = None
        self.wifi_thread = None
        self.running = False
        self.sample_count = 0
        self.rate_window = deque(maxlen=10)
        self.last_timestamp = time.perf_counter()
        self.rate_update_interval = 0.5

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
        self.sampling_rate = sampling_rate

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

    def update_sample_rate(self):
        now = time.perf_counter()
        elapsed = now - self.last_timestamp
        self.sample_count += 1
        
        if elapsed >= self.rate_update_interval:
            current_rate = self.sample_count / elapsed
            self.rate_window.append(current_rate)
            
            # Print average rate
            avg_rate = sum(self.rate_window) / len(self.rate_window)
            print(f"\rCurrent sampling rate: {avg_rate:.2f} Hz", end="", flush=True)
            
            self.sample_count = 0
            self.last_timestamp = now

    def lsl_rate_checker(self, duration=2.0):
        try:
            streams = resolve_stream('type', self.stream_type)
            if not streams:
                print("No LSL stream found to verify.")
                return

            inlet = StreamInlet(streams[0])
            timestamps = []
            start_time = time.time()

            while time.time() - start_time < duration:
                sample, ts = inlet.pull_sample(timeout=1.0)
                if ts:
                    timestamps.append(ts)

            if len(timestamps) > 10:
                diffs = np.diff(timestamps)
                filtered_diffs = [d for d in diffs if d > 0]
                if filtered_diffs:
                    estimated_rate = 1 / np.mean(filtered_diffs)
                else:
                    print("\nAll timestamps had zero difference.")
            else:
                print("\nNot enough timestamps collected to estimate rate.")
        except Exception as e:
            print(f"Error in LSL rate check: {str(e)}")

    def ble_data_handler(self):
        TARGET_SAMPLE_RATE = 500.0
        SAMPLE_INTERVAL = 1.0 / TARGET_SAMPLE_RATE
        next_sample_time = local_clock()
        
        while self.running and self.ble_connection:
            try:
                if hasattr(self.ble_connection, 'data_available') and self.ble_connection.data_available:
                    current_time = local_clock()
                    
                    if current_time >= next_sample_time:
                        sample = self.ble_connection.get_latest_sample()
                        if sample:
                            channel_data = sample[:self.num_channels]
                            
                            # Calculate precise timestamp
                            sample_time = next_sample_time
                            next_sample_time += SAMPLE_INTERVAL
                            
                            # If we're falling behind, skip samples to catch up
                            if current_time > next_sample_time + SAMPLE_INTERVAL:
                                next_sample_time = current_time + SAMPLE_INTERVAL
                            
                            if self.lsl_connection:
                                self.lsl_connection.push_sample(channel_data, timestamp=sample_time)

                            self.update_sample_rate()

                            if self.recording_active:
                                self.log_to_csv(channel_data)
            except Exception as e:
                print(f"BLE data handler error: {str(e)}")
                break

    def wifi_data_handler(self):
        TARGET_SAMPLE_RATE = 500.0
        SAMPLE_INTERVAL = 1.0 / TARGET_SAMPLE_RATE
        next_sample_time = local_clock()
        
        while self.running and self.wifi_connection:
            try:
                if hasattr(self.wifi_connection, 'data_available') and self.wifi_connection.data_available:
                    current_time = local_clock()
                    
                    if current_time >= next_sample_time:
                        sample = self.wifi_connection.get_latest_sample()
                        if sample:
                            channel_data = sample[:self.num_channels]
                            
                            # Calculate precise timestamp
                            sample_time = next_sample_time
                            next_sample_time += SAMPLE_INTERVAL
                            
                            # If we're falling behind, skip samples to catch up
                            if current_time > next_sample_time + SAMPLE_INTERVAL:
                                next_sample_time = current_time + SAMPLE_INTERVAL
                            
                            if self.lsl_connection:
                                self.lsl_connection.push_sample(channel_data, timestamp=sample_time)

                            self.update_sample_rate()

                            if self.recording_active:
                                self.log_to_csv(channel_data)
            except Exception as e:
                print(f"WiFi data handler error: {str(e)}")
                break

    def usb_data_handler(self):
        TARGET_SAMPLE_RATE = 500.0
        SAMPLE_INTERVAL = 1.0 / TARGET_SAMPLE_RATE
        next_sample_time = local_clock()
        
        while self.running and self.usb_connection:
            try:
                if hasattr(self.usb_connection, 'ser') and self.usb_connection.ser.is_open:
                    self.usb_connection.read_data()
                    
                    if hasattr(self.usb_connection, 'data'):
                        current_time = local_clock()
                        
                        if current_time >= next_sample_time:
                            sample = self.usb_connection.data[:, -1]
                            channel_data = sample.tolist()

                            # Calculate precise timestamp
                            sample_time = next_sample_time
                            next_sample_time += SAMPLE_INTERVAL
                            
                            if current_time > next_sample_time + SAMPLE_INTERVAL:
                                next_sample_time = current_time + SAMPLE_INTERVAL
                            
                            if self.lsl_connection:
                                self.lsl_connection.push_sample(channel_data, timestamp=sample_time)

                            self.update_sample_rate()

                            if self.recording_active:
                                self.log_to_csv(channel_data)
            except Exception as e:
                print(f"USB data handler error: {str(e)}")
                break

    def connect_ble(self, device_address=None):
        self.ble_connection = Chords_BLE()
        
        try:
            if device_address:
                print(f"Connecting to BLE device: {device_address}")
                self.ble_connection.connect(device_address)
            else:
                selected_device = asyncio.run(self.get_ble_device())
                if not selected_device:
                    return False
                print(f"Connecting to BLE device: {selected_device.name}")
                self.ble_connection.connect(selected_device.address)
            
            self.num_channels = 3
            self.sampling_rate = 500
            self.setup_lsl(self.num_channels, self.sampling_rate)
            
            self.running = True
            self.ble_thread = threading.Thread(target=self.ble_data_handler)
            self.ble_thread.daemon = True
            self.ble_thread.start()
            
            threading.Thread(target=self.lsl_rate_checker, daemon=True).start()
            print("BLE connection established. Streaming data...")
            return True
        except Exception as e:
            print(f"BLE connection failed: {str(e)}")
            return False

    def connect_wifi(self):
        self.wifi_connection = Chords_WIFI()
        
        try:
            if not self.wifi_connection.connect():
                print("WiFi connection failed")
                return False
                
            self.num_channels = self.wifi_connection.channels
            self.sampling_rate = self.wifi_connection.sampling_rate
            self.setup_lsl(self.num_channels, self.sampling_rate)
            
            self.running = True
            self.wifi_thread = threading.Thread(target=self.wifi_data_handler)
            self.wifi_thread.daemon = True
            self.wifi_thread.start()
            
            threading.Thread(target=self.lsl_rate_checker, daemon=True).start()
            print("WiFi connection established. Streaming data...")
            return True
        except Exception as e:
            print(f"WiFi connection failed: {str(e)}")
            return False

    def connect_usb(self):
        self.usb_connection = Chords_USB()
        if not self.usb_connection.detect_hardware():
            return False
            
        self.num_channels = self.usb_connection.num_channels
        self.sampling_rate = self.usb_connection.supported_boards[self.usb_connection.board]["sampling_rate"]
        
        self.setup_lsl(self.num_channels, self.sampling_rate)
        
        # Start the USB streaming command
        self.usb_connection.send_command('START')
        
        # Start the data handler thread
        self.running = True
        self.usb_thread = threading.Thread(target=self.usb_data_handler)
        self.usb_thread.daemon = True
        self.usb_thread.start()

        threading.Thread(target=self.lsl_rate_checker, daemon=True).start()
        return True

    def cleanup(self):
        self.running = False
        self.stop_csv_recording()

        if self.lsl_connection:
            self.lsl_connection = None
            self.stream_active = False
            print("LSL stream stopped")
        
        threads = []
        if self.usb_thread and self.usb_thread.is_alive():
            threads.append(self.usb_thread)
        if self.ble_thread and self.ble_thread.is_alive():
            threads.append(self.ble_thread)
        if self.wifi_thread and self.wifi_thread.is_alive():
            threads.append(self.wifi_thread)
            
        for t in threads:
            t.join(timeout=1)
        
        # Clean up connections
        if self.usb_connection:
            try:
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
                while manager.running:
                    time.sleep(1)
        elif args.protocol == 'wifi':
            if manager.connect_wifi():
                while manager.running:
                    time.sleep(1)
        elif args.protocol == 'ble':
            if manager.connect_ble(args.ble_address):
                while manager.running:
                    time.sleep(1)
    except KeyboardInterrupt:
        print("\nCleanup Completed.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        manager.cleanup()

if __name__ == '__main__':
    main()