import pygame
import sys

from utils import save_game, load_game

from game_data import *

from scenes import MainScene, PlayScene, SettingsScene



def calculate_letterbox(logical_width, logical_height, screen_width, screen_height):
    logical_aspect = logical_width / logical_height
    screen_aspect = screen_width / screen_height
    if logical_aspect > screen_aspect:
        scale = screen_width / logical_width
        scaled_height = logical_height * scale
        offset_x = 0
        offset_y = (screen_height - scaled_height) // 2
    else:
        scale = screen_height / logical_height
        scaled_width = logical_width * scale
        offset_x = (screen_width - scaled_width) // 2
        offset_y = 0
    return scale, (offset_x, offset_y)


def blur_surface(surface, scale_factor=4):
    small_size = (surface.get_width() // scale_factor, surface.get_height() // scale_factor)
    small_surface = pygame.transform.smoothscale(surface, small_size)
    return pygame.transform.smoothscale(small_surface, surface.get_size())

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("You must know this: Holding down a key will execute it continuously. You do not need to press the key repeatedly.")
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    game_data = load_game()
    current_scene = MainScene(game_data)
    save_game(game_data)
    scale, offset = calculate_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
    clock = pygame.time.Clock()

    while True:
        delta_time = min(clock.tick(MAX_FPS) / 1000.0, MIN_FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(game_data)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                scale, offset = calculate_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                mouse_x = (event.pos[0] - offset[0]) / scale
                mouse_y = (event.pos[1] - offset[1]) / scale
                next_scene = current_scene.handle_event(event, (mouse_x, mouse_y))
                if next_scene:
                    current_scene = next_scene
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                next_scene = current_scene.handle_event(event, (-100, -100))
                if next_scene:
                    current_scene = next_scene

        current_scene.update(delta_time)
        current_scene.draw(logical_surface)
        screen.fill(BACKGROUND_COLOR)
        scaled_surface = pygame.transform.scale(logical_surface, (LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale))
        blured_surface = blur_surface(scaled_surface, scale_factor=1)
        screen.blit(blured_surface, offset)
        pygame.display.flip()
