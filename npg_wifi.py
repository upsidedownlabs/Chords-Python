# import time
# import sys
# import datetime
# import math
# import websocket
# import socket
# from scipy.signal import butter, filtfilt
# from pylsl import StreamInfo, StreamOutlet


# class NPG_Wifi:
#     def __init__(self, stream_name='NPG', channels=3, sampling_rate=250, block_size=13):
#         self.stream_name = stream_name
#         self.channels = channels
#         self.sampling_rate = sampling_rate
#         self.block_size = block_size

#         self.data_info = StreamInfo(stream_name, 'EXG', channels, sampling_rate, 'float32', 'uid007')
#         self.outlet = StreamOutlet(self.data_info)

#         self.packet_size = 0
#         self.data_size = 0
#         self.sample_size = 0
#         self.previous_sample_number = -1
#         self.previous_data = []
#         self.start_time = time.time()

#         self.ws = None

#     def connect(self):
#         try:
#             host_ip = socket.gethostbyname("multi-emg.local")
#             self.ws = websocket.WebSocket()
#             self.ws.connect(f"ws://{host_ip}:81")
#             print(self.stream_name, "WebSocket connected!")
#             sys.stderr.write(f"{self.stream_name} WebSocket connected!\n")
#         except Exception as e:
#             print(f"[ERROR] Could not connect to WebSocket: {e}")
#             sys.exit(1)

#     def calculate_rate(self, size, elapsed_time):
#         return size / elapsed_time if elapsed_time > 0 else 0

#     def process_data(self):
#         try:
#             while True:
#                 data = self.ws.recv()
#                 self.data_size += len(data)

#                 current_time = time.time()
#                 elapsed_time = current_time - self.start_time

#                 if elapsed_time >= 1.0:
#                     sps = self.calculate_rate(self.sample_size, elapsed_time)
#                     fps = self.calculate_rate(self.packet_size, elapsed_time)
#                     bps = self.calculate_rate(self.data_size, elapsed_time)

#                     # You can log these values if needed
#                     # print(f"{math.ceil(fps)} FPS : {math.ceil(sps)} SPS : {math.ceil(bps)} BPS")

#                     self.packet_size = 0
#                     self.sample_size = 0
#                     self.data_size = 0
#                     self.start_time = current_time

#                 if isinstance(data, (bytes, list)):
#                     self.packet_size += 1
#                     for i in range(0, len(data), self.block_size):
#                         self.sample_size += 1
#                         block = data[i:i + self.block_size]
#                         if len(block) < self.block_size:
#                             continue  # Skip incomplete block

#                         sample_number = block[0]
#                         channel_data = []

#                         for ch in range(self.channels):
#                             offset = 1 + ch * 2
#                             sample = int.from_bytes(block[offset:offset + 2], byteorder='big', signed=True)
#                             channel_data.append(sample)

#                         if self.previous_sample_number == -1:
#                             self.previous_sample_number = sample_number
#                             self.previous_data = channel_data
#                         else:
#                             if sample_number - self.previous_sample_number > 1:
#                                 print("Error: Sample Lost")
#                                 sys.exit(1)
#                             elif sample_number == self.previous_sample_number:
#                                 print("Error: Duplicate Sample")
#                                 sys.exit(1)
#                             else:
#                                 self.previous_sample_number = sample_number
#                                 self.previous_data = channel_data

#                         self.outlet.push_sample(channel_data)

#         except KeyboardInterrupt:
#             print("Interrupted by user.")
#             self.disconnect()
#         except Exception as e:
#             print(f"[ERROR] {e}")
#             self.disconnect()

#     def disconnect(self):
#         if self.ws:
#             try:
#                 self.ws.close()
#                 print("WebSocket connection closed.")
#             except Exception as e:
#                 print(f"[ERROR] Closing WebSocket: {e}")

# if __name__ == "__main__":
#     client = NPG_Wifi()
#     client.connect()
#     client.process_data()



import time
import sys
import datetime
import math
import websocket
import socket
from scipy.signal import butter, filtfilt

class NPG_Wifi:
    def __init__(self, stream_name='NPG', channels=3, sampling_rate=250, block_size=13):
        self.stream_name = stream_name
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.block_size = block_size

        self.packet_size = 0
        self.data_size = 0
        self.sample_size = 0
        self.previous_sample_number = -1
        self.previous_data = []
        self.start_time = time.time()

        self.ws = None

    def connect(self):
        try:
            host_ip = socket.gethostbyname("multi-emg.local")
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{host_ip}:81")
            print(self.stream_name, "WebSocket connected!")
            sys.stderr.write(f"{self.stream_name} WebSocket connected!\n")
        except Exception as e:
            print(f"[ERROR] Could not connect to WebSocket: {e}")
            sys.exit(1)

    def calculate_rate(self, size, elapsed_time):
        return size / elapsed_time if elapsed_time > 0 else 0

    def process_data(self):
        try:
            while True:
                data = self.ws.recv()
                self.data_size += len(data)

                current_time = time.time()
                elapsed_time = current_time - self.start_time

                if elapsed_time >= 1.0:
                    sps = self.calculate_rate(self.sample_size, elapsed_time)
                    fps = self.calculate_rate(self.packet_size, elapsed_time)
                    bps = self.calculate_rate(self.data_size, elapsed_time)

                    self.packet_size = 0
                    self.sample_size = 0
                    self.data_size = 0
                    self.start_time = current_time

                if isinstance(data, (bytes, list)):
                    self.packet_size += 1
                    for i in range(0, len(data), self.block_size):
                        self.sample_size += 1
                        block = data[i:i + self.block_size]
                        if len(block) < self.block_size:
                            continue

                        sample_number = block[0]
                        channel_data = []

                        for ch in range(self.channels):
                            offset = 1 + ch * 2
                            sample = int.from_bytes(block[offset:offset + 2], byteorder='big', signed=True)
                            channel_data.append(sample)

                        if self.previous_sample_number == -1:
                            self.previous_sample_number = sample_number
                            self.previous_data = channel_data
                        else:
                            if sample_number - self.previous_sample_number > 1:
                                print("Error: Sample Lost")
                                sys.exit(1)
                            elif sample_number == self.previous_sample_number:
                                print("Error: Duplicate Sample")
                                sys.exit(1)
                            else:
                                self.previous_sample_number = sample_number
                                self.previous_data = channel_data

        except KeyboardInterrupt:
            print("Interrupted by user.")
            self.disconnect()
        except Exception as e:
            print(f"[ERROR] {e}")
            self.disconnect()

    def disconnect(self):
        if self.ws:
            try:
                self.ws.close()
                print("WebSocket connection closed.")
            except Exception as e:
                print(f"[ERROR] Closing WebSocket: {e}")

if __name__ == "__main__":
    client = NPG_Wifi()
    client.connect()
    client.process_data()