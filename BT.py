import utils.session
import pygame
import serial
import time
pygame.init()
# Window setup
win_width, win_height = 800, 600
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Joystick Game")
# Character setup
character_size = 50
character_color = (0, 255, 0)
character_x, character_y = win_width // 2, win_height // 2
character_speed = 5
# Goal setup (WIN condition)
goal_size = 40
goal_color = (0, 0, 255)
goal_rect = pygame.Rect(700, 500, goal_size, goal_size)
# Obstacle setup (FAIL condition)
obstacle_color = (255, 0, 0)
obstacle_rects = [
    pygame.Rect(300, 200, 100, 40),
    pygame.Rect(500, 400, 150, 40),
]
arduino_port = 'COM10'
try:
    ser = serial.Serial(arduino_port, 9600, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port {arduino_port}: {e}")
    exit(1)
running = True
game_over = False
game_win = False
prev_x, prev_y = character_x, character_y
# Flash effect settings
flash_color = None
flash_time = 0
FLASH_DURATION = 300  # milliseconds
def trigger_flash(color):
    global flash_color, flash_time
    flash_color = color
    flash_time = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if not game_over and not game_win:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            data = line.split(',')
            if len(data) == 3:
                try:
                    joy_x, joy_y, button_state = map(int, data)
                    dx = ((joy_x - 512) / 512) * character_speed
                    dy = ((joy_y - 512) / 512) * character_speed
                    new_x = max(character_size // 2,
                                min(win_width - character_size // 2, character_x + dx))
                    new_y = max(character_size // 2,
                                min(win_height - character_size // 2, character_y + dy))
                    if (new_x, new_y) != (prev_x, prev_y):
                        character_x, character_y = new_x, new_y
                    character_color = (0, 0, 225) if button_state == 1 else (0, 255, 0)
                except ValueError:
                    print(f"Skipping invalid data: {line}")
            else:
                print(f"Ignoring line with wrong number of values: {line}")
        # Collision detection with goal (WIN)
        player_rect = pygame.Rect(character_x - character_size // 2,
                                  character_y - character_size // 2,
                                  character_size, character_size)
        if player_rect.colliderect(goal_rect):
            game_win = True
            trigger_flash((0, 255, 0))  # Green flash
        # Collision detection with obstacles (FAIL)
        for obs in obstacle_rects:
            if player_rect.colliderect(obs):
                game_over = True
                trigger_flash((255, 0, 0))  # Red flash
    # Drawing
    win.fill((255, 255, 255))
    if game_win:
        font = pygame.font.SysFont(None, 80)
        text = font.render("YOU WIN!", True, (0, 200, 0))
        win.blit(text, (win_width//2 - text.get_width()//2, win_height//2 - text.get_height()//2))
    elif game_over:
        font = pygame.font.SysFont(None, 80)
        text = font.render("YOU LOSE!", True, (200, 0, 0))
        win.blit(text, (win_width//2 - text.get_width()//2, win_height//2 - text.get_height()//2))
    else:
        # Draw goal
        pygame.draw.rect(win, goal_color, goal_rect)
        # Draw obstacles
        for obs in obstacle_rects:
            pygame.draw.rect(win, obstacle_color, obs)
        # Draw character
        pygame.draw.circle(win, character_color, (int(character_x), int(character_y)), character_size // 2)
    # Flash effect overlay
    if flash_color:
        elapsed = pygame.time.get_ticks() - flash_time
        if elapsed < FLASH_DURATION:
            flash_surface = pygame.Surface((win_width, win_height))
            flash_surface.set_alpha(100)  # Transparency
            flash_surface.fill(flash_color)
            win.blit(flash_surface, (0, 0))
        else:
            flash_color = None  # Stop flashing
    pygame.display.update()
ser.close()
pygame.quit()