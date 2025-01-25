import pygame
import pylsl
import numpy as np
import time
from pylsl import StreamInlet, resolve_stream
from scipy.signal import iirnotch, butter, lfilter
import math

pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Beetle Game')

# Beetle properties
beetle_x, beetle_y = 380, 530
focus_speed_upward = 8     # Speed when moving upward
focus_speed_downward = 4   # Speed when moving downward
focus_timeout = 2          # Time in seconds to stabilize focus
focus_threshold = 5        # Threshold for beta power

# LSL stream setup
streams = resolve_stream('name', 'BioAmpDataStream')
if not streams:
    print("No LSL stream found!")
    pygame.quit()
    exit()

inlet = StreamInlet(streams[0])
print("LSL Stream Started")
sampling_rate = int(inlet.info().nominal_srate())
print(f"Sampling rate: {sampling_rate} Hz")

b_notch, a_notch = iirnotch(50.0 / (500 / 2), 30.0)
b_band, a_band = butter(4, [0.5/ (sampling_rate / 2), 48.0 / (sampling_rate / 2)], btype='band')

# Buffer for EEG data and Focus tracking variables
buffer = []
buffer_size = 500
focus_timer = 0
last_focus_time = time.time()
last_time = time.time()

# Load the beetle image
beetle_image = pygame.image.load('beetle.jpg')
beetle_image = pygame.transform.scale(beetle_image, (80, 80))

# Function to apply filters
def apply_filters(eeg_point):
    filtered = lfilter(b_notch, a_notch, [eeg_point])
    filtered_point = lfilter(b_band, a_band, filtered)
    return filtered_point[0]

def calculate_focus_level(eeg_data, sampling_rate=500):
    window = np.hanning(len(eeg_data))  # Apply a Hanning window
    eeg_data_windowed = eeg_data * window
    fft_data = np.abs(np.fft.fft(eeg_data_windowed))[:len(eeg_data_windowed) // 2]
    fft_data /= len(eeg_data_windowed)
    freqs = np.fft.fftfreq(len(eeg_data_windowed), d=1 / sampling_rate)[:len(eeg_data_windowed) // 2]
    
    # Compute power in different bands
    delta_power = math.sqrt(np.sum((fft_data[(freqs >= 0.5) & (freqs <= 4)]) ** 2))
    theta_power = math.sqrt(np.sum((fft_data[(freqs >= 4) & (freqs <= 8)]) ** 2))
    alpha_power = math.sqrt(np.sum((fft_data[(freqs >= 8) & (freqs <= 13)]) ** 2))
    beta_power = math.sqrt(np.sum((fft_data[(freqs >= 13) & (freqs <= 30)]) ** 2))
    gamma_power = math.sqrt(np.sum((fft_data[(freqs >= 30) & (freqs <= 45)]) ** 2))
    
    power = (beta_power + gamma_power) / (theta_power + alpha_power)
    print(power)
    return power

def update_beetle_position(focus_level, is_focus_stable):
    global beetle_y
    if is_focus_stable:
        beetle_y = max(10 + beetle_image.get_height() // 2, beetle_y - focus_speed_upward)     # Prevent moving above border
    else:
        beetle_y = min(580 - beetle_image.get_height() // 2, beetle_y + focus_speed_downward)  # Prevent moving below border

# Game loop
running = True
while running:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read EEG data from the LSL stream
        sample, _ = inlet.pull_sample(timeout=0.1)
        if sample:
            filtered_sample = apply_filters(sample[0])
            buffer.append(filtered_sample)

        current_time = time.time()
        if current_time - last_time >= 1:
            last_time = current_time
            release_count = int(len(buffer) * 0.2)  # Remove oldest 20%
            buffer = buffer[release_count:]         # Trim buffer

        if len(buffer) >= buffer_size:              # Process EEG data when the buffer is full
            eeg_data = np.array(buffer)             # Use filtered data
            buffer = []                             # Clear the buffer

            focus_level = calculate_focus_level(eeg_data)

            if focus_level > focus_threshold:
                focus_timer = min(focus_timeout, focus_timer + (current_time - last_focus_time))
                is_focus_stable = focus_timer >= focus_timeout
                update_beetle_position(focus_level, is_focus_stable)

            elif 7 <= focus_level <= 8:  # No movement of the beetle
                print("Beetle remains stationary.")

            else:
                focus_timer = max(0, focus_timer - (current_time - last_focus_time))
                is_focus_stable = focus_timer >= focus_timeout
                update_beetle_position(focus_level, is_focus_stable)

            last_focus_time = current_time

        # Clear the screen and draw the beetle
        screen.fill("#FFFFFF")
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, 780, 580), 5)  # Draw border
        screen.blit(beetle_image, (beetle_x - beetle_image.get_width() // 2, beetle_y - beetle_image.get_height() // 2))
        
        pygame.display.update()

    except KeyboardInterrupt:
        print("Exiting gracefully...")
        running = False

pygame.quit()