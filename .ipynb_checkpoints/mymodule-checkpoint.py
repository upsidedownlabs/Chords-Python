from pylsl import StreamInfo, StreamOutlet
import argparse
import serial
import time
import csv
from collections import deque
import serial.tools.list_ports

# Initialize global variables
packet_buffer = deque()  # Buffer to store packets
initial_samples_ignored = False  # Flag to indicate if initial samples have been ignored
total_packet_count = 0  # Counter for packets received in the current minute
minute_start_time = None  # Timestamp for the start of the current minute
ten_minute_start_time = None  # Timestamp for the start of the current 10-minute interval
total_data_received = 0  # Total number of data packets received in the 10-minute interval
previous_sample_number = None  # Variable to store the last sample number
missing_samples = 0  # Counter for missing samples
initial_sample_count = 0  # Counter for samples received before processing starts

# LSL Stream Setup
lsl_stream_info = StreamInfo('ArduinoDataStream', 'Data', 6, 250, 'float32', 'arduino1234')  # Define LSL stream info
lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL outlet for streaming data

def auto_detect_arduino(baudrate=115200, timeout=1):
    """
    Auto-detect Arduino by checking all available serial ports.
    """
    ports = serial.tools.list_ports.comports()  # List all serial ports
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Open serial port
            ser.write(b'TEST\n')  # Send a test command to Arduino
            time.sleep(1)  # Wait for Arduino to respond
            response = ser.readline().strip()  # Read response from Arduino
            if response:
                ser.close()  # Close serial port
                print(f"Arduino detected at {port.device}")  # Print detected port
                return port.device  # Return the detected port
            ser.close()  # Close serial port if no response
        except (OSError, serial.SerialException):
            pass  # Handle errors in serial port communication
    print("Arduino not detected")  # Print message if no Arduino is detected
    return None  # Return None if no Arduino is detected

def read_arduino_data(ser, csv_writer):
    """
    Read data from Arduino, process it, and write to CSV and LSL stream.
    """
    global total_packet_count, previous_sample_number, missing_samples, initial_sample_count, initial_samples_ignored
    raw_data = ser.read(17)  # Read 17 bytes from the serial port

    # Check for valid data packet structure
    if len(raw_data) == 17 and raw_data[0] == 0xA5 and raw_data[1] == 0x5A and raw_data[-1] == 0x01:
        counter = raw_data[3]  # Counter is at index 3

        # Ensure counter number is exactly one more than the previous one
        if previous_sample_number is not None and counter != (previous_sample_number + 1) % 256:
            missing_samples += (counter - previous_sample_number - 1) % 256
            print(f"Error: Expected counter {previous_sample_number + 1} but received {counter}. Missing samples: {missing_samples}")

        previous_sample_number = counter  # Update previous sample number to current counter

        if initial_samples_ignored:
            total_packet_count += 1  # Increment packet count only after initial samples are ignored

        # Merge high and low bytes to form channel data
        channel_data = []
        for i in range(4, 16, 2):  # Indices for channel data
            high_byte = raw_data[i]
            low_byte = raw_data[i + 1]
            value = (high_byte << 8) | low_byte  # Combine high and low bytes to form the 16-bit value
            channel_data.append(float(value))

        # Write counter and channel data to CSV
        csv_writer.writerow([counter] + channel_data)

        # Push channel data to LSL stream
        lsl_outlet.push_sample(channel_data)

        # Count initial samples
        if not initial_samples_ignored:
            initial_sample_count += 1  # Increment initial sample count
            if initial_sample_count >= 2500:  # Check if 2500 samples have been received
                initial_samples_ignored = True  # Set flag to true to start processing actual data
                print("Initial Samples Ignored")
                start_timers()  # Start timers right after ignoring initial samples

    else:
        print("Invalid Data Packet")  # Print message if data packet is invalid

def start_timers():
    """
    Initialize timers for minute and ten-minute intervals and reset packet count.
    """
    global minute_start_time, ten_minute_start_time, total_packet_count
    current_time = time.time()  # Get current timestamp
    minute_start_time = current_time  # Set start time for the minute interval
    ten_minute_start_time = current_time  # Set start time for the 10-minute interval
    total_packet_count = 0  # Reset packet count after ignoring initial samples

def log_minute_data():
    """
    Logs and resets data count per minute.
    """
    global total_packet_count
    count_for_minute = total_packet_count  # Get the count for the current minute
    print(f"Data count for this minute: {count_for_minute}")  # Print count for the current minute
    total_packet_count = 0  # Reset packet count for the next minute
    return count_for_minute  # Return the count for further processing

def log_ten_minute_data():
    """
    Logs data count for every 10 minutes and computes sampling rate and drift.
    """
    global total_data_received, ten_minute_start_time

    # Calculate total data count and sampling rate
    print(f"Total data count after 10 minutes: {total_data_received}")  # Print total data count for the last 10 minutes
    sampling_rate = total_data_received / (10 * 60)  # Calculate sampling rate
    print(f"Sampling rate: {sampling_rate:.2f} samples/second")  # Print sampling rate

    # Calculate drift
    expected_sampling_rate = 250  # Expected sampling rate
    drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600  # Calculate drift in seconds/hour
    print(f"Drift: {drift:.2f} seconds/hour")  # Print drift

    # Reset for the next 10-minute interval
    total_data_received = 0  # Reset total data received
    ten_minute_start_time = time.time()  # Update start time for the next 10-minute interval

def process_data(port, baudrate, duration):
    """
    Main function to process data from the Arduino.
    """
    global packet_buffer, initial_samples_ignored, total_packet_count, minute_start_time, ten_minute_start_time, total_data_received

    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        with open('packet_data.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])  # Write the CSV header

            try:
                time.sleep(2)  # Allow time for Arduino to initialize

                start_timers()  # Initialize timers

                while True:
                    read_arduino_data(ser, csv_writer)  # Read data from Arduino

                    if initial_samples_ignored:
                        current_time = time.time()  # Get current timestamp

                        # Handle minute interval
                        if current_time - minute_start_time >= 60:
                            total_data_received += log_minute_data()  # Log minute data and add to total
                            minute_start_time = current_time  # Reset minute timer

                        # Handle 10-minute interval
                        if current_time - ten_minute_start_time >= 600:
                            total_data_received += log_minute_data()  # Log last minute before the 10-minute interval ends
                            log_ten_minute_data()  # Log data for the 10-minute interval
                            start_timers()  # Reset timers to prevent a partial minute log after the 10-minute interval

            except KeyboardInterrupt:
                # Handle keyboard interrupt
                print(f"Exiting. \nTotal missing samples: {missing_samples}")  # Print missing samples and exit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arduino Data Processing Script")
    parser.add_argument('-d', '--detect', action='store_true', help="Auto-detect Arduino")  # Argument to auto-detect Arduino
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")  # Argument to specify COM port
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")  # Argument for baud rate
    parser.add_argument('-t', '--time', type=int, default=10, help="Set duration in minutes for data processing")  # Argument for duration

    args = parser.parse_args()  # Parse command-line arguments

    if args.detect:
        port = auto_detect_arduino(baudrate=args.baudrate)  # Auto-detect Arduino if specified
    else:
        port = args.port  # Use specified port

    if port is None:
        print("Arduino port not specified or detected. Exiting.")
    else:
        process_data(port, args.baudrate, args.time)  # Start processing data