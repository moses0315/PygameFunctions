import pygame
import sys
import json
import os

DEBUG = True

LOGICAL_WIDTH, LOGICAL_HEIGHT = 600, 300
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SAVE_FILE = "save_data.json"
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


def save_game(data, file_path=SAVE_FILE):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("Game data saved!")


def load_game(file_path=SAVE_FILE):
    if not os.path.exists(file_path):
        print("Game DEFAULT data loaded!")
        return default_data
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print("Game data loaded!")
        return data


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


class Button:
    def __init__(self, rect, color, text="", text_size=32, text_color=(0, 0, 0)):
        self.rect = rect
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.surface_rect = self.surface.get_rect()
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, text_size)
        self.state = "normal"

    def handle_event(self, event, mouse_position):
        if event.type == pygame.MOUSEMOTION:
            if self.state in ("press", "focus"):
                pass
            elif self.rect.collidepoint(mouse_position):
                self.state = "hover"
            else:
                self.state = "normal"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_position):
                self.state = "press"
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == "press" and self.rect.collidepoint(mouse_position):
                self.state = "focus"
                return True
            self.state = "normal"
        return False

    def draw(self, surface):
        if self.state == "normal":
            draw_color = self.color
        elif self.state == "hover":
            r = min(self.color[0] + 40, 255)
            g = min(self.color[1] + 40, 255)
            b = min(self.color[2] + 40, 255)
            a = min(self.color[3] + 40, 255)
            draw_color = (r, g, b, a)
        elif self.state == "press":
            r = max(self.color[0] - 40, 0)
            g = max(self.color[1] - 40, 0)
            b = max(self.color[2] - 40, 0)
            a = max(self.color[3] + 40, 0)
            draw_color = (r, g, b, a)
        elif self.state == "focus":
            draw_color = (255, 255, 255, 255)
        self.surface.fill(draw_color)
        if self.text:
            text_surface = self.font.render(self.text, False, self.text_color)
            text_rect = text_surface.get_rect(center=self.surface_rect.center)
            self.surface.blit(text_surface, text_rect)
        surface.blit(self.surface, self.rect)


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
            frame_rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
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

    def draw(self, surface, rect, flip):
        current_frame_image = self.frames[self.current_frame]
        current_frame_image = pygame.transform.flip(current_frame_image, flip, False)
        self.rect.midbottom = rect.midbottom
        surface.blit(current_frame_image, self.rect)

    def reset(self):
        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False
        return self


