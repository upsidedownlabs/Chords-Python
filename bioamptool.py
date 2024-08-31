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

from pylsl import StreamInfo, StreamOutlet
import argparse
import serial
import time
import csv
from datetime import datetime
import serial.tools.list_ports

# Initialize global variables
total_packet_count = 0  # Total number of packets received
start_time = None  # Start time of data collection
last_ten_minute_time = None  # Time when the last 10-minute interval started
total_data_received = 0  # Accumulated total number of data points received
previous_sample_number = None  # Last received sample number to detect missing samples
missing_samples = 0  # Count of missing samples
buffer = bytearray()  # Buffer to accumulate incoming data bytes
PACKET_LENGTH = 17  # Length of each data packet
SYNC_BYTE1 = 0xA5  # First sync byte value
SYNC_BYTE2 = 0x5A  # Second sync byte value
END_BYTE = 0x01  # End byte value for the packet

# LSL Stream Setup
lsl_outlet = None  # LSL outlet for streaming data

def auto_detect_arduino(baudrate, timeout=1):    #    Auto-detect Arduino by checking all available serial ports.
    ports = serial.tools.list_ports.comports()  # List all available serial ports
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Open serial port
            time.sleep(1)  # Wait for Arduino to initialize
            response = ser.readline().strip()  # Read data from Arduino
            if response:
                ser.close()  # Close the serial port if response is found
                print(f"Arduino detected at {port.device}")  # Print detected port  
                return port.device  # Return the detected port
            ser.close()  # Close the serial port if no response
        except (OSError, serial.SerialException):
            pass  # Handle any exceptions and continue scanning other ports
    print("Arduino not detected")  # Print message if no Arduino is found
    return None  # Return None if no Arduino is detected

def read_arduino_data(ser, csv_writer=None):    #Read data from Arduino, process it, and optionally write to CSV and LSL stream.
    global total_packet_count, previous_sample_number, missing_samples, buffer
    raw_data = ser.read(ser.in_waiting or 1)  # Read data from the serial port
    buffer.extend(raw_data)  # Append the read data to the buffer

    while len(buffer) >= PACKET_LENGTH:  # Process data if buffer has enough bytes
        sync_index = buffer.find(bytes([SYNC_BYTE1, SYNC_BYTE2]))  # Find sync bytes in buffer

        if sync_index == -1:  # If sync bytes are not found
            buffer.clear()  # Clear the buffer and continue
            continue
        
        if len(buffer) >= sync_index + PACKET_LENGTH:  # Check if buffer has a complete packet
            packet = buffer[sync_index:sync_index + PACKET_LENGTH]  # Extract the packet from the buffer
            if len(packet) == 17 and packet[0] == SYNC_BYTE1 and packet[1] == SYNC_BYTE2 and packet[-1] == END_BYTE:
                counter = packet[3]  # Extract the counter value from the packet

                if previous_sample_number is not None and counter != (previous_sample_number + 1) % 256:
                    # Check for missing samples based on the counter
                    missing_samples += (counter - previous_sample_number - 1) % 256
                    print(f"Error: Expected counter {previous_sample_number + 1} but received {counter}. Missing samples: {missing_samples}")

                previous_sample_number = counter  # Update the previous sample number
                total_packet_count += 1  # Increment the total packet count

                channel_data = []  # List to store channel data
                for i in range(4, 16, 2):  # Extract channel data from the packet
                    high_byte = packet[i]  # High byte of the data
                    low_byte = packet[i + 1]  # Low byte of the data
                    value = (high_byte << 8) | low_byte  # Combine high and low byte into a value
                    channel_data.append(float(value))  # Append the value to the channel data list

                if csv_writer:
                    csv_writer.writerow([counter] + channel_data)  # Write data to CSV file
                if lsl_outlet:
                    lsl_outlet.push_sample(channel_data)  # Send data to LSL stream

                del buffer[:sync_index + PACKET_LENGTH]  # Remove processed packet from the buffer
            else:
                del buffer[:sync_index + 1]  # Remove invalid data from the buffer

def start_timer():     # Initialize timers for minute and ten-minute intervals and reset packet count.
    global start_time, last_ten_minute_time, total_packet_count
    time.sleep(0.5)  # Ensure LSL stream setup is complete
    current_time = time.time()  # Get the current time
    start_time = current_time  # Set the start time
    last_ten_minute_time = current_time  # Set the time for the last ten-minute interval
    total_packet_count = 0  # Reset total packet count

