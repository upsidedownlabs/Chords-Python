import pygame
import queue
import threading
from eegRead import eeg_data_thread

pygame.init()  # Initialize Pygame
pygame.mixer.init()  # Initialize Pygame Mixer for sound

# Screen dimensions
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  # Fullscreen mode
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

# Load win sound effect
win_sound = pygame.mixer.Sound("C:\\Users\\PAYAL\\Braingame\\brass-fanfare-with-timpani-and-winchimes-reverberated-146260.wav")

# Ball properties
ball_radius = 20
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_color = WHITE
ball_speed = 40

# Player properties
player_width = 10
player_height = 100
player1_pos = [50, HEIGHT // 2 - player_height // 2]
player2_pos = [WIDTH - 50 - player_width, HEIGHT // 2 - player_height // 2]

clock = pygame.time.Clock()

# Initialize EEG queue
eeg_queue = queue.Queue()
eeg_thread = threading.Thread(target=eeg_data_thread, args=(eeg_queue,))
eeg_thread.daemon = True
eeg_thread.start()

def reset_game():
    global ball_pos, force_player1, force_player2
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    force_player1 = 0
    force_player2 = 0

    # Clear any buffered EEG data
    while not eeg_queue.empty():  
        eeg_queue.get()

def update_ball_position(force_player1, force_player2):
    global ball_pos
    net_force = force_player2 - force_player1  # Correct force direction
    print(force_player2, force_player1)
    ball_pos[0] += net_force * ball_speed * 0.01
    if ball_pos[0] < ball_radius:
        ball_pos[0] = ball_radius
    elif ball_pos[0] > WIDTH - ball_radius:
        ball_pos[0] = WIDTH - ball_radius

def handle_input():
    global force_player1, force_player2
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        force_player1 += 0.25
    elif keys[pygame.K_RIGHT]:
        force_player1 -= 0.25

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

    # Render the text on the buttons
    screen.blit(start_text, start_text_pos)
    screen.blit(resume_pause_text, resume_pause_text_pos)
    screen.blit(exit_text, exit_text_pos)

def check_win_condition():
    if ball_pos[0] <= ball_radius:
        return "PLAYER-A WINS!"
    elif ball_pos[0] >= WIDTH - ball_radius:
        return "PLAYER-B WINS!"
    return None

def draw_countdown(count):
    # Create a circular box for the countdown
    countdown_radius = 100  # Radius for the circular box
    countdown_center = (WIDTH // 2, HEIGHT // 2)  # Center position for the circle

    # Draw the circular background
    pygame.draw.circle(screen, BLACK, countdown_center, countdown_radius)
    pygame.draw.circle(screen, WHITE, countdown_center, countdown_radius - 5)  # Inner white circle for contrast

    # Set the font size for the countdown number
    countdown_font = pygame.font.SysFont('Arial', 96, bold=True)  # Larger font for the countdown number
    countdown_text = countdown_font.render(str(count), True, RED)  # Countdown number in red

    # Center the countdown text in the circular box
    countdown_text_pos = (countdown_center[0] - countdown_text.get_width() // 2,
                          countdown_center[1] - countdown_text.get_height() // 2)

    # Render the countdown number on the screen
    screen.blit(countdown_text, countdown_text_pos)

def draw():
    screen.fill(BLACK)

    pygame.draw.rect(screen, RED, (*player1_pos, player_width, player_height))  # Draw Players
    pygame.draw.rect(screen, BLUE, (*player2_pos, player_width, player_height))
    
    pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)  # Draw ball

    title_text = title_font.render("Force Ball Game", True, WHITE)  # Draw game title at the top middle
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

    player_a_text = font.render("A", True, WHITE)  # Draw player names next to their respective lines
    player_b_text = font.render("B", True, WHITE)
    screen.blit(player_a_text, (player1_pos[0] - player_a_text.get_width() - 20, HEIGHT // 2 - player_a_text.get_height() // 2))
    screen.blit(player_b_text, (player2_pos[0] + player_width + 20, HEIGHT // 2 - player_b_text.get_height() // 2))

    draw_buttons(paused, first_attempt)  # Draw buttons

    pygame.display.flip()

# Initial forces
force_player1 = 0
force_player2 = 0
game_started = False
paused = False
game_running = True
game_won = False
first_attempt = True  # Keeps track if it's the first game or a restart

while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False  # Stops the game but keeps the app running
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check button clicks
            if WIDTH // 4 - 75 <= mouse_pos[0] <= WIDTH // 4 + 75 and HEIGHT - 100 <= mouse_pos[1] <= HEIGHT - 50:
                print("Start/Restart Button Clicked")
                game_started = True
                paused = False
                game_won = False
                first_attempt = False  # After first click, button becomes "Restart"
                reset_game()  # Reset the game state when start/restart is clicked
            elif WIDTH // 2 - 75 <= mouse_pos[0] <= WIDTH // 2 + 75 and HEIGHT - 100 <= mouse_pos[1] <= HEIGHT - 50:
                print("Resume/Pause Button Clicked")
                if game_started:
                    paused = not paused  # Toggle pause/resume
            elif 3 * WIDTH // 4 - 75 <= mouse_pos[0] <= 3 * WIDTH // 4 + 75 and HEIGHT - 100 <= mouse_pos[1] <= HEIGHT - 50:
                print("Exit Button Clicked")
                game_running = False  # Stop the game and return to main GUI

    if game_started and not paused:
        handle_input()

        if not eeg_queue.empty():  # Update forces from EEG data
            force_player1, force_player2 = eeg_queue.get()
        update_ball_position(force_player1, force_player2)

        winner = check_win_condition()  # Check for win condition
        if winner:
            winner_text = title_font.render(winner, True, WHITE)
            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait for 1 second before starting countdown
            win_sound.play()  # Play win sound
            
            for count in range(3, 0, -1):  # Countdown from 3 to 1
                draw()
                draw_countdown(count)  # Call to draw the countdown
                pygame.display.flip()
                pygame.time.wait(1000)  # Wait for 1 second between counts

            reset_game()      # Reset game state
            
            # Automatically start the game after countdown ends
            game_started = True  # Set game started to True after countdown

    draw()
    clock.tick(60)  # 60 frames per second

pygame.quit()  # Quit Pygame when the main loop ends.