class Player:
    def __init__(self, x, y, controls):
        self.idle_animation = Animation("assets/player/Fire_Warrior_FireSwordIdle.png", num_frames=8, frame_length=0.1)
        self.run_animation = Animation("assets/player/Fire_Warrior_FireSwordRun.png", num_frames=8, frame_length=0.1)
        self.attack_animation = Animation("assets/player/Fire_Warrior_FireSwordAttack2.png", num_frames=4, frame_length=0.1, loop=False)
        self.dash_animation = Animation("assets/player/Fire_Warrior_FireSwordDash.png", num_frames=4, frame_length=0.3 / 7, loop=False)
        self.hurt_animation = Animation("assets/player/Fire_Warrior_FireSwordHit.png", num_frames=4, frame_length=0.2 / 4, loop=False)
        self.current_animation = self.idle_animation

        self.rect = pygame.Rect(x, y, 24, 50)
        self.x = x
        self.y = y
        self.speed = 130
        self.dash_distance = 100
        self.dash_speed = self.dash_distance / (self.dash_animation.num_frames * self.dash_animation.frame_length)
        self.attack_dash_distance = 20
        self.attack_dash_speed = self.attack_dash_distance / (self.attack_animation.frame_length)

        self.controls = controls
        self.pressed_directions = [0]
        self.pressed_actions = ["null"]
        self.facing_right = True

        self.health = 100
        self.is_invincible = False
        self.is_being_knocked_back = False
        self.knocked_back_power = 0
        self.knocked_back_timer = 0
        self.enemies = []

        self.state = "normal"
        self.attack_frame_active = False

        self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.top, 45, 50)

        self.knuck_back_distance = 20
        self.knock_back_time = 0.1

        self.dash_cooldown_timer = 0.5
        self.dash_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["move_left"]:
                self.pressed_directions.append(-1)
            elif event.key == self.controls["move_right"]:
                self.pressed_directions.append(1)
            elif event.key == self.controls["attack"]:
                self.pressed_actions.append("attack")
            elif event.key == self.controls["dash"]:
                self.pressed_actions.append("dash")
        elif event.type == pygame.KEYUP:
            if event.key == self.controls["move_left"]:
                self.pressed_directions.remove(-1)
            elif event.key == self.controls["move_right"]:
                self.pressed_directions.remove(1)
            elif event.key == self.controls["attack"]:
                self.pressed_actions.remove("attack")
            elif event.key == self.controls["dash"]:
                self.pressed_actions.remove("dash")

    def update(self, enemies, delta_time):
        match self.state:
            case "dead":
                return
            case "hurt":
                self.hurt(delta_time)
            case "attack":
                self.enemies = enemies
                self.attack(delta_time)
            case "dash":
                self.dash(delta_time)

        if self.state == "normal":
            if self.pressed_actions[-1] == "attack":
                self.state = "attack"
                self.current_animation = self.attack_animation.reset()
            elif self.pressed_actions[-1] == "dash" and self.dash_timer <= 0:
                self.state = "dash"
                self.dash_timer = self.dash_cooldown_timer
                self.is_invincible = True
                self.current_animation = self.dash_animation.reset()
            else:
                if self.pressed_directions[-1] == 0:
                    self.current_animation = self.idle_animation
                else:
                    self.current_animation = self.run_animation
                    self.x += self.pressed_directions[-1] * self.speed * delta_time
                    self.set_facing_direction()

        if self.dash_timer > 0:
            self.dash_timer -= delta_time
        self.current_animation.update(delta_time)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if DEBUG:
            if self.facing_right:
                self.attack_rect.x = self.rect.centerx
            else:
                self.attack_rect.x = self.rect.centerx - self.attack_rect.width
            pygame.draw.rect(surface, (255, 255, 255), self.attack_rect, 1)

            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

        self.current_animation.draw(surface, self.rect, not self.facing_right)

    def set_facing_direction(self):
        if self.pressed_directions[-1] == 1:
            self.facing_right = True
        elif self.pressed_directions[-1] == -1:
            self.facing_right = False

    def dash(self, delta_time):
        if self.facing_right:
            self.x += self.dash_speed * delta_time
        else:
            self.x -= self.dash_speed * delta_time

        if self.current_animation.finished:
            self.state = "normal"
            self.is_invincible = False
            self.current_animation = self.idle_animation.reset()
            self.set_facing_direction()

    def attack(self, delta_time):
        if self.current_animation.current_frame == 1 and not self.attack_frame_active:
            self.attack_frame_active = True
            if self.facing_right:
                self.attack_rect.x = self.rect.centerx
            else:
                self.attack_rect.x = self.rect.centerx - self.attack_rect.width
            for enemy in self.enemies:
                if self.attack_rect.colliderect(enemy.rect):
                    if self.facing_right:
                        knuck_back_direction = 1
                    else:
                        knuck_back_direction = -1
                    enemy.take_damage(10, knuck_back_direction, self.knuck_back_distance, self.knock_back_time)

        if self.current_animation.current_frame == 0:
            self.x += self.pressed_directions[-1] * self.attack_dash_speed * delta_time

        if self.current_animation.finished:
            self.state = "normal"
            self.attack_frame_active = False
            self.current_animation = self.idle_animation.reset()
            self.set_facing_direction()

    def hurt(self, delta_time):
        if self.current_animation.finished:
            self.state = "normal"
            self.set_facing_direction()
        if self.is_being_knocked_back:
            self.knocked_back_timer -= delta_time
            if self.knocked_back_timer <= 0:
                self.is_being_knocked_back = False
            else:
                self.x += self.knocked_back_power * delta_time

    def take_damage(self, damage, knuck_back_direction, knuck_back_distance, knuck_back_time):
        if not self.is_invincible:
            self.state = "hurt"
            self.current_animation = self.hurt_animation.reset()
            self.health -= damage
            self.knocked_back_power = (knuck_back_direction * knuck_back_distance) / knuck_back_time
            self.knocked_back_timer = knuck_back_time
            self.is_being_knocked_back = True
            if self.health <= 0:
                self.health = 0
                self.state = "dead"


