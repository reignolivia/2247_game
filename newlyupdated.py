

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

# Mars rocks used only in Level 2.
mars_rock1 = pygame.image.load("MARS ROCK 1.png").convert_alpha()
mars_rock2 = pygame.image.load("MARS ROCK 2.png").convert_alpha()
mars_rock3 = pygame.image.load("MARS ROCK 3.png").convert_alpha()

mars_rock1 = pygame.transform.scale(mars_rock1, (100, 100))
mars_rock2 = pygame.transform.scale(mars_rock2, (100, 100))
mars_rock3 = pygame.transform.scale(mars_rock3, (100, 100))
mars_rock_images = [mars_rock1, mars_rock2, mars_rock3]

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

# Level 1 has 2 normal meteors.
moon_meteors = []
NUM_MOON_METEORS = 2

# Level 2 has 3 meteors, making them appear a little more often.
mars_meteors = []
NUM_MARS_METEORS = 3

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

# ---------------------------------------------------------
# ROCK LIFTING SYSTEM
# ---------------------------------------------------------
# Rock positions used in the Moon level.
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
    (980, 570),
]

# Each lifted rock is stored by its list index.
lifted_rocks = set()
rock_hold_time = 0
required_hold_time = 2000  # 2 seconds in milliseconds
active_rock_index = None

# Exactly one random rock contains the crystal.
crystal_rock_index = random.randrange(len(rock_positions))
crystal_found = False
crystal_reveal_start = 0
crystal_reveal_duration = 5000  # Show the crystal for 5 seconds
crystal_reveal_position = None
timer_stopped = False
stopped_time_left = LEVEL_TIME

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
def create_meteor(level):
    """Create a meteor with settings based on the current level."""
    if level == 2:
        # Mars meteors are slightly bigger and slightly faster.
        size = random.randint(50, 75)
        meteor_speed = random.randint(4, 10)
        spawn_y = random.randint(-500, -40)
    else:
        # Moon meteors keep the original settings.
        size = random.randint(40, 65)
        meteor_speed = random.randint(3, 9)
        spawn_y = random.randint(-700, -50)

    image = pygame.transform.scale(
        random.choice(meteor_images),
        (size, size),
    )

    return {
        "image": image,
        "x": random.randint(0, WIDTH - size),
        "y": spawn_y,
        "speed": meteor_speed,
        "size": size,
    }


for _ in range(NUM_MOON_METEORS):
    moon_meteors.append(create_meteor(1))

for _ in range(NUM_MARS_METEORS):
    mars_meteors.append(create_meteor(2))



# ---------------------------------------------------------
# LEVEL 2 ASSETS AND TRANSITION SETTINGS
# ---------------------------------------------------------
moon_to_mars = pygame.transform.scale(
    pygame.image.load("moon_to_mars.png"), (WIDTH, HEIGHT)
)
level2_intro = pygame.transform.scale(
    pygame.image.load("level2_intro.png"), (WIDTH, HEIGHT)
)
mars_background = pygame.transform.scale(
    pygame.image.load("mars.png"), (WIDTH, HEIGHT)
)

mars_start_time = 0
current_level = 1
LEVEL_COMPLETE_WAIT = 2000
TRAVEL_HOLD_TIME = 4000
level_complete_start = 0


def reset_rock_search():
    global lifted_rocks, rock_hold_time, active_rock_index
    global crystal_rock_index, crystal_found, crystal_reveal_start
    global crystal_reveal_position, timer_stopped, stopped_time_left

    lifted_rocks.clear()
    rock_hold_time = 0
    active_rock_index = None
    crystal_rock_index = random.randrange(len(rock_positions))
    crystal_found = False
    crystal_reveal_start = 0
    crystal_reveal_position = None
    timer_stopped = False
    stopped_time_left = LEVEL_TIME


