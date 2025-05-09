import asyncio
from bleak import BleakScanner, BleakClient
import time
import sys
import argparse
import threading

class Chords_BLE:
    # Class constants
    DEVICE_NAME_PREFIX = "NPG"
    SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
    DATA_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
    CONTROL_CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
    
    # Packet parameters
    SINGLE_SAMPLE_LEN = 7   # (1 Counter + 3 Channels * 2 bytes)
    BLOCK_COUNT = 10
    NEW_PACKET_LEN = SINGLE_SAMPLE_LEN * BLOCK_COUNT

    def __init__(self):
        self.prev_unrolled_counter = None
        self.samples_received = 0
        self.start_time = None
        self.total_missing_samples = 0
        self.last_received_time = None
        self.DATA_TIMEOUT = 2.0
        self.client = None
        self.monitor_task = None
        self.print_rate_task = None
        self.running = False
        self.loop = None
        self.connection_event = threading.Event()
        self.stop_event = threading.Event()

    @classmethod
    async def scan_devices(cls):
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        filtered = [d for d in devices if d.name and d.name.startswith(cls.DEVICE_NAME_PREFIX)]
        
        if not filtered:
            print("No NPG devices found.")
            return []
        
        return filtered

    def process_sample(self, sample_data: bytearray):
        """Process a single EEG sample packet"""
        self.last_received_time = time.time()
        
        if len(sample_data) != self.SINGLE_SAMPLE_LEN:
            print("Unexpected sample length:", len(sample_data))
            return

        sample_counter = sample_data[0]
        if self.prev_unrolled_counter is None:
            self.prev_unrolled_counter = sample_counter
        else:
            last = self.prev_unrolled_counter % 256
            if sample_counter < last:
                current_unrolled = self.prev_unrolled_counter - last + sample_counter + 256
            else:
                current_unrolled = self.prev_unrolled_counter - last + sample_counter
            
            if current_unrolled != self.prev_unrolled_counter + 1:
                missing = current_unrolled - (self.prev_unrolled_counter + 1)
                print(f"Missing {missing} sample(s)")
                self.total_missing_samples += missing
            
            self.prev_unrolled_counter = current_unrolled
                   
        if self.start_time is None:
            self.start_time = time.time()
        
        channels = [
            int.from_bytes(sample_data[1:3], byteorder='big', signed=True),
            int.from_bytes(sample_data[3:5], byteorder='big', signed=True),
            int.from_bytes(sample_data[5:7], byteorder='big', signed=True)]
        
        self.samples_received += 1

    def notification_handler(self, sender, data: bytearray):
        """Handle incoming notifications from the BLE device"""
        try:
            if len(data) == self.NEW_PACKET_LEN:
                for i in range(0, self.NEW_PACKET_LEN, self.SINGLE_SAMPLE_LEN):
                    self.process_sample(data[i:i+self.SINGLE_SAMPLE_LEN])
            elif len(data) == self.SINGLE_SAMPLE_LEN:
                self.process_sample(data)
            else:
                print(f"Unexpected packet length: {len(data)} bytes")
        except Exception as e:
            print(f"Error processing data: {e}")

    async def print_rate(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(1)
            self.samples_received = 0

    async def monitor_connection(self):
        """Monitor the connection status and check for data interruptions"""
        while not self.stop_event.is_set():
            if self.last_received_time and (time.time() - self.last_received_time) > self.DATA_TIMEOUT:
                print("\nData Interrupted")
                print("Cleanup Completed.")
                self.running = False
                break
            if self.client and not self.client.is_connected:
                print("\nData Interrupted (Bluetooth disconnected)")
                print("Cleanup Completed.")
                self.running = False
                break
            await asyncio.sleep(0.5)

    async def async_connect(self, device_address):
        try:
            print(f"Attempting to connect to {device_address}...")
            
            self.client = BleakClient(device_address)
            await self.client.connect()
            
            if not self.client.is_connected:
                print("Failed to connect")
                return False
            
            print(f"Connected to {device_address}", flush=True)
            self.connection_event.set()
            
            self.last_received_time = time.time()
            self.monitor_task = asyncio.create_task(self.monitor_connection())
            self.print_rate_task = asyncio.create_task(self.print_rate())
            
            await self.client.write_gatt_char(self.CONTROL_CHAR_UUID, b"START", response=True)
            print("Sent START command")
            
            await self.client.start_notify(self.DATA_CHAR_UUID, self.notification_handler)
            print("Subscribed to data notifications")
            
            self.running = True
            while self.running and not self.stop_event.is_set():
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
        finally:
            await self.cleanup()

    async def cleanup(self):
        if self.monitor_task:
            self.monitor_task.cancel()
        if self.print_rate_task:
            self.print_rate_task.cancel()
        if self.client and self.client.is_connected:
            await self.client.disconnect()
        self.running = False
        self.connection_event.clear()

    def connect(self, device_address):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.async_connect(device_address))
        except Exception as e:
            print(f"Error in connection: {str(e)}")
            return False
        finally:
            if self.loop.is_running():
                self.loop.close()

    def stop(self):
        self.stop_event.set()
        self.running = False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="Scan for devices")
    parser.add_argument("--connect", type=str, help="Connect to device address")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    client = Chords_BLE()
    
    try:
        if args.scan:
            devices = asyncio.run(Chords_BLE.scan_devices())
            for dev in devices:
                print(f"DEVICE:{dev.name}|{dev.address}")
        elif args.connect:
            client.connect(args.connect)
            try:
                while client.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                client.stop()
        else:
            print("Please specify --scan or --connect")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)