class Enemy:
    def __init__(self, x, y):
        self.idle_animation = Animation("assets/Knight/tile000.png", num_frames=9, frame_length=0.1)
        self.run_animation = Animation("assets/Knight/tile001.png", num_frames=6, frame_length=0.1)
        self.attack_animation = Animation("assets/Knight/tile002.png", num_frames=12, frame_length=0.1, loop=False)
        self.hurt_animation = Animation("assets/Knight/tile003.png", num_frames=5, frame_length=0.05, loop=False)

        self.current_animation = self.idle_animation

        self.rect = pygame.Rect(x, y, 24, 50)
        self.x = x
        self.y = y
        self.speed = 130
        self.attack_dash_speed = 300
        self.facing_right = True

        self.health = 100

        self.attack_frame_active = False

        self.is_invincible = False
        self.is_being_knocked_back = False
        self.knocked_back_power = 0
        self.knocked_back_timer = 0

        self.knuck_back_distance = 50
        self.knock_back_time = 0.1

        self.state = "normal"
        self.chase_range = 150
        self.attack_range = 40
        self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.top, 40, 50)

        self.player = None

    def update(self, player, delta_time):
        self.player = player
        match self.state:
            case "dead":
                return
            case "hurt":
                self.hurt(delta_time)
            case "attack":
                self.attack(delta_time)

        if self.state == "normal":
            distance_to_player = abs(self.rect.centerx - self.player.rect.centerx) - self.player.rect.w / 2
            if distance_to_player < self.attack_range:
                self.set_facing_direction()
                self.state = "attack"
                self.current_animation = self.attack_animation.reset()
            elif distance_to_player <= self.chase_range:
                self.current_animation = self.run_animation
                if self.rect.x < self.player.rect.x:
                    self.facing_right = True
                    self.x += self.speed * delta_time
                else:
                    self.facing_right = False
                    self.x -= self.speed * delta_time
            else:
                self.current_animation = self.idle_animation

        self.current_animation.update(delta_time)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if DEBUG:
            rect_chase = pygame.Rect(self.rect.centerx - self.chase_range, self.rect.centery, self.chase_range * 2, 1)
            pygame.draw.rect(surface, (255, 255, 255), rect_chase, 1)

            rect_attack_range = pygame.Rect(self.rect.centerx - self.attack_range, self.rect.centery, self.attack_range * 2, 20)
            pygame.draw.rect(surface, (255, 255, 255), rect_attack_range, 1)

            if self.facing_right:
                self.attack_rect.x = self.rect.centerx
            else:
                self.attack_rect.x = self.rect.centerx - self.attack_rect.width
            pygame.draw.rect(surface, (255, 255, 255), self.attack_rect, 1)

            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

        self.current_animation.draw(surface, self.rect, not self.facing_right)

    def set_facing_direction(self):
        if self.rect.x < self.player.rect.x:
            self.facing_right = True
        else:
            self.facing_right = False

    def attack(self, delta_time):
        if self.current_animation.current_frame == 9 and not self.attack_frame_active:
            self.attack_frame_active = True
            if self.facing_right:
                self.attack_rect.x = self.rect.centerx
            else:
                self.attack_rect.x = self.rect.centerx - self.attack_rect.width

            if self.player != None:
                if self.attack_rect.colliderect(self.player.rect):
                    if self.facing_right:
                        knuck_back_direction = 1
                    else:
                        knuck_back_direction = -1
                    self.player.take_damage(10, knuck_back_direction, self.knuck_back_distance, self.knock_back_time)

        if self.current_animation.finished:
            self.state = "normal"
            self.attack_frame_active = False
            self.set_facing_direction()

            self.current_animation = self.idle_animation.reset()

    def hurt(self, delta_time):
        if self.current_animation.finished:
            self.state = "normal"
            self.set_facing_direction()
        if self.is_being_knocked_back:
            self.knocked_back_timer -= delta_time
            if self.knocked_back_timer <= 0:
                self.is_being_knocked_back = False
            else:
                self.x += self.knocked_back_power * delta_time

    def take_damage(self, damage, knuck_back_direction, knuck_back_distance, knuck_back_time):
        if not self.is_invincible:
            self.state = "hurt"
            self.current_animation = self.hurt_animation.reset()
            self.health -= damage
            self.knocked_back_power = (knuck_back_direction * knuck_back_distance) / knuck_back_time
            self.knocked_back_timer = knuck_back_time
            self.is_being_knocked_back = True
            if self.health <= 0:
                self.state = "dead"


class MainScene:
    def __init__(self, switch_scene):
        self.switch_scene = switch_scene
        self.buttons = [
            Button(pygame.Rect(0, 0, 200, 50), pygame.Color(50, 50, 50, 0), text="Play"),
            Button(pygame.Rect(0, 50, 200, 50), pygame.Color(50, 50, 50, 0), text="Settings"),
            Button(pygame.Rect(0, 100, 200, 50), pygame.Color(200, 0, 0, 0), text="Quit"),
        ]
        self.background = pygame.image.load("main_scene_bg.png").convert()
        self.layer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

    def handle_event(self, event, mouse_position):
        for button in self.buttons:
            if button.handle_event(event, mouse_position):
                if button.text == "Play":
                    self.switch_scene("play")
                elif button.text == "Settings":
                    self.switch_scene("settings")
                elif button.text == "Quit":
                    save_game(game_data)
                    pygame.quit()
                    sys.exit()

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        self.layer.blit(self.background, (0, 0))
        for button in self.buttons:
            button.draw(self.layer)
        logical_surface.blit(self.layer, (0, 0))


