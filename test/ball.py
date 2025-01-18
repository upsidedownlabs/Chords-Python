import pygame
import pylsl
import numpy as np
import time
from pylsl import StreamInlet, resolve_stream

pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Focus Game')

# Ball properties
ball_x, ball_y = 400, 550
ball_radius = 20
focus_speed_upward = 8     # Speed when moving upward
focus_speed_downward = 4   # Speed when moving downward
focus_timeout = 2          # Time in seconds to stabilize focus
focus_threshold = 1000000000  # Threshold for beta power

# LSL stream setup
streams = resolve_stream('name', 'BioAmpDataStream')
if not streams:
    print("No LSL stream found!")
    pygame.quit()
    exit()

inlet = StreamInlet(streams[0])
print(" LSL Stream Started")

# Buffer for EEG data and Focus tracking variables
buffer = []
buffer_size = 500
focus_timer = 0
last_focus_time = time.time()
last_time = time.time()

def calculate_focus_level(eeg_data):
    fft_result = np.fft.fft(eeg_data)
    freqs = np.fft.fftfreq(len(eeg_data), 1 / 500)
    positive_freqs = freqs[:len(freqs) // 2]
    fft_magnitude = np.abs(fft_result[:len(freqs) // 2])

    # Extract beta band power (13-30 Hz)
    beta_band = np.where((positive_freqs >= 13) & (positive_freqs <= 30))
    beta_power = np.sum(fft_magnitude[beta_band] ** 2)
    print(f"Beta Power: {beta_power}")

    return beta_power

def update_ball_position(focus_level, is_focus_stable):
    global ball_y
    if is_focus_stable:
        ball_y = max(0, ball_y - focus_speed_upward)                    # Move upward, bounded by top
    else:
        ball_y = min(600 - ball_radius, ball_y + focus_speed_downward)  # Move downward, bounded by bottom

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
            buffer.append(sample[:1])               # Append new data to buffer

        current_time = time.time()
        if current_time - last_time >= 1:
            last_time = current_time
            release_count = int(len(buffer) * 0.2)  # Remove oldest 20%
            buffer = buffer[release_count:]         # Trim buffer

        if len(buffer) >= buffer_size:              # Process EEG data when the buffer is full
            eeg_data = np.array(buffer)[:, 0]       # Use only the first channel
            buffer = []                             # Clear the buffer

            focus_level = calculate_focus_level(eeg_data)

            if focus_level > focus_threshold:
                focus_timer = min(focus_timeout, focus_timer + (current_time - last_focus_time))
            else:
                focus_timer = max(0, focus_timer - (current_time - last_focus_time))

            is_focus_stable = focus_timer >= focus_timeout
            update_ball_position(focus_level, is_focus_stable)
            last_focus_time = current_time

        screen.fill((0, 0, 0))
        pygame.draw.circle(screen, (255, 0, 0), (ball_x, ball_y), ball_radius)  # Draw the ball
        pygame.display.update()

    except KeyboardInterrupt:
        print("Exiting gracefully...")
        running = False

pygame.quit()