def draw_planet_level(level_background, level_start_time):
    global player_x, player_y, current_image, active_rock_index
    global rock_hold_time, crystals_collected, crystal_found
    global crystal_reveal_position, crystal_reveal_start
    global timer_stopped, stopped_time_left, lives
    global level_complete_start, game_state, transition_alpha

    screen.blit(level_background, (0, 0))
    keys = pygame.key.get_pressed()
    current_image = idle

    # Pick Level 1 or Level 2 rocks and meteors.
    if current_level == 2:
        level_rock_images = mars_rock_images
        level_meteors = mars_meteors
        meteor_level = 2
    else:
        level_rock_images = [mrock1, mrock2]
        level_meteors = moon_meteors
        meteor_level = 1

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

    player_x = max(LEFT_LIMIT, min(player_x, RIGHT_LIMIT))
    player_y = max(TOP_LIMIT, min(player_y, BOTTOM_LIMIT))
    player_rect.topleft = (player_x, player_y)
    screen.blit(current_image, (player_x, player_y))

    active_rock_index = None
    closest_distance = float("inf")

    for i, position in enumerate(rock_positions):
        if i in lifted_rocks:
            continue

        # Cycle through the available rock images for this planet.
        rock_image_to_draw = level_rock_images[i % len(level_rock_images)]
        screen.blit(rock_image_to_draw, position)
        rock_rect = pygame.Rect(position[0], position[1], 100, 100)

        if player_rect.colliderect(rock_rect.inflate(80, 80)):
            distance = (
                (player_rect.centerx - rock_rect.centerx) ** 2
                + (player_rect.centery - rock_rect.centery) ** 2
            ) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                active_rock_index = i

    if active_rock_index is not None and not crystal_found:
        prompt = task_font.render(
            "Hold E for 2 seconds to lift the rock", True, WHITE
        )
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 35)))

        if keys[pygame.K_e]:
            rock_hold_time += clock.get_time()
            bar_width, bar_height = 300, 22
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = HEIGHT - 75
            progress = min(1, rock_hold_time / required_hold_time)
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
            pygame.draw.rect(
                screen, WHITE,
                (bar_x + 2, bar_y + 2, int((bar_width - 4) * progress), bar_height - 4)
            )

            if rock_hold_time >= required_hold_time:
                lifted_rock = active_rock_index
                lifted_rocks.add(lifted_rock)
                rock_hold_time = 0

                if lifted_rock == crystal_rock_index:
                    crystal_found = True
                    crystals_collected = min(3, crystals_collected + 1)
                    rock_x, rock_y = rock_positions[lifted_rock]
                    crystal_reveal_position = (rock_x, rock_y)
                    crystal_reveal_start = pygame.time.get_ticks()
                    elapsed = (pygame.time.get_ticks() - level_start_time) // 1000
                    stopped_time_left = max(0, LEVEL_TIME - elapsed)
                    timer_stopped = True
                    level_complete_start = pygame.time.get_ticks()
        else:
            rock_hold_time = 0
    else:
        rock_hold_time = 0

    if (
        crystal_found
        and crystal_reveal_position is not None
        and pygame.time.get_ticks() - crystal_reveal_start < LEVEL_COMPLETE_WAIT
    ):
        big_crystal = pygame.transform.scale(crystal_full, (150, 150))
        screen.blit(big_crystal, crystal_reveal_position)

    if timer_stopped:
        time_left = stopped_time_left
    else:
        elapsed = (pygame.time.get_ticks() - level_start_time) // 1000
        time_left = max(0, LEVEL_TIME - elapsed)

    timer_color = RED if time_left <= 10 else BLACK
    timer_text = task_font.render(f"Time Left: {time_left}", True, timer_color)
    screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, 30)))

    for meteor in level_meteors:
        meteor["y"] += meteor["speed"]
        screen.blit(meteor["image"], (meteor["x"], meteor["y"]))

        meteor_rect = pygame.Rect(
            meteor["x"],
            meteor["y"],
            meteor["size"],
            meteor["size"],
        )

        if meteor_rect.colliderect(player_rect):
            if lives > 0:
                lives -= 1
            meteor.update(create_meteor(meteor_level))
        elif meteor["y"] > HEIGHT:
            meteor.update(create_meteor(meteor_level))

    draw_hearts(screen)
    draw_crystal_hud(screen)

    if (
        current_level == 1
        and crystal_found
        and pygame.time.get_ticks() - level_complete_start >= LEVEL_COMPLETE_WAIT
    ):
        transition_alpha = 0
        game_state = "moon_to_mars_fade"


