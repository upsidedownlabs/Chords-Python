"""
CHORDS WiFi Data Acquisition Script: This script provides a WebSocket client for connecting to and receiving data from
a CHORDS-compatible WiFi device. It handles connection management, data reception, and basic data validation.
"""

# Importing necessary libraries
import time
import sys
import websocket
import socket
from scipy.signal import butter, filtfilt

class Chords_WIFI:
    """
    A class for connecting to and receiving data from a CHORDS WiFi device.
    This class handles WebSocket communication with a CHORDS device, processes incoming data packets, and provides basic data validation and rate calculation.
    Attributes:
        stream_name (str): Name of the data stream (default: 'NPG')
        channels (int): Number of data channels (default: 3)
        sampling_rate (int): Expected sampling rate in Hz (default: 500)
        block_size (int): Size of each data block in bytes (default: 13)
        timeout_sec (int): Timeout period for no data received in seconds (default: 1)
        packet_size (int): Count of received packets
        data_size (int): Total size of received data in bytes
        sample_size (int): Count of received samples
        previous_sample_number (int): Last received sample number for validation
        previous_data (list): Last received channel data
        start_time (float): Timestamp when measurement started
        last_data_time (float): Timestamp of last received data
        cleanup_done (bool): Flag indicating if cleanup was performed
        ws (websocket.WebSocket): WebSocket connection object
    """
    
    def __init__(self, stream_name='NPG', channels=3, sampling_rate=500, block_size=13, timeout_sec=1):
        """
        Initialize the WiFi client with connection parameters.
        Args:
            stream_name (str): Name of the data stream (default: 'NPG')
            channels (int): Number of data channels (default: 3)
            sampling_rate (int): Expected sampling rate in Hz (default: 500)
            block_size (int): Size of each data block in bytes (default: 13)
            timeout_sec (int): Timeout period for no data in seconds (default: 1)
        """
        self.stream_name = stream_name
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.block_size = block_size
        self.timeout_sec = timeout_sec  # Timeout for no data received

        # Data tracking variables
        self.packet_size = 0
        self.data_size = 0
        self.sample_size = 0
        self.previous_sample_number = -1
        self.previous_data = []
        self.start_time = time.time()
        self.last_data_time = time.time()  # Track last received data
        self.cleanup_done = False
        self.ws = None

    def connect(self):
        """
        Establish WebSocket connection to the CHORDS device. It Attempts to resolve the hostname 'multi-emg.local' and connect to its WebSocket server.
        """
        try:
            host_ip = socket.gethostbyname("multi-emg.local")    # Resolve hostname to IP address
            
            # Create and connect WebSocket
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{host_ip}:81")
            sys.stderr.write(f"{self.stream_name} WebSocket connected!\n")
        except Exception as e:
            print(f"[ERROR] Could not connect to WebSocket: {e}")
            self.cleanup()
            sys.exit(1)

    def calculate_rate(self, size, elapsed_time):
        """
        Calculate rate (samples/packets/bytes per second).
        Args:
            size (int): Count of items (samples, packets, or bytes)
            elapsed_time (float): Time period in seconds
        Returns:
            float: Rate in items per second, or 0 if elapsed_time is 0
        """
        return size / elapsed_time if elapsed_time > 0 else 0

    def process_data(self):
        """
        Main data processing loop. It continuously receives data from the WebSocket, validates samples, and calculates rates. Handles connection errors and timeouts.
        The method:
        1. Receives data from WebSocket
        2. Checks for connection timeouts
        3. Calculates rates every second
        4. Validates sample sequence numbers
        5. Processes channel data
        """
        try:
            while True:
                try:
                    data = self.ws.recv()              # Receive data from WebSocket
                    self.last_data_time = time.time()  # Update when data is received
                except (websocket.WebSocketConnectionClosedException, ConnectionResetError) as e:
                    print(f"\nConnection closed: {str(e)}")
                    self.cleanup()
                    return
                except Exception as e:
                    print(f"\n[ERROR] Connection error: {e}")
                    self.cleanup()
                    return

                # Check for timeout (device stopped sending data)
                if time.time() - self.last_data_time > self.timeout_sec:
                    print("\nDevice stopped sending data")
                    self.cleanup()
                    return

                # Process your data here
                self.data_size += len(data)

                current_time = time.time()  # Calculate rates every second
                elapsed_time = current_time - self.start_time

                if elapsed_time >= 1.0:
                    # Calculate samples, packets, and bytes per second
                    sps = self.calculate_rate(self.sample_size, elapsed_time)
                    fps = self.calculate_rate(self.packet_size, elapsed_time)
                    bps = self.calculate_rate(self.data_size, elapsed_time)

                    # Reset counters
                    self.packet_size = 0
                    self.sample_size = 0
                    self.data_size = 0
                    self.start_time = current_time

                # Process binary data
                if isinstance(data, (bytes, list)):
                    self.packet_size += 1
                    # Process each block in the packet
                    for i in range(0, len(data), self.block_size):
                        self.sample_size += 1
                        block = data[i:i + self.block_size]
                        if len(block) < self.block_size:    # Skip incomplete blocks
                            continue

                        sample_number = block[0]  # Extract sample number (first byte)
                        channel_data = []

                        # Extract channel data (2 bytes per channel)
                        for ch in range(self.channels):
                            offset = 1 + ch * 2
                            sample = int.from_bytes(block[offset:offset + 2], byteorder='big', signed=True)
                            channel_data.append(sample)

                        # Validate sample sequence
                        if self.previous_sample_number == -1:
                            self.previous_sample_number = sample_number
                            self.previous_data = channel_data
                        else:
                            # Check for missing samples
                            if sample_number - self.previous_sample_number > 1:
                                print("\nError: Sample Lost")
                                self.cleanup()
                                sys.exit(1)
                            # Check for duplicate samples
                            elif sample_number == self.previous_sample_number:
                                print("\nError: Duplicate Sample")
                                self.cleanup()
                                sys.exit(1)
                            else:
                                self.previous_sample_number = sample_number
                                self.previous_data = channel_data

        except KeyboardInterrupt:
            print("\nInterrupted by user")
            self.cleanup()
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.cleanup()

    def cleanup(self):
        """
        Clean up resources and close connections. It safely closes the WebSocket connection if it exists and ensures cleanup only happens once.
        """
        if not self.cleanup_done:
            try:
                if hasattr(self, 'ws') and self.ws:
                    self.ws.close()
            except Exception as e:
                pass
            
            print("Cleanup Completed")
            self.cleanup_done = True

    def __del__(self):
        """
        Destructor to ensure cleanup when object is garbage collected.
        """
        self.cleanup()

if __name__ == "__main__":
    client = None
    try:
        client = Chords_WIFI()   # Create and run WiFi client
        client.connect()
        client.process_data()
    except Exception as e:
        if client:
            client.cleanup()
        sys.exit(1)