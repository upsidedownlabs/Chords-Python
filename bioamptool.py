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


# Import necessary modules
from pylsl import StreamInfo, StreamOutlet  # For LSL (Lab Streaming Layer) to stream data
import argparse  # For command-line argument parsing
import serial  # For serial communication with Arduino
import time  # For time-related functions
import csv  # For handling CSV file operations
from datetime import datetime  # For getting current timestamps
import serial.tools.list_ports  # To list available serial ports
import numpy as np  # For handling numeric arrays
import pyqtgraph as pg  # For real-time plotting
from pyqtgraph.Qt import QtWidgets, QtCore  # PyQt components for GUI
import threading  # For multi-threading

# Initialize global variables for tracking and processing data
total_packet_count = 0  # Total packets received in the last second
cumulative_packet_count = 0  # Total packets received in the last 10 minutes
start_time = None  # Track the start time for packet counting
last_ten_minute_time = None  # Track the last 10-minute interval
previous_sample_number = None  # Store the previous sample number for detecting missing samples
missing_samples = 0  # Count of missing samples due to packet loss
buffer = bytearray()  # Buffer for storing incoming raw data from Arduino
PACKET_LENGTH = 17  # Expected length of each data packet
SYNC_BYTE1 = 0xA5  # First byte of sync marker
SYNC_BYTE2 = 0x5A  # Second byte of sync marker
END_BYTE = 0x01  # End byte marker
lsl_outlet = None  # Placeholder for LSL stream outlet
verbose = False  # Flag for verbose output mode
data = np.zeros((6, 2000))  # 2D array to store data for real-time plotting (6 channels, 2000 data points)
csv_filename = None  # Store CSV filename
samples_per_second = 0  # Number of samples received per second

# Function to automatically detect the Arduino's serial port
def auto_detect_arduino(baudrate, timeout=1):
    ports = serial.tools.list_ports.comports()  # List available serial ports
    for port in ports:  # Iterate through each port
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)  # Try opening the port
            time.sleep(1)  # Wait for the device to initialize
            response = ser.readline().strip()  # Try reading from the port
            if response:  # If response is received, assume it's the Arduino
                ser.close()  # Close the serial connection
                print(f"Arduino detected at {port.device}")  # Notify the user
                return port.device  # Return the port name
            ser.close()  # Close the port if no response
        except (OSError, serial.SerialException):  # Handle exceptions if the port can't be opened
            pass
    print("Arduino not detected")  # Notify if no Arduino is found
    return None  # Return None if not found

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
                counter = packet[3]  # Read the counter byte (for tracking sample order)

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
                for i in range(4, 16, 2):  # Loop through channel data bytes
                    high_byte = packet[i]
                    low_byte = packet[i + 1]
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

# Function to initialize the real-time plotting GUI
def init_gui():
    global plots, curves, app, win, timer, status_bar, samples_label, lsl_label, csv_label

    app = QtWidgets.QApplication([])  # Create the Qt application
    win = QtWidgets.QWidget()  # Create the main window
    layout = QtWidgets.QVBoxLayout()  # Create a vertical layout for the window
    win.setLayout(layout)  # Set the layout to the window
    win.setWindowTitle("Real-Time Arduino Data")  # Set the window title

    pg.setConfigOption('background', 'w')  #background
    pg.setConfigOption('foreground', 'k')  # Set the foreground (axes, text) color to black for contrast

    # Create plots for each channel (6 in total)
    plots = []
    curves = []
    colors = ['#FF3B3B','#00FF66', '#FF1493', '#007BFF', '#FFA500', '#FF00FF', '#FF1493']  # Different colors for each channel
    for i in range(6):
        plot = pg.PlotWidget(title=f"Channel {i + 1}")  # Create a plot widget for each channel
        layout.addWidget(plot)  # Add the plot to the layout
        curve = plot.plot(pen=colors[i])  # Create a curve (line) for plotting data, with a different color
        curve.setDownsampling(auto=True)  # Automatically downsample if needed
        curve.setClipToView(True)  # Clip the data to the view
        plots.append(plot)  # Store the plot
        curves.append(curve)  # Store the curve

    # Create a status bar at the bottom for displaying information
    status_bar = QtWidgets.QHBoxLayout()
    
    # CSV recording status label
    csv_label = QtWidgets.QLabel("CSV Recording: Not started")
    status_bar.addWidget(csv_label)

    # LSL status label
    lsl_label = QtWidgets.QLabel("LSL Status: Not started")
    status_bar.addWidget(lsl_label)

    # Samples per second and missing samples label
    samples_label = QtWidgets.QLabel("Samples per second: 0 (0 missing)")
    status_bar.addWidget(samples_label)

    layout.addLayout(status_bar)  # Add the status bar to the layout

    win.show()  # Show the window

    # Function to update the plots
    def update():
        global data, samples_per_second, missing_samples
        for i in range(6):
            curves[i].setData(data[i])  # Update each curve with new data
        samples_label.setText(f"Samples per second: {samples_per_second} ({missing_samples} missing)")  # Update the samples/missing count

    # Create a timer to update the plots every 20ms
    timer = QtCore.QTimer()
    timer.timeout.connect(update)  # Connect the timer to the update function
    timer.start(20)  # Start the timer with a 20ms interval

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
        expected_sampling_rate = 250  # Expected sampling rate
        drift = ((sampling_rate - expected_sampling_rate) / expected_sampling_rate) * 3600  # Calculate drift
        print(f"Drift: {drift:.2f} seconds/hour")  # Print drift
    cumulative_packet_count = 0  # Reset cumulative packet count
    last_ten_minute_time = time.time()  # Update the last 10-minute interval start time

