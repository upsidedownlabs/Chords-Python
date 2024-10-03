import pygame
import sys
import queue
import threading
from pylsl import StreamInlet, resolve_stream
import numpy as np
from scipy.signal import welch
from scipy.integrate import simpson
import time
import os

# Pygame Initialization
pygame.init()
pygame.mixer.init()  # For sound

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Force Ball Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.SysFont('Arial', 36, bold=True)
title_font = pygame.font.SysFont('Arial', 72, bold=True)

# Load win sound effect using a cross-platform path
base_path = os.path.dirname(__file__)  # Get the directory of the current script
sound_path = os.path.join(base_path, "media", "brass-fanfare-with-timpani-and-winchimes-reverberated-146260.wav")
win_sound = pygame.mixer.Sound(sound_path)

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
game_started = False
first_attempt = True  # Keeps track if it's the first game or a restart

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
    channel_assignments = {0: 'Player A', 1: 'Player B'}
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
                channel1_data = sample[0]  # PLAYER A
                channel2_data = sample[1]  # PLAYER B

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

def reset_game():
    global ball_pos, force_player1, force_player2, paused, game_started
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    force_player1 = force_player2 = 0
    paused = False  # Ensure the game is not paused after reset
    game_started = True  # Ensure the game is marked as started

    # Clear any buffered EEG data
    while not eeg_queue.empty():
        eeg_queue.get()
        print("Empty")

def update_ball_position(force_player1, force_player2):
    global ball_pos
    net_force = force_player2 - force_player1  # force direction
    ball_pos[0] += net_force * ball_speed * 0.01
    if ball_pos[0] < ball_radius:
        ball_pos[0] = ball_radius
    elif ball_pos[0] > WIDTH - ball_radius:
        ball_pos[0] = WIDTH - ball_radius

    print(f"Force Player 1: {force_player1:.2f}, Force Player 2: {force_player2:.2f}, Net Force: {net_force:.2f}")  # Print the forces to the console

def handle_input():
    global force_player1, force_player2
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        force_player1 += 0.25
    if keys[pygame.K_RIGHT]:
        force_player2 += 0.25

def draw_buttons(paused, first_attempt):  # Button dimensions and positions
    button_width = 120
    button_height = 40
    button_radius = 15  # Radius for rounded corners

    # Button positions (y-position is moved up slightly for a better fit)
    start_button_rect = pygame.Rect(WIDTH // 4 - button_width // 2, HEIGHT - 80, button_width, button_height)
    resume_pause_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT - 80, button_width, button_height)
    exit_button_rect = pygame.Rect(3 * WIDTH // 4 - button_width // 2, HEIGHT - 80, button_width, button_height)

    # Draw buttons
    pygame.draw.rect(screen, GREEN, start_button_rect, border_radius=button_radius)  # Start/Restart Button
    pygame.draw.rect(screen, YELLOW, resume_pause_button_rect, border_radius=button_radius)  # Resume/Pause Button
    pygame.draw.rect(screen, RED, exit_button_rect, border_radius=button_radius)  # Exit Button

    # Button Texts
    start_text = font.render("Restart" if not first_attempt else "Start", True, BLACK)
    resume_pause_text = font.render("Resume" if paused else "Pause", True, BLACK)
    exit_text = font.render("Exit", True, BLACK)

    # Calculate text positions for proper centering inside each button
    start_text_pos = (start_button_rect.x + (button_width - start_text.get_width()) // 2,
                      start_button_rect.y + (button_height - start_text.get_height()) // 2)

    resume_pause_text_pos = (resume_pause_button_rect.x + (button_width - resume_pause_text.get_width()) // 2,
                             resume_pause_button_rect.y + (button_height - resume_pause_text.get_height()) // 2)

    exit_text_pos = (exit_button_rect.x + (button_width - exit_text.get_width()) // 2,
                     exit_button_rect.y + (button_height - exit_text.get_height()) // 2)

    # Draw texts
    screen.blit(start_text, start_text_pos)
    screen.blit(resume_pause_text, resume_pause_text_pos)
    screen.blit(exit_text, exit_text_pos)

def draw_players():
    # Draw Player A
    pygame.draw.rect(screen, BLUE, (player1_pos[0], player1_pos[1], player_width, player_height))  # Player A
    player_a_label = font.render("A", True, WHITE)
    screen.blit(player_a_label, (player1_pos[0] - 30, player1_pos[1] + player_height // 2 - player_a_label.get_height() // 2))  # Position label next to Player A

    # Draw Player B
    pygame.draw.rect(screen, RED, (player2_pos[0], player2_pos[1], player_width, player_height))  # Player B
    player_b_label = font.render("B", True, WHITE)
    screen.blit(player_b_label, (player2_pos[0] + player_width + 10, player2_pos[1] + player_height // 2 - player_b_label.get_height() // 2))  # Position label next to Player B

def check_win_condition():
    if ball_pos[0] <= ball_radius:
        return "PLAYER A WINS!"
    elif ball_pos[0] >= WIDTH - ball_radius:
        return "PLAYER B WINS!"
    return None

def main():
    global paused, game_started, first_attempt
    force_player1 = force_player2 = 0
    win_text = None  # Initialize win text
    latest_data = (0, 0)  # To store the latest EEG data for both players

    while True:
        screen.fill(BLACK)

        pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)       # Draw the ball

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:  # Left mouse button
                    # Check if the mouse click is within the bounds of any button
                    if pygame.Rect(WIDTH // 4 - 60, HEIGHT - 80, 120, 40).collidepoint(mouse_pos):
                        # Start or restart the game
                        reset_game()
                        game_started = True
                        first_attempt = False
                        win_text = None  # Reset win text on new game
                    elif pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 40).collidepoint(mouse_pos):
                        # Pause/Resume the game
                        paused = not paused
                    elif pygame.Rect(3 * WIDTH // 4 - 60, HEIGHT - 80, 120, 40).collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

        if game_started:
            if not paused:
                handle_input()
                if not eeg_queue.empty():
                    force_player1, force_player2 = eeg_queue.get()
                    latest_data = (force_player1, force_player2)  # Store latest data

                update_ball_position(force_player1, force_player2)
            else:
                force_player1 = force_player2 = 0   # When paused, stop the ball movement

        draw_players()
        draw_buttons(paused, first_attempt)

        if game_started:
            win_text = check_win_condition()
            if win_text:
                win_sound.play()  # Play sound on win
                paused = True  # Automatically pause the game on win
                while not eeg_queue.empty():
                    eeg_queue.get()
                force_player1, force_player2 = latest_data    # Store the latest data when the game is won

        # Draw win text if there is a winner
        if win_text:
            win_display = font.render(win_text, True, WHITE)
            screen.blit(win_display, (WIDTH // 2 - win_display.get_width() // 2, HEIGHT // 2 - win_display.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)  # 60 frames per second

if __name__ == "__main__":
    main()