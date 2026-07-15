import pygame
import random

pygame.init() #basically turn pygame on and allow usage

#sizing the window
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save Earth: 2247")  # Window title

#built in colors:
WHITE = (255, 255, 255)
GAME_BLUE = (2,100,147)
BLUE = (95,183,207)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

#Health/Stamina (HUD) bar sizing (shared by hearts + crystals so they match)
HUD_SIZE = 50
HUD_SPACING = 10
HUD_MARGIN = 15

#player limits for og screen
OGLEFT_LIMIT = 50
OGRIGHT_LIMIT = 1190
OGTOP_LIMIT = 485
OGBOTTOM_LIMIT = 560

#player limits for all other levels
LEFT_LIMIT = 0
RIGHT_LIMIT = 1100
TOP_LIMIT = 0
BOTTOM_LIMIT = 505

# Load and resize the background image
background = pygame.image.load("2247_earth.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Earth to Moon background
earth_to_moon = pygame.image.load("earth_to_moon.png")
earth_to_moon = pygame.transform.scale(earth_to_moon, (WIDTH, HEIGHT))

#intro images
intro1 = pygame.image.load("Intro1.png")
intro2 = pygame.image.load("Intro2.png")

intro1 = pygame.transform.scale(intro1, (WIDTH, HEIGHT))
intro2 = pygame.transform.scale(intro2, (WIDTH, HEIGHT))

level1_intro = pygame.image.load("level1_intro.png")
level1_intro = pygame.transform.scale(level1_intro, (WIDTH, HEIGHT))


#moon rocks
mrock1 = pygame.image.load("moon_rock1.png")
mrock2 = pygame.image.load("moon_rock2.png")
mrock1 = pygame.transform.scale(mrock1, (100, 100))
mrock2 = pygame.transform.scale(mrock2, (100, 100))

# Story screen variables
story_images = [intro1, intro2]
current_story = 0
story_alpha = 0
story_fade_speed = 4

# Earth to Moon transition variables
transition_alpha = 0
transition_speed = 4

# Transition timer
transition_timer = 0

# Moon timer
LEVEL_TIME = 60
moon_start_time = 0

#moon backgrounds
level1_into = pygame.image.load("level1_intro.png")
moon_background = pygame.image.load("moon.png")
moon_background = pygame.transform.scale(moon_background, (WIDTH, HEIGHT))

#moon rocks
moon_rock1 = pygame.image.load("moon_rock1.png")
moon_rock2 = pygame.image.load("moon_rock2.png")
moon_rock1 = pygame.transform.scale(moon_rock1, (50, 50))
moon_rock2 = pygame.transform.scale(moon_rock2, (50, 50))

#rockets
rocket1 = pygame.image.load("rocket1.png")
rocket2 = pygame.image.load("rocket2.png")
rocket1 = pygame.transform.scale(rocket1, (135, 250))
rocket2 = pygame.transform.scale(rocket2, (50, 100))

#player images
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

meteors = []
NUM_METEORS = 5

#heart/crystal variables
crystals_collected = 0
lives = 3

#rocket variables
rocket1_x = 1000
rocket1_y = 250
rocket2_x = 0
rocket2_y = 0
speed = 10

#player variables
player_x = 118
player_y = 551
speed = 5
current_image = idle

#player and rocket rectangles
player_rect = pygame.Rect(player_x, player_y, 160, 160)
rocket_rect = pygame.Rect(rocket1_x, rocket1_y, 135, 250)

#tracks whether the player is close enough to interact
near_rocket = False

#FONTS
title_font = pygame.font.Font("PixeloidSans-Bold.ttf", 100)
button_font = pygame.font.Font("PixeloidSans-Bold.ttf", 30)
task_font = pygame.font.Font("PixeloidSans-Bold.ttf", 26)

#title screen
title = title_font.render("2247", True, GAME_BLUE)
title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))

clock = pygame.time.Clock()

#Game State (basically where the game is at)
game_state = "intro"

new_game_button = pygame.Rect(500, 300, 300, 80)
quit_button = pygame.Rect(500, 400, 300, 80)

# Intro animation variables
fade_alpha = 0
fade_speed = 3
intro_stage = "fade_in"
hold_start = 0

# Current image starts as idle
current_image = idle

