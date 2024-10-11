import sys
from pylsl import StreamInlet, resolve_stream
import pyqtgraph as pg  # For real-time plotting
from pyqtgraph.Qt import QtWidgets, QtCore  # PyQt components for GUI
import numpy as np

# Initialize global variables
inlet = None
data = np.zeros((6, 2000))  # Buffer to hold the last 2000 samples for each channel

def update_plots():
    global data
    if inlet is not None:
        # Pull multiple samples at once
        samples, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=10)  # Pull up to 10 samples

        # Update data buffer
        for sample in samples:
            data = np.roll(data, -1, axis=1)  # Shift data left
            data[:, -1] = sample  # Add new channel data to the right end of the array

        # Update the curves with the new data
        for i in range(6):
            curves[i].setData(data[i])

def plot_lsl_data():
    global inlet
    print("Looking for LSL Stream.")
    streams = resolve_stream('name', 'BioAmpDataStream')  

    if not streams:
        print("No LSL Stream found.")
        return
    
    inlet = StreamInlet(streams[0])
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

    # Create plots for each channel (6 in total)
    global plots, curves
    plots = []
    curves = []
    colors = ['#FF3B3B', '#00FF66', '#FF1493', '#007BFF', '#FFA500', '#FF00FF']  # Different colors for each channel
    for i in range(6):
        plot = pg.PlotWidget(title=f"Channel {i + 1}")  # Create a plot widget for each channel
        layout.addWidget(plot)  # Add the plot to the layout
        curve = plot.plot(pen=colors[i])  # Create a curve (line) for plotting data
        curve.setDownsampling(auto=True)  # Automatically downsample if needed
        curve.setClipToView(True)  # Clip the data to the view
        plots.append(plot)  # Store the plot
        curves.append(curve)  # Store the curve

    # Create a status bar at the bottom for displaying information
    status_bar = QtWidgets.QHBoxLayout()

    # LSL status label
    lsl_label = QtWidgets.QLabel("LSL Status: Connected")
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