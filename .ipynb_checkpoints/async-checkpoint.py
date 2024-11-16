from pylsl import StreamInfo, StreamOutlet  # For LSL (Lab Streaming Layer) to stream data
import argparse  # For command-line argument parsing
import serial  # For serial communication with Arduino
import time  # For time-related functions
import csv  # For handling CSV file operations
from datetime import datetime  # For getting current timestamps
import serial.tools.list_ports  # To list available serial ports
import numpy as np  # For handling numeric arrays
import keyboard  #For keyboard interruptions
import sys   #To interact with the Python runtime environment
import asyncio
import threading

# Initialize global variables for tracking and processing data
total_packet_count = 0  # Total packets received in the last second
cumulative_packet_count = 0  # Total packets received in the last 10 minutes
start_time = None  # Track the start time for packet counting
last_ten_minute_time = None  # Track the last 10-minute interval
previous_sample_number = None  # Store the previous sample number for detecting missing samples
missing_samples = 0  # Count of missing samples due to packet loss
buffer = bytearray()  # Buffer for storing incoming raw data from Arduino
data = np.zeros((6, 2000))  # 2D array to store data for real-time plotting (6 channels, 2000 data points)
samples_per_second = 0  # Number of samples received per second

# Initialize gloabal variables for Arduino Board
board = ""          # Variable for Connected Arduino Board
boards_sample_rate = {"UNO-R3":250, "UNO-R4":500}   #Standard Sample rate for Arduino Boards Different Firmware

# Initialize gloabal variables for Incoming Data
PACKET_LENGTH = 16  # Expected length of each data packet
SYNC_BYTE1 = 0xc7  # First byte of sync marker
SYNC_BYTE2 = 0x7c  # Second byte of sync marker
END_BYTE = 0x01  # End byte marker
NUM_CHANNELS = 6    #Number of Channels being received
HEADER_LENGTH = 3   #Length of the Packet Header

## Initialize gloabal variables for Output
lsl_outlet = None  # Placeholder for LSL stream outlet
verbose = False  # Flag for verbose output mode
csv_filename = None  # Store CSV filename

# Function to automatically detect the Arduino's serial port
def auto_detect_arduino(baudrate, timeout=1):
    ports = serial.tools.list_ports.comports()  # List available serial ports
    for port in ports:  # Iterate through each port
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Try opening the port
            time.sleep(2)  # Wait for the device to initialize
            ser.write(b'WHORU\n') # Check board type
            response = ser.readline().strip().decode()  # Try reading from the port
            if response:  # If response is received, assume it's the Arduino
                global board
                ser.close()  # Close the serial connection
                print(f"{response} detected at {port.device}")  # Notify the user
                board = response
                return port.device  # Return the port name
            ser.close()  # Close the port if no response
        except (OSError, serial.SerialException):  # Handle exceptions if the port can't be opened
            pass
    print("Arduino not detected")  # Notify if no Arduino is found
    return None  # Return None if not found

# Function to asynchronously read data from Arduino
async def async_read_arduino_data(ser, csv_writer=None, verbose=False):
    global start_time, last_ten_minute_time

    while True:
        if keyboard.is_pressed('q'):
            print("Process interrupted by user")
            break  # Break out of the loop if 'q' is pressed

        await asyncio.to_thread(read_arduino_data, ser, csv_writer)  # Run data reading in a background thread

        # Track elapsed time for logging every second and every 10 minutes
        current_time = time.time()
        elapsed_time = current_time - start_time
        elapsed_since_last_10_minutes = current_time - last_ten_minute_time

        # Log data count every second
        if elapsed_time >= 1:
            log_one_second_data(verbose)
            start_time = current_time  # Reset start time for next second

        # Log data count every 10 minutes
        if elapsed_since_last_10_minutes >= 600:
            log_ten_minute_data(verbose)
            last_ten_minute_time = current_time  # Reset 10-minute timer

        await asyncio.sleep(0.01)  # Non-blocking wait