#heart/crystal functions
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


#meteor functions
def create_meteor():
    size=random.randint(40,95)
    img=pygame.transform.scale(random.choice(meteor_images),(size,size))
    return {"image":img,"x":random.randint(0,WIDTH-size),"y":random.randint(-700,-50),"speed":random.randint(3,9),"size":size}

for _ in range(NUM_METEORS):
    meteors.append(create_meteor())


#MAIN GAME LOOP
running = True #while the game is running is true...
while running:

#creating new versus load game:

    for event in pygame.event.get(): #checking for events (actions)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.display.set_caption(f"Mouse Position: ({mouse_x}, {mouse_y})")

        if event.type == pygame.QUIT: #if user clicks the close button, end game
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_state == "menu":

                if new_game_button.collidepoint(event.pos):
                    game_state = "story"
                    current_story = 0
                    story_alpha = 0

                elif quit_button.collidepoint(event.pos):
                    running = False

        if event.type == pygame.KEYDOWN:

            #Story screens
            if game_state == "story":

                if event.key == pygame.K_RETURN:
                    current_story += 1
                    story_alpha = 0

                    if current_story >= len(story_images):
                        game_state = "game"

            #Gameplay
            elif game_state == "game":

                #Enter the rocket
                if event.key == pygame.K_e and near_rocket:
                    game_state = "transition"
                    transition_alpha = 0

    #black ominous ahh screen
    screen.fill((0, 0, 0))

    # =========================
    # INTRO
    # =========================
    if game_state == "intro":

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

    #1. MENU
    elif game_state == "menu":

        menu_title = title_font.render("Save Earth: 2247", True, BLUE)
        screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, 220)))

        # Mouse position
        mouse_pos = pygame.mouse.get_pos()

    #Start Game Button
        if new_game_button.collidepoint(mouse_pos):
            start_button = new_game_button.inflate(20, 10)   # Makes button bigger
            start_color = GAME_BLUE                          # Hover color
        else:
            start_button = new_game_button
            start_color = BLUE

        pygame.draw.rect(screen, start_color, start_button, border_radius=20)

        new_text = button_font.render("Start Game", True, WHITE)
        screen.blit(new_text, new_text.get_rect(center=start_button.center))


    #Quit Game Button
        if quit_button.collidepoint(mouse_pos):
            quit_button_draw = quit_button.inflate(20, 10)
            quit_color = GAME_BLUE
        else:
            quit_button_draw = quit_button
            quit_color = RED

        pygame.draw.rect(screen, quit_color, quit_button_draw, border_radius=20)

        quit_text = button_font.render("Quit", True, WHITE)
        screen.blit(quit_text, quit_text.get_rect(center=quit_button_draw.center))

    #2. INTRO STORYYY
    elif game_state == "story":
        story_image = story_images[current_story]

        if story_alpha < 255:
            story_alpha += story_fade_speed

        story_image.set_alpha(story_alpha)

        screen.blit(story_image, (0, 0))

    #3. GAMEPLAY
    elif game_state == "game":

        keys = pygame.key.get_pressed()

        # Character starts as idle each frame
        current_image = idle

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
        player_x = max(OGLEFT_LIMIT, min(player_x, OGRIGHT_LIMIT))
        player_y = max(OGTOP_LIMIT, min(player_y, OGBOTTOM_LIMIT))

        # Update player and rocket rectangles
        player_rect.topleft = (player_x, player_y)
        rocket_rect.topleft = (rocket1_x, rocket1_y)

        # Create a larger interaction area around the rocket
        interaction_rect = rocket_rect.inflate(100, 120)

        # Check if player is near the rocket
        near_rocket = player_rect.colliderect(interaction_rect)

        # Draw Earth background
        screen.blit(background, (0, 0))

        # Draw rocket
        screen.blit(rocket1, (rocket1_x, rocket1_y))

        # Draw player
        screen.blit(current_image, (player_x, player_y))

        # -----------------------------
        # TASK OBJECTIVE
        # -----------------------------
        task_text = task_font.render(
            "Task: Using WASD, head over to your rocket.",
            True,
            WHITE,
        )

        screen.blit(task_text, (25, 20))

        # -----------------------------
        # PLAYER IS CLOSE TO THE ROCKET
        # -----------------------------
        if near_rocket:

            prompt = task_font.render(
                "Press E to enter your rocket",
                True,
                WHITE,
            )

            screen.blit(prompt, (430, 635))

    # 4. EARTH TO MOON FADE TRANSITION
    elif game_state == "transition":
        # Draw the current Earth scene
        screen.blit(background, (0, 0))
        screen.blit(rocket1, (rocket1_x, rocket1_y))
        screen.blit(current_image, (player_x, player_y))

        # Draw the new background over the old one
        earth_to_moon.set_alpha(transition_alpha)
        screen.blit(earth_to_moon, (0, 0))

        # Increase transparency
        transition_alpha += transition_speed

        # Once fully visible, move to the next scene
        if transition_alpha >= 255:
            transition_alpha = 255
            game_state = "rocket_scene"
            transition_timer = pygame.time.get_ticks()

    # 5. EARTH TO MOON SCENE
    elif game_state == "rocket_scene":
        screen.blit(earth_to_moon, (0, 0))

        # Hold this image for 2 seconds
        if pygame.time.get_ticks() - transition_timer > 2000:
            transition_alpha = 0
            game_state = "level1_intro"

    # 6. LEVEL 1 INTRO
    elif game_state == "level1_intro":
        # Draw previous screen
        screen.blit(earth_to_moon, (0, 0))

        # Fade in Level 1 image
        level1_intro.set_alpha(transition_alpha)
        screen.blit(level1_intro, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "moon_transition"

    # 7. HOLD LEVEL 1 SCREEN
    elif game_state == "moon_transition":
        screen.blit(level1_intro, (0, 0))

        # Hold for 3 seconds
        if pygame.time.get_ticks() - transition_timer > 3000:
            transition_alpha = 0

            # Start the Moon level timer
            moon_start_time = pygame.time.get_ticks()
            game_state = "moon_game"

    # 8. MOON GAMEPLAY
    elif game_state == "moon_game":
        # Draw previous screen first
        screen.blit(level1_intro, (0, 0))

        # Fade the Moon background over it
        moon_background.set_alpha(transition_alpha)
        screen.blit(moon_background, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255

        keys = pygame.key.get_pressed()

        # Character starts as idle each frame
        current_image = idle

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

        # Keep player within the Moon level boundaries
        player_x = max(LEFT_LIMIT, min(player_x, RIGHT_LIMIT))
        player_y = max(TOP_LIMIT, min(player_y, BOTTOM_LIMIT))

        #something with collisions:
        player_rect.topleft = (player_x, player_y)

        # Draw the player after updating movement
        screen.blit(current_image, (player_x, player_y))

        # Moon rock positions
        rock_positions = [
            (100, 100),
            (129, 452),
            (538, 24),
            (600, 300),
            (800, 250),
            (1072, 98),
            (1100, 350),
            (500, 450),
            (300, 500),
            (980, 621),
        ]

        # Draw Moon rocks around the map
        for i, position in enumerate(rock_positions):
            if i % 2 == 0:
                screen.blit(mrock1, position)
            else:
                screen.blit(mrock2, position)

        # Timer
        elapsed_time = (pygame.time.get_ticks() - moon_start_time) // 1000
        time_left = max(0, LEVEL_TIME - elapsed_time)

        # Timer is black normally, but turns red with 10 seconds remaining
        if time_left <= 10:
            timer_color = RED
        else:
            timer_color = BLACK

        timer_text = task_font.render(
            f"Time Left: {time_left}",
            True,
            timer_color
        )

        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(timer_text, timer_rect)

        #drawing meteors and like their animation
        for m in meteors:
            m["y"] += m["speed"]
            screen.blit(m["image"], (m["x"], m["y"]))
            
            # Check collision with falling meteor
            meteor_rect = pygame.Rect(m["x"], m["y"], m["size"], m["size"])
            if meteor_rect.colliderect(player_rect):
                if lives > 0:
                    lives -= 1
                m.update(create_meteor())  # Respawn the meteor at the top
            elif m["y"] > HEIGHT:
                m.update(create_meteor())

        # Draw the hearts and crystals
        draw_hearts(screen)
        draw_crystal_hud(screen)

    # Update the screen and limit the game to 60 frames per second
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
