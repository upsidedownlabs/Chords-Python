"""
CHORDS Data Connection-
This scripts provides a unified interface for connecting to CHORDS devices via multiple protocols
(USB, WiFi, BLE) and streaming data to LSL (Lab Streaming Layer) and/or CSV files.

Key Features:
- Multi-protocol support (USB, WiFi, BLE)
- Simultaneous LSL streaming and CSV recording
- Automatic device discovery and connection

Typical Usage:
1. Initialize Connection object
2. Connect to device via preferred protocol
3. Configure LSL stream parameters
4. Start data streaming/CSV recording
5. Process incoming data
6. Clean shutdown on exit
"""

# Importing necessary libraries
from chordspy.chords_serial import Chords_USB    # USB protocol handler
from chordspy.chords_wifi import Chords_WIFI     # WiFi protocol handler
from chordspy.chords_ble import Chords_BLE       # BLE protocol handler
import argparse                                  # For command-line argument parsing
import time                                      # For timing operations and timestamps
import asyncio                                   # For asynchronous BLE operations
import csv                                       # For CSV file recording
from datetime import datetime                    # For timestamp generation
import threading                                 # For multi-threaded operations
from collections import deque                    # For efficient rate calculation
from pylsl import StreamInfo, StreamOutlet       # LSL streaming components
from pylsl import StreamInlet, resolve_stream    # LSL stream resolution
from pylsl import local_clock                    # For precise timing
import numpy as np                               # For numerical operations

