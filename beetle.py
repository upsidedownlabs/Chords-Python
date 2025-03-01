import pygame
import pylsl
import numpy as np
import time
from pylsl import StreamInlet, resolve_streams, resolve_byprop
from scipy.signal import iirnotch, butter, lfilter
import math

# Initialize LSL stream
print("Searching for available LSL streams...")
streams = resolve_streams()
available_streams = [s.name() for s in streams]

if not available_streams:
    print("No LSL streams found!")

for stream_name in available_streams:
    print(f"Trying to connect to {stream_name}...")
    resolved_streams = resolve_byprop('name', stream_name, timeout=2)

    if resolved_streams:
        print(f"Successfully connected to {stream_name}!")
        inlet = StreamInlet(resolved_streams[0])
        break
    else:
        print(f"Failed to connect to {stream_name}.")

if inlet is None:
    print("Could not connect to any stream.")
sampling_rate = int(inlet.info().nominal_srate())
print(f"Sampling rate: {sampling_rate} Hz")

b_notch, a_notch = iirnotch(50.0 / (sampling_rate / 2), 30.0)
b_band, a_band = butter(4, [0.5 / (sampling_rate / 2), 48.0 / (sampling_rate / 2)], btype='band')

# Buffer for EEG data and Focus tracking variables
buffer = []
buffer_size = 500

# Beetle properties
beetle_x, beetle_y = 380, 530
focus_speed_upward = 10
focus_speed_downward = 5
focus_timeout = 2
focus_threshold = None

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Beetle Game')

sprite_count = 10
beetle_sprites = [pygame.image.load(f'media/beetle{i}.JPG') for i in range(1, sprite_count + 1)]
beetle_sprites = [pygame.transform.scale(sprite, (140, 160)) for sprite in beetle_sprites]

# Animation Variables
current_sprite = 0
animation_speed = 100
sprite_timer = 0

# Function to display a message on the screen
def show_message(message, duration=3):
    start_time = time.time()
    font = pygame.font.SysFont("Arial", 50)
    text = font.render(message, True, (0, 0, 0))
    text_rect = text.get_rect(center=(400, 300))

    while time.time() - start_time < duration:
        screen.fill((255, 255, 255))
        screen.blit(text, text_rect)
        pygame.display.update()

# Apply filters
def apply_filters(eeg_point):
    filtered = lfilter(b_notch, a_notch, [eeg_point])
    filtered_point = lfilter(b_band, a_band, filtered)
    return filtered_point[0]

def calculate_focus_level(eeg_data, sampling_rate=500):
    window = np.hanning(len(eeg_data))  
    eeg_data_windowed = eeg_data * window
    fft_data = np.abs(np.fft.fft(eeg_data_windowed))[:len(eeg_data_windowed) // 2]
    fft_data /= len(eeg_data_windowed)
    freqs = np.fft.fftfreq(len(eeg_data_windowed), d=1 / sampling_rate)[:len(eeg_data_windowed) // 2]
    
    delta_power = math.sqrt(np.sum((fft_data[(freqs >= 0.5) & (freqs <= 4)]) ** 2))
    theta_power = math.sqrt(np.sum((fft_data[(freqs >= 4) & (freqs <= 8)]) ** 2))
    alpha_power = math.sqrt(np.sum((fft_data[(freqs >= 8) & (freqs <= 13)]) ** 2))
    beta_power = math.sqrt(np.sum((fft_data[(freqs >= 13) & (freqs <= 30)]) ** 2))
    gamma_power = math.sqrt(np.sum((fft_data[(freqs >= 30) & (freqs <= 45)]) ** 2))
    
    power = (beta_power + gamma_power) / (delta_power + theta_power + alpha_power + beta_power + gamma_power)
    return power

# Calibration Phase
show_message("Sit still and relax for 10 seconds", 3)

print("Starting Calibration... Please relax and stay still for 10 seconds.")
calibration_data = []
calibration_duration = 10
calibration_start_time = time.time()

while time.time() - calibration_start_time < calibration_duration:
    sample, _ = inlet.pull_sample(timeout=0.1)
    if sample:
        filtered_sample = apply_filters(sample[0])
        calibration_data.append(filtered_sample)

if len(calibration_data) >= buffer_size:
    eeg_data = np.array(calibration_data)
    baseline_focus_levels = [calculate_focus_level(eeg_data[i:i + buffer_size]) for i in range(0, len(eeg_data), buffer_size)]

    mean_focus = np.mean(baseline_focus_levels)
    std_focus = np.std(baseline_focus_levels)

    focus_threshold = mean_focus + 1.5 * std_focus  
    print(f"Calibration Complete. Focus Threshold set at: {focus_threshold:.3f}")
else:
    print("Calibration failed due to insufficient data.")
    exit()

# Show Game Start Message
show_message("Game Starting...", 1)
game_start_time = time.time()
game_duration = 45  # Game lasts 45 seconds

# Update beetle position
def update_beetle_position(focus_level, is_focus_stable):
    global beetle_y
    if is_focus_stable:
        beetle_y = max(10 + beetle_sprites[0].get_height() // 2, beetle_y - focus_speed_upward)     
    else:
        beetle_y = min(580 - beetle_sprites[0].get_height() // 2, beetle_y + focus_speed_downward)  

print("STARTING GAME...")
running = True
focus_timer = 0
last_focus_time = time.time()
last_time = time.time()

while running:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        sample, _ = inlet.pull_sample(timeout=0.1)
        if sample:
            filtered_sample = apply_filters(sample[0])
            buffer.append(filtered_sample)

        current_time = time.time()
        elapsed_time = int(current_time - game_start_time)

        if current_time - last_time >= 1:
            last_time = current_time
            buffer = buffer[int(len(buffer) * 0.2):]

        if len(buffer) >= buffer_size:
            eeg_data = np.array(buffer)
            buffer = []

            focus_level = calculate_focus_level(eeg_data)
            print(focus_level)

            if focus_level > focus_threshold:
                focus_timer = min(focus_timeout, focus_timer + (current_time - last_focus_time))
                is_focus_stable = focus_timer >= focus_timeout
                update_beetle_position(focus_level, is_focus_stable)
            else:
                focus_timer = max(0, focus_timer - (current_time - last_focus_time))
                is_focus_stable = focus_timer >= focus_timeout
                update_beetle_position(focus_level, is_focus_stable)

            last_focus_time = current_time

        # Update sprite animation
        sprite_timer += (current_time - last_focus_time)
        if sprite_timer >= animation_speed:
            sprite_timer = 0
            current_sprite = (current_sprite + 1) % len(beetle_sprites)

        # Check win condition
        if beetle_y <= 80:
            show_message("You Win!", 1)
            running = False

        # Check game over condition
        if elapsed_time >= game_duration:
            show_message("Game Over! Try Again.", 1)
            running = False

        # Draw everything
        screen.fill("#FFFFFF")
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, 780, 580), 5)  
        screen.blit(beetle_sprites[current_sprite], (beetle_x - 40, beetle_y - 40))

        # Display Timer
        font = pygame.font.SysFont("Arial", 30)
        timer_text = font.render(f"Time: {game_duration - elapsed_time}s", True, (0, 0, 0))
        screen.blit(timer_text, (650, 20))  

        pygame.display.update()

    except KeyboardInterrupt:
        print("Exiting gracefully...")
        running = False

pygame.quit()