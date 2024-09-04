# BioAmp Tool
# https://github.com/upsidedownlabs/BioAmp-Tool-Python
#
# Upside Down Labs invests time and resources providing this open source code,
# please support Upside Down Labs and open-source hardware by purchasing
# products from Upside Down Labs!
#
# Copyright (c) 2024 Payal Lakra
# Copyright (c) 2024 Upside Down Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from pylsl import StreamInfo, StreamOutlet  # Import necessary classes for LSL streaming
import argparse  # Import for parsing command-line arguments
import serial  # Import for serial communication
import time  # Import for time-related functions
import csv  # Import for handling CSV files
from datetime import datetime  # Import for handling date and time
import serial.tools.list_ports  # Import for serial port detection utilities

# Initialize global variables
total_packet_count = 0  # Tracks the number of packets received in the last 10 seconds
cumulative_packet_count = 0  # Tracks the number of packets received in the last 10 minutes
start_time = None  # Stores the start time for the 10-second interval
last_ten_minute_time = None  # Stores the start time for the 10-minute interval
previous_sample_number = None  # Stores the previous sample number for detecting missing samples
missing_samples = 0  # Tracks the number of missing samples
buffer = bytearray()  # A buffer to hold incoming data until it forms a complete packet
PACKET_LENGTH = 17  # Expected length of each data packet
SYNC_BYTE1 = 0xA5  # First byte of the synchronization pattern
SYNC_BYTE2 = 0x5A  # Second byte of the synchronization pattern
END_BYTE = 0x01  # End byte of each packet
lsl_outlet = None  # LSL stream outlet, initially set to None
verbose = False  # Flag for verbose output, initially set to False

def auto_detect_arduino(baudrate, timeout=1):
    """
    Automatically detects the Arduino by scanning all available serial ports.
    Args:baudrate (int): The baud rate for serial communication.
         timeout (int): Timeout for the serial connection attempt.
    """
    ports = serial.tools.list_ports.comports()  # Get a list of all available serial ports
    for port in ports:  # Iterate over each port
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Try to open the serial port
            time.sleep(1)  # Wait for the port to stabilize
            response = ser.readline().strip()  # Read a line of response from the device
            if response:  # If a response is received
                ser.close()  # Close the serial connection
                print(f"Arduino detected at {port.device}")  # Print the detected port
                return port.device  # Return the detected port
            ser.close()  # Close the serial connection if no response
        except (OSError, serial.SerialException):  # Handle exceptions for serial port access
            pass
    print("Arduino not detected")  # Print if no Arduino is detected
    return None  # Return None if no Arduino is detected

def read_arduino_data(ser, csv_writer=None):
    """
    Reads data from Arduino and processes it. Optionally writes to CSV and LSL stream.
    Args: ser (serial.Serial): The serial object connected to Arduino.
          csv_writer (csv.writer, optional): CSV writer object to log data. Defaults to None.
    """
    global total_packet_count, cumulative_packet_count, previous_sample_number, missing_samples, buffer
    raw_data = ser.read(ser.in_waiting or 1)  # Read available data from the serial buffer
    buffer.extend(raw_data)  # Append the new data to the buffer

    while len(buffer) >= PACKET_LENGTH:  # Check if the buffer has enough data for a full packet
        sync_index = buffer.find(bytes([SYNC_BYTE1, SYNC_BYTE2]))  # Look for the synchronization pattern

        if sync_index == -1:  # If sync pattern is not found
            buffer.clear()  # Clear the buffer
            continue
        
        if len(buffer) >= sync_index + PACKET_LENGTH:  # Check if there's enough data for a complete packet after sync
            packet = buffer[sync_index:sync_index + PACKET_LENGTH]  # Extract the packet
            # Verify packet structure
            if len(packet) == PACKET_LENGTH and packet[0] == SYNC_BYTE1 and packet[1] == SYNC_BYTE2 and packet[-1] == END_BYTE:
                counter = packet[3]  # Extract the packet counter

                # Check for missing samples
                if previous_sample_number is not None and counter != (previous_sample_number + 1) % 256:
                    missing_samples += (counter - previous_sample_number - 1) % 256
                    if verbose:
                        print(f"Error: Expected counter {previous_sample_number + 1} but received {counter}. Missing samples: {missing_samples}")

                previous_sample_number = counter  # Update the previous sample number
                total_packet_count += 1  # Increment packet count for 10-second interval
                cumulative_packet_count += 1  # Increment cumulative packet count for 10-minute interval

                channel_data = []  # Initialize list to store channel data
                for i in range(4, 16, 2):  # Extract channel data from the packet
                    high_byte = packet[i]
                    low_byte = packet[i + 1]
                    value = (high_byte << 8) | low_byte  # Combine high and low bytes to form the actual value
                    channel_data.append(float(value))  # Append the value to the channel data list

                if csv_writer:  # If CSV writer is provided
                    csv_writer.writerow([counter] + channel_data)  # Write data to CSV
                if lsl_outlet:  # If LSL outlet is initialized
                    lsl_outlet.push_sample(channel_data)  # Push data to LSL stream

                del buffer[:sync_index + PACKET_LENGTH]  # Remove processed packet from the buffer
            else:
                del buffer[:sync_index + 1]  # Remove only the incorrect part of the buffer

def start_timer():
    """
    Initializes the timers for 10-second and 10-minute intervals.
    """
    global start_time, last_ten_minute_time, total_packet_count, cumulative_packet_count
    time.sleep(0.5)  # Brief delay to ensure stable timing
    current_time = time.time()  # Get the current time
    start_time = current_time  # Set the start time for the 10-second interval
    last_ten_minute_time = current_time  # Set the start time for the 10-minute interval
    total_packet_count = 0  # Reset the 10-second packet counter
    cumulative_packet_count = 0  # Reset the 10-minute packet counter

