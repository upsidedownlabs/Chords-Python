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
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)
            time.sleep(2)
            ser.write(b'WHORU\n')
            response = ser.readline().strip().decode()
            if response:
                global board
                ser.close()
                print(f"{response} detected at {port.device}")
                board = response
                return port.device
            ser.close()
        except (OSError, serial.SerialException):
            pass
    print("Arduino not detected")
    return None

# Function to send a stop command to Arduino
def send_stop_command(ser):
    ser.write(b'STOP\n')

# Asynchronous function to read data from Arduino
async def async_read_arduino_data(ser, csv_writer=None, stop_event=None):
    global start_time, last_ten_minute_time

    while not stop_event.is_set():
        if keyboard.is_pressed('q'):
            print("Process interrupted by user")
            stop_event.set()  # Set stop event on keyboard interrupt
            break

        await asyncio.to_thread(read_arduino_data, ser, csv_writer)

        # Track elapsed time for logging
        current_time = time.time()
        if current_time - start_time >= 1:
            log_one_second_data(verbose)
            start_time = current_time

        if current_time - last_ten_minute_time >= 600:
            log_ten_minute_data(verbose)
            last_ten_minute_time = current_time

        await asyncio.sleep(0.01)  # Non-blocking wait
        
# Function to read data from Arduino
def read_arduino_data(ser, csv_writer=None, verbose=False):
    global buffer, data
    raw_data = ser.read(ser.in_waiting or 1)
    buffer.extend(raw_data)

    while len(buffer) >= PACKET_LENGTH:
        sync_index = buffer.find(bytes([SYNC_BYTE1, SYNC_BYTE2]))
        if sync_index == -1:
            buffer.clear()
            continue

        if len(buffer) >= sync_index + PACKET_LENGTH:
            packet = buffer[sync_index:sync_index + PACKET_LENGTH]
            if packet[0] == SYNC_BYTE1 and packet[1] == SYNC_BYTE2 and packet[-1] == END_BYTE:
                channel_data = [(packet[2*i + 2] << 8) | packet[2*i + 3] for i in range(NUM_CHANNELS)]
                if csv_writer:
                    csv_writer.writerow(channel_data)
                data = channel_data
                del buffer[:sync_index + PACKET_LENGTH]
            else:
                del buffer[:sync_index + 1]

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

# Function to parse data from Arduino
async def parse_data(port, baudrate, timer=None, lsl_flag=False, csv_flag=False, verbose=False):
    global total_packet_count, cumulative_packet_count, start_time, lsl_outlet, last_ten_minute_time, csv_filename

    csv_writer = None
    ser = None
    csv_file = None
    stop_event = asyncio.Event()  # Create a stop event

    # Start LSL streaming if requested
    if lsl_flag:
        lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, boards_sample_rate[board], 'float32', 'UpsideDownLabs')  # Define LSL
        lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL outlet
        print("LSL stream started")  # Notify user
        time.sleep(0.5)  # Wait for the LSL stream to start

    if csv_flag:
        csv_filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        print(f"CSV recording started. Data will be saved to {csv_filename}")

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
        csv_file = open(csv_filename, mode='w', newline='') if csv_flag else None
        if csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])

        start_timer()
        ser.write(b'START\n')

        # Run data reading in the background
        asyncio.create_task(async_read_arduino_data(ser, csv_writer, stop_event))

        # Timer logic
        if timer:
            await asyncio.sleep(timer)
            print("Timer expired, sending stop command...")
            send_stop_command(ser)
            stop_event.set()  # Signal to stop reading data
            return

        # Main loop to monitor keyboard for 'q' press
        while not stop_event.is_set():
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("Process interrupted by user")

    finally:
        if ser:
            if ser.is_open:
                print("Sending STOP command...")
                send_stop_command(ser)
                time.sleep(1)  # Ensure Arduino processes the STOP command
                print("Closing serial connection...")
                ser.close()

        if lsl_outlet:
            lsl_outlet = None
        
        if csv_file:
            csv_file.close()
            print(f"CSV recording saved as {csv_filename}")

    print(f"Exiting.\nTotal missing samples: {missing_samples}")
    sys.exit(0)

# Main entry point of the script
def main():
    global verbose
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")
    parser.add_argument('-b', '--baudrate', type=int, default=230400, help="Set baud rate for the serial communication")
    parser.add_argument('--csv', action='store_true', help="Create and write to a CSV file")
    parser.add_argument('--lsl', action='store_true', help="Start LSL stream")
    parser.add_argument('-t', '--timer', type=int, help="Set a timer in seconds to stop the program")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output with statistical data")

    args = parser.parse_args()
    verbose = args.verbose

    if not args.csv and not args.lsl:
        parser.print_help()
        return

    port = args.port or auto_detect_arduino(args.baudrate)
    if port is None:
        print("Arduino port not specified or detected. Exiting.")
        return

    asyncio.run(parse_data(port, args.baudrate, timer=args.timer, lsl_flag=args.lsl, csv_flag=args.csv, verbose=args.verbose))

# Run the main function if this script is executed
if __name__ == "__main__":
    main()