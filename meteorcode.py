
import pygame
import random

# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------
pygame.init()

# Window sizing
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save Earth: 2247")

# Colors
WHITE = (255, 255, 255)
GAME_BLUE = (2, 100, 147)
BLUE = (95, 183, 207)
RED = (95, 183, 207)

# HUD sizing (shared by hearts + crystals so they match)
HUD_SIZE = 50
HUD_SPACING = 10
HUD_MARGIN = 15

# ---------------------------------------------------------
# ASSET LOADING
# ---------------------------------------------------------
# Background
background = pygame.image.load("2247_earth.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Player images
player = pygame.image.load("astro_front.png")
walk_right = pygame.image.load("astro_right.png")
walk_left = pygame.image.load("astro_left.png")
idle = pygame.transform.scale(player, (160, 160))
walk_right = pygame.transform.scale(walk_right, (160, 160))
walk_left = pygame.transform.scale(walk_left, (160, 160))

# Heart image
heart = pygame.image.load("heart.png")
heart = pygame.transform.scale(heart, (HUD_SIZE, HUD_SIZE))

# Crystal images
crystal_full = pygame.image.load("crystal.png").convert_alpha()
crystal_empty = pygame.image.load("crystal_empty.png").convert_alpha()
crystal_full = pygame.transform.scale(crystal_full, (HUD_SIZE, HUD_SIZE))
crystal_empty = pygame.transform.scale(crystal_empty, (HUD_SIZE, HUD_SIZE))



# Meteor images
meteor1 = pygame.image.load("METEOR 1.png").convert_alpha()
meteor2 = pygame.image.load("METEOR 2.png").convert_alpha()
meteor_images=[meteor1,meteor2]

meteors=[]
NUM_METEORS=5

def create_meteor():
    size=random.randint(40,95)
    img=pygame.transform.scale(random.choice(meteor_images),(size,size))
    return {"image":img,"x":random.randint(0,WIDTH-size),"y":random.randint(-700,-50),"speed":random.randint(3,9),"size":size}

for _ in range(NUM_METEORS):
    meteors.append(create_meteor())

# Fonts
title_font = pygame.font.Font("PixeloidSans-Bold.ttf", 100)
button_font = pygame.font.Font("PixeloidSans-Bold.ttf", 30)

# ---------------------------------------------------------
# GAME VARIABLES
# ---------------------------------------------------------
player_x = 100
player_y = 100
speed = 5
current_image = idle

lives = 3
crystals_collected = 0

title = title_font.render("2247", True, GAME_BLUE)
title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))

clock = pygame.time.Clock()

game_state = "intro"
new_game_button = pygame.Rect(500, 300, 300, 80)
quit_button = pygame.Rect(500, 400, 300, 80)

# Intro animation
fade_alpha = 0
fade_speed = 3
intro_stage = "fade_in"
hold_start = 0

# ---------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------
def draw_hearts(screen):
    """Draws the player's remaining lives in the bottom-right corner."""
    y = HEIGHT - HUD_SIZE - HUD_MARGIN
    for i in range(lives):
        x = WIDTH - HUD_MARGIN - (lives - i) * HUD_SIZE - (lives - 1 - i) * HUD_SPACING
        screen.blit(heart, (x, y))

def draw_crystal_hud(screen):
    """Draws 3 crystal slots in the bottom-left corner, parallel to hearts."""
    y = HEIGHT - HUD_SIZE - HUD_MARGIN
    for i in range(3):
        x = HUD_MARGIN + i * (HUD_SIZE + HUD_SPACING)
        img = crystal_full if i < crystals_collected else crystal_empty
        screen.blit(img, (x, y))

def draw_intro():
    """Handles the intro fade-in / hold / fade-out animation."""
    global fade_alpha, intro_stage, hold_start, game_state
    title.set_alpha(fade_alpha)
    screen.blit(title, title_rect)

    if intro_stage == "fade_in":
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            fade_alpha = 255
            intro_stage = "hold"
            hold_start = pygame.time.get_ticks()
    elif intro_stage == "hold":
        if pygame.time.get_ticks() - hold_start >= 2000:
            intro_stage = "fade_out"
    elif intro_stage == "fade_out":
        fade_alpha -= fade_speed
        if fade_alpha <= 0:
            fade_alpha = 0
            game_state = "menu"

def draw_menu():
    """Draws the main menu with Start Game and Quit buttons."""
    menu_title = title_font.render("Save Earth: 2247", True, BLUE)
    screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, 220)))

    mouse_pos = pygame.mouse.get_pos()

    # Start Game Button
    if new_game_button.collidepoint(mouse_pos):
        start_button = new_game_button.inflate(20, 10)
        start_color = GAME_BLUE
    else:
        start_button = new_game_button
        start_color = BLUE
    pygame.draw.rect(screen, start_color, start_button, border_radius=20)
    new_text = button_font.render("Start Game", True, WHITE)
    screen.blit(new_text, new_text.get_rect(center=start_button.center))

    # Quit Button
    if quit_button.collidepoint(mouse_pos):
        quit_button_draw = quit_button.inflate(20, 10)
        quit_color = GAME_BLUE
    else:
        quit_button_draw = quit_button
        quit_color = RED
    pygame.draw.rect(screen, quit_color, quit_button_draw, border_radius=20)
    quit_text = button_font.render("Quit", True, WHITE)
    screen.blit(quit_text, quit_text.get_rect(center=quit_button_draw.center))

def update_gameplay():
    """Handles player movement, drawing player, hearts, and crystal HUD."""
    global player_x, player_y, current_image

    keys = pygame.key.get_pressed()
    current_image = idle

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

    player_x = max(0, min(player_x, WIDTH - 160))
    player_y = max(0, min(player_y, HEIGHT - 160))

    player_rect=pygame.Rect(player_x,player_y,160,160)
    screen.blit(current_image,(player_x,player_y))
    global lives
    for m in meteors:
        m["y"]+=m["speed"]
        screen.blit(m["image"],(m["x"],m["y"]))
        if pygame.Rect(m["x"],m["y"],m["size"],m["size"]).colliderect(player_rect):
            if lives>0:
                lives-=1
            m.update(create_meteor())
        elif m["y"]>HEIGHT:
            m.update(create_meteor())

    draw_hearts(screen)
    draw_crystal_hud(screen)

    # ----------------------------------------
    # FUTURE DAMAGE CODE GOES HERE
    # Example:
    #
    # if player_hits_enemy:
    #     lives = max(0, lives - 1)
    # ----------------------------------------

# ---------------------------------------------------------
# MAIN GAME LOOP
# ---------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                if new_game_button.collidepoint(event.pos):
                    game_state = "game"
                elif quit_button.collidepoint(event.pos):
                    running = False

    screen.blit(background, (0, 0))

    if game_state == "intro":
        draw_intro()
    elif game_state == "menu":
        draw_menu()
    elif game_state == "game":
        update_gameplay()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

