import asyncio
from bleak import BleakScanner, BleakClient
import time
from pylsl import StreamInfo, StreamOutlet
import sys
import argparse

# BLE parameters (must match your firmware)
DEVICE_NAME_PREFIX = "NPG"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
DATA_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
CONTROL_CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"

# Packet parameters for batched samples:
SINGLE_SAMPLE_LEN = 7              # Each sample is 7 bytes
BLOCK_COUNT = 10                   # Batch size: 10 samples per notification
NEW_PACKET_LEN = SINGLE_SAMPLE_LEN * BLOCK_COUNT  # Total packet length (70 bytes)

# Global variables
prev_unrolled_counter = None
samples_received = 0
start_time = None
total_missing_samples = 0
outlet = None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="Scan for devices and print them")
    parser.add_argument("--connect", type=str, help="Connect to a specific device address")
    return parser.parse_args()

async def scan_devices():
    print("Scanning for BLE devices...", file=sys.stderr)
    devices = await BleakScanner.discover()
    filtered = [d for d in devices if d.name and d.name.startswith(DEVICE_NAME_PREFIX)]
    
    if not filtered:
        print("No devices found.", file=sys.stderr)
        return
    
    # Print devices in format that Flask can parse
    for dev in filtered:
        print(f"DEVICE:{dev.name}|{dev.address}")

def process_sample(sample_data: bytearray):
    global prev_unrolled_counter, samples_received, start_time, total_missing_samples, outlet
    
    if len(sample_data) != SINGLE_SAMPLE_LEN:
        print("Unexpected sample length:", len(sample_data))
        return
        
    sample_counter = sample_data[0]
    # Unroll the counter:
    if prev_unrolled_counter is None:
        prev_unrolled_counter = sample_counter
    else:
        last = prev_unrolled_counter % 256
        if sample_counter < last:
            current_unrolled = prev_unrolled_counter - last + sample_counter + 256
        else:
            current_unrolled = prev_unrolled_counter - last + sample_counter
        
        if current_unrolled != prev_unrolled_counter + 1:
            missing = current_unrolled - (prev_unrolled_counter + 1)
            print(f"Missing {missing} sample(s): expected {prev_unrolled_counter + 1}, got {current_unrolled}")
            total_missing_samples += missing
        
        prev_unrolled_counter = current_unrolled

    # Set start_time when first sample is received
    if start_time is None:
        start_time = time.time()
    
    # Process channels
    channels = [
        int.from_bytes(sample_data[1:3]),  # Channel 0
        int.from_bytes(sample_data[3:5]),  # Channel 1
        int.from_bytes(sample_data[5:7])]
    
    # Push to LSL
    if outlet:
        outlet.push_sample(channels)
    
    samples_received += 1
    
    # Periodic status print
    if samples_received % 100 == 0:
        elapsed = time.time() - start_time
        print(f"Sample {prev_unrolled_counter} at {elapsed:.2f}s - Channels: {channels} - Missing: {total_missing_samples}")

def notification_handler(sender, data: bytearray):
    try:
        if len(data) == NEW_PACKET_LEN:
            # Process batched samples
            for i in range(0, NEW_PACKET_LEN, SINGLE_SAMPLE_LEN):
                process_sample(data[i:i+SINGLE_SAMPLE_LEN])
        elif len(data) == SINGLE_SAMPLE_LEN:
            # Process single sample
            process_sample(data)
        else:
            print(f"Unexpected packet length: {len(data)} bytes")
    except Exception as e:
        print(f"Error processing data: {e}")

async def connect_to_device(device_address):
    global outlet
    
    print(f"Attempting to connect to {device_address}...", file=sys.stderr)
    
    # Set up LSL stream (500Hz sampling rate)
    info = StreamInfo("NPG", "EXG", 3, 500, "int16", "npg1234")
    outlet = StreamOutlet(info)
    
    client = None
    try:
        client = BleakClient(device_address)
        await client.connect()
        
        if not client.is_connected:
            print("Failed to connect", file=sys.stderr)
            return False
        
        print(f"Connected to {device_address}")
        
        # Send start command
        await client.write_gatt_char(CONTROL_CHAR_UUID, b"START", response=True)
        print("Sent START command")
        
        # Subscribe to notifications
        await client.start_notify(DATA_CHAR_UUID, notification_handler)
        print("Subscribed to data notifications")
        
        # Keep connection alive
        while client.is_connected:
            await asyncio.sleep(1)
            
        return True
        
    except Exception as e:
        print(f"Connection error: {str(e)}", file=sys.stderr)
        return False
    finally:
        if client and client.is_connected:
            await client.disconnect()

if __name__ == "__main__":
    args = parse_args()
    
    if args.scan:
        asyncio.run(scan_devices())
    elif args.connect:
        asyncio.run(connect_to_device(args.connect))
    else:
        print("Please specify --scan or --connect", file=sys.stderr)
        sys.exit(1)