# ---------------------------------------------------------
# MAIN GAME LOOP
# ---------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "menu":
            if new_game_button.collidepoint(event.pos):
                game_state = "story"
                current_story = 0
                story_alpha = 0
            elif quit_button.collidepoint(event.pos):
                running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "story" and event.key == pygame.K_RETURN:
                current_story += 1
                story_alpha = 0
                if current_story >= len(story_images):
                    game_state = "game"
            elif game_state == "game" and event.key == pygame.K_e and near_rocket:
                transition_alpha = 0
                game_state = "earth_to_moon_fade"

    screen.fill(BLACK)

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

    elif game_state == "menu":
        menu_title = title_font.render("Save Earth: 2247", True, BLUE)
        screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, 220)))
        mouse_pos = pygame.mouse.get_pos()
        start_button = new_game_button.inflate(20, 10) if new_game_button.collidepoint(mouse_pos) else new_game_button
        start_color = GAME_BLUE if new_game_button.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(screen, start_color, start_button, border_radius=20)
        new_text = button_font.render("Start Game", True, WHITE)
        screen.blit(new_text, new_text.get_rect(center=start_button.center))
        quit_draw = quit_button.inflate(20, 10) if quit_button.collidepoint(mouse_pos) else quit_button
        quit_color = GAME_BLUE if quit_button.collidepoint(mouse_pos) else RED
        pygame.draw.rect(screen, quit_color, quit_draw, border_radius=20)
        quit_text = button_font.render("Quit", True, WHITE)
        screen.blit(quit_text, quit_text.get_rect(center=quit_draw.center))

    elif game_state == "story":
        story_image = story_images[current_story]
        story_alpha = min(255, story_alpha + story_fade_speed)
        story_image.set_alpha(story_alpha)
        screen.blit(story_image, (0, 0))

    elif game_state == "game":
        keys = pygame.key.get_pressed()
        current_image = idle
        if keys[pygame.K_d]:
            player_x += speed
            current_image = walk_right
        elif keys[pygame.K_a]:
            player_x -= speed
            current_image = walk_left
        if keys[pygame.K_w]: player_y -= speed
        if keys[pygame.K_s]: player_y += speed
        player_x = max(OGLEFT_LIMIT, min(player_x, OGRIGHT_LIMIT))
        player_y = max(OGTOP_LIMIT, min(player_y, OGBOTTOM_LIMIT))
        player_rect.topleft = (player_x, player_y)
        rocket_rect.topleft = (rocket1_x, rocket1_y)
        near_rocket = player_rect.colliderect(rocket_rect.inflate(100, 120))
        screen.blit(background, (0, 0))
        screen.blit(rocket1, (rocket1_x, rocket1_y))
        screen.blit(current_image, (player_x, player_y))
        task_text = task_font.render("Task: Using WASD, head over to your rocket.", True, WHITE)
        screen.blit(task_text, (25, 20))
        if near_rocket:
            prompt = task_font.render("Press E to enter your rocket", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 650)))

    elif game_state == "earth_to_moon_fade":
        screen.blit(background, (0, 0))
        screen.blit(rocket1, (rocket1_x, rocket1_y))
        screen.blit(current_image, (player_x, player_y))
        earth_to_moon.set_alpha(transition_alpha)
        screen.blit(earth_to_moon, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "earth_to_moon_hold"

    elif game_state == "earth_to_moon_hold":
        screen.blit(earth_to_moon, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= 2000:
            transition_alpha = 0
            game_state = "level1_intro"

    elif game_state == "level1_intro":
        screen.blit(earth_to_moon, (0, 0))
        level1_intro.set_alpha(transition_alpha)
        screen.blit(level1_intro, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "level1_intro_hold"

    elif game_state == "level1_intro_hold":
        screen.blit(level1_intro, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= 3000:
            player_x, player_y = 50, 450
            crystals_collected = 0
            current_level = 1
            reset_rock_search()
            moon_start_time = pygame.time.get_ticks()
            game_state = "moon_game"

    elif game_state == "moon_game":
        draw_planet_level(moon_background, moon_start_time)

    elif game_state == "moon_to_mars_fade":
        # No heart HUD, crystal HUD, or timer is drawn during this transition.
        screen.blit(moon_background, (0, 0))
        screen.blit(current_image, (player_x, player_y))
        moon_to_mars.set_alpha(transition_alpha)
        screen.blit(moon_to_mars, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "moon_to_mars_hold"

    elif game_state == "moon_to_mars_hold":
        screen.blit(moon_to_mars, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= TRAVEL_HOLD_TIME:
            transition_alpha = 0
            game_state = "level2_intro"

    elif game_state == "level2_intro":
        screen.blit(moon_to_mars, (0, 0))
        level2_intro.set_alpha(transition_alpha)
        screen.blit(level2_intro, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "level2_intro_hold"

    elif game_state == "level2_intro_hold":
        screen.blit(level2_intro, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= 3000:
            player_x, player_y = 50, 450
            lives = 3
            current_level = 2
            reset_rock_search()
            mars_start_time = pygame.time.get_ticks()
            game_state = "mars_game"

    elif game_state == "mars_game":
        draw_planet_level(mars_background, mars_start_time)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

Library

save_earth_moon_to_mars_fixed.py


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
NUM_METEORS = 2

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

# ---------------------------------------------------------
# ROCK LIFTING SYSTEM
# ---------------------------------------------------------
# Rock positions used in the Moon level.
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
    (980, 570),
]

# Each lifted rock is stored by its list index.
lifted_rocks = set()
rock_hold_time = 0
required_hold_time = 2000  # 2 seconds in milliseconds
active_rock_index = None

# Exactly one random rock contains the crystal.
crystal_rock_index = random.randrange(len(rock_positions))
crystal_found = False
crystal_reveal_start = 0
crystal_reveal_duration = 5000  # Show the crystal for 5 seconds
crystal_reveal_position = None
timer_stopped = False
stopped_time_left = LEVEL_TIME

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
    size=random.randint(40,65)
    img=pygame.transform.scale(random.choice(meteor_images),(size,size))
    return {"image":img,"x":random.randint(0,WIDTH-size),"y":random.randint(-700,-50),"speed":random.randint(3,9),"size":size}

for _ in range(NUM_METEORS):
    meteors.append(create_meteor())



# ---------------------------------------------------------
# LEVEL 2 ASSETS AND TRANSITION SETTINGS
# ---------------------------------------------------------
moon_to_mars = pygame.transform.scale(
    pygame.image.load("moon_to_mars.png"), (WIDTH, HEIGHT)
)
level2_intro = pygame.transform.scale(
    pygame.image.load("level2_intro.png"), (WIDTH, HEIGHT)
)
mars_background = pygame.transform.scale(
    pygame.image.load("mars.png"), (WIDTH, HEIGHT)
)

mars_start_time = 0
current_level = 1
LEVEL_COMPLETE_WAIT = 2000
TRAVEL_HOLD_TIME = 4000
level_complete_start = 0


def reset_rock_search():
    global lifted_rocks, rock_hold_time, active_rock_index
    global crystal_rock_index, crystal_found, crystal_reveal_start
    global crystal_reveal_position, timer_stopped, stopped_time_left

    lifted_rocks.clear()
    rock_hold_time = 0
    active_rock_index = None
    crystal_rock_index = random.randrange(len(rock_positions))
    crystal_found = False
    crystal_reveal_start = 0
    crystal_reveal_position = None
    timer_stopped = False
    stopped_time_left = LEVEL_TIME


def draw_planet_level(level_background, level_start_time):
    global player_x, player_y, current_image, active_rock_index
    global rock_hold_time, crystals_collected, crystal_found
    global crystal_reveal_position, crystal_reveal_start
    global timer_stopped, stopped_time_left, lives
    global level_complete_start, game_state, transition_alpha

    screen.blit(level_background, (0, 0))
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

    player_x = max(LEFT_LIMIT, min(player_x, RIGHT_LIMIT))
    player_y = max(TOP_LIMIT, min(player_y, BOTTOM_LIMIT))
    player_rect.topleft = (player_x, player_y)
    screen.blit(current_image, (player_x, player_y))

    active_rock_index = None
    closest_distance = float("inf")

    for i, position in enumerate(rock_positions):
        if i in lifted_rocks:
            continue

        rock_image_to_draw = mrock1 if i % 2 == 0 else mrock2
        screen.blit(rock_image_to_draw, position)
        rock_rect = pygame.Rect(position[0], position[1], 100, 100)

        if player_rect.colliderect(rock_rect.inflate(80, 80)):
            distance = (
                (player_rect.centerx - rock_rect.centerx) ** 2
                + (player_rect.centery - rock_rect.centery) ** 2
            ) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                active_rock_index = i

    if active_rock_index is not None and not crystal_found:
        prompt = task_font.render(
            "Hold E for 2 seconds to lift the rock", True, WHITE
        )
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 35)))

        if keys[pygame.K_e]:
            rock_hold_time += clock.get_time()
            bar_width, bar_height = 300, 22
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = HEIGHT - 75
            progress = min(1, rock_hold_time / required_hold_time)
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
            pygame.draw.rect(
                screen, WHITE,
                (bar_x + 2, bar_y + 2, int((bar_width - 4) * progress), bar_height - 4)
            )

            if rock_hold_time >= required_hold_time:
                lifted_rock = active_rock_index
                lifted_rocks.add(lifted_rock)
                rock_hold_time = 0

                if lifted_rock == crystal_rock_index:
                    crystal_found = True
                    crystals_collected = min(3, crystals_collected + 1)
                    rock_x, rock_y = rock_positions[lifted_rock]
                    crystal_reveal_position = (rock_x, rock_y)
                    crystal_reveal_start = pygame.time.get_ticks()
                    elapsed = (pygame.time.get_ticks() - level_start_time) // 1000
                    stopped_time_left = max(0, LEVEL_TIME - elapsed)
                    timer_stopped = True
                    level_complete_start = pygame.time.get_ticks()
        else:
            rock_hold_time = 0
    else:
        rock_hold_time = 0

    if (
        crystal_found
        and crystal_reveal_position is not None
        and pygame.time.get_ticks() - crystal_reveal_start < LEVEL_COMPLETE_WAIT
    ):
        big_crystal = pygame.transform.scale(crystal_full, (150, 150))
        screen.blit(big_crystal, crystal_reveal_position)

    if timer_stopped:
        time_left = stopped_time_left
    else:
        elapsed = (pygame.time.get_ticks() - level_start_time) // 1000
        time_left = max(0, LEVEL_TIME - elapsed)

    timer_color = RED if time_left <= 10 else BLACK
    timer_text = task_font.render(f"Time Left: {time_left}", True, timer_color)
    screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, 30)))

    for meteor in meteors:
        meteor["y"] += meteor["speed"]
        screen.blit(meteor["image"], (meteor["x"], meteor["y"]))
        meteor_rect = pygame.Rect(
            meteor["x"], meteor["y"], meteor["size"], meteor["size"]
        )
        if meteor_rect.colliderect(player_rect):
            if lives > 0:
                lives -= 1
            meteor.update(create_meteor())
        elif meteor["y"] > HEIGHT:
            meteor.update(create_meteor())

    draw_hearts(screen)
    draw_crystal_hud(screen)

    if (
        current_level == 1
        and crystal_found
        and pygame.time.get_ticks() - level_complete_start >= LEVEL_COMPLETE_WAIT
    ):
        transition_alpha = 0
        game_state = "moon_to_mars_fade"


# ---------------------------------------------------------
# MAIN GAME LOOP
# ---------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "menu":
            if new_game_button.collidepoint(event.pos):
                game_state = "story"
                current_story = 0
                story_alpha = 0
            elif quit_button.collidepoint(event.pos):
                running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "story" and event.key == pygame.K_RETURN:
                current_story += 1
                story_alpha = 0
                if current_story >= len(story_images):
                    game_state = "game"
            elif game_state == "game" and event.key == pygame.K_e and near_rocket:
                transition_alpha = 0
                game_state = "earth_to_moon_fade"

    screen.fill(BLACK)

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

    elif game_state == "menu":
        menu_title = title_font.render("Save Earth: 2247", True, BLUE)
        screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, 220)))
        mouse_pos = pygame.mouse.get_pos()
        start_button = new_game_button.inflate(20, 10) if new_game_button.collidepoint(mouse_pos) else new_game_button
        start_color = GAME_BLUE if new_game_button.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(screen, start_color, start_button, border_radius=20)
        new_text = button_font.render("Start Game", True, WHITE)
        screen.blit(new_text, new_text.get_rect(center=start_button.center))
        quit_draw = quit_button.inflate(20, 10) if quit_button.collidepoint(mouse_pos) else quit_button
        quit_color = GAME_BLUE if quit_button.collidepoint(mouse_pos) else RED
        pygame.draw.rect(screen, quit_color, quit_draw, border_radius=20)
        quit_text = button_font.render("Quit", True, WHITE)
        screen.blit(quit_text, quit_text.get_rect(center=quit_draw.center))

    elif game_state == "story":
        story_image = story_images[current_story]
        story_alpha = min(255, story_alpha + story_fade_speed)
        story_image.set_alpha(story_alpha)
        screen.blit(story_image, (0, 0))

    elif game_state == "game":
        keys = pygame.key.get_pressed()
        current_image = idle
        if keys[pygame.K_d]:
            player_x += speed
            current_image = walk_right
        elif keys[pygame.K_a]:
            player_x -= speed
            current_image = walk_left
        if keys[pygame.K_w]: player_y -= speed
        if keys[pygame.K_s]: player_y += speed
        player_x = max(OGLEFT_LIMIT, min(player_x, OGRIGHT_LIMIT))
        player_y = max(OGTOP_LIMIT, min(player_y, OGBOTTOM_LIMIT))
        player_rect.topleft = (player_x, player_y)
        rocket_rect.topleft = (rocket1_x, rocket1_y)
        near_rocket = player_rect.colliderect(rocket_rect.inflate(100, 120))
        screen.blit(background, (0, 0))
        screen.blit(rocket1, (rocket1_x, rocket1_y))
        screen.blit(current_image, (player_x, player_y))
        task_text = task_font.render("Task: Using WASD, head over to your rocket.", True, WHITE)
        screen.blit(task_text, (25, 20))
        if near_rocket:
            prompt = task_font.render("Press E to enter your rocket", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 650)))

    elif game_state == "earth_to_moon_fade":
        screen.blit(background, (0, 0))
        screen.blit(rocket1, (rocket1_x, rocket1_y))
        screen.blit(current_image, (player_x, player_y))
        earth_to_moon.set_alpha(transition_alpha)
        screen.blit(earth_to_moon, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "earth_to_moon_hold"

    elif game_state == "earth_to_moon_hold":
        screen.blit(earth_to_moon, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= 2000:
            transition_alpha = 0
            game_state = "level1_intro"

    elif game_state == "level1_intro":
        screen.blit(earth_to_moon, (0, 0))
        level1_intro.set_alpha(transition_alpha)
        screen.blit(level1_intro, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "level1_intro_hold"

    elif game_state == "level1_intro_hold":
        screen.blit(level1_intro, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= 3000:
            player_x, player_y = 50, 450
            crystals_collected = 0
            current_level = 1
            reset_rock_search()
            moon_start_time = pygame.time.get_ticks()
            game_state = "moon_game"

    elif game_state == "moon_game":
        draw_planet_level(moon_background, moon_start_time)

    elif game_state == "moon_to_mars_fade":
        # No heart HUD, crystal HUD, or timer is drawn during this transition.
        screen.blit(moon_background, (0, 0))
        screen.blit(current_image, (player_x, player_y))
        moon_to_mars.set_alpha(transition_alpha)
        screen.blit(moon_to_mars, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "moon_to_mars_hold"

    elif game_state == "moon_to_mars_hold":
        screen.blit(moon_to_mars, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= TRAVEL_HOLD_TIME:
            transition_alpha = 0
            game_state = "level2_intro"

    elif game_state == "level2_intro":
        screen.blit(moon_to_mars, (0, 0))
        level2_intro.set_alpha(transition_alpha)
        screen.blit(level2_intro, (0, 0))
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "level2_intro_hold"

    elif game_state == "level2_intro_hold":
        screen.blit(level2_intro, (0, 0))
        if pygame.time.get_ticks() - transition_timer >= 3000:
            player_x, player_y = 50, 450
            current_level = 2
            reset_rock_search()
            mars_start_time = pygame.time.get_ticks()
            game_state = "mars_game"

    elif game_state == "mars_game":
        draw_planet_level(mars_background, mars_start_time)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