class Connection:
    """
    Main connection manager class for supported devices.
    This class serves as the central hub for all device communication, providing:
    - Unified interface across multiple connection protocols(WiFi/BLE/USB)
    - Data streaming to LSL
    - Data recording to CSV files
    - Connection state management
    - Sample validation and rate monitorin
    The class maintains separate connection handlers for each protocol (USB/WiFi/BLE)
    and manages their lifecycle. It implements thread-safe operations for concurrent
    data handling and provides clean shutdown procedures.
    """
    def __init__(self):
        """
        Initialize the connection manager with default values.
        """
        # Protocol Connection Handlers
        self.ble_connection = None                 # BLE protocol handler
        self.wifi_connection = None                # WiFi protocol handler
        self.usb_connection = None                 # USB protocol handler
        self.lsl_connection = None                 # LSL stream outlet (created when streaming starts)
        
        # LSL Stream Configuration
        self.stream_name = "BioAmpDataStream"      # Default LSL stream name
        self.stream_type = "EXG"                   # LSL stream type
        self.stream_format = "float32"             # Data format for LSL samples
        self.stream_id = "UDL"                     # Unique stream identifier
        
        # Data Tracking Systems
        self.last_sample = None                    # Stores the most recent sample received
        self.samples_received = 0                  # Total count of samples received
        self.start_time = time.time()              # Timestamp when connection was established
        
        # CSV Recording Systems
        self.csv_file = None                       # File handle for CSV output
        self.csv_writer = None                     # CSV writer object
        self.sample_counter = 0                    # Count of samples written to CSV

        # Stream Parameters
        self.num_channels = 0                      # Number of data channels
        self.sampling_rate = 0                     # Current sampling rate in Hz
        
        # System State Flags
        self.stream_active = False                 # True when LSL streaming is active
        self.recording_active = False              # True when CSV recording is active
        
        # Thread Management
        self.usb_thread = None                     # Thread for USB data handling
        self.ble_thread = None                     # Thread for BLE data handling
        self.wifi_thread = None                    # Thread for WiFi data handling
        self.running = False                       # Main system running flag
        
        # Rate Monitoring Systems
        self.sample_count = 0                      # Samples received in current interval
        self.rate_window = deque(maxlen=10)        # Window for rate calculation
        self.last_timestamp = time.perf_counter()  # Last rate calculation time
        self.rate_update_interval = 0.5            # Seconds between rate updates
        self.ble_samples_received = 0              # Count of BLE-specific samples

    async def get_ble_device(self):
        """
        Scan for and select a BLE device interactively.
        This asynchronous method: Scans for available BLE devices using Chords_BLE scanner, presents discovered devices to user, handles user selection, returns selected device object.
        Returns:
            Device: The selected BLE device object or None if no devices found, invalid selection, user cancellation.
        """
        devices = await Chords_BLE.scan_devices()    # Scan for available BLE devices
        
        # Handle case where no devices are found
        if not devices:
            print("No NPG devices found!")
            return None
        
        print("\nFound NPG Devices:")                # Display discovered devices to user
        for i, device in enumerate(devices):
            print(f"[{i}] {device.name} - {device.address}")
        
        try:
            selection = int(input("\nEnter device number to connect: "))    # Get user selection
            if 0 <= selection < len(devices):          # Validate selection
                return devices[selection]
            print("Invalid selection!")
            return None
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")       # Handle invalid input or user cancellation
            return None

    def setup_lsl(self, num_channels, sampling_rate):
        """
        Set up LSL (Lab Streaming Layer) stream outlet.
        This method: creates a new LSL stream info object, initializes the LSL outlet, updates stream parameters, sets streaming state flag.
        Args:
            num_channels (int): Number of data channels in stream
            sampling_rate (float): Sampling rate in Hz
        """
        # Create LSL stream info with configured parameters
        info = StreamInfo(self.stream_name, self.stream_type, num_channels, sampling_rate, self.stream_format, self.stream_id)
        self.lsl_connection = StreamOutlet(info)   # Initialize LSL outlet
        print(f"LSL stream started: {num_channels} channels at {sampling_rate}Hz")
        self.stream_active = True
        self.num_channels = num_channels
        self.sampling_rate = sampling_rate

    def start_csv_recording(self, filename=None):
        """
        Start CSV recording session.
        This method: Verify recording isn't already active, generates filename, opens CSV file and initializes writer, writes column headers, sets recording state flag.
        Args:
            filename (str, optional): Custom filename without extension
        Returns:
            bool: True if recording started successfully, False otherwise
        """
        # Check if recording is already active
        if self.recording_active:
            return False
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ChordsPy_{timestamp}.csv"
            elif not filename.endswith('.csv'):
                filename += '.csv'
                
            self.csv_file = open(filename, 'w', newline='')         # Open CSV file and initialize writer
            headers = ['Counter'] + [f'Channel{i+1}' for i in range(self.num_channels)]    # Create column headers
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(headers)
            self.recording_active = True     # Update state
            self.sample_counter = 0
            print(f"CSV recording started: {filename}")
            return True
        except Exception as e:
            print(f"Error starting CSV recording: {str(e)}")    # Handle file operation errors
            return False

    def stop_csv_recording(self):
        """
        Stop CSV recording session.
        This method: Validates recording is active, closes CSV file, cleans up resources, resets recording state.
        Returns:
            bool: True if recording stopped successfully, False otherwise
        """
        # Check if recording is inactive
        if not self.recording_active:
            return False
        
        try:
            # Close file and clean up
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
                self.csv_writer = None
            self.recording_active = False   # Update state
            print("CSV recording stopped")
            return True
        except Exception as e:
            print(f"Error stopping CSV recording: {str(e)}")   # Handle file closing errors
            return False

    def log_to_csv(self, sample_data):
        """
        Log a sample to CSV file.
        This method: Validates recording is active, formats sample data, writes to CSV, handles write errors.
        Args:
            sample_data (list): List of channel values to record
        """
        # Check if recording is inactive
        if not self.recording_active or not self.csv_writer:
            return
            
        try:
            # Format and write sample
            self.sample_counter += 1
            row = [self.sample_counter] + sample_data
            self.csv_writer.writerow(row)
        except Exception as e:
            print(f"Error writing to CSV: {str(e)}")     # Handle write errors and stop recording
            self.stop_csv_recording()

    def update_sample_rate(self):
        """
        Update and display current sample rate. It calculates rate over a moving window and prints to console. It uses perf_counter() for highest timing precision.
        """
        now = time.perf_counter()              # Get current high-resolution timestamp
        elapsed = now - self.last_timestamp    # Calculate time elapsed since last calculation
        self.sample_count += 1                 # Increment sample counter for this interval
        
        # Only update display if we've collected enough time (default 0.5s)
        if elapsed >= self.rate_update_interval:
            current_rate = self.sample_count / elapsed  # Calculate current instantaneous rate (samples/second)
            self.rate_window.append(current_rate)       # Add to our moving window of recent rates (default 10 values)
            
            # Print average rate
            avg_rate = sum(self.rate_window) / len(self.rate_window)
            print(f"\rCurrent sampling rate: {avg_rate:.2f} Hz", end="", flush=True)   # Using \r to overwrite previous line
            
            # Reset counters for next interval
            self.sample_count = 0
            self.last_timestamp = now

    def lsl_rate_checker(self, duration=1.0):
        """
        Independently verifies the actual streaming rate of the LSL outlet.
        This method: Collects timestamps over a measurement period -> calculates rate from timestamp differences.
        Args:
            duration: Measurement duration in seconds
        """
        try:
            streams = resolve_stream('type', self.stream_type)
            if not streams:
                print("No LSL stream found to verify.")
                return
            inlet = StreamInlet(streams[0])     # Create an inlet to receive data
            timestamps = []
            start_time = time.time()

            # Collect data for specified duration
            while time.time() - start_time < duration:
                sample, ts = inlet.pull_sample(timeout=1.0)
                if ts:
                    timestamps.append(ts)

            if len(timestamps) > 10:
                diffs = np.diff(timestamps)     # Calculate time differences between consecutive samples
                filtered_diffs = [d for d in diffs if d > 0]     # Filter out zero/negative differences (invalid)
                if filtered_diffs:
                    estimated_rate = 1 / np.mean(filtered_diffs) # Rate = 1/average interval between samples
                else:
                    print("\nAll timestamps had zero difference (invalid).")
            else:
                print("\nNot enough timestamps collected to estimate rate.")
                
        except Exception as e:
            print(f"Error in LSL rate check: {str(e)}")

    def ble_data_handler(self):
        """
        BLE-specific data handler with precise timing control.
        The handler ensures:
        1. Precise sample timing using local_clock()
        2. Constant sampling rate regardless of BLE packet timing
        3. Graceful handling of buffer overflows
        4. Thread-safe operation with the main controller
        """
        # Target specifications for the BLE stream
        SAMPLE_INTERVAL = 1.0 / self.sampling_rate     # Time between samples in seconds
        next_sample_time = local_clock()               # Initialize timing baseline
        
        # Main processing loop - runs while system is active and BLE connected
        while self.running and self.ble_connection:
            try:
                # Check if new BLE data is available
                if hasattr(self.ble_connection, 'data_available') and self.ble_connection.data_available:
                    current_time = local_clock()  # Get precise current timestamp
                    
                    # Only process if we've reached the next scheduled sample time
                    if current_time >= next_sample_time:
                        sample = self.ble_connection.get_latest_sample()
                        if sample:
                            channel_data = sample[:self.num_channels]   # Extract channel data
                            
                            # Calculate precise timestamp
                            sample_time = next_sample_time
                            next_sample_time += SAMPLE_INTERVAL     # Schedule next sample time
                            
                            # If we're falling behind, skip samples to catch up
                            if current_time > next_sample_time + SAMPLE_INTERVAL:
                                next_sample_time = current_time + SAMPLE_INTERVAL
                            
                            # Stream to LSL if enabled
                            if self.lsl_connection:
                                self.lsl_connection.push_sample(channel_data, timestamp=sample_time)

                            # Update rate display
                            self.update_sample_rate()

                            # Log to CSV if recording
                            if self.recording_active:
                                self.log_to_csv(channel_data)
            except Exception as e:
                print(f"BLE data handler error: {str(e)}")
                break

    def wifi_data_handler(self):
        """
        WiFi-specific data handler with network-optimized timing.
        """
        SAMPLE_INTERVAL = 1.0 / self.sampling_rate     # Time between samples in seconds
        next_sample_time = local_clock()               # Initialize timing baseline
        
        while self.running and self.wifi_connection:
            try:
                # Verify WiFi data is available
                if hasattr(self.wifi_connection, 'data_available') and self.wifi_connection.data_available:
                    current_time = local_clock()
                    
                    # Timing gate ensures precise sample rate
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
        """
        USB data handler with serial port optimization.
        """
        SAMPLE_INTERVAL = 1.0 / self.sampling_rate     # Time between samples in seconds
        next_sample_time = local_clock()               # Initialize timing baseline
        
        while self.running and self.usb_connection:
            try:
                # Verify USB port is open and active
                if hasattr(self.usb_connection, 'ser') and self.usb_connection.ser.is_open:
                    self.usb_connection.read_data()     # Read raw data from serial port
                    
                    # Process if new data exists
                    if hasattr(self.usb_connection, 'data'):
                        current_time = local_clock()
                        
                        if current_time >= next_sample_time:
                            sample = self.usb_connection.data[:, -1]  # Get most recent sample from numpy array
                            channel_data = sample.tolist()            # Convert to list format

                            # Calculate precise timestamp
                            sample_time = next_sample_time
                            next_sample_time += SAMPLE_INTERVAL
                            
                            # USB-specific overflow handling
                            if current_time > next_sample_time + SAMPLE_INTERVAL:
                                next_sample_time = current_time + SAMPLE_INTERVAL
                            
                            if self.lsl_connection:
                                self.lsl_connection.push_sample(channel_data, timestamp=sample_time)

                            self.update_sample_rate()

                            if self.recording_active:
                                self.log_to_csv(channel_data)
            except Exception as e:
                print(f"\nUSB data handler error: {str(e)}")
                break

    def connect_ble(self, device_address=None):
        """
        Establishes and manages a Bluetooth Low Energy (BLE) connection with a device.
        The method handles the complete BLE lifecycle including:
        - Device discovery and selection (if no address provided)
        - Connection establishment
        - Data stream configuration
        - Real-time data processing pipeline
        Args:
            device_address (str, optional): MAC address in "XX:XX:XX:XX:XX:XX" format. If None, initiates interactive device selection.
        Returns:
            bool: True if connection succeeds, False on failure
        Workflow: Initialize BLE handler instance -> Configure custom data notification handler -> Establish connection (direct or interactive) -> Set up data processing pipeline -> Maintain connection until termination.
        """
        # Initialize BLE protocol handler
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
                        channels = [int.from_bytes(sample_data[i:i+2], byteorder='big', signed=True) 
                            for i in range(1, len(sample_data), 2)]
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
                    return False
                print(f"Connecting to BLE device: {selected_device.name}")
                self.ble_connection.connect(selected_device.address)

            self.running = True
            self.ble_thread = threading.Thread(target=self.ble_data_handler)
            self.ble_thread.daemon = True
            self.ble_thread.start()
            threading.Thread(target=self.lsl_rate_checker, daemon=True).start()    # Start independent rate monitoring
            return True
        except Exception as e:
            print(f"BLE connection failed: {str(e)}")
            return False

    def connect_wifi(self):
        """
        Manages WiFi connection and data streaming for CHORDS devices.
        Implements a persistent connection loop that:
        - Maintains websocket connection
        - Validates incoming data blocks
        - Handles data conversion and distribution
        - Provides graceful shutdown on interrupt
        The method runs continuously until KeyboardInterrupt, automatically cleaning up resources on exit.
        """
        # Initialize WiFi handler and establish connection
        self.wifi_connection = Chords_WIFI()
        self.wifi_connection.connect()

        # Configure stream parameters from device
        self.num_channels = self.wifi_connection.channels
        sampling_rate = self.wifi_connection.sampling_rate

        # Initialize LSL stream if needed
        if not self.lsl_connection:
            self.setup_lsl(self.num_channels, sampling_rate)

        # Start the data handler thread
        self.running = True
        self.wifi_thread = threading.Thread(target=self.wifi_data_handler)
        self.wifi_thread.daemon = True
        self.wifi_thread.start()
        threading.Thread(target=self.lsl_rate_checker, daemon=True).start()    # Start independent rate monitoring
        
        try:
            print("\nConnected! (Press Ctrl+C to stop)")
            while True:
                data = self.wifi_connection.ws.recv()        # Receive data via websocket
                
                # Handle both binary and text-formatted data
                if isinstance(data, (bytes, list)):
                    # Process data in protocol-defined blocks
                    block_size = self.wifi_connection.block_size
                    for i in range(0, len(data), block_size):
                        block = data[i:i + block_size]
                        
                        # Skip partial blocks
                        if len(block) < block_size:
                            continue
                        
                        # Extract and convert channel samples
                        channel_data = []
                        for ch in range(self.wifi_connection.channels):
                            offset = 1 + ch * 2        # Calculate byte offset for each channel
                            sample = int.from_bytes(block[offset:offset + 2], byteorder='big', signed=True)
                            channel_data.append(sample)
                        
                        if self.lsl_connection:                   # Push to LSL
                            self.lsl_connection.push_sample(channel_data)
                            
                        # Record to CSV
                        if self.recording_active:
                            self.log_to_csv(channel_data)
                    
        except KeyboardInterrupt:
            print("\nDisconnected")
        finally:
            self.stop_csv_recording()            # Ensure resources are released

    def connect_usb(self):
        """
        Handles USB device connection and data streaming.
        Implements: Automatic device detection, Hardware-specific configuration, Multi-threaded data handling, Rate monitoring.
        Returns:
            bool: True if successful initialization, False on failure
        """
        # Initialize USB handler
        self.usb_connection = Chords_USB()
        # Detect and validate connected hardware
        if not self.usb_connection.detect_hardware():
            return False
            
        # Configure stream based on detected board
        self.num_channels = self.usb_connection.num_channels
        board_config = self.usb_connection.supported_boards[self.usb_connection.board]
        self.sampling_rate = board_config["sampling_rate"]
        
        # Initialize LSL stream
        self.setup_lsl(self.num_channels, self.sampling_rate)
        
        # Start the USB streaming command
        self.usb_connection.send_command('START')
        
        # Start the data handler thread
        self.running = True
        self.usb_thread = threading.Thread(target=self.usb_data_handler)
        self.usb_thread.daemon = True
        self.usb_thread.start()

        # Start independent rate monitoring
        threading.Thread(target=self.lsl_rate_checker, daemon=True).start()
        return True

    def cleanup(self):
        """
        Clean up all resources and connections in a safe and orderly manner.
        The cleanup process follows this sequence: First stop data recording -> Then stop LSL streaming -> Next terminate all threads -> Finally close all hardware connections.
        """
        self.running = False         # Signal all threads to stop
        self.stop_csv_recording()    # Stop CSV recording if active

        # Clean up LSL stream if active
        if self.lsl_connection:
            self.lsl_connection = None
            self.stream_active = False
            print("\nLSL stream stopped")
        
        # Collect all active threads
        threads = []
        if self.usb_thread and self.usb_thread.is_alive():
            threads.append(self.usb_thread)
        if self.ble_thread and self.ble_thread.is_alive():
            threads.append(self.ble_thread)
        if self.wifi_thread and self.wifi_thread.is_alive():
            threads.append(self.wifi_thread)
            
        # Wait for threads to finish (with timeout to prevent hanging)
        for t in threads:
            t.join(timeout=1)  # 1 second timeout per thread
        
        # Clean up USB connection
        if self.usb_connection:
            try:
                # Check if serial port is open and send stop command
                if hasattr(self.usb_connection, 'ser') and self.usb_connection.ser.is_open:
                    self.usb_connection.send_command('STOP')  # Graceful stop
                    self.usb_connection.ser.close()           # Close serial port
                print("USB connection closed")
            except Exception as e:
                print(f"Error closing USB connection: {str(e)}")
            finally:
                self.usb_connection = None
        
        # Clean up BLE connection
        if self.ble_connection:
            try:
                self.ble_connection.stop()  # Stop BLE operations
                print("BLE connection closed")
            except Exception as e:
                print(f"Error closing BLE connection: {str(e)}")
            finally:
                self.ble_connection = None
        
        # Clean up WiFi connection
        if self.wifi_connection:
            try:
                self.wifi_connection.cleanup()  # WiFi-specific cleanup
                print("WiFi connection closed")
            except Exception as e:
                print(f"Error closing WiFi connection: {str(e)}")
            finally:
                self.wifi_connection = None
        
        # Reset all state flags
        self.stream_active = False
        self.recording_active = False

    def __del__(self):
        """
        Destructor to ensure cleanup when object is garbage collected. It simply calls the main cleanup method.
        """
        self.cleanup()