def log_minute_data():   #Logs and resets data count per minute
    global total_packet_count
    count_for_minute = total_packet_count  # Get the data count for the current minute
    print(f"Data count for this minute: {count_for_minute} samples")  # Print the data count
    total_packet_count = 0  # Reset total packet count for the next minute
    return count_for_minute  # Return the count for further use

def log_ten_minute_data():    #Logs data count for every 10 minutes and computes sampling rate and drift.
    global total_data_received, last_ten_minute_time

    print(f"Total data count after 10 minutes: {total_data_received} samples")  # Print total data count
    sampling_rate = total_data_received / (10 * 60)  # Calculate the sampling rate
    print(f"Sampling rate: {sampling_rate:.2f} samples/second")  # Print the sampling rate

    expected_sampling_rate = 250  # Expected sampling rate
    drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600  # Calculate drift in seconds per hour
    print(f"Drift: {drift:.2f} seconds/hour")  # Print drift

    total_data_received = 0  # Reset total data received for the next 10-minute interval
    last_ten_minute_time = time.time()  # Update the last ten-minute interval start

def parse_data(port, baudrate, lsl_flag=False, csv_flag=False):   # Main function to process data from the Arduino.
    global total_packet_count, start_time, total_data_received, lsl_outlet, last_ten_minute_time

    csv_writer = None  # CSV writer is initially None
    csv_filename = None

    # Check if LSL stream is enabled
    if lsl_flag:
        lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, 250, 'float32', 'UpsideDownLabs')  # Define LSL stream info
        lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL outlet
        print("LSL stream started")  # Print message indicating LSL stream has started
        time.sleep(0.5)  # Delay to ensure that LSL stream setup is complete
    
    # If CSV logging is requested
    if csv_flag:
        # Generate the filename dynamically based on current date and time
        csv_filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        print(f"CSV recording started. Data will be saved to {csv_filename}")  # Print CSV recording message

    # Open the serial port and CSV file
    with serial.Serial(port, baudrate, timeout=0.1) as ser:  # Open serial port
        csv_file = open(csv_filename, mode='w', newline='') if csv_flag else None  # Open CSV file if specified
        
        if csv_file:
            csv_writer = csv.writer(csv_file)  # Create CSV writer
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])  # Write CSV header

        # Delay to account for initial data and ensure accurate timing
        start_timer()

        try:
            while True:
                read_arduino_data(ser, csv_writer)  # Read and process data from Arduino

                current_time = time.time()  # Get the current time

                # Check if a minute has passed and log minute data
                if current_time - start_time >= 60:
                    total_data_received += log_minute_data()  # Update total data received
                    start_time += 60  # Adjust the start time to handle next interval accurately

                # Check if 10 minutes have passed and log ten-minute data
                if current_time - last_ten_minute_time >= 600:
                    total_data_received += log_minute_data()  # Update total data received
                    log_ten_minute_data()  # Log ten-minute data
                    start_timer()  # Restart timers

        except KeyboardInterrupt:
            if csv_file:
                csv_file.close()  # Close CSV file
                print(f"CSV recording stopped. Data saved to {csv_filename}.")  # Print message indicating CSV recording stopped
            print(f"Exiting. \nTotal missing samples: {missing_samples}")  # Print total missing samples

if __name__ == "__main__":
    # Argument parser for command-line interface
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")
    parser.add_argument('--csv', action='store_true', help="Create and write to a CSV file")
    parser.add_argument('--lsl', action='store_true', help="Start LSL stream")

    args = parser.parse_args()

    # Determine port and start data parsing based on arguments
    if args.lsl:
        if args.port:
            port = args.port  # Use specified port
        else:
            port = auto_detect_arduino(baudrate=args.baudrate)  # Auto-detect Arduino port
        
        if port is None:
            print("Arduino port not specified or detected. Exiting.")  # Print message if no port detected
        else:
            parse_data(port, args.baudrate, lsl_flag=args.lsl, csv_flag=args.csv)  # Start data parsing
    else:
        parser.print_help()  # Print help message if no valid arguments are provided