# Chords - Python

Chords Python script is designed to interface with an Arduino-based bioamplifier, read data from it, optionally log this data to CSV or stream it via the Lab Streaming Layer (LSL), and visualize it through a graphical user interface (GUI) with live plotting.

> [!NOTE]
> Flash Arduino code to your hardware from [Chords Arduino Firmware](https://github.com/upsidedownlabs/Chords-Arduino-Firmware) to use this python tool.

## Features

- **Automatic Arduino Detection:** Automatically detects connected Arduino devices via serial ports.
- **Data Reading:** Read  ModularEEG P2 format data packets from the Arduino's serial port.
- **CSV Logging:** Optionally logs data to a CSV file.
- **LSL Streaming:** Optionally streams data to an LSL outlet for integration with other software.
- **Verbose Output:** Provides detailed statistics and error reporting, including sampling rate and drift.
- **GUI:** Live plotting of six channels using a PyQt-based GUI.
- **Timer:** Record data for a set time period in seconds.

## Requirements

-  Python 3.x
- `pyserial` library (for serial communication)
- `pylsl` library (for LSL streaming)
- `argparse`, `time`, `csv`, `datetime` (standard libraries)
- `pyqtgraph` library (for GUI)
- `PyQt5` library
- `numpy` library

## Installation

1. Ensure you have Python 3.x installed.
2. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use the script, run it from the command line with various options:

First Create Virtual Environment

  ```bash
   python -m venv venv      #Create Virtual Environment
   .\venv\Scripts\activate  #to activate environment 
  ```
Then,

  ```bash
  python chords.py [options]
  ```

### Options

- `-p`, `--port` <port>: Specify the serial port to use (e.g., COM5, /dev/ttyUSB0).
- `-b`, `--baudrate` <baudrate>: Set the baud rate for serial communication (default is 230400).
- `--csv`: Enable CSV logging. Data will be saved to a timestamped file.
- `--lsl`: Enable LSL streaming. Sends data to an LSL outlet.
- `-v`, `--verbose`: Enable verbose output with detailed statistics and error reporting.
- `-t` : Enable the timer to run program for a set time in seconds.

## Applications

### GUI

- `python gui.py`: Enable the real-time data plotting GUI.

### FORCE BALL GAME

- `python game.py`: Enable a GUI to play game using EEG Signal.

## Script Functions

 `auto_detect_arduino(baudrate, timeout=1)`

Detects an Arduino connected via serial port. Returns the port name if detected.

`read_arduino_data(ser, csv_writer=None)`

Reads and processes data from the Arduino. Writes data to CSV and/or LSL stream if enabled.

 `start_timer()`

Initializes timers for 1-second and 10-minute intervals.

 `log_one_second_data(verbose=False)`

Logs and resets data for the 1-second interval.

 `log_ten_minute_data(verbose=False)`

Logs data and statistics for the 10-minute interval.

 `parse_data(port, baudrate, lsl_flag=False, csv_flag=False, gui_flag=False, verbose=False)`

Parses data from Arduino and manages logging, streaming, and GUI updates.

 `init_gui()`

Initializes and displays the GUI with six real-time plots, one for each bio-signal channel.

`cleanup()`

Handles all the cleanup tasks.

 `main()`

Handles command-line argument parsing and initiates data processing.

## Data Logging

- **CSV Output**: The script saves the processed data in a CSV file with a timestamped name.
  - The CSV file contains the following columns:
    - `Counter`: The sample counter from the Arduino.
    - `Channel1` to `Channel6`: The data values from each channel.

- **Log Intervals**: The script logs data counts every second and provides a summary every 10 minutes, including the sampling rate and drift in seconds per hour.

## LSL Streaming

- **Stream Name**: `BioAmpDataStream`
- **Stream Type**: `EXG`
- **Channel Count**: `6`
- **Sampling Rate**: `UNO-R3 : 250 Hz` , `UNO-R4 : 500 Hz`
- **Data Format**: `float32`

If GUI is not enabled, you can use an LSL viewer (e.g., BrainVision LSL Viewer) to visualize the streamed data in real-time.

## Troubleshooting

- **Arduino Not Detected:** Ensure the Arduino is properly connected and powered. Check the serial port and baud rate settings.
- **CSV File Not Created:** Ensure you have write permissions in the directory where the script is run.
- **LSL Stream Issues:** Verify that the `pylsl` library is installed and configured correctly.

## Contributors

We are thankful to our awesome contributors, the list below is alphabetically sorted.

- [Payal Lakra](https://github.com/payallakra)

The audio file used in `game.py` is sourced from [Pixabay](https://pixabay.com/sound-effects/brass-fanfare-with-timpani-and-windchimes-reverberated-146260/)