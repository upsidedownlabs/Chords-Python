"""
This scripts scan and then connects to the selected devices via BLE, reads data packets, processes them, and handles connection status.
"""

# Importing necessary libraries
import asyncio
from bleak import BleakScanner, BleakClient
import time
import sys
import argparse
import threading

class Chords_BLE:
    """
    A class to handle BLE communication with NPG devices via BLE.
    This class provides functionality to:
    - Scan for compatible BLE devices
    - Connect to a device
    - Receive and process data packets
    - Monitor connection status
    - Handle disconnections and errors
    """
    
    # Class constants
    DEVICE_NAME_PREFIX = "NPG"                                 # Prefix for compatible device names
    SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"      # UUID for the BLE service
    DATA_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"    # UUID for data characteristic
    CONTROL_CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb" # UUID for control characteristic
    
    # Packet parameters
    NUM_CHANNELS = 3  # Number of channels
    SINGLE_SAMPLE_LEN = (NUM_CHANNELS * 2) + 1        # (1 Counter + Num_Channels * 2 bytes)
    BLOCK_COUNT = 10
    NEW_PACKET_LEN = SINGLE_SAMPLE_LEN * BLOCK_COUNT  # Total length of a data packet

    def __init__(self):
        """
        Initialize the BLE client with default values and state variables.
        """
        self.prev_unrolled_counter = None          # Tracks the last sample counter value
        self.samples_received = 0                  # Count of received samples
        self.start_time = None                     # Timestamp when first sample is received
        self.total_missing_samples = 0             # Count of missing samples
        self.last_received_time = None             # Timestamp of last received data
        self.DATA_TIMEOUT = 2.0                    # Timeout period for data reception (seconds)
        self.client = None                         # BLE client instance
        self.monitor_task = None                   # Task for monitoring connection
        self.print_rate_task = None                # Task for printing sample rate
        self.running = False                       # Flag indicating if client is running
        self.loop = None                           # Asyncio event loop
        self.connection_event = threading.Event()  # Event for connection status
        self.stop_event = threading.Event()        # Event for stopping operations

    @classmethod
    async def scan_devices(cls):
        """
        Scan for BLE devices with the NPG prefix.
        Returns:
            list: A list of discovered devices matching the NPG prefix
        """
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        filtered = [d for d in devices if d.name and d.name.startswith(cls.DEVICE_NAME_PREFIX)]    # Filter devices by name prefix
        
        if not filtered:
            print("No NPG devices found.")
            return []
        
        return filtered

    def process_sample(self, sample_data: bytearray):
        """
        Process a single sample packet.
        Args:
            sample_data (bytearray): The raw sample data to process
        """
        self.last_received_time = time.time()
        
        # Validate sample length
        if len(sample_data) != self.SINGLE_SAMPLE_LEN:
            print("Unexpected sample length:", len(sample_data))
            return

        # Extract and process sample counter
        sample_counter = sample_data[0]
        if self.prev_unrolled_counter is None:
            self.prev_unrolled_counter = sample_counter
        else:
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
                   
        # Record start time if this is the first sample
        if self.start_time is None:
            self.start_time = time.time()
        
        # Extract channel data (2 bytes per channel, big-endian, signed)
        channels = [int.from_bytes(sample_data[i:i+2], byteorder='big', signed=True) 
            for i in range(1, len(sample_data), 2)]
        
        self.samples_received += 1

    def notification_handler(self, sender, data: bytearray):
        """
        Handle incoming notifications from the BLE device.        
        Args:
            sender: The characteristic that sent the notification
            data (bytearray): The received data packet
        """
        try:
            if len(data) == self.NEW_PACKET_LEN:     # Process data based on packet length
                for i in range(0, self.NEW_PACKET_LEN, self.SINGLE_SAMPLE_LEN):   # Process a block of samples
                    self.process_sample(data[i:i+self.SINGLE_SAMPLE_LEN])
            elif len(data) == self.SINGLE_SAMPLE_LEN:
                self.process_sample(data)    # Process a single sample
            else:
                print(f"Unexpected packet length: {len(data)} bytes")
        except Exception as e:
            print(f"Error processing data: {e}")

    async def print_rate(self):
        """Print the current sample rate every second."""
        while not self.stop_event.is_set():
            await asyncio.sleep(1)
            self.samples_received = 0

    async def monitor_connection(self):
        """
        Monitor the connection status and check for data interruptions.
        This runs in a loop to check:
        - If data hasn't been received within the timeout period
        - If the BLE connection has been lost
        """
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
        """
        Asynchronously connect to a BLE device and start data reception.
        Args:
            device_address (str): The MAC address of the device to connect to
        Returns:
            bool: True if connection was successful, otherwise False
        """
        try:
            print(f"Attempting to connect to {device_address}...")
            
            self.client = BleakClient(device_address)
            await self.client.connect()
            
            if not self.client.is_connected:
                print("Failed to connect")
                return False
            
            print(f"Connected to {device_address}", flush=True)
            self.connection_event.set()
            
            # Initialize monitoring tasks
            self.last_received_time = time.time()
            self.monitor_task = asyncio.create_task(self.monitor_connection())
            self.print_rate_task = asyncio.create_task(self.print_rate())
            
            # Send start command to device
            await self.client.write_gatt_char(self.CONTROL_CHAR_UUID, b"START", response=True)
            print("Sent START command")
            
            # Subscribe to data notifications
            await self.client.start_notify(self.DATA_CHAR_UUID, self.notification_handler)
            print("Subscribed to data notifications")
            
            # Main loop
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
        """Clean up resources and disconnect from the device."""
        if self.monitor_task:
            self.monitor_task.cancel()
        if self.print_rate_task:
            self.print_rate_task.cancel()
        if self.client and self.client.is_connected:
            await self.client.disconnect()
        self.running = False
        self.connection_event.clear()

    def connect(self, device_address):
        """
        Connect to a BLE device (wrapper for async_connect).
        Args:
            device_address (str): The MAC address of the device to connect to
        """
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
        """Stop all operations and clean up resources."""
        self.stop_event.set()
        self.running = False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="Scan for devices")
    parser.add_argument("--connect", type=str, help="Connect to device address")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    client = Chords_BLE()
    
    try:
        if args.scan:
            devices = asyncio.run(Chords_BLE.scan_devices())    # Scan for devices
            for dev in devices:
                print(f"DEVICE:{dev.name}|{dev.address}")
        elif args.connect:
            client.connect(args.connect)    # Connect to specified device
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