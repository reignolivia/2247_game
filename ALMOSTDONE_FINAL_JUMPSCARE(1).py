import os
import csv
import pygame
import random

pygame.init()  # basically turn pygame on and allow usage
pygame.mixer.init()  # allows for background music
pygame.mixer.init()

# =========================================================
# FILE/FOLDER SETUP
# =========================================================

# Folder containing this Python file
folder = os.path.dirname(os.path.abspath(__file__))

# Player statistics CSV saved beside this Python file
STATS_CSV_NAME = "player_stats.csv"
stats_csv_path = os.path.join(folder, STATS_CSV_NAME)

player_name = ""
name_input = ""
name_error = ""
death_count = 0
level_times = {1: None, 2: None, 3: None}


def asset_path(filename):
    """Creates the complete path to an image, font, or music file."""
    return os.path.join(folder, filename)


current_music = None


def change_music(filename, loop=True, volume=0.5):
    """Changes music only when a different track is requested."""
    global current_music

    # Do not restart the same song every frame
    if current_music == filename:
        return

    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_path(filename))
    pygame.mixer.music.set_volume(volume)

    if loop:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play(0)

    current_music = filename


def normalize_player_name(raw_name):
    """Remove extra spaces and format the name."""
    cleaned = " ".join(raw_name.split())

    if not cleaned:
        return None, "Please enter a name."

    # Fewer than 12 characters: maximum length is 11.
    if len(cleaned) >= 12:
        return None, "Name must be fewer than 12 characters."

    if not all(character.isalpha() or character == " " for character in cleaned):
        return None, "Please use letters and spaces only."

    return cleaned[0].upper() + cleaned[1:].lower(), ""


