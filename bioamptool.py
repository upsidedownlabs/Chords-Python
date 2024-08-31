from pylsl import StreamInfo, StreamOutlet
import argparse
import serial
import time
import csv
from datetime import datetime
from collections import deque
import serial.tools.list_ports

# Initialize global variables
total_packet_count = 0
start_time = None
total_data_received = 0
previous_sample_number = None
missing_samples = 0
buffer = bytearray()
PACKET_LENGTH = 17
SYNC_BYTE1 = 0xA5
SYNC_BYTE2 = 0x5A
END_BYTE = 0x01

# LSL Stream Setup
lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, 250, 'float32', 'UpsideDownLabs')
lsl_outlet = StreamOutlet(lsl_stream_info)

def auto_detect_arduino(baudrate, timeout=1):
    """
    Auto-detect Arduino by checking all available serial ports.
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)
            time.sleep(1)
            response = ser.readline().strip()
            if response:
                ser.close()
                print(f"Arduino detected at {port.device}")
                return port.device
            ser.close()
        except (OSError, serial.SerialException):
            pass
    print("Arduino not detected")
    return None

def read_arduino_data(ser, csv_writer):
    """
    Read data from Arduino, process it, and write to CSV and LSL stream.
    """
    global total_packet_count, previous_sample_number, missing_samples, buffer
    raw_data = ser.read(ser.in_waiting or 1)
    buffer.extend(raw_data)

    while len(buffer) >= PACKET_LENGTH:
        sync_index = buffer.find(bytes([SYNC_BYTE1, SYNC_BYTE2]))

        if sync_index == -1:
            buffer.clear()
            continue
        
        if len(buffer) >= sync_index + PACKET_LENGTH:
            packet = buffer[sync_index:sync_index + PACKET_LENGTH]
            if len(packet) == 17 and packet[0] == SYNC_BYTE1 and packet[1] == SYNC_BYTE2 and packet[-1] == END_BYTE:
                counter = packet[3]

                if previous_sample_number is not None and counter != (previous_sample_number + 1) % 256:
                    missing_samples += (counter - previous_sample_number - 1) % 256
                    print(f"Error: Expected counter {previous_sample_number + 1} but received {counter}. Missing samples: {missing_samples}")

                previous_sample_number = counter

                total_packet_count += 1

                channel_data = []
                for i in range(4, 16, 2):
                    high_byte = packet[i]
                    low_byte = packet[i + 1]
                    value = (high_byte << 8) | low_byte
                    channel_data.append(float(value))

                csv_writer.writerow([counter] + channel_data)
                lsl_outlet.push_sample(channel_data)

                del buffer[:sync_index + PACKET_LENGTH]
            else:
                del buffer[:sync_index + 1]

def start_timer():
    """
    Initialize timers for minute and ten-minute intervals and reset packet count.
    """
    global start_time, total_packet_count
    current_time = time.time()
    start_time = current_time
    total_packet_count = 0

def log_minute_data():
    """
    Logs and resets data count per minute.
    """
    global total_packet_count
    count_for_minute = total_packet_count
    print(f"Data count for this minute: {count_for_minute} samples")
    total_packet_count = 0
    return count_for_minute

def log_ten_minute_data():
    """
    Logs data count for every 10 minutes and computes sampling rate and drift.
    """
    global total_data_received, start_time

    print(f"Total data count after 10 minutes: {total_data_received} samples")
    sampling_rate = total_data_received / (10 * 60)
    print(f"Sampling rate: {sampling_rate:.2f} samples/second")

    expected_sampling_rate = 250
    drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600
    print(f"Drift: {drift:.2f} seconds/hour")

    total_data_received = 0
    start_time = time.time()

def parse_data(port, baudrate):
    # Main function to process data from the Arduino.
    global total_packet_count, start_time, total_data_received

    filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        with open(filename, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])

            try:
                time.sleep(2)

                start_timer()

                while True:
                    read_arduino_data(ser, csv_writer)

                    current_time = time.time()

                    if current_time - start_time >= 60:
                        total_data_received += log_minute_data()
                        start_time = current_time

                    if current_time - start_time >= 600:
                        total_data_received += log_minute_data()
                        log_ten_minute_data()
                        start_timer()

            except KeyboardInterrupt:
                print(f"Exiting. \nTotal missing samples: {missing_samples}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")

    args = parser.parse_args()

    if args.port:
        port = args.port
    else:
        port = auto_detect_arduino(baudrate=args.baudrate)

    if port is None:
        print("Arduino port not specified or detected. Exiting.")
    else:
        parse_data(port, args.baudrate)