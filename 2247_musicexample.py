import os
import pygame

pygame.init()
pygame.mixer.init()

# =========================================================
# FILE/FOLDER SETUP
# =========================================================

# Folder containing this Python file
folder = os.path.dirname(os.path.abspath(__file__))


def asset_path(filename):
    """Creates the complete path to an image, font, or music file."""
    return os.path.join(folder, filename)


def change_music(filename, loop=True, volume=0.5):
    """Stops the old music and starts a new music file."""
    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_path(filename))
    pygame.mixer.music.set_volume(volume)

    if loop:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play(0)


# =========================================================
# WINDOW SETUP
# =========================================================

WIDTH, HEIGHT = 1300, 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save Earth: 2247")

clock = pygame.time.Clock()


# =========================================================
# MUSIC FILES
# Change these names if your actual filenames are different.
# =========================================================

OPENING_MUSIC = "instructions&levelscreensmusic.mp3"
MOON_MUSIC = "moonmusic.mp3"
MARS_MUSIC = "marsmusic.mp3"
SATURN_MUSIC = "saturnmusic.mp3"
DEATH_MUSIC = "deathscreenmusic.mp3"
FINAL_MUSIC = "finalcutscenemusic.mp3"


# Start the opening music immediately.
# This continues through the intro, menu, and story screens.
change_music(OPENING_MUSIC)


# =========================================================
# COLORS
# =========================================================

WHITE = (255, 255, 255)
GAME_BLUE = (2, 100, 147)
BLUE = (95, 183, 207)
RED = (95, 183, 207)


# =========================================================
# LOAD BACKGROUND
# =========================================================

background = pygame.image.load(
    asset_path("2247_earth.png")
).convert()

background = pygame.transform.scale(
    background,
    (WIDTH, HEIGHT)
)


# =========================================================
# INTRO/STORY IMAGES
# =========================================================

intro1 = pygame.image.load(
    asset_path("Intro1.png")
).convert()

intro2 = pygame.image.load(
    asset_path("Intro2.png")
).convert()

intro1 = pygame.transform.scale(
    intro1,
    (WIDTH, HEIGHT)
)

intro2 = pygame.transform.scale(
    intro2,
    (WIDTH, HEIGHT)
)

story_images = [intro1, intro2]

current_story = 0
story_alpha = 0
story_fade_speed = 4


# =========================================================
# ROCKET IMAGES
# =========================================================

rocket1 = pygame.image.load(
    asset_path("rocket1.png")
).convert_alpha()

rocket2 = pygame.image.load(
    asset_path("ROCKET.png")
).convert_alpha()

rocket1 = pygame.transform.scale(
    rocket1,
    (50, 100)
)

rocket2 = pygame.transform.scale(
    rocket2,
    (50, 100)
)


# =========================================================
# PLAYER IMAGES
# =========================================================

player = pygame.image.load(
    asset_path("astro_front.png")
).convert_alpha()

walk_right_image = pygame.image.load(
    asset_path("astro_right.png")
).convert_alpha()

walk_left_image = pygame.image.load(
    asset_path("astro_left.png")
).convert_alpha()

idle = pygame.transform.scale(
    player,
    (160, 160)
)

walk_right = pygame.transform.scale(
    walk_right_image,
    (160, 160)
)

walk_left = pygame.transform.scale(
    walk_left_image,
    (160, 160)
)


# =========================================================
# ROCKET VARIABLES
# =========================================================

rocket1_x = 0
rocket1_y = 0

rocket2_x = 0
rocket2_y = 0


# =========================================================
# PLAYER VARIABLES
# =========================================================

player_x = 100
player_y = 100

player_speed = 5
current_image = idle


# =========================================================
# FONTS
# =========================================================

# =========================================================
# FONTS
# =========================================================

title_font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 30)


# =========================================================
# TITLE SCREEN
# =========================================================

title = title_font.render(
    "2247",
    True,
    GAME_BLUE
)

