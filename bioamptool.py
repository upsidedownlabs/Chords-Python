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
from collections import deque
import serial.tools.list_ports

# Initialize global variables
total_packet_count = 0  # Counter for packets received in the current minute
start_time = None  # Timestamp for the start of the current time
total_data_received = 0  # Total number of data packets received in the 10-minute interval
previous_sample_number = None  # Variable to store the last sample number
missing_samples = 0  # Counter for missing samples
buffer = bytearray()
PACKET_LENGTH = 17
SYNC_BYTE1 = 0xA5
SYNC_BYTE2 = 0x5A
END_BYTE = 0x01

# LSL Stream Setup
lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, 250, 'float32', 'UpsideDownLabs')  # Define LSL stream info
lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL outlet for streaming data

def auto_detect_arduino(baudrate, timeout=1):
    """
    Auto-detect Arduino by checking all available serial ports.
    """
    ports = serial.tools.list_ports.comports()  # List all serial ports
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Open serial port
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
    global total_packet_count, previous_sample_number, missing_samples, buffer
    raw_data = ser.read(ser.in_waiting or 1)  # Read 17 bytes from the serial port
    buffer.extend(raw_data)

    # Check for valid data packet structure
    while len(buffer) >= PACKET_LENGTH:
        sync_index = buffer.find(bytes([SYNC_BYTE1, SYNC_BYTE2]))

        if sync_index == -1:
            buffer.clear
            continue
        
        if(len(buffer) >= sync_index + PACKET_LENGTH):
            packet = buffer[sync_index:sync_index+PACKET_LENGTH]
            print(packet)
            if len(packet) == 17 and packet[0] == SYNC_BYTE1 and packet[1] == SYNC_BYTE2 and packet[-1] == END_BYTE:
                counter = packet[3]  # Counter is at index 3

                # Ensure counter number is exactly one more than the previous one
                if previous_sample_number is not None and counter != (previous_sample_number + 1) % 256:
                    missing_samples += (counter - previous_sample_number - 1) % 256
                    print(f"Error: Expected counter {previous_sample_number + 1} but received {counter}. Missing samples: {missing_samples}")
                    exit()
                    
                previous_sample_number = counter  # Update previous sample number to current counter

                total_packet_count += 1  # Increment packet count only after initial samples are ignored

                # Merge high and low bytes to form channel data
                channel_data = []
                for i in range(4, 16, 2):  # Indices for channel data
                    high_byte = packet[i]
                    low_byte = packet[i + 1]
                    value = (high_byte << 8) | low_byte  # Combine high and low bytes to form the 16-bit value
                    channel_data.append(float(value))

                # Write counter and channel data to CSV
                csv_writer.writerow([counter] + channel_data)

                # Push channel data to LSL stream
                lsl_outlet.push_sample(channel_data)

                del buffer[:sync_index + PACKET_LENGTH]
            else:
                del buffer[:sync_index + 1]
                print("Invalid Data Packet")  # Print message if data packet is invalid

def start_timer():
    """
    Initialize timers for minute and ten-minute intervals and reset packet count.
    """
    global start_time, total_packet_count
    current_time = time.time()  # Get current timestamp
    start_time = current_time  # Set start time
    total_packet_count = 0  # Reset packet count

def log_minute_data():
    """
    Logs and resets data count per minute.
    """
    global total_packet_count
    count_for_minute = total_packet_count  # Get the count for the current minute
    print(f"Data count for this minute: {count_for_minute} samples")  # Print count for the current minute
    total_packet_count = 0  # Reset packet count for the next minute
    return count_for_minute  # Return the count for further processing

def log_ten_minute_data():
    """
    Logs data count for every 10 minutes and computes sampling rate and drift.
    """
    global total_data_received, start_time

    # Calculate total data count and sampling rate
    print(f"Total data count after 10 minutes: {total_data_received} samples")  # Print total data count for the last 10 minutes
    sampling_rate = total_data_received / (10 * 60)  # Calculate sampling rate
    print(f"Sampling rate: {sampling_rate:.2f} samples/second")  # Print sampling rate

    # Calculate drift
    expected_sampling_rate = 250  # Expected sampling rate
    drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600  # Calculate drift in seconds/hour
    print(f"Drift: {drift:.2f} seconds/hour")  # Print drift

    # Reset for the next 10-minute interval
    total_data_received = 0  # Reset total data received
    start_time = time.time()  # Update start time for the next 10-minute interval

def parse_data(port, baudrate):
    """
    Main function to process data from the Arduino.
    """
    global total_packet_count, start_time, start_time, total_data_received

    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        with open('packet_data.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])  # Write the CSV header

            try:
                time.sleep(2)  # Allow time for Arduino to initialize

                start_timer()  # Initialize timer

                while True:
                    read_arduino_data(ser, csv_writer)  # Read data from Arduino

                    # if initial_samples_ignored:
                    current_time = time.time()  # Get current timestamp

                    # Handle minute interval
                    if current_time - start_time >= 60:
                        total_data_received += log_minute_data()  # Log minute data and add to total
                        start_time = current_time  # Reset minute timer

                    # Handle 10-minute interval
                    if current_time - start_time >= 600:
                        total_data_received += log_minute_data()  # Log last minute before the 10-minute interval ends
                        log_ten_minute_data()  # Log data for the 10-minute interval
                        start_timer()  # Reset timers to prevent a partial minute log after the 10-minute interval

            except KeyboardInterrupt:
                # Handle keyboard interrupt
                print(f"Exiting. \nTotal missing samples: {missing_samples}")  # Print missing samples and exit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")
    parser.add_argument('-d', '--detect', action='store_true', help="Auto-detect Arduino")  # Argument to auto-detect Arduino
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")  # Argument to specify COM port
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")  # Argument for baud rate

    args = parser.parse_args()  # Parse command-line arguments

    if args.detect:
        port = auto_detect_arduino(baudrate=args.baudrate)  # Auto-detect Arduino if specified
    else:
        port = args.port  # Use specified port

    if port is None:
        print("Arduino port not specified or detected. Exiting.")
    else:
        parse_data(port, args.baudrate)  # Start processing data