# Main function to parse command-line arguments and handle data acquisition
def parse_data(port, baudrate, lsl_flag=False, csv_flag=False, gui_flag=False, verbose=False):
    global total_packet_count, cumulative_packet_count, start_time, lsl_outlet, last_ten_minute_time, csv_filename

    csv_writer = None  # Placeholder for CSV writer

    # Start LSL streaming if requested
    if lsl_flag:
        lsl_stream_info = StreamInfo('BioAmpDataStream', 'EXG', 6, 250, 'float32', 'UpsideDownLabs')  # Define LSL stream info
        lsl_outlet = StreamOutlet(lsl_stream_info)  # Create LSL outlet
        print("LSL stream started")  # Notify user
        time.sleep(0.5)  # Wait for the LSL stream to start
    
    # Start CSV logging if requested
    if csv_flag:
        csv_filename = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"  # Create timestamped filename
        print(f"CSV recording started. Data will be saved to {csv_filename}")  # Notify user
    # Initialize GUI if requested
    if gui_flag:
        init_gui()  # Initialize GUI
        if lsl_flag:
            lsl_label.setText("LSL Status: Started")  # Update LSL status in the GUI
        if csv_flag:
            csv_label.setText(f"CSV Recording: {csv_filename}")  # Update CSV status in the GUI

    # Open serial connection
    with serial.Serial(port, baudrate, timeout=0.1) as ser:
        csv_file = open(csv_filename, mode='w', newline='') if csv_flag else None  # Open CSV file if logging is enabled
        if csv_file:
            csv_writer = csv.writer(csv_file)  # Create CSV writer
            csv_writer.writerow(['Counter', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6'])  # Write header

        start_timer()  # Start timers for logging

        try:
            while True:
                read_arduino_data(ser, csv_writer)  # Read and process data from Arduino
                current_time = time.time()  # Get the current time
                elapsed_time = current_time - start_time  # Time elapsed since the last second
                elapsed_since_last_10_minutes = current_time - last_ten_minute_time  # Time elapsed since the last 10-minute interval

                if elapsed_time >= 1:  # Check if one second has passed
                    log_one_second_data(verbose)  # Log data for the last second
                    start_time = current_time  # Reset the start time for the next second
                if elapsed_since_last_10_minutes >= 600:  # Check if 10 minutes have passed
                    log_ten_minute_data(verbose)  # Log data for the last 10 minutes
                if gui_flag:
                    QtWidgets.QApplication.processEvents()  # Process GUI events if GUI is enabled
                
        except KeyboardInterrupt:  # Handle interruption (Ctrl+C)
            if csv_file:
                csv_file.close()  # Close CSV file
                print(f"CSV recording stopped. Data saved to {csv_filename}.")  # Notify user
            print(f"Exiting.\nTotal missing samples: {missing_samples}")  # Print final missing samples count

# Main entry point of the script
def main():
    global verbose
    parser = argparse.ArgumentParser(description="Upside Down Labs - BioAmp Tool")  # Create argument parser
    parser.add_argument('-p', '--port', type=str, help="Specify the COM port")  # Port argument
    parser.add_argument('-b', '--baudrate', type=int, default=57600, help="Set baud rate for the serial communication")  # Baud rate 
    parser.add_argument('--csv', action='store_true', help="Create and write to a CSV file")  # CSV logging flag
    parser.add_argument('--lsl', action='store_true', help="Start LSL stream")  # LSL streaming flag
    parser.add_argument('--gui', action='store_true', help="Start GUI for real-time plotting")  # GUI flag
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output with statistical data")  # Verbose flag

    args = parser.parse_args()  # Parse command-line arguments
    verbose = args.verbose  # Set verbose mode

    # Check if any logging or GUI options are selected, else show help
    if not args.csv and not args.lsl and not args.gui:
        parser.print_help()  # Print help if no options are selected
        return

    port = args.port or auto_detect_arduino(args.baudrate)  # Get the port from arguments or auto-detect
    if port is None:
        print("Arduino port not specified or detected. Exiting.")  # Notify if no port is available
        return

    # Start data acquisition
    parse_data(port, args.baudrate, lsl_flag=args.lsl, csv_flag=args.csv, gui_flag=args.gui, verbose=args.verbose)

# Run the main function if this script is executed
if __name__ == "__main__":
    main()