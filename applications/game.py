import pygame
import sys
import queue
import threading
from pylsl import StreamInlet, resolve_stream
import numpy as np
from scipy.signal import welch
from scipy.integrate import simpson
import time

# Pygame Initialization
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Force Ball Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Ball properties
ball_radius = 20
ball_color = WHITE
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_speed = 40

# Player properties
player_width = 10
player_height = 100
player1_pos = [50, HEIGHT // 2 - player_height // 2]
player2_pos = [WIDTH - 50 - player_width, HEIGHT // 2 - player_height // 2]

clock = pygame.time.Clock()

eeg_queue = queue.Queue()     # Initialize EEG queue

running = True    # Game state
paused = False

def bandpower(data, sf, band, window_sec=None, relative=False):
    band = np.asarray(band)
    low, high = band

    if window_sec is not None:
        nperseg = window_sec * sf
    else:
        nperseg = (2 / low) * sf

    freqs, psd = welch(data, sf, nperseg=nperseg)
    freq_res = freqs[1] - freqs[0]
    idx_band = np.logical_and(freqs >= low, freqs <= high)
    bp = simpson(psd[idx_band], dx=freq_res)

    if relative:
        bp /= simpson(psd, dx=freq_res)
    return bp

def eeg_data_thread(eeg_queue):
    streams = resolve_stream('name', 'BioAmpDataStream')
    if not streams:
        print("No LSL stream found!")
        return

    inlet = StreamInlet(streams[0])
    sampling_frequency = 250
    bands = {
        'Delta': [0.5, 4],
        'Theta': [4, 8],
        'Alpha': [8, 13],
        'Beta': [13, 30],
        'Gamma': [30, 40]
    }
    buffer_length = sampling_frequency * 4
    data_buffer = {'Channel1': [], 'Channel2': []}
    powerData1 = []
    powerData2 = []
    c = 0
    start_time = time.time()

    baseline1 = baseline2 = 1  # Initialize baselines

    while running:
        try:
            sample, timestamp = inlet.pull_sample()
            if len(sample) >= 6:
                channel1_data = sample[0]  # First channel
                channel2_data = sample[1]  # Second channel

                data_buffer['Channel1'].append(channel1_data)
                data_buffer['Channel2'].append(channel2_data)

                # Keep the data buffer length in check
                if len(data_buffer['Channel1']) > buffer_length:
                    data_buffer['Channel1'].pop(0)
                    data_buffer['Channel2'].pop(0)

                elapsed_time = time.time() - start_time
                if len(data_buffer['Channel1']) >= buffer_length:
                    power_data = {'Channel1': {}, 'Channel2': {}}
                    for band_name, band_freqs in bands.items():
                        power_data['Channel1'][band_name] = bandpower(
                            np.array(data_buffer['Channel1']), sampling_frequency, band_freqs
                        )
                        power_data['Channel2'][band_name] = bandpower(
                            np.array(data_buffer['Channel2']), sampling_frequency, band_freqs
                        )

                    powerData1.append(power_data['Channel1']['Beta'] / power_data['Channel1']['Alpha'])
                    powerData2.append(power_data['Channel2']['Beta'] / power_data['Channel2']['Alpha'])

                    if elapsed_time >= 5:
                        if c != 1:
                            baseline1 = max(powerData1)
                            baseline2 = max(powerData2)
                            c = 1
                            data_time = elapsed_time
                            powerData1 = []
                            powerData2 = []
                        elif elapsed_time - data_time >= 0.25:
                            current_power1 = (max(powerData1) - baseline1) / baseline1 if baseline1 > 0 else 0
                            current_power2 = (max(powerData2) - baseline2) / baseline2 if baseline2 > 0 else 0

                            eeg_queue.put((current_power1, current_power2))
                            powerData1 = []
                            powerData2 = []
                            data_time = elapsed_time
            else:
                time.sleep(0.1)  # Prevent busy waiting
        except Exception as e:
            print(f"Error occurred while pulling sample: {e}")  
            time.sleep(0.1)  

# Start the EEG thread
eeg_thread = threading.Thread(target=eeg_data_thread, args=(eeg_queue,))
eeg_thread.daemon = True
eeg_thread.start()

def update_ball_position(force_player1, force_player2):
    global ball_pos
    net_force = force_player1 - force_player2
    ball_pos[0] += net_force * ball_speed * 0.01

    if ball_pos[0] < ball_radius:     # Keep the ball within the screen bounds
        ball_pos[0] = ball_radius
    elif ball_pos[0] > WIDTH - ball_radius:
        ball_pos[0] = WIDTH - ball_radius

def restart_game():
    global ball_pos, force_player1, force_player2
    ball_pos[0] = WIDTH // 2
    ball_pos[1] = HEIGHT // 2
    force_player1 = 0
    force_player2 = 0

# Initial forces
force_player1 = 0
force_player2 = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        # Handle key presses for pause and restart
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Pause
                paused = not paused
            elif event.key == pygame.K_r:  # Restart
                restart_game()
            elif event.key == pygame.K_q:  # Quit
                running = False

    if not paused:
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            force_player1 += 0.1  # Apply a small force to player 1
        elif keys[pygame.K_RIGHT]:
            force_player1 -= 0.1  # Apply a small force to player 1

        # Update forces from EEG data
        if not eeg_queue.empty():
            force_player1_eeg, force_player2_eeg = eeg_queue.get()
            force_player1 += force_player1_eeg
            force_player2 += force_player2_eeg

        update_ball_position(force_player1, force_player2)

        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, (*player1_pos, player_width, player_height))
        pygame.draw.rect(screen, BLUE, (*player2_pos, player_width, player_height))
        pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

        # Print net forces
        print(f"Net Force - Player 1: {force_player1:.4f}, Player 2: {force_player2:.4f}")

        pygame.display.flip()
        clock.tick(60)  # 60 frames per second

    # Check for a win condition
    if ball_pos[0] < player1_pos[0] + player_width and ball_pos[1] >= player1_pos[1] and ball_pos[1] <= player1_pos[1] + player_height:
        print("Player 2 wins!")
        pygame.time.wait(3000)  # Wait for 3 seconds before restarting
        restart_game()
    elif ball_pos[0] > player2_pos[0] - ball_radius and ball_pos[1] >= player2_pos[1] and ball_pos[1] <= player2_pos[1] + player_height:
        print("Player 1 wins!")
        pygame.time.wait(3000)  # Wait for 3 seconds before restarting
        restart_game()

pygame.quit()