def main():
    """
    Main entry point for command line execution of the CHORDS connection manager.
    It handles: Command line argument parsing, protocol-specific connection setup, main execution loop, clean shutdown on exit.

    Usage Examples:
    $ python chords_connection.py --protocol usb
    $ python chords_connection.py --protocol wifi
    $ python chords_connection.py --protocol ble
    $ python chords_connection.py --protocol ble --ble-address AA:BB:CC:DD:EE:FF

    The main execution flow:
    1. Parse command line arguments
    2. Create connection manager instance
    3. Establish requested connection
    4. Enter main loop (until interrupted)
    5. Clean up resources on exit
    """
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Connect to device')
    parser.add_argument('--protocol', choices=['usb', 'wifi', 'ble'], required=True, help='Connection protocol to use (usb|wifi|ble)')
    parser.add_argument('--ble-address', help='Direct BLE device address')
    
    args = parser.parse_args()  # Parse command line arguments
    manager = Connection()      # Create connection manager instance

    try:
        # USB Protocol Handling
        if args.protocol == 'usb':
            if manager.connect_usb():                  # Attempt USB connection
                while manager.running:                 # Main execution loop
                    time.sleep(1)                      # Prevent CPU overutilization
                    
        # WiFi Protocol Handling        
        elif args.protocol == 'wifi':
            if manager.connect_wifi():                 # Attempt WiFi connection
                while manager.running:                 # Main execution loop
                    time.sleep(1)                      # Prevent CPU overutilization
                    
        # BLE Protocol Handling
        elif args.protocol == 'ble':
            if manager.connect_ble(args.ble_address):  # Attempt BLE connection
                while manager.running:                 # Main execution loop
                    time.sleep(1)                      # Prevent CPU overutilization
                    
    except KeyboardInterrupt:
        print("\nCleanup Completed.")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        manager.cleanup()    # Ensure cleanup always runs

if __name__ == '__main__':
    main()