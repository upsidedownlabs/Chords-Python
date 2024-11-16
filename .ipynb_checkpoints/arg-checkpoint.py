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

# Timer and Data Count Initialization
last_10_sec_time = None  # Last time at which the 10-second count was logged
data_count_10_sec = 0  # Count of data points in the last 10 seconds

def auto_detect_arduino(baudrate, timeout=1):
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

def read_arduino_data(ser, csv_writer=None):
    global total_packet_count, previous_sample_number, missing_samples, buffer, data_count_10_sec
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
                data_count_10_sec += 1  # Increment 10-second data count

                channel_data = []
                for i in range(4, 16, 2):
                    high_byte = packet[i]
                    low_byte = packet[i + 1]
                    value = (high_byte << 8) | low_byte
                    channel_data.append(float(value))

                if csv_writer:
                    csv_writer.writerow([counter] + channel_data)
                if lsl_outlet:
                    lsl_outlet.push_sample(channel_data)

                del buffer[:sync_index + PACKET_LENGTH]
            else:
                del buffer[:sync_index + 1]

def start_timer():
    global start_time, last_ten_minute_time, last_10_sec_time, data_count_10_sec
    time.sleep(0.5)  # Ensure LSL stream setup is complete
    current_time = time.time()
    start_time = current_time
    last_ten_minute_time = current_time
    last_10_sec_time = current_time - (current_time % 10)  # Align to the nearest 10-second mark
    data_count_10_sec = 0  # Initialize count for 10-second interval

def log_10_sec_data():
    global last_10_sec_time, data_count_10_sec
    current_time = time.time()
    if current_time - last_10_sec_time >= 10:
        print(f"Verbose: Data count in the last 10 seconds: {data_count_10_sec}")
        last_10_sec_time = current_time - (current_time % 10)  # Align to the nearest 10-second mark
        data_count_10_sec = 0  # Reset count for the new 10-second interval

def log_minute_data():
    global total_packet_count
    count_for_minute = total_packet_count
    print(f"Data count for this minute: {count_for_minute} samples")
    total_packet_count = 0
    return count_for_minute

def log_ten_minute_data():
    global total_data_received, last_ten_minute_time
    print(f"Total data count after 10 minutes: {total_data_received} samples")
    sampling_rate = total_data_received / (10 * 60)
    print(f"Sampling rate: {sampling_rate:.2f} samples/second")
    expected_sampling_rate = 250
    drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600
    print(f"Drift: {drift:.2f} seconds/hour")
    total_data_received = 0
    last_ten_minute_time = time.time()

def parse_data(port, baudrate, lsl_flag=False, csv_flag=False, verbose_flag=False):
    global total_packet_count, start_time, total_data_received, lsl_outlet, last_ten_minute_time

    csv_writer = None
    csv_filename = None

    if lsl_flag:
        lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, 250, 'float32', 'UpsideDownLabs')
        lsl_outlet = StreamOutlet(lsl_stream_info)
        print("LSL stream started")
        time.sleep(0.5)  # Delay to ensure LSL stream setup is complete
    
    if csv_flag:
        csv_filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        print(f"CSV recording started. Data will be saved to {csv_filename}")

    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        csv_file = open(csv_filename, mode='w', newline='') if csv_flag else None
        
        if csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])

        start_timer()

        try:
            while True:
                read_arduino_data(ser, csv_writer)
                current_time = time.time()

                if verbose_flag:
                    log_10_sec_data()  # Check and log data count every 10 seconds

                if current_time - start_time >= 60:
                    total_data_received += log_minute_data()
                    start_time += 60

                if current_time - last_ten_minute_time >= 600:
                    total_data_received += log_minute_data()
                    log_ten_minute_data()
                    start_timer()

        except KeyboardInterrupt:
            if csv_file:
                csv_file.close()
                print(f"CSV recording stopped. Data saved to {csv_filename}.")
            print(f"Exiting. \nTotal missing samples: {missing_samples}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")
    parser.add_argument('--csv', action='store_true', help="Create and write to a CSV file")
    parser.add_argument('--lsl', action='store_true', help="Start LSL stream")
    parser.add_argument('--verbose', '-v', action='store_true', help="Print data count every 10 seconds")

    args = parser.parse_args()

    if args.lsl:
        if args.port:
            port = args.port
        else:
            port = auto_detect_arduino(baudrate=args.baudrate)
        
        if port is None:
            print("Arduino port not specified or detected. Exiting.")
        else:
            parse_data(port, args.baudrate, lsl_flag=args.lsl, csv_flag=args.csv, verbose_flag=args.verbose)
    else:
        parser.print_help()