title_rect = title.get_rect(
    center=(WIDTH // 2, HEIGHT // 2)
)


# =========================================================
# GAME STATE
# =========================================================

game_state = "intro"

new_game_button = pygame.Rect(
    500,
    300,
    300,
    80
)

quit_button = pygame.Rect(
    500,
    400,
    300,
    80
)


# =========================================================
# INTRO ANIMATION VARIABLES
# =========================================================

fade_alpha = 0
fade_speed = 3

intro_stage = "fade_in"
hold_start = 0


# =========================================================
# MAIN GAME LOOP
# =========================================================

running = True

while running:

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_state == "menu":

                if new_game_button.collidepoint(event.pos):

                    game_state = "story"
                    current_story = 0
                    story_alpha = 0

                    # Do not change the music here.
                    # The opening music continues playing.

                elif quit_button.collidepoint(event.pos):
                    running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "story":

                if event.key == pygame.K_RETURN:

                    current_story += 1
                    story_alpha = 0

                    if current_story >= len(story_images):

                        game_state = "game"

                        # The story is finished.
                        # Stop opening music and begin Moon music.
                        change_music(MOON_MUSIC)

    # -----------------------------------------------------
    # DRAW BACKGROUND
    # -----------------------------------------------------

    screen.blit(background, (0, 0))


    # =====================================================
    # INTRO
    # =====================================================

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

            time_held = pygame.time.get_ticks() - hold_start

            if time_held >= 2000:
                intro_stage = "fade_out"

        elif intro_stage == "fade_out":

            fade_alpha -= fade_speed

            if fade_alpha <= 0:
                fade_alpha = 0
                game_state = "menu"


    # =====================================================
    # MENU
    # =====================================================

    elif game_state == "menu":

        menu_title = title_font.render(
            "Save Earth: 2247",
            True,
            BLUE
        )

        menu_title_rect = menu_title.get_rect(
            center=(WIDTH // 2, 220)
        )

        screen.blit(menu_title, menu_title_rect)

        mouse_pos = pygame.mouse.get_pos()

        # -------------------------------------------------
        # START GAME BUTTON
        # -------------------------------------------------

        if new_game_button.collidepoint(mouse_pos):

            start_button = new_game_button.inflate(20, 10)
            start_color = GAME_BLUE

        else:

            start_button = new_game_button
            start_color = BLUE

        pygame.draw.rect(
            screen,
            start_color,
            start_button,
            border_radius=20
        )

        new_text = button_font.render(
            "Start Game",
            True,
            WHITE
        )

        new_text_rect = new_text.get_rect(
            center=start_button.center
        )

        screen.blit(new_text, new_text_rect)

        # -------------------------------------------------
        # QUIT BUTTON
        # -------------------------------------------------

        if quit_button.collidepoint(mouse_pos):

            quit_button_draw = quit_button.inflate(20, 10)
            quit_color = GAME_BLUE

        else:

            quit_button_draw = quit_button
            quit_color = RED

        pygame.draw.rect(
            screen,
            quit_color,
            quit_button_draw,
            border_radius=20
        )

        quit_text = button_font.render(
            "Quit",
            True,
            WHITE
        )

        quit_text_rect = quit_text.get_rect(
            center=quit_button_draw.center
        )

        screen.blit(quit_text, quit_text_rect)


    # =====================================================
    # STORY SCREENS
    # =====================================================

    elif game_state == "story":

        story_image = story_images[current_story]

        if story_alpha < 255:
            story_alpha += story_fade_speed

        story_alpha = min(story_alpha, 255)

        story_image.set_alpha(story_alpha)

        screen.blit(story_image, (0, 0))


    # =====================================================
    # MOON GAMEPLAY
    # =====================================================

    elif game_state == "game":

        keys = pygame.key.get_pressed()

        # Player starts as idle during each frame
        current_image = idle

        # Move right
        if keys[pygame.K_d]:

            player_x += player_speed
            current_image = walk_right

        # Move left
        elif keys[pygame.K_a]:

            player_x -= player_speed
            current_image = walk_left

        # Move up
        if keys[pygame.K_w]:
            player_y -= player_speed

        # Move down
        if keys[pygame.K_s]:
            player_y += player_speed

        # Keep player inside the window
        player_x = max(
            0,
            min(player_x, WIDTH - 160)
        )

        player_y = max(
            0,
            min(player_y, HEIGHT - 160)
        )

        # Draw player
        screen.blit(
            current_image,
            (player_x, player_y)
        )

    pygame.display.flip()
    clock.tick(60)


# =========================================================
# CLOSE GAME
# =========================================================

pygame.mixer.music.stop()
pygame.quit()