import sys
from pylsl import StreamInlet, resolve_stream
import pyqtgraph as pg  # For real-time plotting
from pyqtgraph.Qt import QtWidgets, QtCore  # PyQt components for GUI
import numpy as np

# Initialize global variables
inlet = None
data = None
num_channels = 6  # Default number of channels
curves = []
plots = []

def update_plots():
    global data
    if inlet is not None:
        # Pull multiple samples at once
        samples, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=10)  # Pull up to 10 samples

        # Update data buffer
        for sample in samples:
            data = np.roll(data, -1, axis=1)  # Shift data left
            data[:, -1] = sample[:num_channels]  # Add new channel data to the right end of the array

        # Update the curves with the new data
        for i in range(num_channels):
            curves[i].setData(data[i])

def plot_lsl_data():
    global inlet, num_channels, data
    print("Looking for LSL Stream.")
    streams = resolve_stream('name', 'BioAmpDataStream')  

    if not streams:
        print("No LSL Stream found.")
        return
    
    inlet = StreamInlet(streams[0])

    # Get the number of channels from the stream
    info = inlet.info()
    num_channels = info.channel_count()
    print(f"Detected {num_channels} channels.")
    
    # Initialize data buffer based on the number of channels
    data = np.zeros((num_channels, 2000))  # Buffer to hold the last 2000 samples for each channel

    init_gui()

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
    global plots, curves
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

    QtWidgets.QApplication.processEvents()  # Process any pending events

if __name__ == "__main__":
    plot_lsl_data()
    sys.exit(app.exec_())  # Start the Qt application