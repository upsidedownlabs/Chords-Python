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
SINGLE_SAMPLE_LEN = 7   # (1 Counter + 3 Channels * 2 bytes)
BLOCK_COUNT = 10
NEW_PACKET_LEN = SINGLE_SAMPLE_LEN * BLOCK_COUNT

class NPGBluetoothClient:
    def __init__(self):
        self.prev_unrolled_counter = None          # Previous Counter
        self.samples_received = 0                  # Number of Samples received
        self.start_time = None                     # Start time of the first sample
        self.total_missing_samples = 0             # Total missing samples
        self.outlet = None                         # LSL outlet
        self.last_received_time = None             # Last time a sample was received
        self.DATA_TIMEOUT = 2.0                    # Timeout for considering data interrupted
        self.client = None                         # Bleak client instance
        self.monitor_task = None                   # Task for monitoring connection
        self.print_rate_task = None                # Task for printing sample rate
        self.running = False                       # Flag indicating if NPGBluetoothClient is running or not
        self.loop = None                           # Event loop for asyncio
        self.connection_event = threading.Event()  # Event for connection status
        self.stop_event = threading.Event()        # Event for stopping all operations

    def process_sample(self, sample_data: bytearray):
        """Process a single EEG sample packet"""
        self.last_received_time = time.time()
        
        # Validate Sample Length 
        if len(sample_data) != SINGLE_SAMPLE_LEN:
            print("Unexpected sample length:", len(sample_data))
            return

        # Extract and Validate Sample Counter   
        sample_counter = sample_data[0]
        if self.prev_unrolled_counter is None:
            self.prev_unrolled_counter = sample_counter
        else:
            # Calculate unrolled counter (handling 0-255)
            last = self.prev_unrolled_counter % 256
            if sample_counter < last:
                current_unrolled = self.prev_unrolled_counter - last + sample_counter + 256
            else:
                current_unrolled = self.prev_unrolled_counter - last + sample_counter
            
            # Check for missing samples
            if current_unrolled != self.prev_unrolled_counter + 1:
                missing = current_unrolled - (self.prev_unrolled_counter + 1)
                print(f"Missing {missing} sample(s)")
                self.total_missing_samples += missing
            
            self.prev_unrolled_counter = current_unrolled
                   
        # Initialize timing on first sample received
        if self.start_time is None:
            self.start_time = time.time()
        
        # Extract 3 channels of EEG data (16-bit signed integers, big-endian)
        channels = [
            int.from_bytes(sample_data[1:3], byteorder='big', signed=True),
            int.from_bytes(sample_data[3:5], byteorder='big', signed=True),
            int.from_bytes(sample_data[5:7], byteorder='big', signed=True)]
        
        # Push sample to LSL outlet
        if self.outlet:
            self.outlet.push_sample(channels)
        
        self.samples_received += 1
        
        # Periodically print the number of samples received and the elapsed time when 500 samples are received
        if self.samples_received % 500 == 0:
            elapsed = time.time() - self.start_time
            print(f"Received {self.samples_received} samples in {elapsed:.2f}s")

    def notification_handler(self, sender, data: bytearray):
        """Handle incoming notifications from the BLE device"""
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
        """Periodically print the sample rate every second"""
        while not self.stop_event.is_set():      # Continue running until stop event is triggered
            await asyncio.sleep(1)
            print(f"Samples per second: {self.samples_received}")
            self.samples_received = 0            # Reset the counter after printing

    async def monitor_connection(self):
        """Monitor the connection status and check for data interruptions"""
        while not self.stop_event.is_set():      # Continue running until stop event is triggered
            if self.last_received_time and (time.time() - self.last_received_time) > self.DATA_TIMEOUT:     # Check for Data Timeout
                print("\nData Interrupted")
                self.running = False
                break
            if self.client and not self.client.is_connected:     # Check for BLE Disconnection
                print("\nData Interrupted (Bluetooth disconnected)")
                self.running = False                             # Set running flag to False
                break                                            # Exit the monitoring loop
            await asyncio.sleep(0.5)                             # Short sleep to prevent busy-waiting

    async def async_connect(self, device_address):
        """Asynchronous function to establish BLE connection and start data streaming"""
        try:
            print(f"Attempting to connect to {device_address}...")
            
            info = StreamInfo("NPG", "EXG", 3, 500, "int16", "npg1234")   # Set up LSL stream
            self.outlet = StreamOutlet(info)                              # Create the LSL output stream
            
            self.client = BleakClient(device_address)  # Initialize and connect BLE client using the device address
            await self.client.connect()                # Asynchronously connect to the BLE device
            
            if not self.client.is_connected:           # Verify connection was successful
                print("Failed to connect")
                return False                           # Return False if connection failed
            
            print(f"Connected to {device_address}", flush=True)
            self.connection_event.set()                # Shows connection is established
            
            self.last_received_time = time.time()                               # Record current time as last received
            self.monitor_task = asyncio.create_task(self.monitor_connection())  # Task to monitor connection status
            self.print_rate_task = asyncio.create_task(self.print_rate())       # Task to periodically print sample rate
            
            # Send start command
            await self.client.write_gatt_char(CONTROL_CHAR_UUID, b"START", response=True)
            print("Sent START command")
            
            # Subscribe to notifications
            await self.client.start_notify(DATA_CHAR_UUID, self.notification_handler)
            print("Subscribed to data notifications")
            
            # Main processing loop
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
        """Clean up resources and disconnect from the BLE device"""
        if self.monitor_task:
            self.monitor_task.cancel()               # Cancel the background monitoring task if it exists
        if self.print_rate_task:
            self.print_rate_task.cancel()            # Cancel the sample rate printing task if it exists
        if self.client and self.client.is_connected:
            await self.client.disconnect()           # Disconnect from the BLE device if currently connected
        self.running = False                         # Set running flag to False
        self.connection_event.clear()                # Clear the connection event flag

    def connect(self, device_address):
        self.loop = asyncio.new_event_loop()         # Create a new async event loop (required for async operations)
        asyncio.set_event_loop(self.loop)            # Set this as the active loop for our thread
        
        try:
            self.loop.run_until_complete(self.async_connect(device_address))  # Run the async connection until it finishes
        except Exception as e:
            print(f"Error in connection: {str(e)}")                           # If connection fails, print error and return False
            return False
        finally:
            if self.loop.is_running():                                        # Always clean up by closing the loop when everything is done
                self.loop.close()

    def stop(self):
        """Stop all operations and clean up"""
        self.stop_event.set()
        self.running = False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="Scan for devices")
    parser.add_argument("--connect", type=str, help="Connect to device address")
    return parser.parse_args()

async def scan_devices():
    """Scan for BLE devices with NPG prefix"""
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()                                              # Discover all nearby BLE devices
    filtered = [d for d in devices if d.name and d.name.startswith(DEVICE_NAME_PREFIX)]  # Filter devices to only those with matching name prefix
    
    if not filtered:
        print("No devices found.")
        return
    
    for dev in filtered:            # Print each matching device's name and address
        print(f"DEVICE:{dev.name}|{dev.address}")

if __name__ == "__main__":
    args = parse_args()                  # Handle command line arguments
    client = NPGBluetoothClient()        # Create Bluetooth client instance
    
    try:
        if args.scan:                    # Scan flag - discover available devices
            asyncio.run(scan_devices())
        elif args.connect:               # Connect flag - connect to a specific device
            client.connect(args.connect)
            try:                         # Keep running until data interrupted or connection fails
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