class PlayScene:
    def __init__(self, switch_scene, game_data):
        self.switch_scene = switch_scene
        self.camera = Camera(LOGICAL_WIDTH, LOGICAL_HEIGHT)
        self.background_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT))
        self.midground_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.foreground_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.canvas_layer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")
        self.player = Player(100, 110, game_data["controls"])
        self.enemies = [Enemy(200, 110)]
        self.background = pygame.image.load("Layer_0009_2.png").convert_alpha()
        self.background1 = pygame.image.load("Layer_0003_6.png").convert_alpha()
        self.background2 = pygame.image.load("Layer_0002_7.png").convert_alpha()

        for x in range(0, LOGICAL_WIDTH * 2, self.background.get_width()):
            self.background_layer.blit(self.background, (x, -500))
        self.midground_layer.blit(self.background1, (0, -500))

    def handle_event(self, event, mouse_position):
        if self.back_button.handle_event(event, mouse_position):
            self.switch_scene("main")
        self.player.handle_event(event)

    def update(self, delta_time):
        self.player.update(self.enemies, delta_time)
        for enemy in self.enemies:
            enemy.update(self.player, delta_time)
            if enemy.state == "dead":
                self.enemies.remove(enemy)
        self.camera.update(self.player.rect, LOGICAL_WIDTH * 2, LOGICAL_HEIGHT)

    def draw(self, logical_surface):
        self.foreground_layer.fill((0, 0, 0, 0))
        self.canvas_layer.fill((0, 0, 0, 0))

        self.foreground_layer.blit(self.background2, (0, 0))
        self.player.draw(self.foreground_layer)
        for enemy in self.enemies:
            enemy.draw(self.foreground_layer)
        self.back_button.draw(self.canvas_layer)

        logical_surface.blit(self.background_layer, (0, 0))
        logical_surface.blit(self.midground_layer, (0, 0))
        logical_surface.blit(self.foreground_layer, (0, 0))
        logical_surface.blit(self.canvas_layer, (0, 0))


class SettingsScene:
    def __init__(self, switch_scene, game_data):
        self.switch_scene = switch_scene
        self.game_data = game_data
        self.controls = game_data["controls"]
        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")
        self.background = pygame.image.load("settings_scene_bg.png").convert()
        self.selected_action = None
        self.action_buttons = {
            "move_left": Button(pygame.Rect(100, 50, 200, 50), pygame.Color(100, 100, 200, 0), text=f"move_left: {pygame.key.name(self.controls['move_left'])}"),
            "move_right": Button(pygame.Rect(100, 100, 200, 50), pygame.Color(100, 100, 200, 0), text=f"move_right: {pygame.key.name(self.controls['move_right'])}"),
            "attack": Button(pygame.Rect(100, 150, 200, 50), pygame.Color(100, 100, 200, 0), text=f"attack: {pygame.key.name(self.controls['attack'])}"),
            "dash": Button(pygame.Rect(100, 200, 200, 50), pygame.Color(100, 100, 200, 0), text=f"dash: {pygame.key.name(self.controls['dash'])}"),
        }

    def handle_event(self, event, mouse_position):
        for action, button in self.action_buttons.items():
            if button.handle_event(event, mouse_position):
                self.selected_action = action
        if event.type == pygame.KEYDOWN:
            self.controls[self.selected_action] = event.key
            self.action_buttons[self.selected_action].text = f"{self.selected_action}: {pygame.key.name(event.key)}"
            self.action_buttons[self.selected_action].state = "normal"
            save_game(self.game_data)
            self.selected_action = None
        if self.back_button.handle_event(event, mouse_position):
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


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("You must know this: Holding down a key will execute it continuously. You do not need to press the key repeatedly.")
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    current_scene = None
    game_data = load_game()
    save_game(game_data)
    scale, offset = calculate_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

    def switch_scene(scene_name):
        global current_scene
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
        delta_time = min(clock.tick(900) / 1000.0, 0.02)
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
                current_scene.handle_event(event, (mouse_x, mouse_y))
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                current_scene.handle_event(event, (-100, -100))

        current_scene.update(delta_time)
        current_scene.draw(logical_surface)
        screen.fill((0, 0, 0))
        scaled_surface = pygame.transform.scale(logical_surface, (LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale))
        #  blured_surface = blur_surface(scaled_surface, scale_factor=2)
        screen.blit(scaled_surface, offset)
        pygame.display.flip()
