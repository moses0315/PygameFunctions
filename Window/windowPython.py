import pygame
import sys
import math
import time

LOGICAL_WIDTH, LOGICAL_HEIGHT = 400, 300
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


def calculate_letterbox(logical_width, logical_height, screen_width, screen_height):
    logical_aspect = logical_width / logical_height
    screen_aspect = screen_width / screen_height

    if logical_aspect > screen_aspect:
        scale = screen_width / logical_width
        scaled_width = screen_width
        scaled_height = math.floor(logical_height * scale)
        offset_x = 0
        offset_y = (screen_height - scaled_height) // 2
    else:
        scale = screen_height / logical_height
        scaled_width = math.floor(logical_width * scale)
        scaled_height = screen_height
        offset_x = (screen_width - scaled_width) // 2
        offset_y = 0

    return scale, offset_x, offset_y, scaled_width, scaled_height


def convert_screen_to_logical(screen_x, screen_y, scale, offset_x, offset_y):
    logical_x = (screen_x - offset_x) / scale
    logical_y = (screen_y - offset_y) / scale
    return logical_x, logical_y


class Button:
    def __init__(self, x, y, width, height, color, text="", text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 50)
        self.is_pressed = False
        self.state = "normal"

    def draw(self, surface):
        if self.state == "normal":
            draw_color = self.color
        elif self.state == "hover":
            draw_color = tuple(min(c + 40, 255) for c in self.color)
        elif self.state == "pressed":
            draw_color = tuple(max(c - 40, 0) for c in self.color)
        else:
            draw_color = self.color

        pygame.draw.rect(surface, draw_color, self.rect)

        if self.text:
            text_surface = self.font.render(self.text, False, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def handle_event(self, event, logical_x, logical_y):
        if event.type == pygame.MOUSEMOTION:
            if self.state == "pressed":
                pass
            elif self.rect.collidepoint(logical_x, logical_y):
                self.state = "hover"
            else:
                self.state = "normal"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(logical_x, logical_y):
                self.state = "pressed"
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(logical_x, logical_y):
                self.is_pressed = False
                self.state = "hover"
                return True
            self.state = "normal"
            self.is_pressed = False

        return False


class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        self.speed = 100

    def update(self, keys, delta_time):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * delta_time
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * delta_time
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class MainScene:
    def __init__(self, switch_scene):
        self.switch_scene = switch_scene
        self.buttons = [
            Button(100, 100, 200, 50, (0, 0, 200), text="Play"),
            Button(100, 160, 200, 50, (0, 200, 0), text="Settings"),
            Button(100, 220, 200, 50, (200, 0, 0), text="Quit"),
        ]
        self.background = pygame.image.load("main_scene_bg.png").convert()

    def handle_event(self, event, logical_x, logical_y):
        for button in self.buttons:
            if button.handle_event(event, logical_x, logical_y):
                if button.text == "Play":
                    self.switch_scene("play")
                elif button.text == "Settings":
                    self.switch_scene("settings")
                elif button.text == "Quit":
                    pygame.quit()
                    sys.exit()

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        logical_surface.blit(self.background, (0, 0))
        for button in self.buttons:
            button.draw(logical_surface)


class PlayScene:
    def __init__(self, switch_scene):
        self.switch_scene = switch_scene
        self.background_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT))
        self.midground_layer = pygame.Surface(
            (LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA
        )
        self.foreground_layer = pygame.Surface(
            (LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA
        )
        self.canvas_layer = pygame.Surface(
            (LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA
        )

        self.back_button = Button(150, 200, 100, 50, (255, 255, 0), text="Back")
        self.player = Player(100, 100)
        self.background = pygame.image.load("play_scene_bg.png").convert()
        self.floor = pygame.image.load("floor.png").convert_alpha()

    def handle_event(self, event, logical_x, logical_y):
        if self.back_button.handle_event(event, logical_x, logical_y):
            self.switch_scene("main")

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        self.player.update(keys, delta_time)

    def draw(self, logical_surface):
        camera_x = self.player.rect.x - LOGICAL_WIDTH // 2
        camera_y = self.player.rect.y - LOGICAL_HEIGHT // 2
        camera_x = max(0, min(camera_x, LOGICAL_WIDTH))
        camera_y = max(0, min(camera_y, 0))

        self.background_layer.fill((0, 0, 0))
        for x in range(0, LOGICAL_WIDTH * 2, self.background.get_width()):
            self.background_layer.blit(self.background, (x, 0))

        self.midground_layer.fill((0, 0, 0, 0))
        self.midground_layer.blit(self.floor, (0, 230))

        self.foreground_layer.fill((0, 0, 0, 0))
        self.player.draw(self.foreground_layer)

        self.canvas_layer.fill((0, 0, 0, 0))
        self.back_button.draw(self.canvas_layer)

        logical_surface.blit(self.background_layer, (-camera_x * 0.5, 0))
        logical_surface.blit(self.midground_layer, (-camera_x * 0.7, 0))
        logical_surface.blit(self.foreground_layer, (-camera_x, 0))
        logical_surface.blit(self.canvas_layer, (0, 0))


class SettingsScene:
    def __init__(self, switch_scene):
        self.switch_scene = switch_scene
        self.back_button = Button(150, 200, 100, 50, (255, 255, 0), text="Back")
        self.background = pygame.image.load("settings_scene_bg.png").convert()

    def handle_event(self, event, logical_x, logical_y):
        if self.back_button.handle_event(event, logical_x, logical_y):
            self.switch_scene("main")

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        logical_surface.blit(self.background, (0, 0))
        self.back_button.draw(logical_surface)


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Simple Scene Management")
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    current_scene = None

    def switch_scene(scene_name):
        nonlocal current_scene
        if scene_name == "main":
            current_scene = MainScene(switch_scene)
        elif scene_name == "play":
            current_scene = PlayScene(switch_scene)
        elif scene_name == "settings":
            current_scene = SettingsScene(switch_scene)

    switch_scene("main")
    running = True
    clock = pygame.time.Clock()

    while running:
        delta_time = clock.tick(900) / 1000.0
        scale, offset_x, offset_y, scaled_width, scaled_height = calculate_letterbox(
            LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            elif event.type in (
                pygame.MOUSEMOTION,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
            ):
                mouse_x, mouse_y = event.pos
                logical_x, logical_y = convert_screen_to_logical(
                    mouse_x, mouse_y, scale, offset_x, offset_y
                )
                current_scene.handle_event(event, logical_x, logical_y)

        current_scene.update(delta_time)
        current_scene.draw(logical_surface)
        screen.fill((0, 0, 0))
        scaled_surface = pygame.transform.scale(
            logical_surface, (scaled_width, scaled_height)
        )
        screen.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()


if __name__ == "__main__":
    main()
