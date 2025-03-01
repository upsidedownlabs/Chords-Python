import time
import sys
import datetime
import math
import websocket
import socket
from scipy.signal import butter, filtfilt
from pylsl import StreamInfo, StreamOutlet

stream_name = 'ORIC'
data = StreamInfo(stream_name, 'EXG', 3, 250, 'float32', 'uid007')
outlet = StreamOutlet(data)
ws = websocket.WebSocket()
ws.connect("ws://" + socket.gethostbyname("multi-emg.local") + ":81")
print(stream_name, "WebSocket connected!")
sys.stderr.write("ORIC WebSocket connected!\n")

block_size = 13
packet_size = 0 
data_size = 0
sample_size = 0
previousSampleNumber = -1
previousData = []
start_time = time.time()

def calculate_rate(data_size, elapsed_time):
    rate = data_size / elapsed_time
    return rate

while (1):
    data = ws.recv()
    data_size += len(data)

    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= 1.0:
        samples_per_second = calculate_rate(sample_size, elapsed_time)
        refresh_rate = calculate_rate(packet_size, elapsed_time)
        bytes_per_second = calculate_rate(data_size, elapsed_time)
        # Get the current local time
        local_time = datetime.datetime.now()

        hours = local_time.hour
        minutes = local_time.minute
        seconds = local_time.second
        print(f"{math.ceil(refresh_rate)} FPS : {math.ceil(samples_per_second)} SPS : {math.ceil(bytes_per_second)} BPS")
        packet_size = 0
        sample_size = 0
        data_size = 0
        start_time = current_time

    if data and (type(data) is list or type(data) is bytes):
        packet_size += 1
        print("Packet size: ", len(data), "Bytes")
        for blockLocation in range(0, len(data), block_size):
            sample_size += 1
            block = data[blockLocation:blockLocation + block_size]
            sample_number = block[0]
            channel_data = []
            for channel in range(0, 3):
                channel_offset = 1 + (channel * 2)
                sample = int.from_bytes(block[channel_offset:channel_offset + 2], byteorder='big', signed=True)
                channel_data.append(sample)

            if previousSampleNumber == -1:
                previousSampleNumber = sample_number
                previousData = channel_data
            else:
                if sample_number - previousSampleNumber > 1:
                    print("Error: Sample Lost")
                    exit()
                elif sample_number == previousSampleNumber:
                    print("Error: Duplicate sample")
                    exit()
                else:
                    previousSampleNumber = sample_number
                    previousData = channel_data

            print("EEG Data: ", sample_number, channel_data[0], channel_data[1], channel_data[2])
            outlet.push_sample(channel_data)