# Function to read data from Arduino
def read_arduino_data(ser, csv_writer=None):
    global total_packet_count, cumulative_packet_count, previous_sample_number, missing_samples, buffer, data

    raw_data = ser.read(ser.in_waiting or 1)  # Read available data from the serial port
    buffer.extend(raw_data)  # Add received data to the buffer
    while len(buffer) >= PACKET_LENGTH:  # Continue processing if the buffer contains at least one full packet
        sync_index = buffer.find(bytes([SYNC_BYTE1, SYNC_BYTE2]))  # Search for the sync marker

        if sync_index == -1:  # If sync marker not found, clear the buffer
            buffer.clear()
            continue
        
        if len(buffer) >= sync_index + PACKET_LENGTH:  # Check if a full packet is available
            packet = buffer[sync_index:sync_index + PACKET_LENGTH]  # Extract the packet
            if len(packet) == PACKET_LENGTH and packet[0] == SYNC_BYTE1 and packet[1] == SYNC_BYTE2 and packet[-1] == END_BYTE:
                    
                # Extract the packet if it is valid (correct length, sync bytes, and end byte)
                counter = packet[2]  # Read the counter byte (for tracking sample order)

                # Check for missing samples by comparing the counter values
                if previous_sample_number is not None and counter != (previous_sample_number + 1) % 256:
                    missing_samples += (counter - previous_sample_number - 1) % 256  # Calculate missing samples
                    if verbose:
                        print(f"Error: Expected counter {previous_sample_number + 1} but received {counter}. Missing samples: {missing_samples}")

                previous_sample_number = counter  # Update the previous sample number
                total_packet_count += 1  # Increment total packet count for the current second
                cumulative_packet_count += 1  # Increment cumulative packet count for the last 10 minutes

                # Extract channel data (6 channels, 2 bytes per channel)
                channel_data = []
                for channel in range(NUM_CHANNELS):  # Loop through channel data bytes
                    high_byte = packet[2*channel + HEADER_LENGTH]
                    low_byte = packet[2*channel + HEADER_LENGTH + 1]
                    value = (high_byte << 8) | low_byte  # Combine high and low bytes
                    channel_data.append(float(value))  # Convert to float and add to channel data

                if csv_writer:  # If CSV logging is enabled, write the data to the CSV file
                    csv_writer.writerow([counter] + channel_data)
                if lsl_outlet:  # If LSL streaming is enabled, send the data to the LSL stream
                    lsl_outlet.push_sample(channel_data)

                # Update the data array for real-time plotting
                data = np.roll(data, -1, axis=1)  # Shift data to the left
                data[:, -1] = channel_data  # Add new channel data to the right end of the array

                del buffer[:sync_index + PACKET_LENGTH]  # Remove the processed packet from the buffer
            else:
                del buffer[:sync_index + 1]  # If the packet is invalid, remove only the sync marker

# Function to start timers for logging data
def start_timer():
    global start_time, last_ten_minute_time, total_packet_count, cumulative_packet_count
    time.sleep(0.5)  # Give some time to settle before starting
    current_time = time.time()  # Get the current time
    start_time = current_time  # Set the start time for packet counting
    last_ten_minute_time = current_time  # Set the start time for 10-minute interval logging
    total_packet_count = 0  # Initialize total packet count
    cumulative_packet_count = 0  # Initialize cumulative packet count

# Function to log data every second
def log_one_second_data(verbose=False):
    global total_packet_count, samples_per_second
    samples_per_second = total_packet_count  # Update the samples per second
    if verbose:
        print(f"Data count for the last second: {total_packet_count} samples, Missing samples: {missing_samples}")  # Print verbose output
    total_packet_count = 0  # Reset total packet count for the next second

# Function to log data for 10-minute intervals
def log_ten_minute_data(verbose=False):
    global cumulative_packet_count, last_ten_minute_time
    if verbose:
        print(f"Total data count after 10 minutes: {cumulative_packet_count}")  # Print cumulative data count
        sampling_rate = cumulative_packet_count / (10 * 60)  # Calculate sampling rate
        print(f"Sampling rate: {sampling_rate:.2f} samples/second")  # Print sampling rate
        expected_sampling_rate = boards_sample_rate[board]  # Expected sampling rate
        drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600  # Calculate drift
        print(f"Drift: {drift:.2f} seconds/hour")  # Print drift
    cumulative_packet_count = 0  # Reset cumulative packet count
    last_ten_minute_time = time.time()  # Update the last 10-minute interval start time

