# Chords - Python

Chords Python script is designed to interface with an Arduino-based bio-potential amplifier, read data from it, optionally log this data to CSV or stream it via the Lab Streaming Layer (LSL), and visualize it through a graphical user interface (GUI) with live plotting.

> [!NOTE]
> Flash Arduino code to your hardware from [Chords Arduino Firmware](https://github.com/upsidedownlabs/Chords-Arduino-Firmware) to use this python tool.

## Features

- **Automatic Arduino Detection:** Automatically detects connected Arduino devices via serial ports.
- **Data Reading:** Read data packets from the Arduino's serial port.
- **CSV Logging:** Optionally logs data to a CSV file.
- **LSL Streaming:** Optionally streams data to an LSL outlet for integration with other software.
- **Verbose Output:** Provides detailed statistics and error reporting, including sampling rate and drift.
- **GUI:** Live plotting of six channels using a PyQt-based GUI.
- **Invert:** Optionally Invert the signal before streaming LSL and logging
- **Timer:** Record data for a set time period in seconds.

## Requirements

-  Python
- `pyserial` library (for serial communication)
- `pylsl` library (for LSL streaming)
- `argparse`, `time`, `csv`, `datetime` (standard libraries)
- `pyqtgraph` library (for GUI)
- `PyQt5` library
- `numpy` library

## Installation

1. Ensure you have latest version of Python installed.
2. Create Virtual Environment
   ```bash
   python -m venv venv    
   ```

   ```bash
   .\venv\Scripts\activate  
   ```
3. Install the required Python libraries:
    ```bash
    pip install -r chords_requirements.txt
    ```

## Usage

To use the script, run it from the command line with various options:
  ```bash
  python chords.py [options]
  ```
### Options

- `-p`, `--port` <port>: Specify the serial port to use (e.g., COM5, /dev/ttyUSB0).
- `-b`, `--baudrate` <baudrate>: Set the baud rate for serial communication. By default the script will first attempt to use 230400, and if that fails, it will automatically fallback to 115200.
- `--csv`: Enable CSV logging. Data will be saved to a timestamped file.
- `--lsl`: Enable LSL streaming. Sends data to an LSL outlet.
- `-v`, `--verbose`: Enable verbose output with detailed statistics and error reporting.
- `-t` : Enable the timer to run program for a set time in seconds.

### Data Logging

- **CSV Output**: The script saves the processed data in a CSV file with a timestamped name.
  - The CSV file contains the following columns:
    - `Counter`: The sample counter from the Arduino.
    - `Channel1` to `Channel6`: The data values from each channel.

- **Log Intervals**: The script logs data counts every second and provides a summary every 10 minutes, including the sampling rate and drift in seconds per hour.

## Applications

### GUI

- `python gui.py`: Enable the real-time data plotting GUI.

### FORCE BALL GAME

- `python game.py`: Enable a GUI to play game using EEG Signal.

### HEART RATE

- `python heartbeat_ecg.py`:Enable a GUI with real-time ECG and heart rate.

### EMG ENVELOPE

- `python emgenvelope.py`: Enable a GUI with real-time EMG & its Envelope.

### EOG

- `python eog.py`: Enable a GUI with real-time EOG that detects the blinks and mark them with red dot.

### EEG

- `python ffteeg.py`: Enable a GUI with real-time EEG data with its FFT.

### Keystroke

- `python keystroke.py`: On running, a pop-up opens for connecting, and on pressing Start, blinks are detected to simulate spacebar key presses.

## Running All Applications Together

To run all applications together:

```bash
python app.py
```

> [!NOTE] 
> Before running, make sure to install all dependencies by running the command:
```bash
pip install -r app_requirements.txt
```

This will launch a Web interface. Use the interface to control the applications:

1. Click the `Start LSL Stream` button to initiate the LSL stream.
2. Then, click on any application button to run the desired module.

### Available Applications
- `ffteeg`: Real-time EEG analysis with FFT and brainwave power calculation.
- `heartbeat_ecg`: Analyze ECG data and extract heartbeat metrics.
- `eog`: Real-time EOG monitoring with blink detection.
- `emgenvelope`: Real-time EMG monitor with filtering and RMS envelope.
- `keystroke`: GUI for EOG-based blink detection triggering a keystroke.
- `game`: Launch an EEG game for 2 players (Tug of War).
- `csv_plotter`: Plot data from a CSV file.
- `gui`: Launch the GUI for real time signal visualization.

## Troubleshooting

- **Arduino Not Detected:** Ensure the Arduino is properly connected and powered. Check the serial port and baud rate settings.
- **CSV File Not Created:** Ensure you have write permissions in the directory where the script is run.
- **LSL Stream Issues:** Verify that the `pylsl` library is installed and configured correctly.

## Contributors

We are thankful to our awesome contributors, the list below is alphabetically sorted.

- [Payal Lakra](https://github.com/payallakra)

The audio file used in `game.py` is sourced from [Pixabay](https://pixabay.com/sound-effects/brass-fanfare-with-timpani-and-windchimes-reverberated-146260/)