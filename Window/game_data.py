import pygame

MAX_FPS = 900
MIN_FPS = 0.03
LOGICAL_WIDTH, LOGICAL_HEIGHT = 600, 300
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SAVE_FILE = "save_data.json"
BACKGROUND_COLOR = (0, 0, 0)

default_data = {
    "controls": {
        "move_left": pygame.K_LEFT,
        "move_right": pygame.K_RIGHT,
        "attack": pygame.K_z,
        "dash": pygame.K_SPACE,
    },
    "player_progress": {
        "level": 1,
        "stage": 1,
        "experience": 0,
    },
    "settings": {
        "sound_volume": 0.5,
        "music_volume": 0.5,
    },
}