def parse_data(port, baudrate, lsl_flag=False, csv_flag=False, verbose=False,run_time=None):
    global total_packet_count, cumulative_packet_count, start_time, lsl_outlet, last_ten_minute_time, csv_filename

    csv_writer = None  # Placeholder for CSV writer
    ser = None
    csv_file = None

    # Start LSL streaming if requested
    if lsl_flag:
        lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, boards_sample_rate[board], 'float32', 'UpsideDownLabs')  # Define LSL
        lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL outlet
        print("LSL stream started")  # Notify user
        time.sleep(0.5)  # Wait for the LSL stream to start
    
    if csv_flag:
        csv_filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"  # Create timestamped filename
        print(f"CSV recording started. Data will be saved to {csv_filename}")  # Notify user

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
        csv_file = open(csv_filename, mode='w', newline='') if csv_flag else None  # Open CSV file if logging is
        if csv_file:
            csv_writer = csv.writer(csv_file)  # Create CSV writer
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])  # Write header

        start_timer()  # Start timers for logging
        end_time = time.time() + run_time if run_time else None
        ser.write(b'START\n')

        asyncio.run(async_read_arduino_data(ser, csv_writer, verbose))

        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            elapsed_since_last_10_minutes = current_time - last_ten_minute_time

            if elapsed_time >= 1:
                log_one_second_data(verbose)
                start_time = current_time
            if elapsed_since_last_10_minutes >= 600:
                log_ten_minute_data(verbose)

            if keyboard.is_pressed('q'):
                print("Process interrupted by user")
                break
                
            if run_time and current_time >= end_time:
                print("Runtime Over, sending STOP command...")
                break

    except KeyboardInterrupt:
        print("Process interrupted by user")
    
    finally:      # Ensure the serial connection is closed and STOP command is sent
        if ser:
            if ser.is_open:
                print("Sending STOP command...")
                ser.write(b'STOP\n')
                time.sleep(1)  # Ensure Arduino processes the STOP command
                print("Closing serial connection...")
                ser.close()

        if lsl_outlet:     # Assuming LSL outlet cleanup if required
            lsl_outlet = None
        
        if csv_file:    # Ensure CSV file is closed
            csv_file.close()
            print(f"CSV recording saved as {csv_filename}")
            
    print(f"Exiting.\nTotal missing samples: {missing_samples}")
    sys.exit(0)

# Main entry point of the script
def main():
    global verbose
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")  # Create argument parser
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")  # Port argument
    parser.add_argument('-b', '--baudrate', type=int, default=230400, help="Set baud rate for the serial communication")  # Baud rate 
    parser.add_argument('--csv', action='store_true', help="Create and write to a CSV file")  # CSV logging flag
    parser.add_argument('--lsl', action='store_true', help="Start LSL stream")  # LSL streaming flag
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output with statistical data")  # Verbose flag
    parser.add_argument('-t', '--time', type=int, help="Run the program for a specified number of seconds and then exit")   #set time

    args = parser.parse_args()  # Parse command-line arguments
    verbose = args.verbose  # Set verbose mode

    # Check if any logging or GUI options are selected, else show help
    if not args.csv and not args.lsl and not args.time is None:
        parser.print_help()  # Print help if no options are selected
        return

    port = args.port or auto_detect_arduino(args.baudrate)  # Get the port from arguments or auto-detect
    if port is None:
        print("Arduino port not specified or detected. Exiting.")  # Notify if no port is available
        return
    # Start data acquisition
    parse_data(port, args.baudrate, lsl_flag=args.lsl, csv_flag=args.csv, verbose=args.verbose,run_time=args.time)

# Run the main function if this script is executed
if __name__ == "__main__":
    main()