# BioAmp-Tool-Python

A python tool to record data from BioAmp hardware.This project is designed to read data from an Arduino via a serial connection, process the data, and stream it using the Lab Streaming Layer (LSL) protocol. It also logs the processed data to a CSV file for further analysis.

## Features

- Auto-detects connected Arduino devices.
- Reads and processes data packets from Arduino.
- Streams data via LSL for real-time analysis.
- Logs data to a CSV file, including counters and channel data.
- Calculates and logs sampling rate and drift.
- Handles missing samples and prints relevant errors.

## Requirements

- Python 3.7 or higher
- [pySerial](https://pypi.org/project/pyserial/)
- [pylsl](https://pypi.org/project/pylsl/)
- An Arduino device capable of sending serial data packets

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/upsidedownlabs/BioAmp-Tool-Python.git
    ```

2. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Connect your Arduino** to your computer via USB.

2. **Run the script** with the desired options:
    ```bash
    python bioamptool.py --detect
    ```

3. **View the output** on your console, which will include minute-by-minute data counts, 10-minute summaries, sampling rate , any detected errors or drift.

## Command-line Options

- `-d, --detect`: Auto-detect the Arduino COM port.
- `-p, --port`: Specify the COM port (e.g., `COM3` on Windows or `/dev/ttyUSB0` on Linux).
- `-b, --baudrate`: Set the baud rate for serial communication (default is `57600`).

Example:
```bash
python bioamptool.py --detect
```

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

Use an LSL viewer (e.g., BrainVision Recorder) to visualize the streamed data in real-time.

## Troubleshooting

- **Arduino Not Detected**: Ensure your Arduino is properly connected and recognized by your system. Use the `--detect` option to automatically find the Arduino port.
- **Invalid Data Packets**: If you see messages about invalid data packets, check the data format and synchronization bytes being sent from the Arduino.
- **Zero LSL Stream Utilization**: If the LSL stream shows 0% utilization, verify the stream is properly set up and data is being pushed to the outlet.

## Contributors

We are thankful to our awesome contributors, the list below is alphabetically sorted.

- [Payal Lakra](https://github.com/payallakra)

