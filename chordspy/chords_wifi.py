import time
import sys
import websocket
import socket
from scipy.signal import butter, filtfilt

class Chords_WIFI:
    def __init__(self, stream_name='NPG', channels=3, sampling_rate=500, block_size=13, timeout_sec=1):
        self.stream_name = stream_name
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.block_size = block_size
        self.timeout_sec = timeout_sec  # Timeout for no data received

        self.packet_size = 0
        self.data_size = 0
        self.sample_size = 0
        self.previous_sample_number = -1
        self.previous_data = []
        self.start_time = time.time()
        self.last_data_time = time.time()  # Track last received data
        self.cleanup_done = False
        self.ws = None

    def connect(self):
        try:
            host_ip = socket.gethostbyname("multi-emg.local")
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{host_ip}:81")
            sys.stderr.write(f"{self.stream_name} WebSocket connected!\n")
        except Exception as e:
            print(f"[ERROR] Could not connect to WebSocket: {e}")
            self.cleanup()
            sys.exit(1)

    def calculate_rate(self, size, elapsed_time):
        return size / elapsed_time if elapsed_time > 0 else 0

    def process_data(self):
        try:
            while True:
                try:
                    data = self.ws.recv()
                    self.last_data_time = time.time()  # Update when data is received
                except (websocket.WebSocketConnectionClosedException, ConnectionResetError) as e:
                    print(f"\nConnection closed: {str(e)}")
                    self.cleanup()
                    return
                except Exception as e:
                    print(f"\n[ERROR] Connection error: {e}")
                    self.cleanup()
                    return

                # Check for timeout (device stopped sending data)
                if time.time() - self.last_data_time > self.timeout_sec:
                    print("\nDevice stopped sending data")
                    self.cleanup()
                    return

                # Process your data here
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
                                print("\nError: Sample Lost")
                                self.cleanup()
                                sys.exit(1)
                            elif sample_number == self.previous_sample_number:
                                print("\nError: Duplicate Sample")
                                self.cleanup()
                                sys.exit(1)
                            else:
                                self.previous_sample_number = sample_number
                                self.previous_data = channel_data

        except KeyboardInterrupt:
            print("\nInterrupted by user")
            self.cleanup()
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.cleanup()

    def cleanup(self):
        if not self.cleanup_done:
            try:
                if hasattr(self, 'ws') and self.ws:
                    self.ws.close()
            except Exception as e:
                pass
            
            print("Cleanup Completed")
            self.cleanup_done = True

    def __del__(self):
        self.cleanup()

if __name__ == "__main__":
    client = None
    try:
        client = Chords_WIFI()
        client.connect()
        client.process_data()
    except Exception as e:
        if client:
            client.cleanup()
        sys.exit(1)