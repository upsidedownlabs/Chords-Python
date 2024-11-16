import argparse
import serial
import time
import csv
from collections import deque
import serial.tools.list_ports

# Initialize global variables for processing
packet_buffer = deque()
initial_samples_ignored = False
total_packet_count = 0
minute_start_time = None
ten_minute_start_time = None
EXPECTED_DATA_COUNT = 150000  # Expected data packets in 10 minutes

# 1. Arduino Auto-Detection Function
def auto_detect_arduino(baudrate=115200, timeout=1):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)
            ser.write(b'TEST\n')  # Write a test string to the port
            time.sleep(1)  # Give the device time to respond
            response = ser.readline().strip()
            if response:  # Check if the device responded
                ser.close()
                print(f"Arduino detected at {port.device}")
                return port.device
            ser.close()
        except (OSError, serial.SerialException):
            pass
    print("Arduino not detected")
    return None

# 2. Main Data Processing Functions

def read_arduino_data(ser):
    """Function to read and process data from the Arduino."""
    global total_packet_count
    # Read 17 bytes of data from the serial port
    raw_data = ser.read(17)
    
    if len(raw_data) == 17:  # Ensure that a full packet (17 bytes) has been received
        packet_buffer.append(raw_data)  # Store the raw data in the buffer
        if initial_samples_ignored:
            total_packet_count += 1  # Increment packet count only after ignoring initial samples

def log_minute_data(csv_writer):
    """Function to log the number of packets received every minute to a CSV file."""
    global total_packet_count
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # Get the current timestamp
    csv_writer.writerow([current_time, total_packet_count])  # Write the data to the CSV file
    print(f"Data count for this minute: {total_packet_count}")  # Print data count for this minute
    total_packet_count = 0  # Reset the packet count for the next minute

def calculate_ppm(actual_data_count, expected_data_count):
    """Function to calculate and print the parts per million (PPM)."""
    missed_packets = expected_data_count - actual_data_count
    ppm = (missed_packets / expected_data_count) * 1_000_000
    print(f"Expected Data Count (10 minutes): {expected_data_count}")
    print(f"Actual Data Count (10 minutes): {actual_data_count}")
    print(f"Missed Packets: {missed_packets}")
    print(f"Parts Per Million (PPM) of missed packets: {ppm:.2f} PPM")

def process_data(port, baudrate, duration):
    """Function to handle the main data processing."""
    global packet_buffer, initial_samples_ignored, total_packet_count, minute_start_time, ten_minute_start_time
    
    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        with open('packet_data.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Timestamp', 'Packets Received'])  # Write the header row

            try:
                time.sleep(2)  # Allow board initialization

                while True:  # Infinite loop to continuously read data from the Arduino
                    read_arduino_data(ser)  # Call the function to read and process the data

                    if not initial_samples_ignored:
                        # Ignore the first 2500 samples
                        if len(packet_buffer) >= 2500:
                            # Discard initial samples
                            for _ in range(2500):
                                packet_buffer.popleft()
                            initial_samples_ignored = True  # Set the flag to start counting
                            minute_start_time = time.time()  # Initialize the minute timer
                            ten_minute_start_time = time.time()  # Initialize the 10-minute timer

                    if initial_samples_ignored:
                        current_time = time.time()  # Update the current time

                        # Check if 10 minutes have passed since the start
                        if current_time - ten_minute_start_time >= 600:
                            data_received_after_10_minutes = total_packet_count
                            print(f"Number of data received after 10 minutes: {data_received_after_10_minutes}")

                            # Calculate and print the PPM
                            calculate_ppm(data_received_after_10_minutes, EXPECTED_DATA_COUNT)

                            # Reset the 10-minute timer and buffer for the next cycle
                            ten_minute_start_time = current_time
                            packet_buffer.clear()  # Clear the buffer for the next 10 minutes
                            total_packet_count = 0  # Reset total packet count

                        # Check if one minute has passed since the last minute reset
                        if current_time - minute_start_time >= 60:
                            log_minute_data(csv_writer)  # Log the data for the last minute
                            minute_start_time = current_time  # Reset the minute timer

            except KeyboardInterrupt:
                print("Exiting...")  # When the user interrupts, exit the loop
                if initial_samples_ignored:
                    log_minute_data(csv_writer)  # Log the last minute's data before exiting

# 3. Argparse Configuration
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arduino Data Processing Script")
    
    parser.add_argument('-d', '--detect', action='store_true', help="Auto-detect Arduino")
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")
    parser.add_argument('-t', '--time', type=int, default=10, help="Set duration in minutes for data processing")
    
    args = parser.parse_args()
    
    if args.detect:
        port = auto_detect_arduino(baudrate=args.baudrate)
        if not port:
            print("Could not auto-detect Arduino. Exiting.")
            exit(1)
    else:
        port = args.port
    
    if port:
        process_data(port, args.baudrate, args.time)
    else:
        print("Please specify a port using the -p or --port argument.")