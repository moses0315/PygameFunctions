import pygame
import sys
import math
import json
import os

LOGICAL_WIDTH, LOGICAL_HEIGHT = 1280, 720
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SAVE_FILE = "save_data.json"
default_data = {
    "controls": {
        "move_left": pygame.K_LEFT,
        "move_right": pygame.K_RIGHT,
        "jump": pygame.K_SPACE,
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


def save_game(data, file_path=SAVE_FILE):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("게임 데이터가 저장되었습니다!")
    except Exception as e:
        print(f"저장 중 오류 발생: {e}")


def load_game(file_path=SAVE_FILE):
    if not os.path.exists(file_path):
        print("저장 파일이 없습니다. 기본 데이터를 로드합니다.")
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print("게임 데이터가 로드되었습니다!")
        return data
    except Exception as e:
        print(f"로드 중 오류 발생: {e}")
        return default_data


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


def convert_position_to_logical(screen_x, screen_y, scale, offset_x, offset_y):
    logical_x = (screen_x - offset_x) / scale
    logical_y = (screen_y - offset_y) / scale
    return logical_x, logical_y


class Button:
    def __init__(self, x, y, width, height, color, text="", text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 32)
        self.is_pressed = False
        self.state = "normal"

    def draw(self, surface):
        if self.state == "normal":
            draw_color = self.color
        elif self.state == "hover":
            draw_color = tuple(min(c + 40, 255) for c in self.color)
        elif self.state == "pressed":
            draw_color = tuple(max(c - 40, 0) for c in self.color)
        elif self.state == "focus":
            draw_color = (255, 255, 255)
        else:
            draw_color = self.color
        pygame.draw.rect(surface, draw_color, self.rect)
        if self.text:
            text_surface = self.font.render(self.text, False, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def handle_event(self, event, logical_x, logical_y):
        if event.type == pygame.MOUSEMOTION:
            if self.state in ("pressed", "focus"):
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
                self.state = "focus"
                return True
            self.state = "normal"
            self.is_pressed = False
        return False


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def update(self, target_rect, map_width, map_height):
        self.x = target_rect.centerx - self.width // 2
        self.y = target_rect.centery - self.height // 2
        self.x = max(0, min(self.x, map_width - self.width))
        self.y = max(0, min(self.y, map_height - self.height))

    def apply(self, surface):
        return surface, (-self.x, -self.y)


class Animation:
    def __init__(self, sprite_sheet_path, num_frames, frame_length, loop=True):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.num_frames = num_frames
        self.frame_length = frame_length
        self.loop = loop

        self.frame_width = self.sprite_sheet.get_width() // num_frames
        self.frame_height = self.sprite_sheet.get_height()
        self.frames = self.load_frames()

        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False

        self.rect = pygame.rect.Rect(0, 0, self.frame_width, self.frame_height)

    def load_frames(self):
        frames = []
        for i in range(self.num_frames):
            frame_rect = pygame.Rect(
                i * self.frame_width, 0, self.frame_width, self.frame_height
            )
            frame = self.sprite_sheet.subsurface(frame_rect)
            frames.append(frame)
        return frames

    def update(self, dt):
        if self.finished:
            return

        self.accumulated_time += dt

        while self.accumulated_time >= self.frame_length:
            self.accumulated_time -= self.frame_length
            self.current_frame += 1

            if self.current_frame == self.num_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.finished = True
                    self.current_frame = self.num_frames - 1

    def draw(self, surface, rect):
        current_frame_image = self.frames[self.current_frame]
        self.rect.midbottom = rect.midbottom
        surface.blit(current_frame_image, self.rect)

    def reset(self):
        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False
        return self


class Player:
    def __init__(self, x, y, controls):
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y
        self.speed = 100
        self.pressed_directions = [0]
        self.controls = controls

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["move_left"]:
                self.pressed_directions.append(-1)
            elif event.key == self.controls["move_right"]:
                self.pressed_directions.append(1)
        elif event.type == pygame.KEYUP:
            if event.key == self.controls["move_left"]:
                self.pressed_directions.remove(-1)
            elif event.key == self.controls["move_right"]:
                self.pressed_directions.remove(1)

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[self.controls["jump"]]:
            print("Jump!!")
        self.x += self.pressed_directions[-1] * self.speed * delta_time
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


class MainScene:
    def __init__(self, switch_scene):
        self.switch_scene = switch_scene
        self.buttons = [
            Button(0, 0, 200, 50, (0, 0, 255), text="Play"),
            Button(0, 50, 200, 50, (0, 200, 0), text="Settings"),
            Button(0, 100, 200, 50, (200, 0, 0), text="Quit"),
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
    def __init__(self, switch_scene, game_data):
        self.switch_scene = switch_scene
        self.camera = Camera(LOGICAL_WIDTH, LOGICAL_HEIGHT)
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
        self.back_button = Button(5, 5, 100, 50, (200, 200, 0), text="Back")
        self.player = Player(100, 100, game_data["controls"])
        self.background = pygame.image.load("play_scene_bg.png").convert()
        self.floor = pygame.image.load("floor.png").convert_alpha()
        for x in range(0, LOGICAL_WIDTH * 2, self.background.get_width()):
            self.background_layer.blit(self.background, (x, 0))
        self.midground_layer.blit(self.floor, (0, 230))

    def handle_event(self, event, logical_x, logical_y):
        if self.back_button.handle_event(event, logical_x, logical_y):
            self.switch_scene("main")
        self.player.handle_event(event)

    def update(self, delta_time):
        self.player.update(delta_time)
        self.camera.update(self.player.rect, LOGICAL_WIDTH * 2, LOGICAL_HEIGHT)

    def draw(self, logical_surface):
        self.foreground_layer.fill((0, 0, 0, 0))
        self.player.draw(self.foreground_layer)
        self.back_button.draw(self.canvas_layer)
        logical_surface.blit(self.background_layer, (-self.camera.x * 0.5, 0))
        logical_surface.blit(self.midground_layer, (-self.camera.x * 0.7, 0))
        logical_surface.blit(self.foreground_layer, (-self.camera.x, 0))
        logical_surface.blit(self.canvas_layer, (0, 0))


class SettingsScene:
    def __init__(self, switch_scene, game_data):
        self.switch_scene = switch_scene
        self.game_data = game_data
        self.controls = game_data["controls"]
        self.back_button = Button(10, 10, 100, 50, (200, 200, 0), text="Back")
        self.background = pygame.image.load("settings_scene_bg.png").convert()
        self.selected_action = None
        self.action_buttons = {
            "move_left": Button(
                100,
                100,
                200,
                50,
                (100, 100, 200),
                text=f"move_left: {pygame.key.name(self.controls['move_left'])}",
            ),
            "move_right": Button(
                100,
                160,
                200,
                50,
                (100, 100, 200),
                text=f"move_right: {pygame.key.name(self.controls['move_right'])}",
            ),
            "jump": Button(
                100,
                220,
                200,
                50,
                (100, 100, 200),
                text=f"jump: {pygame.key.name(self.controls['jump'])}",
            ),
        }

    def handle_event(self, event, logical_x, logical_y):
        if self.selected_action is None:
            for action, button in self.action_buttons.items():
                if button.handle_event(event, logical_x, logical_y):
                    self.selected_action = action
        else:
            if event.type == pygame.KEYDOWN:
                self.controls[self.selected_action] = event.key
                self.action_buttons[self.selected_action].text = (
                    f"{self.selected_action}: {pygame.key.name(event.key)}"
                )
                self.action_buttons[self.selected_action].state = "normal"
                save_game(self.game_data)
                self.selected_action = None
        if self.back_button.handle_event(event, logical_x, logical_y):
            self.game_data["controls"] = self.controls
            save_game(self.game_data)
            self.switch_scene("main")

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        logical_surface.blit(self.background, (0, 0))
        for button in self.action_buttons.values():
            button.draw(logical_surface)
        self.back_button.draw(logical_surface)


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Save/Load System Example")
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    current_scene = None
    game_data = load_game()
    scale, offset_x, offset_y, scaled_width, scaled_height = calculate_letterbox(
        LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    )

    def switch_scene(scene_name):
        nonlocal current_scene
        if scene_name == "main":
            current_scene = MainScene(switch_scene)
        elif scene_name == "play":
            current_scene = PlayScene(switch_scene, game_data)
        elif scene_name == "settings":
            current_scene = SettingsScene(switch_scene, game_data)

    switch_scene("main")
    running = True
    clock = pygame.time.Clock()

    while running:
        delta_time = min(clock.tick() / 1000.0, 0.03)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(game_data)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                scale, offset_x, offset_y, scaled_width, scaled_height = (
                    calculate_letterbox(
                        LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
                    )
                )
            elif event.type in (
                pygame.MOUSEMOTION,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
            ):
                mouse_x, mouse_y = event.pos
                logical_x, logical_y = convert_position_to_logical(
                    mouse_x, mouse_y, scale, offset_x, offset_y
                )
                current_scene.handle_event(event, logical_x, logical_y)
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                current_scene.handle_event(event, -100, -100)

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
