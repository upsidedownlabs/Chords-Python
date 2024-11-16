from pylsl import StreamInfo, StreamOutlet  # Import LSL library for data streaming
import argparse  # Import argparse for command-line argument parsing
import serial  # Import serial for serial communication
import time  # Import time for time-related functions
import csv  # Import csv for handling CSV files
from collections import deque  # Import deque for a buffer to store data packets
import serial.tools.list_ports  # Import list_ports to list available serial ports

# Initialize global variables for processing
packet_buffer = deque()  # Create a deque to buffer incoming data packets
initial_samples_ignored = False  # Flag to indicate if initial samples have been ignored
total_packet_count = 0  # Counter for the total number of packets received
minute_start_time = None  # Timestamp to mark the start of each minute
ten_minute_start_time = None  # Timestamp to mark the start of the 10-minute interval
total_data_received = 0  # Accumulator for total data received over 10 minutes
EXPECTED_DATA_COUNT = 150000  # Expected number of data packets in 10 minutes

# LSL Stream Setup
lsl_stream_info = StreamInfo('ArduinoDataStream', 'Data', 6, 250, 'float32', 'arduino1234')  # Create LSL stream info with 6 channels, 250 Hz, and float32 data type
lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL stream outlet for sending data

# 1. Arduino Auto-Detection Function
def auto_detect_arduino(baudrate=115200, timeout=1):
    """
    Function to auto-detect Arduino connected to a serial port.
    """
    ports = serial.tools.list_ports.comports()  # List all available serial ports
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Open serial connection to the port
            ser.write(b'TEST\n')  # Write a test string to the port
            time.sleep(1)  # Wait for the device to respond
            response = ser.readline().strip()  # Read response from the device
            if response:  # Check if response is not empty
                ser.close()  # Close the serial connection
                print(f"Arduino detected at {port.device}")  # Print detected port
                return port.device  # Return the detected port
            ser.close()  # Close the serial connection if no response
        except (OSError, serial.SerialException):  # Handle potential errors
            pass  # Ignore errors and continue
    print("Arduino not detected")  # Print if no Arduino was detected
    return None  # Return None if Arduino is not found

# 2. Main Data Processing Functions
def read_arduino_data(ser):
    """
    Function to read and process data from the Arduino.
    """
    global total_packet_count  # Access global variable for total packet count
    raw_data = ser.read(17)  # Read 17 bytes of data from the serial port
    
    if len(raw_data) == 17:  # Ensure that the data length is exactly 17 bytes
        packet_buffer.append(raw_data)  # Append the raw data to the buffer
        if initial_samples_ignored:  # Check if initial samples have been ignored
            total_packet_count += 1  # Increment total packet count

def log_minute_data(csv_writer):
    """
    Function to log the number of packets received every minute to a CSV file.
    """
    global total_packet_count  # Access global variable for total packet count
    global total_data_received  # Access global variable for total data received
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # Get current timestamp
    csv_writer.writerow([current_time, total_packet_count])  # Write timestamp and packet count to CSV
    total_data_received += total_packet_count  # Accumulate total data count
    total_packet_count = 0  # Reset packet count for the next minute

def process_data(port, baudrate, duration):
    """
    Function to handle the main data processing.
    """
    global packet_buffer, initial_samples_ignored, total_packet_count, minute_start_time, ten_minute_start_time, total_data_received
    
    with serial.Serial(port, baudrate, timeout=0.1) as ser:  # Open serial connection
        with open('packet_data.csv', mode='w', newline='') as csv_file:  # Open CSV file for writing
            csv_writer = csv.writer(csv_file)  # Create CSV writer object
            csv_writer.writerow(['Timestamp', 'Packets Received'])  # Write header row to CSV

            try:
                time.sleep(2)  # Allow Arduino board to initialize

                while True:  # Continuous loop to read data
                    read_arduino_data(ser)  # Read and process data from Arduino

                    if not initial_samples_ignored:
                        # Ignore the first 2500 samples to account for initialization
                        if len(packet_buffer) >= 2500:
                            for _ in range(2500):
                                packet_buffer.popleft()
                            initial_samples_ignored = True  # Set flag to indicate initial samples are ignored
                            minute_start_time = time.time()  # Initialize minute timer
                            ten_minute_start_time = time.time()  # Initialize 10-minute timer

                    if initial_samples_ignored:
                        current_time = time.time()  # Get current time

                        # Check if one minute has passed
                        if current_time - minute_start_time >= 60:
                            print(f"Data count for this minute: {total_packet_count}")  # Print minute data count
                            log_minute_data(csv_writer)  # Log data for the minute
                            minute_start_time = current_time  # Reset minute timer

                        # Check if 10 minutes have passed
                        if current_time - ten_minute_start_time >= 600:
                            # Log the number of packets received in the last 10 minutes
                            log_minute_data(csv_writer)  # Log data for the 10th minute
                            data_received_after_10_minutes = total_data_received  # Ensure the 10th minute data is added
                            print(f"Total data count after 10 minutes: {data_received_after_10_minutes}")  # Print total data count

                            # Calculate and print the sampling rate
                            sampling_rate = data_received_after_10_minutes / (10 * 60)  # Calculate sampling rate per second
                            print(f"Sampling rate: {sampling_rate:.2f} samples/second")  # Print sampling rate

                            # Calculate drift rate
                            expected_sampling_rate = 250  # Expected sampling rate (samples per second)
                            drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate ) * 3600 #Drift in seconds per hour
                            print(f"Drift: {drift:.2f} seconds/hour")  # Print drift

                            # Reset for the next 10-minute cycle
                            packet_buffer.clear()  # Clear the buffer
                            total_data_received = 0  # Reset total data received
                            minute_start_time = current_time  # Reset minute timer to avoid overlap
                            ten_minute_start_time = current_time  # Reset 10-minute timer to continue correctly

            except KeyboardInterrupt:  # Handle user interruption
                print("Exiting.")  # Only print "Exiting" after keyboard interruption

# 3. Argparse Configuration
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arduino Data Processing Script")  # Create argument parser
    parser.add_argument('-d', '--detect', action='store_true', help="Auto-detect Arduino")  # Option to auto-detect Arduino
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")  # Argument to specify the COM port
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")  # Argument to specify baud rate
    parser.add_argument('-t', '--time', type=int, default=10, help="Set duration in minutes for data processing")  # Argument to specify duration

    args = parser.parse_args()  # Parse command-line arguments
    
    if args.detect:  # Check if auto-detection is requested
        port = auto_detect_arduino(baudrate=args.baudrate)  # Auto-detect Arduino and get port
        if not port:  # If no port was detected
            exit(1)  # Exit with error code
    else:
        port = args.port  # Use specified port

    if port:  # If a valid port is provided
        process_data(port, args.baudrate, args.time)  # Start processing data
    else:
        print("Please provide a valid COM port.")  # Request valid COM port if none was provided. 