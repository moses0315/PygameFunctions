import pygame
import sys
import json
import os
from enum import Enum, auto
from dataclasses import dataclass
import ctypes
ctypes.windll.user32.SetProcessDPIAware()


DEBUG = True

MAX_FPS = 900
MIN_FPS = 0.03
LOGICAL_WIDTH, LOGICAL_HEIGHT = 400, 300
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SAVE_FILE = "save_data.json"
BACKGROUND_COLOR = (0, 0, 0)
FLOOR_Y = 165

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



class Button:
    class State(Enum):
        NORMAL = auto()
        HOVER = auto()
        PRESS = auto()
        FOCUS = auto()

    def __init__(self, rect, color, text="", text_size=32, text_color=(0, 0, 0)):
        self.rect = rect
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.surface_rect = self.surface.get_rect()
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, text_size)
        self.state = Button.State.NORMAL

    def handle_event_and_check_clicked(self, event, mouse_position):
        if event.type == pygame.MOUSEMOTION:
            if self.state in (Button.State.PRESS, Button.State.FOCUS):
                pass
            elif self.rect.collidepoint(mouse_position):
                self.state = Button.State.HOVER
            else:
                self.state = Button.State.NORMAL
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_position):
                self.state = Button.State.PRESS
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == Button.State.PRESS and self.rect.collidepoint(mouse_position):
                self.state = Button.State.FOCUS
                return True
            self.state = Button.State.NORMAL
        return False

    def draw(self, surface):
        if self.state == Button.State.NORMAL:
            draw_color = self.color
        elif self.state == Button.State.HOVER:
            r = min(self.color[0] + 40, 255)
            g = min(self.color[1] + 40, 255)
            b = min(self.color[2] + 40, 255)
            a = min(self.color[3] + 40, 255)
            draw_color = (r, g, b, a)
        elif self.state == Button.State.PRESS:
            r = max(self.color[0] - 40, 0)
            g = max(self.color[1] - 40, 0)
            b = max(self.color[2] - 40, 0)
            a = max(self.color[3] + 40, 0)
            draw_color = (r, g, b, a)
        elif self.state == Button.State.FOCUS:
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

        # 흔들림 관련 속성
        self.offset_x = 0
        self.offset_y = 0
        self.shake_magnitude = 0
        self.shake_duration = 0
        self.shake_frequency = 0.1
        self.accumulated_time = 0

        # 흔들림 방향
        self.shake_axis = None  # 'x' 또는 'y'
        self.shake_direction = 1  # +1 또는 -1

    def update(self, target_rect, map_width, map_height, delta_time):
        if self.shake_duration > 0:
            self.shake_duration -= delta_time
            self.accumulated_time += delta_time
            while self.accumulated_time >= self.shake_frequency:
                self.accumulated_time -= self.shake_frequency
                if self.shake_axis == 'x':
                    self.offset_x = self.shake_direction * self.shake_magnitude
                    self.shake_direction *= -1
                    self.offset_y = 0
                elif self.shake_axis == 'y':
                    self.offset_y = self.shake_direction * self.shake_magnitude
                    self.shake_direction *= -1
                    self.offset_x = 0

            # 흔들림이 종료되면 초기화
            if self.shake_duration <= 0:
                self.offset_x = 0
                self.offset_y = 0
                self.shake_magnitude = 0
                self.shake_duration = 0
                self.accumulated_time = 0

        # 카메라 기본 위치 계산 (오프셋 포함)
        self.x = (target_rect.centerx - self.width // 2) + self.offset_x
        self.y = (target_rect.centery - self.height // 2) + self.offset_y

        # 맵 경계 내로 제한
        self.x = max(0, min(self.x, map_width - self.width))
        self.y = max(0, min(self.y, map_height - self.height))

    def shake(self, magnitude, duration, axis='x', frequency=0.05):
        """
        magnitude: 흔들림 강도
        duration: 흔들림 지속 시간
        axis: 흔들림 축 ('x' 또는 'y')
        frequency: 흔들림 빈도
        """
        self.shake_magnitude = magnitude
        self.shake_duration = duration
        self.shake_frequency = frequency
        self.shake_axis = axis
        self.shake_direction = 1  # 초기 방향 설정
        self.accumulated_time = 0





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

    def update(self, delta_time):
        if self.finished:
            return

        self.accumulated_time += delta_time

        if self.accumulated_time >= self.frame_length:
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


@dataclass
class AttackData:
    animation: Animation
    active_frame: int
    dash_frame: int
    dash_distance: int
    dash_time: float
    knuck_back_distance: int
    knock_back_time: float
    damage: int
    rect: pygame.Rect

    def __post_init__(self):
        self.dash_speed = self.dash_distance / self.dash_time
        self.knock_back_speed = self.knuck_back_distance / self.knock_back_time


class Player:
    class State(Enum):
        NORMAL = auto()
        ATTACK = auto()
        DASH = auto()
        HURT = auto()
        DEAD = auto()

    def __init__(self, x, y, controls):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 24, 50)

        self.controls = controls
        self.pressed_directions = [0]
        self.pressed_actions = ["null"]

        self.idle_animation = Animation("assets/player/idle.png", num_frames=8, frame_length=0.1)
        self.run_animation = Animation("assets/player/Fire_Warrior_FireSwordRun.png", num_frames=8, frame_length=0.1)
        self.dash_animation = Animation("assets/player/Fire_Warrior_FireSwordDash.png", num_frames=4, frame_length=0.3 / 7, loop=False)
        self.hurt_animation = Animation("assets/player/Fire_Warrior_FireSwordHit.png", num_frames=4, frame_length=0.2 / 4, loop=False)
        self.death_animation = Animation("assets/player/Fire_Warrior_FireSwordDeath.png", num_frames=11, frame_length=0.1, loop=False)
        self.current_animation = self.idle_animation

        self.attack_datas = (
            AttackData(
                animation=Animation("assets/player/attack1.png", num_frames=6, frame_length=0.1, loop=False),
                active_frame=2,
                dash_frame=1,
                dash_distance=20,
                dash_time=0.1,
                knuck_back_distance=20,
                knock_back_time=0.1,
                damage=10,
                rect=pygame.Rect(self.rect.centerx, self.rect.top, 45, 50),
            ),
            AttackData(
                animation=Animation("assets/player/attack2.png", num_frames=4, frame_length=0.1, loop=False),
                active_frame=0,
                dash_frame=0,
                dash_distance=20,
                dash_time=0.1,
                knuck_back_distance=20,
                knock_back_time=0.1,
                damage=10,
                rect=pygame.Rect(self.rect.centerx, self.rect.top, 45, 50),
            ),
            AttackData(
                animation=Animation("assets/player/attack3.png", num_frames=6, frame_length=0.1, loop=False),
                active_frame=0,
                dash_frame=0,
                dash_distance=40,
                dash_time=0.1,
                knuck_back_distance=40,
                knock_back_time=0.1,
                damage=20,
                rect=pygame.Rect(self.rect.centerx, self.rect.top, 45, 50),
            ),
        )
        self.attack_buffer_time = 0.3
        self.attack_buffer_timer = 0
        self.attack_combo_time = 0.1
        self.attack_combo_timer = 0
        self.attack_combo = 0
        self.current_attack = self.attack_datas[self.attack_combo]

        self.state = Player.State.NORMAL
        self.is_invincible = False
        self.is_being_knocked_back = False
        self.knocked_back_power = 0
        self.knocked_back_timer = 0
        self.is_attack_frame_active = False
        self.facing_direction = 1

        self.max_health = 100
        self.current_health = self.max_health
        self.health_bar = pygame.Rect(0, 0, 10, 3)

        self.speed = 120
        self.dash_distance = 100
        self.dash_speed = self.dash_distance / (self.dash_animation.num_frames * self.dash_animation.frame_length)
        self.dash_cooldown_time = 0.5
        self.dash_cooldown_timer = 0

        self.enemies = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["move_left"]:
                self.pressed_directions.append(-1)
            elif event.key == self.controls["move_right"]:
                self.pressed_directions.append(1)
            elif event.key == self.controls["attack"]:
                self.pressed_actions.append("attack")
                self.attack_buffer_timer = self.attack_buffer_time
            elif event.key == self.controls["dash"]:
                self.pressed_actions.append("dash")
        elif event.type == pygame.KEYUP:
            if event.key == self.controls["move_left"]:
                self.pressed_directions.remove(-1)
            elif event.key == self.controls["move_right"]:
                self.pressed_directions.remove(1)
            elif event.key == self.controls["attack"]:
                if "attack" in self.pressed_actions:
                    self.pressed_actions.remove("attack")
            elif event.key == self.controls["dash"]:
                if "dash" in self.pressed_actions:
                    self.pressed_actions.remove("dash")

    def update(self, enemies, delta_time):
        match self.state:
            case Player.State.DEAD:
                if self.death_animation.finished:
                    return
                else:
                    self.current_animation = self.death_animation

            case Player.State.HURT:
                self.hurt(delta_time)

            case Player.State.ATTACK:
                self.enemies = enemies
                self.attack(self.current_attack, delta_time)

            case Player.State.DASH:
                self.dash(delta_time)

        if self.state == Player.State.NORMAL:
            if self.pressed_directions[-1] != 0:
                self.facing_direction = self.pressed_directions[-1]
            if self.pressed_actions[-1] == "attack" or self.attack_buffer_timer > 0:
                self.state = Player.State.ATTACK
                self.current_attack = self.attack_datas[self.attack_combo]
                self.current_animation = self.current_attack.animation.reset()
                self.attack_combo += 1
                if self.attack_combo >= len(self.attack_datas):
                    self.attack_combo = 0
            elif self.pressed_actions[-1] == "dash" and self.dash_cooldown_timer <= 0:
                self.state = Player.State.DASH
                self.dash_cooldown_timer = self.dash_cooldown_time
                self.is_invincible = True
                self.current_animation = self.dash_animation.reset()
            else:
                if self.pressed_directions[-1] == 0:
                    self.current_animation = self.idle_animation
                else:
                    self.current_animation = self.run_animation
                    self.x += self.pressed_directions[-1] * self.speed * delta_time

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= delta_time
        if self.attack_buffer_timer > 0:
            self.attack_buffer_timer -= delta_time

        if self.attack_combo_timer > 0:
            self.attack_combo_timer -= delta_time
        if self.state != Player.State.ATTACK:
            if self.attack_combo_timer <= 0:
                self.attack_combo = 0

        self.current_animation.update(delta_time)
        self.rect.topleft = (self.x, self.y)
        self.health_bar.midtop = self.rect.midbottom

    def draw(self, surface):
        if DEBUG:
            if self.facing_direction == 1:
                self.current_attack.rect.x = self.rect.centerx
            else:
                self.current_attack.rect.x = self.rect.centerx - self.current_attack.rect.width
            self.current_attack.rect.y = self.rect.y
            pygame.draw.rect(surface, "white", self.current_attack.rect, 1)

            pygame.draw.rect(surface, "white", self.rect, 1)

        self.current_animation.draw(surface, self.rect, True if self.facing_direction == -1 else False)

        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(surface, "black", self.health_bar)
        pygame.draw.rect(surface, "green", (*self.health_bar.topleft, self.health_bar.w * health_ratio, self.health_bar.h))

    def dash(self, delta_time):
        self.x += self.facing_direction * self.dash_speed * delta_time
        if self.current_animation.finished:
            self.state = Player.State.NORMAL
            self.current_animation = self.idle_animation.reset()
            self.is_invincible = False

    def attack(self, current_attack: AttackData, delta_time):
        if self.current_animation.current_frame == current_attack.active_frame and not self.is_attack_frame_active:
            self.is_attack_frame_active = True
            if self.facing_direction == 1:
                self.current_attack.rect.x = self.rect.centerx
            else:
                self.current_attack.rect.x = self.rect.centerx - self.current_attack.rect.width
            self.current_attack.rect.y = self.rect.y
            for enemy in self.enemies:
                if self.current_attack.rect.colliderect(enemy.rect):
                    enemy.take_damage(current_attack.damage, self.facing_direction, current_attack.knuck_back_distance, current_attack.knock_back_time)

        if self.current_animation.current_frame == current_attack.dash_frame:
            self.x += self.pressed_directions[-1] * self.current_attack.dash_speed * delta_time

        if self.current_animation.finished:
            self.state = Player.State.NORMAL
            self.is_attack_frame_active = False
            self.current_animation = self.idle_animation.reset()
            self.attack_combo_timer = self.attack_combo_time

    def hurt(self, delta_time):
        if self.current_animation.finished:
            self.state = Player.State.NORMAL
        if self.is_being_knocked_back:
            self.knocked_back_timer -= delta_time
            if self.knocked_back_timer <= 0:
                self.is_being_knocked_back = False
            else:
                self.x += self.knocked_back_power * delta_time

    def take_damage(self, damage, knuck_back_direction, knuck_back_distance, knuck_back_time):
        if not self.is_invincible:
            if self.state != Player.State.DEAD:
                self.is_attack_frame_active = False
                self.state = Player.State.HURT
                self.current_animation = self.hurt_animation.reset()
                self.current_health -= damage
                self.knocked_back_power = (knuck_back_direction * knuck_back_distance) / knuck_back_time
                self.knocked_back_timer = knuck_back_time
                self.is_being_knocked_back = True
                if self.current_health <= 0:
                    self.current_health = 0
                    self.state = Player.State.DEAD


class Enemy:
    class State(Enum):
        NORMAL = auto()
        ATTACK = auto()
        HURT = auto()
        DEAD = auto()

    def __init__(self, x, y):
        self.idle_animation = Animation("assets/enemy/idle.png", num_frames=10, frame_length=0.2)
        self.run_animation = Animation("assets/enemy/run.png", num_frames=4, frame_length=0.2)
        self.hurt_animation = Animation("assets/enemy/hurt.png", num_frames=2, frame_length=0.1, loop=False)
        self.current_animation = self.idle_animation
        
        self.rect = pygame.Rect(x, y, 24, 50)
        self.x = x
        self.y = y
        self.speed = 60
        self.attack_dash_speed = 300
        self.facing_direction = 1

        self.attack_datas = (
            AttackData(
                animation=Animation("assets/enemy/attack.png", num_frames=7, frame_length=0.1, loop=False),
                active_frame=3,
                dash_frame=2,
                dash_distance=20,
                dash_time=0.1,
                knuck_back_distance=20,
                knock_back_time=0.1,
                damage=1,
                rect=pygame.Rect(self.rect.centerx, self.rect.y, 40, 50),
            ),
        )
        self.attack_combo = 0
        self.current_attack = self.attack_datas[self.attack_combo]

        self.max_health = 10000
        self.current_health = self.max_health
        self.health_bar = pygame.Rect(0, 0, 10, 3)

        self.is_attack_frame_active = False

        self.is_invincible = False
        self.is_being_knocked_back = False
        self.knocked_back_power = 0
        self.knocked_back_timer = 0

        self.knuck_back_distance = 50
        self.knock_back_time = 0.1

        self.state = Enemy.State.NORMAL
        self.chase_range = 150
        self.attack_range = 40

        self.player = None

    def update(self, player, delta_time):
        self.player = player
        match self.state:
            case Enemy.State.DEAD:
                return
            case Enemy.State.HURT:
                self.hurt(delta_time)
            case Enemy.State.ATTACK:
                self.attack(self.current_attack, delta_time)

        if self.state == Enemy.State.NORMAL:
            distance_to_player = abs(self.rect.centerx - self.player.rect.centerx) - self.player.rect.w / 2

            if distance_to_player < self.attack_range:
                if self.rect.x < self.player.rect.x:
                    self.facing_direction = 1
                else:
                    self.facing_direction = -1
                self.state = Enemy.State.ATTACK
                self.current_animation = self.current_attack.animation.reset()
            elif distance_to_player < self.chase_range:
                if self.rect.x < self.player.rect.x:
                    self.facing_direction = 1
                else:
                    self.facing_direction = -1
                self.current_animation = self.run_animation
                self.x += self.facing_direction * self.speed * delta_time
            else:
                self.current_animation = self.idle_animation

        self.current_animation.update(delta_time)
        self.rect.topleft = (self.x, self.y)
        self.health_bar.midtop = self.rect.midbottom

    def draw(self, surface):
        if DEBUG:
            rect_chase = pygame.Rect(self.rect.centerx - self.chase_range, self.rect.centery, self.chase_range * 2, 1)
            pygame.draw.rect(surface, "red", rect_chase, 1)

            rect_attack_range = pygame.Rect(self.rect.centerx - self.attack_range, self.rect.centery, self.attack_range * 2, 20)
            pygame.draw.rect(surface, "red", rect_attack_range, 1)

            if self.facing_direction == 1:
                self.current_attack.rect.x = self.rect.centerx
            else:
                self.current_attack.rect.x = self.rect.centerx - self.current_attack.rect.width
            self.current_attack.rect.y = self.rect.y

            pygame.draw.rect(surface, "red", self.current_attack.rect, 1)

            pygame.draw.rect(surface, "red", self.rect, 1)

        self.current_animation.draw(surface, self.rect, True if self.facing_direction == -1 else False)
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(surface, "black", self.health_bar)
        pygame.draw.rect(surface, "green", (*self.health_bar.topleft, self.health_bar.w * health_ratio, self.health_bar.h))

    def attack(self, current_attack: AttackData, delta_time):
        if self.current_animation.current_frame == current_attack.active_frame and not self.is_attack_frame_active:
            self.is_attack_frame_active = True
            if self.facing_direction == 1:
                self.current_attack.rect.x = self.rect.centerx
            else:
                self.current_attack.rect.x = self.rect.centerx - self.current_attack.rect.width
            self.current_attack.rect.y = self.rect.y
            if self.player != None:
                if self.current_attack.rect.colliderect(self.player.rect):
                    self.player.take_damage(current_attack.damage, self.facing_direction, current_attack.knuck_back_distance, current_attack.knock_back_time)
        if self.current_animation.current_frame == current_attack.dash_frame:
            self.x += self.facing_direction * self.current_attack.dash_speed * delta_time
        if self.current_animation.finished:
            self.state = Enemy.State.NORMAL
            self.is_attack_frame_active = False
            self.current_animation = self.idle_animation.reset()

    def hurt(self, delta_time):
        if self.current_animation.finished:
            self.state = Enemy.State.NORMAL
        if self.is_being_knocked_back:
            self.knocked_back_timer -= delta_time
            if self.knocked_back_timer <= 0:
                self.is_being_knocked_back = False
            else:
                self.x += self.knocked_back_power * delta_time

    def take_damage(self, damage, knuck_back_direction, knuck_back_distance, knuck_back_time):
        if not self.is_invincible:
            self.is_attack_frame_active = False
            self.state = Enemy.State.HURT
            self.current_animation = self.hurt_animation.reset()
            self.current_health -= damage
            self.knocked_back_power = (knuck_back_direction * knuck_back_distance) / knuck_back_time
            self.knocked_back_timer = knuck_back_time
            self.is_being_knocked_back = True
            if self.current_health <= 0:
                self.state = Enemy.State.DEAD


class MainScene:
    def __init__(self, game_data):
        self.game_data = game_data

        self.buttons = [
            Button(
                pygame.Rect(0, 0, 200, 50),
                pygame.Color(50, 50, 50, 0),
                text="Play",
            ),
            Button(
                pygame.Rect(0, 50, 200, 50),
                pygame.Color(50, 50, 50, 0),
                text="Settings",
            ),
            Button(
                pygame.Rect(0, 100, 200, 50),
                pygame.Color(200, 0, 0, 0),
                text="Quit",
            ),
        ]
        self.background = pygame.image.load("main_scene_bg.png").convert()
        self.layer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

    def handle_event(self, event, mouse_position):
        for button in self.buttons:
            if button.handle_event_and_check_clicked(event, mouse_position):
                if button.text == "Play":
                    return MapScene(self.game_data)
                elif button.text == "Settings":
                    return SettingsScene(self.game_data)
                elif button.text == "Quit":
                    save_game(self.game_data)
                    pygame.quit()
                    sys.exit()
        return None

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        self.layer.blit(self.background, (0, 0))
        for button in self.buttons:
            button.draw(self.layer)
        logical_surface.blit(self.layer, (0, 0))


@dataclass
class PlaySceneData:
    background: pygame.Surface
    midground: pygame.Surface
    foreground: pygame.Surface
    player: Player
    enemies: list[Enemy]


class MapScene:
    def __init__(self, game_data):

        self.game_data = game_data

        stage1_data = PlaySceneData(
            background=pygame.image.load("assets/background/background.png").convert_alpha(),
            midground=pygame.image.load("assets/background/midground.png").convert_alpha(),
            foreground=pygame.image.load("assets/background/foreground.png").convert_alpha(),
            player=Player(100, FLOOR_Y, self.game_data["controls"]),
            enemies=[Enemy(200, FLOOR_Y)],
        )
        stage2_data = PlaySceneData(
            background=pygame.image.load("assets/background/background.png").convert_alpha(),
            midground=pygame.image.load("assets/background/midground.png").convert_alpha(),
            foreground=pygame.image.load("assets/background/foreground.png").convert_alpha(),
            player=Player(100, FLOOR_Y, self.game_data["controls"]),
            enemies=[Enemy(400, FLOOR_Y)],
        )
        stage3_data = PlaySceneData(
            background=pygame.image.load("assets/background/background.png").convert_alpha(),
            midground=pygame.image.load("assets/background/midground.png").convert_alpha(),
            foreground=pygame.image.load("assets/background/foreground.png").convert_alpha(),
            player=Player(100, FLOOR_Y, self.game_data["controls"]),
            enemies=[Enemy(400, FLOOR_Y),Enemy(200, FLOOR_Y)],
        )
        stage4_data = PlaySceneData(
            background=pygame.image.load("assets/background/background.png").convert_alpha(),
            midground=pygame.image.load("assets/background/midground.png").convert_alpha(),
            foreground=pygame.image.load("assets/background/foreground.png").convert_alpha(),
            player=Player(100, FLOOR_Y, self.game_data["controls"]),
            enemies=[Enemy(0, FLOOR_Y)],
        )

        self.stage_datas = (stage1_data, stage2_data, stage3_data, stage4_data)

        self.background = pygame.image.load("assets/background/map.png").convert_alpha()

        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")

        self.stage_buttons = (
            Button(
                pygame.Rect(100, 50, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text="Stage1",
            ),
            Button(
                pygame.Rect(100, 100, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text="Stage2",
            ),
            Button(
                pygame.Rect(100, 150, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text="Stage3",
            ),
            Button(
                pygame.Rect(100, 200, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text="Stage4",
            ),
        )

    def handle_event(self, event, mouse_position):
        for i, button in enumerate(self.stage_buttons):
            if button.handle_event_and_check_clicked(event, mouse_position):
                return PlayScene(self.game_data, self.stage_datas[i])

        if self.back_button.handle_event_and_check_clicked(event, mouse_position):
            return MainScene(self.game_data)

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        logical_surface.blit(self.background, (0, 0))

        for button in self.stage_buttons:
            button.draw(logical_surface)
        self.back_button.draw(logical_surface)


class PlayScene:
    def __init__(self, game_data, play_scene_data: PlaySceneData):
        self.game_data = game_data
        self.camera = Camera(LOGICAL_WIDTH, LOGICAL_HEIGHT)
        self.background_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT))
        self.midground_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.foreground_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.canvas_layer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")
        self.player = play_scene_data.player
        self.enemies = play_scene_data.enemies
        self.background = play_scene_data.background
        self.background1 = play_scene_data.midground
        self.background2 = play_scene_data.foreground

        for x in range(0, LOGICAL_WIDTH * 2, self.background.get_width()):
            self.background_layer.blit(self.background, (x, 0))
        for x in range(0, LOGICAL_WIDTH * 2, self.background1.get_width()):
            self.midground_layer.blit(self.background1, (x, 0))

    def handle_event(self, event, mouse_position):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.camera.shake(3, 0.1)

        if self.back_button.handle_event_and_check_clicked(event, mouse_position):
            return MapScene(self.game_data)
        self.player.handle_event(event)
        return None

    def update(self, delta_time):
        self.player.update(self.enemies, delta_time)
        for enemy in self.enemies:
            enemy.update(self.player, delta_time)
            if enemy.state == Enemy.State.DEAD:
                self.enemies.remove(enemy)
        self.camera.update(self.player.rect, LOGICAL_WIDTH * 2, LOGICAL_HEIGHT, delta_time)

    def draw(self, logical_surface):
        self.foreground_layer.fill((0, 0, 0, 0))
        self.canvas_layer.fill((0, 0, 0, 0))

        self.foreground_layer.blit(self.background2, (0, 0))
        for enemy in self.enemies:
            enemy.draw(self.foreground_layer)
        self.player.draw(self.foreground_layer)
        self.back_button.draw(self.canvas_layer)

        logical_surface.blit(self.background_layer, (-self.camera.x, 0))
        logical_surface.blit(self.midground_layer, (-self.camera.x, 0))
        logical_surface.blit(self.foreground_layer, (-self.camera.x, 0))
        logical_surface.blit(self.canvas_layer, (0, 0))


class SettingsScene:
    def __init__(self, game_data):
        self.game_data = game_data
        self.controls = self.game_data["controls"]
        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")
        self.background = pygame.image.load("settings_scene_bg.png").convert()
        self.selected_action = None
        self.action_buttons = {
            "move_left": Button(
                pygame.Rect(100, 50, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text=f"move_left: {pygame.key.name(self.controls['move_left'])}",
            ),
            "move_right": Button(
                pygame.Rect(100, 100, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text=f"move_right: {pygame.key.name(self.controls['move_right'])}",
            ),
            "attack": Button(
                pygame.Rect(100, 150, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text=f"attack: {pygame.key.name(self.controls['attack'])}",
            ),
            "dash": Button(
                pygame.Rect(100, 200, 200, 50),
                pygame.Color(100, 100, 200, 0),
                text=f"dash: {pygame.key.name(self.controls['dash'])}",
            ),
        }

    def handle_event(self, event, mouse_position):
        for action, button in self.action_buttons.items():
            if button.handle_event_and_check_clicked(event, mouse_position):
                self.selected_action = action
        if event.type == pygame.KEYDOWN:
            self.controls[self.selected_action] = event.key
            self.action_buttons[self.selected_action].text = f"{self.selected_action}: {pygame.key.name(event.key)}"
            self.action_buttons[self.selected_action].state = Button.State.NORMAL
            save_game(self.game_data)
            self.selected_action = None
        if self.back_button.handle_event_and_check_clicked(event, mouse_position):
            self.game_data["controls"] = self.controls
            save_game(self.game_data)
            return MainScene(self.game_data)
        return None

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        logical_surface.blit(self.background, (0, 0))
        for button in self.action_buttons.values():
            button.draw(logical_surface)
        self.back_button.draw(logical_surface)


if __name__ == "__main__":

    def calculate_scale_and_letterbox(logical_width, logical_height, screen_width, screen_height):
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
    
    def draw_scanlines(surface):
        for y in range(0, surface.get_height(), 2):
            pygame.draw.line(surface, (0, 0, 0, 50), (0, y), (surface.get_width(), y))
        for x in range(0, surface.get_width(), 2):
            pygame.draw.line(surface, (0, 0, 0, 50), (x, 0), (x, surface.get_height()))

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("You must know this: Holding down a key will execute it continuously. You do not need to press the key repeatedly.")
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    game_data = load_game()
    current_scene = MainScene(game_data)
    save_game(game_data)
    scale, offset = calculate_scale_and_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
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
                scale, offset = calculate_scale_and_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                mouse_x = (event.pos[0] - offset[0]) / scale
                mouse_y = (event.pos[1] - offset[1]) / scale
                next_scene = current_scene.handle_event(event, (mouse_x, mouse_y))
                if next_scene:
                    current_scene = next_scene
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
                        scale, offset = calculate_scale_and_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                    elif event.key == pygame.K_ESCAPE:
                        screen = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.RESIZABLE)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
                        scale, offset = calculate_scale_and_letterbox(LOGICAL_WIDTH, LOGICAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                next_scene = current_scene.handle_event(event, (-100, -100))
                if next_scene:
                    current_scene = next_scene

        current_scene.update(delta_time)
        current_scene.draw(logical_surface)
        screen.fill(BACKGROUND_COLOR)
        blured_surface = blur_surface(logical_surface, scale_factor=1)
        scaled_surface = pygame.transform.scale(blured_surface, (LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale))
        screen.blit(scaled_surface, offset)
        pygame.display.flip()
