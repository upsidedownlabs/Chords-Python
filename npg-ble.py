import asyncio
from bleak import BleakScanner, BleakClient
import time
from pylsl import StreamInfo, StreamOutlet
import sys
import argparse
import threading

# BLE parameters (must match your firmware)
DEVICE_NAME_PREFIX = "NPG"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
DATA_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
CONTROL_CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"

# Packet parameters
SINGLE_SAMPLE_LEN = 7
BLOCK_COUNT = 10
NEW_PACKET_LEN = SINGLE_SAMPLE_LEN * BLOCK_COUNT

class NPGBluetoothClient:
    def __init__(self):
        self.prev_unrolled_counter = None
        self.samples_received = 0
        self.start_time = None
        self.total_missing_samples = 0
        self.outlet = None
        self.last_received_time = None
        self.DATA_TIMEOUT = 2.0
        self.client = None
        self.monitor_task = None
        self.print_rate_task = None
        self.running = False
        self.loop = None
        self.connection_event = threading.Event()
        self.stop_event = threading.Event()

    def process_sample(self, sample_data: bytearray):
        self.last_received_time = time.time()
        
        if len(sample_data) != SINGLE_SAMPLE_LEN:
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
        
        if self.outlet:
            self.outlet.push_sample(channels)
        
        self.samples_received += 1
        
        if self.samples_received % 500 == 0:
            elapsed = time.time() - self.start_time
            print(f"Received {self.samples_received} samples in {elapsed:.2f}s")

    def notification_handler(self, sender, data: bytearray):
        try:
            if len(data) == NEW_PACKET_LEN:
                for i in range(0, NEW_PACKET_LEN, SINGLE_SAMPLE_LEN):
                    self.process_sample(data[i:i+SINGLE_SAMPLE_LEN])
            elif len(data) == SINGLE_SAMPLE_LEN:
                self.process_sample(data)
            else:
                print(f"Unexpected packet length: {len(data)} bytes")
        except Exception as e:
            print(f"Error processing data: {e}")

    async def print_rate(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(1)
            print(f"Samples per second: {self.samples_received}")
            self.samples_received = 0

    async def monitor_connection(self):
        while not self.stop_event.is_set():
            if self.last_received_time and (time.time() - self.last_received_time) > self.DATA_TIMEOUT:
                print("\nData Interrupted")
                self.running = False
                break
            if self.client and not self.client.is_connected:
                print("\nData Interrupted (Bluetooth disconnected)")
                self.running = False
                break
            await asyncio.sleep(0.5)

    async def async_connect(self, device_address):
        try:
            print(f"Attempting to connect to {device_address}...")
            
            # Set up LSL stream
            info = StreamInfo("NPG", "EXG", 3, 500, "int16", "npg1234")
            self.outlet = StreamOutlet(info)
            
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
            
            # Send start command
            await self.client.write_gatt_char(CONTROL_CHAR_UUID, b"START", response=True)
            print("Sent START command")
            
            # Subscribe to notifications
            await self.client.start_notify(DATA_CHAR_UUID, self.notification_handler)
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

async def scan_devices():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    filtered = [d for d in devices if d.name and d.name.startswith(DEVICE_NAME_PREFIX)]
    
    if not filtered:
        print("No devices found.")
        return
    
    for dev in filtered:
        print(f"DEVICE:{dev.name}|{dev.address}")

if __name__ == "__main__":
    args = parse_args()
    client = NPGBluetoothClient()
    
    try:
        if args.scan:
            asyncio.run(scan_devices())
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