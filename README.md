## BioAmp-Tool-Python

The BioAmp Tool is a Python script designed to interface with an Arduino-based bioamplifier, read data from it, and optionally log this data to CSV or stream it via the Lab Streaming Layer (LSL).

## Features

- **Automatic Arduino Detection:** Automatically detects connected Arduino devices via serial ports.
- **Data Reading:** Reads ModularEEG P2 format data packets from the Arduino's serial port.
- **CSV Logging:** Optionally logs data to a CSV file.
- **LSL Streaming:** Optionally streams data to an LSL outlet for integration with other software.
- **Verbose Output:** Provides detailed statistics and error reporting.

## Requirements

- Python 3.x
- `pyserial` library (for serial communication)
- `pylsl` library (for LSL streaming)
- `argparse`, `time`, `csv`, `datetime` (standard libraries)

## Installation

1. Ensure you have Python 3.x installed.
2. Install the required Python libraries:
   ```bash
   pip install pyserial pylsl
   ```

## Usage

To use the script, you can run it from the command line with various options:

```bash
python bioamp_tool.py [options]
```

### Options

- `-p`, `--port` <port>: Specify the serial port to use (e.g., COM5, /dev/ttyUSB0).
- `-b`, `--baudrate` <baudrate>: Set the baud rate for serial communication (default is 57600).
- `--csv`: Enable CSV logging. Data will be saved to a file with a timestamped name.
- `--lsl`: Enable LSL streaming. Sends data to an LSL outlet.
- `-v`, `--verbose`: Enable verbose output with detailed statistics and error reporting.


## Script Functions

- `auto_detect_arduino(baudrate, timeout=1)`

Detects an Arduino connected via serial port. Returns the port name if detected.

- `read_arduino_data(ser, csv_writer=None)`

Reads and processes data from the Arduino. Writes data to CSV and/or LSL stream if enabled.

- `start_timer()`

Initializes timers for 10-second and 10-minute intervals.

- `log_ten_second_data(verbose=False)`

Logs and resets data for the 10-second interval.

- `log_ten_minute_data(verbose=False)`

Logs data and statistics for the 10-minute interval.

- `parse_data(port, baudrate, lsl_flag=False, csv_flag=False, verbose=False)`

Parses data from Arduino and manages logging and streaming.

- `main()`

Handles command-line argument parsing and initiates data processing.

## Data Logging

- **CSV Output**: The script saves the processed data in a CSV file named `packet_data.csv`.
  - The CSV contains the following columns:
    - `Counter`: The sample counter from the Arduino.
    - `Channel1` to `Channel6`: The data values from each channel.

- **Log Intervals**: The script logs data counts every minute and provides a summary every 10 minutes, including the sampling rate and drift in seconds per hour.

## LSL Streaming

- **Stream Name**: `BioAmpDataStream`
- **Stream Type**: `EXG`
- **Channel Count**: `6`
- **Sampling Rate**: `250 Hz`
- **Data Format**: `float32`

Use an LSL viewer (e.g., BrainVision LSL Viewer) to visualize the streamed data in real-time.

## Troubleshooting

- **Arduino Not Detected:** Ensure the Arduino is properly connected and powered. Check the serial port and baud rate settings.
- **CSV File Not Created:** Ensure you have write permissions in the directory where the script is run.
- **LSL Stream Issues:** Verify that the `pylsl` library is installed and configured correctly.

## Contributors

We are thankful to our awesome contributors, the list below is alphabetically sorted.

- [Payal Lakra](https://github.com/payallakra)
 