def save_player_stats():
    """Replace this player's previous CSV row with the newest run."""
    if not player_name:
        return

    fieldnames = [
        "Name",
        "Moon_Time_Seconds",
        "Mars_Time_Seconds",
        "Saturn_Time_Seconds",
        "Deaths",
    ]

    rows = []

    if os.path.exists(stats_csv_path):
        try:
            with open(stats_csv_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                rows = [
                    row for row in reader
                    if row.get("Name", "").casefold() != player_name.casefold()
                ]
        except (OSError, csv.Error):
            rows = []

    rows.append({
        "Name": player_name,
        "Moon_Time_Seconds": (
            "" if level_times.get(1) is None else int(level_times[1])
        ),
        "Mars_Time_Seconds": (
            "" if level_times.get(2) is None else int(level_times[2])
        ),
        "Saturn_Time_Seconds": (
            "" if level_times.get(3) is None else int(level_times[3])
        ),
        "Deaths": int(death_count),
    })

    with open(stats_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def begin_player_run(formatted_name):
    """Begin a new run and replace older data for this name."""
    global player_name, death_count, level_times
    global player_x, player_y, current_image, game_state

    player_name = formatted_name
    death_count = 0
    level_times = {1: None, 2: None, 3: None}

    player_x = 118
    player_y = 551
    sync_player_hitbox()
    current_image = idle
    game_state = "game"

    save_player_stats()


def record_death():
    global death_count
    death_count += 1
    save_player_stats()


def record_level_completion(level_number):
    """Record the elapsed seconds for one specific level."""
    elapsed_seconds = max(
        0,
        (pygame.time.get_ticks() - moon_start_time) // 1000,
    )

    level_times[level_number] = elapsed_seconds
    save_player_stats()

    # Useful confirmation in Terminal while testing.
    level_names = {
        1: "Moon",
        2: "Mars",
        3: "Saturn",
    }
    print(
        f"Saved {level_names[level_number]} time: "
        f"{elapsed_seconds} seconds to {stats_csv_path}"
    )

    return elapsed_seconds


# music files

OPENING_MUSIC = "instructions&levelscreensmusic.mp3"
MOON_MUSIC = "moonmusic.mp3"
MARS_MUSIC = "marsmusic.mp3"
SATURN_MUSIC = "saturnmusic.mp3"
DEATH_MUSIC = "deathscreenmusic.mp3"
FINAL_MUSIC = "finalcutscenemusic.mp3"
JUMPSCARE_MUSIC = "NEWJUMPSCARE.mp3"
YAY_MUSIC = "YAY.mp3"

# sizing the window
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save Earth: 2247")  # Window title

# built in colors:
WHITE = (255, 255, 255)
GAME_BLUE = (2, 100, 147)
BLUE = (95, 183, 207)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Health/Stamina (HUD) bar sizing (shared by hearts + crystals so they match)
HUD_SIZE = 50
HUD_SPACING = 10
HUD_MARGIN = 15

# player limits for og screen
OGLEFT_LIMIT = 50
OGRIGHT_LIMIT = 1190
OGTOP_LIMIT = 485
OGBOTTOM_LIMIT = 560

# player limits for all other levels
LEFT_LIMIT = 0
RIGHT_LIMIT = 1100
TOP_LIMIT = 0
BOTTOM_LIMIT = 505

# Load and resize the background image
background = pygame.image.load("2247_earth.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# start music
change_music(OPENING_MUSIC)

# Earth to Moon background
earth_to_moon = pygame.image.load("earth_to_moon.png")
earth_to_moon = pygame.transform.scale(earth_to_moon, (WIDTH, HEIGHT))

# intro images
intro1 = pygame.image.load("Intro1.png")
intro2 = pygame.image.load("Intro2.png")

intro1 = pygame.transform.scale(intro1, (WIDTH, HEIGHT))
intro2 = pygame.transform.scale(intro2, (WIDTH, HEIGHT))

level1_intro = pygame.image.load("level1_intro.png")
level1_intro = pygame.transform.scale(level1_intro, (WIDTH, HEIGHT))

# Level 2 intro and Mars background
level2_intro = pygame.image.load("level2_intro.png")
level2_intro = pygame.transform.scale(level2_intro, (WIDTH, HEIGHT))

mars_background = pygame.image.load("marsbackground.png")
mars_background = pygame.transform.scale(mars_background, (WIDTH, HEIGHT))

# Moon-to-Mars transition
moon_to_mars = pygame.image.load("moon_to_mars.png")
moon_to_mars = pygame.transform.scale(moon_to_mars, (WIDTH, HEIGHT))

# Level 3 intro, Saturn background, and Mars-to-Saturn transition
level3_intro = pygame.image.load("level3_intro.png")
level3_intro = pygame.transform.scale(level3_intro, (WIDTH, HEIGHT))

saturn_background = pygame.image.load("saturnbackground.png")
saturn_background = pygame.transform.scale(saturn_background, (WIDTH, HEIGHT))

mars_to_saturn = pygame.image.load("mars_to_saturn.png")
mars_to_saturn = pygame.transform.scale(mars_to_saturn, (WIDTH, HEIGHT))

space_rocket_bg = pygame.transform.scale(
    pygame.image.load("spacerocketbg.png"), (WIDTH, HEIGHT)
)
alien_jump_bg = pygame.transform.scale(
    pygame.image.load(asset_path("ALIENJUMP.png")).convert(),
    (WIDTH, HEIGHT),
)

# Scale SAVEDEARTH.png to exactly match the full game window.
saved_earth_bg = pygame.transform.scale(
    pygame.image.load(asset_path("SAVEDEARTH.png")).convert(),
    (WIDTH, HEIGHT),
)
credits1 = pygame.transform.scale(
    pygame.image.load("credits1.png"), (WIDTH, HEIGHT)
)
credits2 = pygame.transform.scale(
    pygame.image.load("credits2.png"), (WIDTH, HEIGHT)
)
credits3 = pygame.transform.scale(
    pygame.image.load("credits3.png"), (WIDTH, HEIGHT)
)

# Level-specific rock images
mrock1 = pygame.image.load(asset_path("moon_rock1.png")).convert_alpha()
mrock2 = pygame.image.load(asset_path("moon_rock2.png")).convert_alpha()
mrock1 = pygame.transform.scale(mrock1, (100, 100))
mrock2 = pygame.transform.scale(mrock2, (100, 100))

mars_rock1 = pygame.image.load(asset_path("MARS ROCK 1.png")).convert_alpha()
mars_rock2 = pygame.image.load(asset_path("MARS ROCK 2.png")).convert_alpha()
mars_rock3 = pygame.image.load(asset_path("MARS ROCK 3.png")).convert_alpha()
mars_rock_images = [
    pygame.transform.scale(mars_rock1, (100, 100)),
    pygame.transform.scale(mars_rock2, (100, 100)),
    pygame.transform.scale(mars_rock3, (100, 100)),
]

saturn_rock1 = pygame.image.load(asset_path("SATURN ROCK 1.png")).convert_alpha()
saturn_rock2 = pygame.image.load(asset_path("SATURN ROCK 2.png")).convert_alpha()
saturn_rock3 = pygame.image.load(asset_path("SATURN ROCK 3.png")).convert_alpha()
saturn_rock_images = [
    pygame.transform.scale(saturn_rock1, (100, 100)),
    pygame.transform.scale(saturn_rock2, (100, 100)),
    pygame.transform.scale(saturn_rock3, (100, 100)),
]

alien_image = pygame.image.load(asset_path("ALIEN.png")).convert_alpha()
alien_image = pygame.transform.scale(alien_image, (100, 100))

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

# Final cutscene timer
cutscene_timer = 0

# Moon timer
LEVEL_TIME = 60
moon_start_time = 0

# moon backgrounds
level1_into = pygame.image.load("level1_intro.png")
moon_background = pygame.image.load("moon.png")
moon_background = pygame.transform.scale(moon_background, (WIDTH, HEIGHT))

# moon rocks (scaled down images used in gameplay)
moon_rock1 = pygame.image.load("moon_rock1.png")
moon_rock2 = pygame.image.load("moon_rock2.png")
moon_rock1 = pygame.transform.scale(moon_rock1, (50, 50))
moon_rock2 = pygame.transform.scale(moon_rock2, (50, 50))

# rockets
rocket1 = pygame.image.load("rocket1.png")
rocket2 = pygame.image.load("rocket2.png")
rocket1 = pygame.transform.scale(rocket1, (135, 250))
rocket2 = pygame.transform.scale(rocket2, (50, 100))

# player images
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
meteor1 = pygame.image.load(asset_path("METEOR 1.png")).convert_alpha()
meteor2 = pygame.image.load(asset_path("METEOR 2.png")).convert_alpha()
meteor_images = [meteor1, meteor2]

# Level 3 uses diamonds instead of normal meteors
diamond1 = pygame.image.load(asset_path("DIAMOND 1.png")).convert_alpha()
diamond2 = pygame.image.load(asset_path("DIAMOND 2.png")).convert_alpha()
diamond_meteor_images = [diamond1, diamond2]

meteors = []
NUM_METEORS = 2

# Ran-out-of-time screen
ran_out_of_time_screen = pygame.image.load("ranoutoftime.png").convert_alpha()
ran_out_of_time_screen = pygame.transform.scale(
    ran_out_of_time_screen, (WIDTH, HEIGHT)
)

# Death screen
death_screen = pygame.image.load("deathscreen.png").convert_alpha()
death_screen = pygame.transform.scale(
    death_screen, (WIDTH, HEIGHT)
)

# heart/crystal variables
crystals_collected = 0
lives = 3

# Prevent one meteor collision from removing multiple hearts instantly
DAMAGE_COOLDOWN = 1200  # milliseconds
last_damage_time = -DAMAGE_COOLDOWN

# rocket variables
rocket1_x = 1000
rocket1_y = 250
rocket2_x = 0
rocket2_y = 0
speed = 10

final_rocket_x = 1000
final_rocket_y = 250
final_near_rocket = False

# player variables
player_x = 118
player_y = 551
speed = 5
current_image = idle

# Smaller collision hitboxes than the visible sprites
PLAYER_HITBOX_WIDTH = 110
PLAYER_HITBOX_HEIGHT = 120
FALLING_HITBOX_SCALE = 0.72
GROUND_ROCK_HITBOX_SIZE = 50

# ---------------------------------------------------------
# ROCK LIFTING SYSTEM DEFINITIONS
# ---------------------------------------------------------
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

# Generate centered, scaled-down collision hitboxes (60x60 pixels) for the rocks
rock_rects = []
hitbox_width = GROUND_ROCK_HITBOX_SIZE
hitbox_height = GROUND_ROCK_HITBOX_SIZE
offset_x = (100 - hitbox_width) // 2
offset_y = (100 - hitbox_height) // 2

for pos in rock_positions:
    shrunk_rect = pygame.Rect(
        pos[0] + offset_x, pos[1] + offset_y, hitbox_width, hitbox_height
    )
    rock_rects.append(shrunk_rect)

# Lifting mechanics variables
lifted_rocks = set()
rock_hold_time = 0
required_hold_time = 2000  # 2 seconds in milliseconds
active_rock_index = None

# Hide the crystal inside one random rock
crystal_rock_index = random.randrange(len(rock_positions))
crystal_found = False
crystal_reveal_start = 0
crystal_reveal_duration = 2000  # Freeze on the crystal for 2 seconds
crystal_reveal_position = None
timer_stopped = False
stopped_time_left = LEVEL_TIME

# Saturn alien stun system
ALIEN_STUN_DURATION = 5000
alien_rock_indices = set()
alien_reveal_positions = {}
stunned_until = 0

# player and rocket rectangles
player_rect = pygame.Rect(
    player_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
    player_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
    PLAYER_HITBOX_WIDTH,
    PLAYER_HITBOX_HEIGHT,
)
rocket_rect = pygame.Rect(rocket1_x, rocket1_y, 135, 250)

# tracks whether the player is close enough to interact
near_rocket = False


def sync_player_hitbox():
    """Center the smaller player hitbox inside the astronaut sprite."""
    player_rect.topleft = (
        player_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
        player_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
    )

# FONTS
title_font = pygame.font.Font("PixeloidSans-Bold.ttf", 100)
button_font = pygame.font.Font("PixeloidSans-Bold.ttf", 30)
task_font = pygame.font.Font("PixeloidSans-Bold.ttf", 26)

# title screen
title = title_font.render("2247", True, GAME_BLUE)
title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))

clock = pygame.time.Clock()

# Game State (basically where the game is at)
game_state = "intro"

# Tracks whether the player is on the Moon or Mars
current_level = 1

new_game_button = pygame.Rect(500, 300, 300, 80)
quit_button = pygame.Rect(500, 400, 300, 80)

# Intro animation variables
fade_alpha = 0
fade_speed = 3
intro_stage = "fade_in"
hold_start = 0

# Current image starts as idle
current_image = idle


# restart screen reset function
def restart_current_level():
    global player_x, player_y, moon_start_time, transition_alpha, current_image, game_state
    global crystals_collected, lives, lifted_rocks, rock_hold_time, crystal_found
    global crystal_reveal_start, crystal_reveal_position, timer_stopped
    global stopped_time_left, crystal_rock_index, last_damage_time
    global alien_rock_indices, alien_reveal_positions, stunned_until

    # Reset player position and image
    player_x = 200
    player_y = 300
    current_image = idle
    sync_player_hitbox()

    # Reset health and level systems
    lives = 3

    # Keep crystals earned from earlier completed levels.
    crystals_collected = current_level - 1
    last_damage_time = -DAMAGE_COOLDOWN
    lifted_rocks.clear()
    rock_hold_time = 0
    crystal_found = False
    crystal_reveal_start = 0
    crystal_reveal_position = None
    timer_stopped = False
    stopped_time_left = LEVEL_TIME
    crystal_rock_index = random.randrange(len(rock_positions))
    alien_reveal_positions.clear()
    stunned_until = 0
    if current_level == 3:
        possible_alien_rocks = [
            i for i in range(len(rock_positions)) if i != crystal_rock_index
        ]
        alien_rock_indices = set(random.sample(possible_alien_rocks, 3))
    else:
        alien_rock_indices = set()

    # Reset meteors above the screen
    meteors.clear()
    for _ in range(NUM_METEORS):
        meteors.append(create_meteor(current_level))

    # Reset visuals and timer
    transition_alpha = 255
    moon_start_time = pygame.time.get_ticks()

    # Restart the level the player was currently on
    if current_level == 1:
        game_state = "moon_game"
        change_music(MOON_MUSIC)

    elif current_level == 2:
        game_state = "mars_game"
        change_music(MARS_MUSIC)

    else:
        game_state = "saturn_game"
        change_music(SATURN_MUSIC)


# heart/crystal functions
def draw_hearts(screen):
    """Draws the player's remaining lives in the bottom-right corner."""
    y = HEIGHT - HUD_SIZE - HUD_MARGIN
    for i in range(lives):
        x = (
            WIDTH
            - HUD_MARGIN
            - (lives - i) * HUD_SIZE
            - (lives - 1 - i) * HUD_SPACING
        )
        screen.blit(heart, (x, y))


def draw_crystal_hud(screen):
    """Draws 3 crystal slots in the bottom-left corner, parallel to hearts."""
    y = HEIGHT - HUD_SIZE - HUD_MARGIN
    for i in range(3):
        x = HUD_MARGIN + i * (HUD_SIZE + HUD_SPACING)
        img = crystal_full if i < crystals_collected else crystal_empty
        screen.blit(img, (x, y))


# meteor functions
def create_meteor(level=None):
    """Creates meteors that get larger and faster each level."""
    if level is None:
        level = current_level

    if level == 1:
        size = random.randint(40, 65)
        fall_speed = random.randint(3, 9)

    elif level == 2:
        size = random.randint(50, 75)
        fall_speed = random.randint(5, 11)

    else:
        size = random.randint(60, 85)
        fall_speed = random.randint(7, 13)

    images_for_level = diamond_meteor_images if level == 3 else meteor_images

    img = pygame.transform.scale(
        random.choice(images_for_level),
        (size, size)
    )

    return {
        "image": img,
        "x": random.randint(0, WIDTH - size),
        "y": random.randint(-700, -50),
        "speed": fall_speed,
        "size": size,
    }


for _ in range(NUM_METEORS):
    meteors.append(create_meteor(1))


# MAIN GAME LOOP
running = True  # while the game is running is true...
while running:

    # creating new versus load game:

    for event in pygame.event.get():  # checking for events (actions)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.display.set_caption(f"Mouse Position: ({mouse_x}, {mouse_y})")

        if event.type == pygame.QUIT:  # if user clicks the close button, end game
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_state == "menu":

                if new_game_button.collidepoint(event.pos):
                    game_state = "story"
                    current_story = 0
                    story_alpha = 0
                    name_input = ""
                    name_error = ""

                elif quit_button.collidepoint(event.pos):
                    running = False

        if event.type == pygame.KEYDOWN:

            # Story screens
            if game_state == "story":

                if event.key == pygame.K_RETURN:
                    current_story += 1
                    story_alpha = 0

                    if current_story >= len(story_images):
                        name_input = ""
                        name_error = ""
                        game_state = "name_entry"

            # Name entry
            elif game_state == "name_entry":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    formatted_name, validation_error = normalize_player_name(
                        name_input
                    )

                    if formatted_name is None:
                        name_error = validation_error
                    else:
                        begin_player_run(formatted_name)

                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                    name_error = ""

                elif event.unicode and event.unicode.isprintable():
                    if len(name_input) < 24:
                        name_input += event.unicode
                        name_error = ""

            # Gameplay
            elif game_state == "game":

                # Enter the rocket
                if event.key == pygame.K_e and near_rocket:
                    game_state = "transition"
                    transition_alpha = 0

            # Ran-out-of-time retry listener
            elif game_state == "ran_out_of_time":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    restart_current_level()

            # Death-screen retry listener
            elif game_state == "death_screen":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    restart_current_level()

            elif game_state == "final_rocket_scene":
                if event.key == pygame.K_e and final_near_rocket:
                    cutscene_timer = pygame.time.get_ticks()
                    change_music(JUMPSCARE_MUSIC, loop=False, volume=1.0)
                    game_state = "alien_jumpscare"

    # black ominous ahh screen
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

    # 1. MENU
    elif game_state == "menu":

        menu_title = title_font.render("Save Earth: 2247", True, BLUE)
        screen.blit(menu_title, menu_title.get_rect(center=(WIDTH // 2, 220)))

        # Mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Start Game Button
        if new_game_button.collidepoint(mouse_pos):
            start_button = new_game_button.inflate(20, 10)  # Makes button bigger
            start_color = GAME_BLUE  # Hover color
        else:
            start_button = new_game_button
            start_color = BLUE

        pygame.draw.rect(screen, start_color, start_button, border_radius=20)

        new_text = button_font.render("Start Game", True, WHITE)
        screen.blit(new_text, new_text.get_rect(center=start_button.center))

        # Quit Game Button
        if quit_button.collidepoint(mouse_pos):
            quit_button_draw = quit_button.inflate(20, 10)
            quit_color = GAME_BLUE
        else:
            quit_button_draw = quit_button
            quit_color = RED

        pygame.draw.rect(screen, quit_color, quit_button_draw, border_radius=20)

        quit_text = button_font.render("Quit", True, WHITE)
        screen.blit(
            quit_text, quit_text.get_rect(center=quit_button_draw.center)
        )

    # 2. INTRO STORYYY
    elif game_state == "story":
        story_image = story_images[current_story]

        if story_alpha < 255:
            story_alpha += story_fade_speed

        story_image.set_alpha(story_alpha)

        screen.blit(story_image, (0, 0))

    # 3. PLAYER NAME ENTRY
    elif game_state == "name_entry":
        screen.blit(background, (0, 0))
        screen.blit(rocket1, (rocket1_x, rocket1_y))
        screen.blit(idle, (118, 551))

        name_title = button_font.render(
            "Enter your name before beginning:",
            True,
            WHITE,
        )
        screen.blit(
            name_title,
            name_title.get_rect(center=(WIDTH // 2, 240)),
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (WIDTH // 2 - 250, 290, 500, 65),
            3,
            border_radius=12,
        )

        displayed_name = name_input if name_input else "_"
        name_surface = button_font.render(displayed_name, True, WHITE)
        screen.blit(
            name_surface,
            name_surface.get_rect(center=(WIDTH // 2, 322)),
        )

        enter_message = task_font.render(
            "Press ENTER to confirm",
            True,
            WHITE,
        )
        screen.blit(
            enter_message,
            enter_message.get_rect(center=(WIDTH // 2, 395)),
        )

        if name_error:
            error_surface = task_font.render(name_error, True, RED)
            screen.blit(
                error_surface,
                error_surface.get_rect(center=(WIDTH // 2, 440)),
            )

    # 4. GAMEPLAY
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
        sync_player_hitbox()
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
        # start Moon music
        change_music(MOON_MUSIC)
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

            # Start the Moon level timer and place the player on the Moon.
            current_level = 1
            moon_start_time = pygame.time.get_ticks()
            player_x = 200
            player_y = 300
            sync_player_hitbox()

            # Reset the rocks and randomly hide the one crystal.
            lifted_rocks.clear()
            rock_hold_time = 0
            crystals_collected = 0
            crystal_found = False
            crystal_reveal_start = 0
            crystal_reveal_position = None
            timer_stopped = False
            stopped_time_left = LEVEL_TIME
            crystal_rock_index = random.randrange(len(rock_positions))

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
        crystal_freeze = crystal_found

        # Character starts as idle each frame
        current_image = idle

        # Store changes to X and Y movement separately for smooth sliding collisions
        dx = 0
        dy = 0

        # Movement keys
        if not crystal_freeze and keys[pygame.K_d]:
            dx += speed
            current_image = walk_right
        elif not crystal_freeze and keys[pygame.K_a]:
            dx -= speed
            current_image = walk_left

        if not crystal_freeze and keys[pygame.K_w]:
            dy -= speed
        if not crystal_freeze and keys[pygame.K_s]:
            dy += speed

        # Handle X-axis movement and wall/rock collisions
        if dx != 0:
            temp_x = max(LEFT_LIMIT, min(player_x + dx, RIGHT_LIMIT))
            temp_rect = pygame.Rect(
                temp_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
                player_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )
            collided = False
            for r_idx, r_rect in enumerate(rock_rects):
                if r_idx in lifted_rocks:
                    continue  # No collisions for rocks that have been lifted!
                if temp_rect.colliderect(r_rect):
                    collided = True
                    break
            if not collided:
                player_x = temp_x

        # Handle Y-axis movement and wall/rock collisions
        if dy != 0:
            temp_y = max(TOP_LIMIT, min(player_y + dy, BOTTOM_LIMIT))
            temp_rect = pygame.Rect(
                player_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
                temp_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )
            collided = False
            for r_idx, r_rect in enumerate(rock_rects):
                if r_idx in lifted_rocks:
                    continue  # No collisions for rocks that have been lifted!
                if temp_rect.colliderect(r_rect):
                    collided = True
                    break
            if not collided:
                player_y = temp_y

        # Sync player's physical hitbox updates
        sync_player_hitbox()

        # Draw player after processing movement
        screen.blit(current_image, (player_x, player_y))

        # Draw unlifted Moon rocks and find the closest interactive rock
        active_rock_index = None
        closest_distance = float("inf")

        for i, position in enumerate(rock_positions):
            if i in lifted_rocks:
                continue

            rock_image_to_draw = mrock1 if i % 2 == 0 else mrock2
            screen.blit(rock_image_to_draw, position)

            # Use the global custom rock rect for interaction checks
            rock_rect = pygame.Rect(
                position[0] + 25,
                position[1] + 25,
                GROUND_ROCK_HITBOX_SIZE,
                GROUND_ROCK_HITBOX_SIZE,
            )
            interaction_rect = rock_rect.inflate(80, 80)

            if player_rect.colliderect(interaction_rect):
                player_center = player_rect.center
                rock_center = rock_rect.center
                distance = (
                    (player_center[0] - rock_center[0]) ** 2
                    + (player_center[1] - rock_center[1]) ** 2
                ) ** 0.5

                if distance < closest_distance:
                    closest_distance = distance
                    active_rock_index = i

        # Hold E to lift mechanics
        if active_rock_index is not None and not crystal_freeze:
            prompt = task_font.render(
                "Hold E for 2 seconds to lift the rock",
                True,
                WHITE,
            )
            screen.blit(
                prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 35))
            )

            if keys[pygame.K_e]:
                rock_hold_time += clock.get_time()

                # Lift Progress Bar
                bar_width = 300
                bar_height = 22
                bar_x = WIDTH // 2 - bar_width // 2
                bar_y = HEIGHT - 75
                progress = min(1, rock_hold_time / required_hold_time)

                pygame.draw.rect(
                    screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2
                )
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        bar_x + 2,
                        bar_y + 2,
                        int((bar_width - 4) * progress),
                        bar_height - 4,
                    ),
                )

                if rock_hold_time >= required_hold_time:
                    lifted_rock = active_rock_index
                    lifted_rocks.add(lifted_rock)
                    rock_hold_time = 0

                    # Check if the lifted rock is hiding the crystal
                    if lifted_rock == crystal_rock_index and not crystal_found:
                        crystal_found = True
                        crystals_collected += 1

                        # Spawning location for revealed crystal
                        rock_x, rock_y = rock_positions[lifted_rock]
                        crystal_reveal_position = (
                            rock_x + 25,
                            rock_y + 25,
                        )
                        crystal_reveal_start = pygame.time.get_ticks()

                        # Stop level countdown
                        elapsed_when_found = record_level_completion(1)
                        stopped_time_left = max(
                            0,
                            LEVEL_TIME - elapsed_when_found,
                        )
                        timer_stopped = True
            else:
                rock_hold_time = 0
        else:
            rock_hold_time = 0

        # Show the revealed crystal (lasts 2 seconds)
        if (
            crystal_found
            and crystal_reveal_position is not None
            and pygame.time.get_ticks() - crystal_reveal_start
            < crystal_reveal_duration
        ):
            big_crystal = pygame.transform.scale(crystal_full, (150, 150))
            screen.blit(big_crystal, crystal_reveal_position)

        # After the Moon crystal has been shown for 2 seconds,
        # move to the Level 2 intro screen.
        if (
            crystal_found
            and crystal_reveal_start > 0
            and pygame.time.get_ticks() - crystal_reveal_start
            >= crystal_reveal_duration
        ):
            current_level = 2
            transition_alpha = 0
            transition_timer = pygame.time.get_ticks()
            game_state = "moon_to_mars_transition"

        # Calculate time left
        if timer_stopped:
            time_left = stopped_time_left
        else:
            elapsed_time = (pygame.time.get_ticks() - moon_start_time) // 1000
            time_left = max(0, LEVEL_TIME - elapsed_time)

        if time_left <= 0:
            record_death()
            game_state = "ran_out_of_time"

        # Timer is black normally, but turns red with 10 seconds remaining
        if time_left <= 10:
            timer_color = RED
        else:
            timer_color = BLACK

        timer_text = task_font.render(
            f"Time Left: {time_left}", True, timer_color
        )

        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(timer_text, timer_rect)

        # drawing meteors and checking collision
        for m in meteors:
            if not crystal_freeze:
                m["y"] += m["speed"]
            screen.blit(m["image"], (m["x"], m["y"]))

            # Check collision with falling meteor
            meteor_hitbox_size = max(
                12,
                int(m["size"] * FALLING_HITBOX_SCALE),
            )
            meteor_rect = pygame.Rect(
                m["x"] + (m["size"] - meteor_hitbox_size) // 2,
                m["y"] + (m["size"] - meteor_hitbox_size) // 2,
                meteor_hitbox_size,
                meteor_hitbox_size,
            )
            if not crystal_freeze and meteor_rect.colliderect(player_rect):
                current_time = pygame.time.get_ticks()

                # Only remove one heart after the damage cooldown has passed
                if current_time - last_damage_time >= DAMAGE_COOLDOWN:
                    lives -= 1
                    last_damage_time = current_time

                    # Show the death screen only after all three hearts are gone
                    if lives == 0:
                        record_death()
                        game_state = "death_screen"
                        break

                # Move the meteor away after a collision
                m.update(create_meteor(current_level))

            elif not crystal_freeze and m["y"] > HEIGHT:
                m.update(create_meteor(current_level))

        # Draw the hearts and crystals
        draw_hearts(screen)
        draw_crystal_hud(screen)

    # 9. MOON-TO-MARS FADE TRANSITION
    elif game_state == "moon_to_mars_transition":
        # Keep Moon music during the travel transition
        change_music(MOON_MUSIC)

        screen.blit(moon_background, (0, 0))

        moon_to_mars.set_alpha(transition_alpha)
        screen.blit(moon_to_mars, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "moon_to_mars_hold"

    # 10. HOLD MOON-TO-MARS TRANSITION
    elif game_state == "moon_to_mars_hold":
        screen.blit(moon_to_mars, (0, 0))

        if pygame.time.get_ticks() - transition_timer > 2000:
            transition_alpha = 0
            game_state = "level2_intro"

    # 11. LEVEL 2 INTRO
    elif game_state == "level2_intro":
        change_music(MARS_MUSIC)

        # Fade the Level 2 page over the Moon background
        screen.blit(moon_background, (0, 0))
        level2_intro.set_alpha(transition_alpha)
        screen.blit(level2_intro, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "mars_transition"

    # 12. HOLD LEVEL 2 SCREEN
    elif game_state == "mars_transition":
        screen.blit(level2_intro, (0, 0))

        # Hold the Level 2 page for 3 seconds
        if pygame.time.get_ticks() - transition_timer > 3000:
            current_level = 2
            transition_alpha = 0

            # Reset the player and all shared level systems
            player_x = 200
            player_y = 300
            sync_player_hitbox()
            current_image = idle

            lives = 3
            crystals_collected = 1
            last_damage_time = -DAMAGE_COOLDOWN
            lifted_rocks.clear()
            rock_hold_time = 0
            crystal_found = False
            crystal_reveal_start = 0
            crystal_reveal_position = None
            timer_stopped = False
            stopped_time_left = LEVEL_TIME
            crystal_rock_index = random.randrange(len(rock_positions))

            meteors.clear()
            for _ in range(NUM_METEORS):
                meteors.append(create_meteor(2))

            moon_start_time = pygame.time.get_ticks()
            game_state = "mars_game"

    # 13. MARS GAMEPLAY
    elif game_state == "mars_game":
        # Draw previous screen first
        screen.blit(level2_intro, (0, 0))

        # Fade the Moon background over it
        mars_background.set_alpha(transition_alpha)
        screen.blit(mars_background, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255

        keys = pygame.key.get_pressed()
        crystal_freeze = crystal_found

        # Character starts as idle each frame
        current_image = idle

        # Store changes to X and Y movement separately for smooth sliding collisions
        dx = 0
        dy = 0

        # Movement keys
        if not crystal_freeze and keys[pygame.K_d]:
            dx += speed
            current_image = walk_right
        elif not crystal_freeze and keys[pygame.K_a]:
            dx -= speed
            current_image = walk_left

        if not crystal_freeze and keys[pygame.K_w]:
            dy -= speed
        if not crystal_freeze and keys[pygame.K_s]:
            dy += speed

        # Handle X-axis movement and wall/rock collisions
        if dx != 0:
            temp_x = max(LEFT_LIMIT, min(player_x + dx, RIGHT_LIMIT))
            temp_rect = pygame.Rect(
                temp_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
                player_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )
            collided = False
            for r_idx, r_rect in enumerate(rock_rects):
                if r_idx in lifted_rocks:
                    continue  # No collisions for rocks that have been lifted!
                if temp_rect.colliderect(r_rect):
                    collided = True
                    break
            if not collided:
                player_x = temp_x

        # Handle Y-axis movement and wall/rock collisions
        if dy != 0:
            temp_y = max(TOP_LIMIT, min(player_y + dy, BOTTOM_LIMIT))
            temp_rect = pygame.Rect(
                player_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
                temp_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )
            collided = False
            for r_idx, r_rect in enumerate(rock_rects):
                if r_idx in lifted_rocks:
                    continue  # No collisions for rocks that have been lifted!
                if temp_rect.colliderect(r_rect):
                    collided = True
                    break
            if not collided:
                player_y = temp_y

        # Sync player's physical hitbox updates
        sync_player_hitbox()

        # Draw player after processing movement
        screen.blit(current_image, (player_x, player_y))

        # Draw unlifted Mars rocks and find the closest interactive rock
        active_rock_index = None
        closest_distance = float("inf")

        for i, position in enumerate(rock_positions):
            if i in lifted_rocks:
                continue

            rock_image_to_draw = mars_rock_images[i % len(mars_rock_images)]
            screen.blit(rock_image_to_draw, position)

            # Use the global custom rock rect for interaction checks
            rock_rect = pygame.Rect(
                position[0] + 25,
                position[1] + 25,
                GROUND_ROCK_HITBOX_SIZE,
                GROUND_ROCK_HITBOX_SIZE,
            )
            interaction_rect = rock_rect.inflate(80, 80)

            if player_rect.colliderect(interaction_rect):
                player_center = player_rect.center
                rock_center = rock_rect.center
                distance = (
                    (player_center[0] - rock_center[0]) ** 2
                    + (player_center[1] - rock_center[1]) ** 2
                ) ** 0.5

                if distance < closest_distance:
                    closest_distance = distance
                    active_rock_index = i

        # Hold E to lift mechanics
        if active_rock_index is not None and not crystal_freeze:
            prompt = task_font.render(
                "Hold E for 2 seconds to lift the rock",
                True,
                WHITE,
            )
            screen.blit(
                prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 35))
            )

            if keys[pygame.K_e]:
                rock_hold_time += clock.get_time()

                # Lift Progress Bar
                bar_width = 300
                bar_height = 22
                bar_x = WIDTH // 2 - bar_width // 2
                bar_y = HEIGHT - 75
                progress = min(1, rock_hold_time / required_hold_time)

                pygame.draw.rect(
                    screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2
                )
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        bar_x + 2,
                        bar_y + 2,
                        int((bar_width - 4) * progress),
                        bar_height - 4,
                    ),
                )

                if rock_hold_time >= required_hold_time:
                    lifted_rock = active_rock_index
                    lifted_rocks.add(lifted_rock)
                    rock_hold_time = 0

                    # Check if the lifted rock is hiding the crystal
                    if lifted_rock == crystal_rock_index and not crystal_found:
                        crystal_found = True
                        crystals_collected += 1

                        # Spawning location for revealed crystal
                        rock_x, rock_y = rock_positions[lifted_rock]
                        crystal_reveal_position = (
                            rock_x + 25,
                            rock_y + 25,
                        )
                        crystal_reveal_start = pygame.time.get_ticks()

                        # Stop level countdown
                        elapsed_when_found = record_level_completion(2)
                        stopped_time_left = max(
                            0,
                            LEVEL_TIME - elapsed_when_found,
                        )
                        timer_stopped = True
            else:
                rock_hold_time = 0
        else:
            rock_hold_time = 0

        # Show the revealed crystal (lasts 2 seconds)
        if (
            crystal_found
            and crystal_reveal_position is not None
            and pygame.time.get_ticks() - crystal_reveal_start
            < crystal_reveal_duration
        ):
            big_crystal = pygame.transform.scale(crystal_full, (150, 150))
            screen.blit(big_crystal, crystal_reveal_position)

        # After the Mars crystal has been shown for 2 seconds,
        # move to the Mars-to-Saturn transition.
        if (
            crystal_found
            and crystal_reveal_start > 0
            and pygame.time.get_ticks() - crystal_reveal_start
            >= crystal_reveal_duration
        ):
            current_level = 3
            transition_alpha = 0
            transition_timer = pygame.time.get_ticks()
            game_state = "mars_to_saturn_transition"

        # Calculate time left
        if timer_stopped:
            time_left = stopped_time_left
        else:
            elapsed_time = (pygame.time.get_ticks() - moon_start_time) // 1000
            time_left = max(0, LEVEL_TIME - elapsed_time)

        if time_left <= 0:
            record_death()
            game_state = "ran_out_of_time"

        # Timer is black normally, but turns red with 10 seconds remaining
        if time_left <= 10:
            timer_color = RED
        else:
            timer_color = BLACK

        timer_text = task_font.render(
            f"Time Left: {time_left}", True, timer_color
        )

        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(timer_text, timer_rect)

        # drawing meteors and checking collision
        for m in meteors:
            if not crystal_freeze:
                m["y"] += m["speed"]
            screen.blit(m["image"], (m["x"], m["y"]))

            # Check collision with falling meteor
            meteor_hitbox_size = max(
                12,
                int(m["size"] * FALLING_HITBOX_SCALE),
            )
            meteor_rect = pygame.Rect(
                m["x"] + (m["size"] - meteor_hitbox_size) // 2,
                m["y"] + (m["size"] - meteor_hitbox_size) // 2,
                meteor_hitbox_size,
                meteor_hitbox_size,
            )
            if not crystal_freeze and meteor_rect.colliderect(player_rect):
                current_time = pygame.time.get_ticks()

                # Only remove one heart after the damage cooldown has passed
                if current_time - last_damage_time >= DAMAGE_COOLDOWN:
                    lives -= 1
                    last_damage_time = current_time

                    # Show the death screen only after all three hearts are gone
                    if lives == 0:
                        record_death()
                        game_state = "death_screen"
                        break

                # Move the meteor away after a collision
                m.update(create_meteor(current_level))

            elif not crystal_freeze and m["y"] > HEIGHT:
                m.update(create_meteor(current_level))

        # Draw the hearts and crystals
        draw_hearts(screen)
        draw_crystal_hud(screen)

    # 14. MARS-TO-SATURN FADE TRANSITION
    elif game_state == "mars_to_saturn_transition":
        # Keep Mars music during the travel transition
        change_music(MARS_MUSIC)

        screen.blit(mars_background, (0, 0))

        mars_to_saturn.set_alpha(transition_alpha)
        screen.blit(mars_to_saturn, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "mars_to_saturn_hold"

    # 15. HOLD MARS-TO-SATURN TRANSITION
    elif game_state == "mars_to_saturn_hold":
        screen.blit(mars_to_saturn, (0, 0))

        if pygame.time.get_ticks() - transition_timer > 2000:
            transition_alpha = 0
            game_state = "level3_intro"

    # 16. LEVEL 3 INTRO
    elif game_state == "level3_intro":
        change_music(SATURN_MUSIC)

        screen.blit(mars_to_saturn, (0, 0))

        level3_intro.set_alpha(transition_alpha)
        screen.blit(level3_intro, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255
            transition_timer = pygame.time.get_ticks()
            game_state = "saturn_transition"

    # 17. HOLD LEVEL 3 SCREEN
    elif game_state == "saturn_transition":
        screen.blit(level3_intro, (0, 0))

        if pygame.time.get_ticks() - transition_timer > 3000:
            current_level = 3
            transition_alpha = 0

            player_x = 200
            player_y = 300
            sync_player_hitbox()
            current_image = idle

            lives = 3
            crystals_collected = 2
            last_damage_time = -DAMAGE_COOLDOWN
            lifted_rocks.clear()
            rock_hold_time = 0
            crystal_found = False
            crystal_reveal_start = 0
            crystal_reveal_position = None
            timer_stopped = False
            stopped_time_left = LEVEL_TIME
            crystal_rock_index = random.randrange(len(rock_positions))

            # Hide aliens under exactly 3 rocks, never under the crystal rock.
            possible_alien_rocks = [
                i for i in range(len(rock_positions)) if i != crystal_rock_index
            ]
            alien_rock_indices = set(random.sample(possible_alien_rocks, 3))
            alien_reveal_positions.clear()
            stunned_until = 0

            meteors.clear()
            for _ in range(NUM_METEORS):
                meteors.append(create_meteor(3))

            moon_start_time = pygame.time.get_ticks()
            game_state = "saturn_game"

    # 17. SATURN GAMEPLAY
    elif game_state == "saturn_game":
        # Draw previous screen first
        screen.blit(level3_intro, (0, 0))

        # Fade the Moon background over it
        saturn_background.set_alpha(transition_alpha)
        screen.blit(saturn_background, (0, 0))

        transition_alpha += transition_speed

        if transition_alpha >= 255:
            transition_alpha = 255

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        is_stunned = current_time < stunned_until
        crystal_freeze = crystal_found

        # Character starts as idle each frame
        current_image = idle

        # Store changes to X and Y movement separately for smooth sliding collisions
        dx = 0
        dy = 0

        # The player cannot move while stunned.
        if not is_stunned and not crystal_freeze:
            if keys[pygame.K_d]:
                dx += speed
                current_image = walk_right
            elif keys[pygame.K_a]:
                dx -= speed
                current_image = walk_left

            if keys[pygame.K_w]:
                dy -= speed
            if keys[pygame.K_s]:
                dy += speed

        # Handle X-axis movement and wall/rock collisions
        if dx != 0:
            temp_x = max(LEFT_LIMIT, min(player_x + dx, RIGHT_LIMIT))
            temp_rect = pygame.Rect(
                temp_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
                player_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )
            collided = False
            for r_idx, r_rect in enumerate(rock_rects):
                if r_idx in lifted_rocks:
                    continue  # No collisions for rocks that have been lifted!
                if temp_rect.colliderect(r_rect):
                    collided = True
                    break
            if not collided:
                player_x = temp_x

        # Handle Y-axis movement and wall/rock collisions
        if dy != 0:
            temp_y = max(TOP_LIMIT, min(player_y + dy, BOTTOM_LIMIT))
            temp_rect = pygame.Rect(
                player_x + (160 - PLAYER_HITBOX_WIDTH) // 2,
                temp_y + (160 - PLAYER_HITBOX_HEIGHT) // 2,
                PLAYER_HITBOX_WIDTH,
                PLAYER_HITBOX_HEIGHT,
            )
            collided = False
            for r_idx, r_rect in enumerate(rock_rects):
                if r_idx in lifted_rocks:
                    continue  # No collisions for rocks that have been lifted!
                if temp_rect.colliderect(r_rect):
                    collided = True
                    break
            if not collided:
                player_y = temp_y

        # Sync player's physical hitbox updates
        sync_player_hitbox()

        # Draw player after processing movement
        screen.blit(current_image, (player_x, player_y))

        # Draw unlifted Saturn rocks and find the closest interactive rock
        active_rock_index = None
        closest_distance = float("inf")

        for i, position in enumerate(rock_positions):
            if i in lifted_rocks:
                continue

            rock_image_to_draw = saturn_rock_images[i % len(saturn_rock_images)]
            screen.blit(rock_image_to_draw, position)

            # Use the global custom rock rect for interaction checks
            rock_rect = pygame.Rect(
                position[0] + 25,
                position[1] + 25,
                GROUND_ROCK_HITBOX_SIZE,
                GROUND_ROCK_HITBOX_SIZE,
            )
            interaction_rect = rock_rect.inflate(80, 80)

            if player_rect.colliderect(interaction_rect):
                player_center = player_rect.center
                rock_center = rock_rect.center
                distance = (
                    (player_center[0] - rock_center[0]) ** 2
                    + (player_center[1] - rock_center[1]) ** 2
                ) ** 0.5

                if distance < closest_distance:
                    closest_distance = distance
                    active_rock_index = i

        # Hold E to lift mechanics
        if active_rock_index is not None and not is_stunned and not crystal_freeze:
            prompt = task_font.render(
                "Hold E for 2 seconds to lift the rock",
                True,
                WHITE,
            )
            screen.blit(
                prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 35))
            )

            if keys[pygame.K_e]:
                rock_hold_time += clock.get_time()

                # Lift Progress Bar
                bar_width = 300
                bar_height = 22
                bar_x = WIDTH // 2 - bar_width // 2
                bar_y = HEIGHT - 75
                progress = min(1, rock_hold_time / required_hold_time)

                pygame.draw.rect(
                    screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2
                )
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        bar_x + 2,
                        bar_y + 2,
                        int((bar_width - 4) * progress),
                        bar_height - 4,
                    ),
                )

                if rock_hold_time >= required_hold_time:
                    lifted_rock = active_rock_index
                    lifted_rocks.add(lifted_rock)
                    rock_hold_time = 0

                    # Three Saturn rocks hide aliens. Finding one stuns the player
                    # and pauses all falling diamonds for 5 seconds.
                    if lifted_rock in alien_rock_indices:
                        rock_x, rock_y = rock_positions[lifted_rock]
                        alien_reveal_positions[lifted_rock] = (rock_x, rock_y)
                        stunned_until = pygame.time.get_ticks() + ALIEN_STUN_DURATION

                    # Check if the lifted rock is hiding the crystal
                    if lifted_rock == crystal_rock_index and not crystal_found:
                        crystal_found = True
                        crystals_collected += 1

                        # Spawning location for revealed crystal
                        rock_x, rock_y = rock_positions[lifted_rock]
                        crystal_reveal_position = (
                            rock_x + 25,
                            rock_y + 25,
                        )
                        crystal_reveal_start = pygame.time.get_ticks()

                        # Stop level countdown
                        elapsed_when_found = record_level_completion(3)
                        stopped_time_left = max(
                            0,
                            LEVEL_TIME - elapsed_when_found,
                        )
                        timer_stopped = True
            else:
                rock_hold_time = 0
        else:
            rock_hold_time = 0

        # Keep discovered aliens visible underneath their lifted rocks.
        for alien_position in alien_reveal_positions.values():
            screen.blit(alien_image, alien_position)

        if is_stunned:
            stun_text = task_font.render(
                "You found an alien! You're stunned for 5 seconds",
                True,
                WHITE,
            )
            screen.blit(stun_text, stun_text.get_rect(center=(WIDTH // 2, 70)))

        # Show the revealed crystal (lasts 2 seconds)
        if (
            crystal_found
            and crystal_reveal_position is not None
            and pygame.time.get_ticks() - crystal_reveal_start
            < crystal_reveal_duration
        ):
            big_crystal = pygame.transform.scale(crystal_full, (150, 150))
            screen.blit(big_crystal, crystal_reveal_position)

        # After the Saturn crystal has been shown for 2 seconds,
        # begin the final cutscene.
        if (
            crystal_found
            and crystal_reveal_start > 0
            and pygame.time.get_ticks() - crystal_reveal_start
            >= crystal_reveal_duration
        ):
            save_player_stats()
            change_music(FINAL_MUSIC)
            player_x = 150
            player_y = 450
            sync_player_hitbox()
            current_image = idle
            game_state = "final_rocket_scene"

            # Prevent Saturn hazards from overwriting the new cutscene state.
            pygame.display.flip()
            clock.tick(60)
            continue

        # Calculate time left
        if timer_stopped:
            time_left = stopped_time_left
        else:
            elapsed_time = (pygame.time.get_ticks() - moon_start_time) // 1000
            time_left = max(0, LEVEL_TIME - elapsed_time)

        if time_left <= 0:
            record_death()
            game_state = "ran_out_of_time"

        # Timer is black normally, but turns red with 10 seconds remaining
        if time_left <= 10:
            timer_color = RED
        else:
            timer_color = BLACK

        timer_text = task_font.render(
            f"Time Left: {time_left}", True, timer_color
        )

        timer_rect = timer_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(timer_text, timer_rect)

        # Draw diamonds. Their movement and collisions pause while stunned.
        for m in meteors:
            if not is_stunned and not crystal_freeze:
                m["y"] += m["speed"]

            screen.blit(m["image"], (m["x"], m["y"]))

            # Check collision only while the diamonds are active.
            meteor_hitbox_size = max(
                12,
                int(m["size"] * FALLING_HITBOX_SCALE),
            )
            meteor_rect = pygame.Rect(
                m["x"] + (m["size"] - meteor_hitbox_size) // 2,
                m["y"] + (m["size"] - meteor_hitbox_size) // 2,
                meteor_hitbox_size,
                meteor_hitbox_size,
            )
            if not is_stunned and not crystal_freeze and meteor_rect.colliderect(player_rect):
                current_time = pygame.time.get_ticks()

                # Only remove one heart after the damage cooldown has passed
                if current_time - last_damage_time >= DAMAGE_COOLDOWN:
                    lives -= 1
                    last_damage_time = current_time

                    # Show the death screen only after all three hearts are gone
                    if lives == 0:
                        record_death()
                        game_state = "death_screen"
                        break

                # Move the meteor away after a collision
                m.update(create_meteor(current_level))

            elif not is_stunned and not crystal_freeze and m["y"] > HEIGHT:
                m.update(create_meteor(current_level))

        # Draw the hearts and crystals
        draw_hearts(screen)
        draw_crystal_hud(screen)

    # 18. FINAL ROCKET SCENE
    elif game_state == "final_rocket_scene":
        change_music(FINAL_MUSIC)
        screen.blit(space_rocket_bg, (0, 0))

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
        sync_player_hitbox()

        final_rocket_rect = pygame.Rect(
            final_rocket_x, final_rocket_y, 135, 250
        )
        final_near_rocket = player_rect.colliderect(
            final_rocket_rect.inflate(100, 120)
        )

        screen.blit(rocket1, (final_rocket_x, final_rocket_y))
        screen.blit(current_image, (player_x, player_y))

        task_text = task_font.render(
            "Task: Using WASD, head over to your rocket.",
            True,
            WHITE,
        )
        screen.blit(task_text, (25, 20))

        if final_near_rocket:
            prompt = task_font.render(
                "Press E to enter your rocket", True, WHITE
            )
            screen.blit(prompt, (430, 635))

    # 19. FULL-SCREEN ALIEN JUMPSCARE
    elif game_state == "alien_jumpscare":
        # Cover the entire screen for 3 seconds. The player does not board
        # the rocket until this image and sound have finished.
        screen.blit(alien_jump_bg, (0, 0))

        if pygame.time.get_ticks() - cutscene_timer >= 5000:
            cutscene_timer = pygame.time.get_ticks()
            change_music(YAY_MUSIC, loop=False, volume=1.0)
            game_state = "saved_earth"

    # 20. FULL-SCREEN EARTH SAVED CELEBRATION
    elif game_state == "saved_earth":
        # This image is scaled to WIDTH x HEIGHT, so it covers the entire screen.
        screen.blit(saved_earth_bg, (0, 0))

        # Keep the image and YAY.mp3 playing for 8 seconds.
        if pygame.time.get_ticks() - cutscene_timer >= 8000:
            cutscene_timer = pygame.time.get_ticks()
            change_music(FINAL_MUSIC)
            game_state = "credits_1"

    # 21. CREDITS 1
    elif game_state == "credits_1":
        screen.blit(credits1, (0, 0))
        if pygame.time.get_ticks() - cutscene_timer >= 4000:
            cutscene_timer = pygame.time.get_ticks()
            game_state = "credits_2"

    # 22. CREDITS 2
    elif game_state == "credits_2":
        screen.blit(credits2, (0, 0))
        if pygame.time.get_ticks() - cutscene_timer >= 4000:
            cutscene_timer = pygame.time.get_ticks()
            game_state = "credits_3"

    # 23. CREDITS 3
    elif game_state == "credits_3":
        screen.blit(credits3, (0, 0))
        if pygame.time.get_ticks() - cutscene_timer >= 4000:
            save_player_stats()
            pygame.mixer.music.stop()
            current_music = None

            current_level = 1
            current_story = 0
            story_alpha = 0
            fade_alpha = 0
            intro_stage = "fade_in"
            hold_start = 0
            transition_alpha = 0
            transition_timer = 0

            player_x = 118
            player_y = 551
            sync_player_hitbox()
            current_image = idle

            lives = 3
            crystals_collected = 0
            lifted_rocks.clear()
            rock_hold_time = 0
            crystal_found = False
            crystal_reveal_start = 0
            crystal_reveal_position = None
            timer_stopped = False
            stopped_time_left = LEVEL_TIME
            last_damage_time = -DAMAGE_COOLDOWN
            stunned_until = 0
            alien_rock_indices = set()
            alien_reveal_positions.clear()

            meteors.clear()
            for _ in range(NUM_METEORS):
                meteors.append(create_meteor(1))

            game_state = "menu"
            change_music(OPENING_MUSIC)

    # 24. RAN OUT OF TIME SCREEN
    elif game_state == "ran_out_of_time":
        change_music(DEATH_MUSIC)
        screen.blit(ran_out_of_time_screen, (0, 0))

    # 25. DEATH SCREEN
    elif game_state == "death_screen":
        change_music(DEATH_MUSIC)
        screen.blit(death_screen, (0, 0))

    # Update the screen and limit the game to 60 frames per second
    pygame.display.flip()
    clock.tick(60)

pygame.mixer.music.stop()
pygame.quit()
