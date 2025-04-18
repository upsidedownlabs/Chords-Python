import sys
from pylsl import StreamInlet, resolve_streams, resolve_byprop
import pyqtgraph as pg  # For real-time plotting
from pyqtgraph.Qt import QtWidgets, QtCore  # PyQt components for GUI
import numpy as np
import time

# Initialize global variables
inlet = None
data = None
num_channels = 6  # Default number of channels
curves = []
plots = []
last_data_time = None
stream_active = True

def update_plots():
    global data, last_data_time, stream_active
    if inlet is None or not stream_active:
        return
    
    # Pull multiple samples at once
    samples, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=10)  # Pull up to 10 samples
    
    if samples:
        last_data_time = time.time()
        # Update data buffer
        for sample in samples:
            data = np.roll(data, -1, axis=1)  # Shift data left
            data[:, -1] = sample[:num_channels]  # Add new channel data to the right end of the array

        # Update the curves with the new data
        for i in range(num_channels):
            curves[i].setData(data[i])
    else:
        # Check if data not received for more than 2 seconds
        if last_data_time and (time.time() - last_data_time) > 2:
            stream_active = False
            lsl_label.setText("LSL Status: Stream disconnected")
            QtWidgets.QApplication.processEvents()
            timer.stop()
            win.close()

def plot_lsl_data():
    global inlet, num_channels, data, last_data_time, stream_active

    print("Searching for available LSL streams...")
    streams = resolve_streams()                         # Discover available LSL streams
    available_streams = [s.name() for s in streams]     # Get list of stream names

    if not available_streams:
        print("No LSL streams found!")
        return None

    for stream_name in available_streams:
        print(f"Trying to connect to {stream_name}...")
        resolved_streams = resolve_byprop('name', stream_name, timeout=2)

        if resolved_streams:
            print(f"Successfully connected to {stream_name}!")
            inlet = StreamInlet(resolved_streams[0])           # Create an inlet to receive data from the stream
            last_data_time = time.time()  # Initialize last data time
            stream_active = True  # Set stream active flag
            break
        else:
            print(f"Failed to connect to {stream_name}.")

    if inlet is None:
        print("Could not connect to any stream.")
        return None

    info = inlet.info()
    num_channels = info.channel_count()
    print(f"Detected {num_channels} channels.")
    
    # Initialize data buffer based on the number of channels
    data = np.zeros((num_channels, 2000))  # Buffer to hold the last 2000 samples for each channel

    return init_gui()

def init_gui():
    global plots, curves, app, win, timer, status_bar, lsl_label

    app = QtWidgets.QApplication(sys.argv)  # Create the Qt application
    win = QtWidgets.QWidget()  # Create the main window
    layout = QtWidgets.QVBoxLayout()  # Create a vertical layout for the window
    win.setLayout(layout)  # Set the layout to the window
    win.setWindowTitle("Real-Time Arduino Data")  # Set the window title

    pg.setConfigOption('background', 'w')  # Background color
    pg.setConfigOption('foreground', 'k')  # Foreground color

    # Create plots for each channel based on num_channels
    plots = []
    curves = []
    colors = ['#D10054', '#007A8C', '#0A6847', '#674188', '#E65C19', '#2E073F' ]  # Different colors for each channel
    for i in range(num_channels):
        plot = pg.PlotWidget(title=f"Channel {i + 1}")  # Create a plot widget for each channel
        layout.addWidget(plot)  # Add the plot to the layout
        color = colors[i % len(colors)]  # Cycle colors if fewer colors than channels
        curve = plot.plot(pen=color)  # Create a curve (line) for plotting data
        curve.setDownsampling(auto=True)  # Automatically downsample if needed
        curve.setClipToView(True)  # Clip the data to the view
        plots.append(plot)  # Store the plot
        curves.append(curve)  # Store the curve

    # Create a status bar at the bottom for displaying information
    status_bar = QtWidgets.QHBoxLayout()

    # LSL status label
    lsl_label = QtWidgets.QLabel(f"LSL Status: Connected ({num_channels} channels detected)")
    status_bar.addWidget(lsl_label)

    layout.addLayout(status_bar)  # Add the status bar to the layout

    win.show()  # Show the window

    # Create a timer to update the plots every 1ms
    timer = QtCore.QTimer()
    timer.timeout.connect(update_plots)  # Connect the update function to the timer
    timer.start(10)  # Start the timer with a 10ms interval

    return app

if __name__ == "__main__":
    plot_lsl_data()
    if inlet:
        sys.exit(app.exec_())  # Start the Qt application only if a stream was connected