def log_ten_second_data(verbose=False):
    """
    Logs and resets data for the 10-second interval.
    Args: verbose (bool, optional): If True, prints the number of samples in the last 10 seconds. Defaults to False.
    """
    global total_packet_count
    if verbose:
        print(f"Data count for the last 10 seconds: {total_packet_count} samples")  # Print the number of samples
    total_packet_count = 0  # Reset the packet count for the next 10 seconds

def log_ten_minute_data(verbose=False):
    """
    Logs data and statistics for the 10-minute interval.
    Args: verbose (bool, optional): If True, prints the number of samples and sampling statistics for the last 10 minutes. Defaults to False.
    """
    global cumulative_packet_count, last_ten_minute_time

    if verbose:
        print(f"Total data count after 10 minutes: {cumulative_packet_count} samples")  # Print the total number of samples
        
        # Calculate and print the sampling rate over the last 10 minutes
        sampling_rate = cumulative_packet_count / (10 * 60)
        print(f"Sampling rate: {sampling_rate:.2f} samples/second")

        # Calculate and print the drift in sampling rate
        expected_sampling_rate = 250  # Expected sampling rate in samples per second
        drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600  # Calculate drift in seconds per hour
        print(f"Drift: {drift:.2f} seconds/hour")

    cumulative_packet_count = 0  # Reset the cumulative packet count for the next 10 minutes
    last_ten_minute_time = time.time()  # Update the last 10-minute start time

def parse_data(port, baudrate, lsl_flag=False, csv_flag=False, verbose=False):
    """
    Parses data from Arduino and manages the data logging and streaming process.
    Args:port (str): The serial port to use.
         baudrate (int): The baud rate for serial communication.
         lsl_flag (bool, optional): If True, enables LSL streaming. Defaults to False.
         csv_flag (bool, optional): If True, enables CSV logging. Defaults to False.
         verbose (bool, optional): If True, enables verbose output. Defaults to False.
    """
    global total_packet_count, cumulative_packet_count, start_time, lsl_outlet, last_ten_minute_time

    csv_writer = None  # Initialize CSV writer as None
    csv_filename = None  # Initialize CSV filename as None

    if lsl_flag:  # If LSL streaming is enabled
        # Initialize LSL stream with the specified parameters
        lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, 250, 'float32', 'UpsideDownLabs')
        lsl_outlet = StreamOutlet(lsl_stream_info)  # Create an LSL outlet
        print("LSL stream started")  # Print confirmation
        time.sleep(0.5)  # Brief delay for LSL outlet setup
    
    if csv_flag:  # If CSV logging is enabled
        # Generate a unique filename based on the current date and time
        csv_filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        print(f"CSV recording started. Data will be saved to {csv_filename}")  # Print confirmation

    # Open the serial port with the specified parameters
    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        csv_file = open(csv_filename, mode='w', newline='') if csv_flag else None  # Open CSV file if needed
        
        if csv_file:  # If CSV file is opened
            csv_writer = csv.writer(csv_file)  # Initialize CSV writer
            # Write the header row to the CSV file
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])

        start_timer()  # Start the timers for 10-second and 10-minute intervals

        try:
            while True:  # Main loop for data reading and processing
                read_arduino_data(ser, csv_writer)  # Read and process data from Arduino

                current_time = time.time()  # Get the current time

                # Calculate elapsed time since last 10-second and 10-minute logs
                elapsed_time = current_time - start_time
                elapsed_since_last_10_minutes = current_time - last_ten_minute_time

                if elapsed_time >= 10:  # If 10 seconds have passed
                    log_ten_second_data(verbose)  # Log data for the 10-second interval
                    start_time = current_time  # Reset the start time for the next 10 seconds
                if elapsed_since_last_10_minutes >= 600:  # If 10 minutes have passed
                    log_ten_minute_data(verbose)  # Log data for the 10-minute interval
        except KeyboardInterrupt:  # Handle keyboard interrupt (Ctrl+C)
            if csv_file:  # If CSV file is opened
                csv_file.close()  # Close the CSV file
                print(f"CSV recording stopped. Data saved to {csv_filename}.")  # Print confirmation
            print(f"Exiting.\nTotal missing samples: {missing_samples}")  # Print the total number of missing samples

def main():
    """
    Main function to handle argument parsing and initiate data processing.
    """
    global verbose
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")  # Initialize argument parser
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")  # Argument for specifying the serial port
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")# baud rate
    parser.add_argument('--csv', action='store_true', help="Create and write to a CSV file")  # Flag to enable CSV logging
    parser.add_argument('--lsl', action='store_true', help="Start LSL stream")  # Flag to enable LSL streaming
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output with statistical data")  #  verbose output

    args = parser.parse_args()  # Parse command-line arguments
    verbose = args.verbose  # Set the global verbose flag

    if not args.csv and not args.lsl:  # Check if neither CSV nor LSL is enabled
        parser.print_help()  # Print help message
        return
    # Get the specified port or auto-detect Arduino if no port is specified
    port = args.port or auto_detect_arduino(args.baudrate)
    if port is None:  # If no port is found or specified
        print("Arduino port not specified or detected. Exiting.")  # Print error message
        return
    # Start data parsing and processing
    parse_data(port, args.baudrate, lsl_flag=args.lsl, csv_flag=args.csv, verbose=args.verbose)

if __name__ == "__main__":
    main()  # Call the main function when script is executed directly