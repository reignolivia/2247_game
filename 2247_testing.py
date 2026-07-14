import pygame

pygame.init() #basically turn pygame on and allow usage

#sizing the window
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save Earth: 2247")  # Window title

#built in colors:
WHITE = (255, 255, 255)
GAME_BLUE = (2,100,147)
BLUE = (95,183,207)
RED = (95,183,207)

#player limits
LEFT_LIMIT = 50
RIGHT_LIMIT = 1150
TOP_LIMIT = 485
BOTTOM_LIMIT = 560

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

# Story screen variables
story_images = [intro1, intro2]
current_story = 0
story_alpha = 0
story_fade_speed = 4

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
                    game_state = "rocket_scene"

    # Draw Everything
    screen.blit(background, (0, 0))

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
        player_x = max(LEFT_LIMIT, min(player_x, RIGHT_LIMIT))
        player_y = max(TOP_LIMIT, min(player_y, BOTTOM_LIMIT))

        # Update player and rocket rectangles
        player_rect.topleft = (player_x, player_y)
        rocket_rect.topleft = (rocket1_x, rocket1_y)

        # Create a larger interaction area around the rocket
        interaction_rect = rocket_rect.inflate(120, 120)

        # Check if player is near the rocket
        near_rocket = player_rect.colliderect(interaction_rect)

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

    #4. Transition from Earth to Moon
    elif game_state == "rocket_scene":

        # Draw the Earth to Moon background
        screen.blit(earth_to_moon, (0, 0))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
