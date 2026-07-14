import pygame

pygame.init() #basically turn pygame on and allow usage

#sizing the window
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save Earth: 2247")  # Window title

#built in colors:
WHITE = (255, 255, 255)
GAME_BLUE = (54, 82, 80)
RED = (180, 50, 50)

# Load and resize the background image
background = pygame.image.load("2247_earth.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

#player images
player = pygame.image.load("astro_front.png")
walk_right = pygame.image.load("astro_right.png")
walk_left = pygame.image.load("astro_left.png")

idle = pygame.transform.scale(player, (160, 160))
walk_right = pygame.transform.scale(walk_right, (160, 160))
walk_left = pygame.transform.scale(walk_left, (160, 160))

#player variables
player_x = 100
player_y = 100
speed = 5
current_image = idle

#FONTS



#title screen
title_font = pygame.font.SysFont("Arial", 72, bold=True)

title = title_font.render("2247", True, (54, 82, 80))
title_rect = title.get_rect(center = (WIDTH // 2, HEIGHT // 2))

clock = pygame.time.Clock()

#Game State
game_state = "menu"
button_font = pygame.font.Font(None, 50)

new_game_button = pygame.Rect(500, 250, 300, 80)
load_game_button = pygame.Rect(500, 370, 300, 80)
quit_button = pygame.Rect(500, 490, 300, 80)

# Fade In
for alpha in range(0, 256, 5):

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    screen.blit(background, (0, 0))

    title.set_alpha(alpha)
    screen.blit(title, title_rect)

    pygame.display.flip()
    clock.tick(60)

# Hold for 2 seconds
hold_start = pygame.time.get_ticks()
while pygame.time.get_ticks() - hold_start < 2000:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    screen.blit(background, (0, 0))
    screen.blit(title, title_rect)
    pygame.display.flip()
    clock.tick(60)

# Fade Out
for alpha in range(255, -1, -5):

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    screen.blit(background, (0, 0))

    title.set_alpha(alpha)
    screen.blit(title, title_rect)

    pygame.display.flip()
    clock.tick(60)

# Current image starts as idle
current_image = idle

#MAIN GAME LOOP
running = True #while the game is running is true...
while running:

#creating new versus load game:

    for event in pygame.event.get(): #checking for events (actions)
        if event.type == pygame.QUIT: #if user clicks the close button, end game
            running = False

    keys = pygame.key.get_pressed()
    
    # Movement
    if keys[pygame.K_d]:
        player_x += speed
        current_image = walk_right

    elif keys[pygame.K_a]:
        player_x -= speed
        current_image = walk_left

    if keys[pygame.K_w]:
        player_y -= speed

    if keys[pygame.K_s]:
        player_y += speed

    # Keep player on screen
    player_x = max(0, min(player_x, WIDTH - 60))
    player_y = max(0, min(player_y, HEIGHT - 120))

    # Draw Everything
    screen.blit(background, (0, 0))
    pygame.draw.rect(screen, BLUE, (400, 400, 200, 80))
    screen.blit(current_image, (player_x, player_y))

    

    pygame.display.update()

pygame.quit()