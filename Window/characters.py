import pygame
from enum import Enum, auto
from dataclasses import dataclass
from utils import Button, Camera, Animation, Timer

DEBUG = True
@dataclass
class AttackData:
    animation: Animation  # 애니메이션
    active_frame: int     # 공격 활성 프레임
    dash_frame: int       # 대시 프레임
    dash_distance: int
    dash_time: float
    rect: pygame.Rect

    def __post_init__(self):
        self.dash_speed = self.dash_distance / self.dash_time

class Player:
    class State(Enum):
        NORMAL = auto()
        ATTACK = auto()
        DASH = auto()
        HURT = auto()
        DEAD = auto()

    def __init__(self, x, y, controls):
        self.idle_animation = Animation("assets/player/Fire_Warrior_FireSwordIdle.png", num_frames=8, frame_length=0.1)
        self.run_animation = Animation("assets/player/Fire_Warrior_FireSwordRun.png", num_frames=8, frame_length=0.1)


        self.dash_animation = Animation("assets/player/Fire_Warrior_FireSwordDash.png", num_frames=4, frame_length=0.3 / 7, loop=False)
        self.hurt_animation = Animation("assets/player/Fire_Warrior_FireSwordHit.png", num_frames=4, frame_length=0.2 / 4, loop=False)
        self.death_animation = Animation("assets/player/Fire_Warrior_FireSwordDeath.png", num_frames=11, frame_length=0.1, loop=False)
        self.current_animation = self.idle_animation

        self.rect = pygame.Rect(x, y, 24, 50)
        self.x = x
        self.y = y
        self.speed = 120
        self.dash_distance = 100
        self.dash_speed = self.dash_distance / (self.dash_animation.num_frames * self.dash_animation.frame_length)
        self.attack_data = (
            AttackData(
                animation=Animation("assets/player/Fire_Warrior_FireSwordAttack1.png", num_frames=5, frame_length=0.1, loop=False),
                active_frame=2,
                dash_frame=1,
                dash_distance=20,
                dash_time=0.1,
                rect=pygame.Rect(self.rect.centerx, self.rect.top, 45, 50),
            ),
            AttackData(
                animation=Animation("assets/player/Fire_Warrior_FireSwordAttack2.png", num_frames=4, frame_length=0.1, loop=False),
                active_frame=1,
                dash_frame=0,
                dash_distance=20,
                dash_time=0.1,
                rect=pygame.Rect(self.rect.centerx, self.rect.top, 45, 50),
            ),
            AttackData(
                animation=Animation("assets/player/Fire_Warrior_FireSwordAttack3.png", num_frames=8, frame_length=0.1, loop=False),
                active_frame=3,
                dash_frame=2,
                dash_distance=0,
                dash_time=0.1,
                rect=pygame.Rect(self.rect.centerx, self.rect.top, 45, 50),
            ),
        )
        self.controls = controls
        self.pressed_directions = [0]
        self.pressed_actions = ["null"]
        self.facing_right = True

        self.max_health = 100
        self.current_health = self.max_health
        self.health_bar = pygame.Rect(0, 0, 10, 3)

        self.is_invincible = False
        self.is_being_knocked_back = False
        self.knocked_back_power = 0
        self.knocked_back_timer = 0

        self.attack_combo_time = 0.5
        self.attack_combo_timer = 0
        self.attack_combo = 0
        self.current_attack = self.attack_data[self.attack_combo]

        self.enemies = []

        self.state = Player.State.NORMAL
        self.is_attack_frame_active = False

        self.knuck_back_distance = 20
        self.knock_back_time = 0.1

        self.dash_cooldown_time = 0.5
        self.dash_cooldown_timer = Timer(0.5, False)

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
            if self.pressed_actions[-1] == "attack":
                self.state = Player.State.ATTACK
                self.current_attack = self.attack_data[self.attack_combo]
                self.current_animation = self.current_attack.animation.reset()
                self.attack_combo += 1
                if self.attack_combo >= 3:
                    self.attack_combo = 0
            elif self.pressed_actions[-1] == "dash" and not self.dash_cooldown_timer.is_running:
                self.state = Player.State.DASH
                self.dash_cooldown_timer.start()
                self.is_invincible = True
                self.current_animation = self.dash_animation.reset()
            else:
                if self.pressed_directions[-1] == 0:
                    self.current_animation = self.idle_animation
                else:
                    self.current_animation = self.run_animation
                    self.x += self.pressed_directions[-1] * self.speed * delta_time
                    self.set_facing_direction()

        self.dash_cooldown_timer.update(delta_time)

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
            if self.facing_right:
                self.current_attack.rect.x = self.rect.centerx
            else:
                self.current_attack.rect.x = self.rect.centerx - self.current_attack.rect.width
            self.current_attack.rect.y = self.rect.y
            pygame.draw.rect(surface, "white", self.current_attack.rect, 1)

            pygame.draw.rect(surface, "white", self.rect, 1)

        self.current_animation.draw(surface, self.rect, not self.facing_right)

        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(surface, "black", self.health_bar)
        pygame.draw.rect(surface, "green", (*self.health_bar.topleft, self.health_bar.w * health_ratio, self.health_bar.h))

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
            self.state = Player.State.NORMAL
            self.current_animation = self.idle_animation.reset()
            self.is_invincible = False
            self.set_facing_direction()

    def attack(self, current_attack: AttackData, delta_time):
        if self.current_animation.current_frame == current_attack.active_frame and not self.is_attack_frame_active:
            self.is_attack_frame_active = True
            if self.facing_right:
                self.current_attack.rect.x = self.rect.centerx
            else:
                self.current_attack.rect.x = self.rect.centerx - self.current_attack.rect.width
            self.current_attack.rect.y = self.rect.y
            for enemy in self.enemies:
                if self.current_attack.rect.colliderect(enemy.rect):
                    if self.facing_right:
                        knuck_back_direction = 1
                    else:
                        knuck_back_direction = -1
                    enemy.take_damage(10, knuck_back_direction, self.knuck_back_distance, self.knock_back_time)

        if self.current_animation.current_frame == current_attack.dash_frame:
            self.x += self.pressed_directions[-1] * self.current_attack.dash_speed * delta_time

        if self.current_animation.finished:
            self.state = Player.State.NORMAL
            self.is_attack_frame_active = False
            self.current_animation = self.idle_animation.reset()
            self.set_facing_direction()
            self.attack_combo_timer = self.attack_combo_time

    def hurt(self, delta_time):
        if self.current_animation.finished:
            self.state = Player.State.NORMAL
            self.set_facing_direction()
        if self.is_being_knocked_back:
            self.knocked_back_timer -= delta_time
            if self.knocked_back_timer <= 0:
                self.is_being_knocked_back = False
            else:
                self.x += self.knocked_back_power * delta_time

    def take_damage(self, damage, knuck_back_direction, knuck_back_distance, knuck_back_time):
        if not self.is_invincible:
            if self.state != Player.State.DEAD:
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

        self.max_health = 100
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
        self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 40, 50)

        self.player = None

    def update(self, player, delta_time):
        self.player = player
        match self.state:
            case Enemy.State.DEAD:
                return
            case Enemy.State.HURT:
                self.hurt(delta_time)
            case Enemy.State.ATTACK:
                self.attack(delta_time)

        if self.state == Enemy.State.NORMAL:
            distance_to_player = abs(self.rect.centerx - self.player.rect.centerx) - self.player.rect.w / 2
            if distance_to_player < self.attack_range:
                self.set_facing_direction()
                self.state = Enemy.State.ATTACK
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
        self.health_bar.midtop = self.rect.midbottom

    def draw(self, surface):
        if DEBUG:
            rect_chase = pygame.Rect(self.rect.centerx - self.chase_range, self.rect.centery, self.chase_range * 2, 1)
            pygame.draw.rect(surface, "red", rect_chase, 1)

            rect_attack_range = pygame.Rect(self.rect.centerx - self.attack_range, self.rect.centery, self.attack_range * 2, 20)
            pygame.draw.rect(surface, "red", rect_attack_range, 1)

            if self.facing_right:
                self.attack_rect.x = self.rect.centerx
            else:
                self.attack_rect.x = self.rect.centerx - self.attack_rect.width
            pygame.draw.rect(surface, "red", self.attack_rect, 1)

            pygame.draw.rect(surface, "red", self.rect, 1)

        self.current_animation.draw(surface, self.rect, not self.facing_right)
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(surface, "black", self.health_bar)
        pygame.draw.rect(surface, "green", (*self.health_bar.topleft, self.health_bar.w * health_ratio, self.health_bar.h))

    def set_facing_direction(self):
        if self.rect.x < self.player.rect.x:
            self.facing_right = True
        else:
            self.facing_right = False

    def attack(self, delta_time):
        if self.current_animation.current_frame == 9 and not self.is_attack_frame_active:
            self.is_attack_frame_active = True
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
            self.state = Enemy.State.NORMAL
            self.is_attack_frame_active = False
            self.set_facing_direction()

            self.current_animation = self.idle_animation.reset()

    def hurt(self, delta_time):
        if self.current_animation.finished:
            self.state = Enemy.State.NORMAL
            self.set_facing_direction()
        if self.is_being_knocked_back:
            self.knocked_back_timer -= delta_time
            if self.knocked_back_timer <= 0:
                self.is_being_knocked_back = False
            else:
                self.x += self.knocked_back_power * delta_time

    def take_damage(self, damage, knuck_back_direction, knuck_back_distance, knuck_back_time):
        if not self.is_invincible:
            self.state = Enemy.State.HURT
            self.current_animation = self.hurt_animation.reset()
            self.current_health -= damage
            self.knocked_back_power = (knuck_back_direction * knuck_back_distance) / knuck_back_time
            self.knocked_back_timer = knuck_back_time
            self.is_being_knocked_back = True
            if self.current_health <= 0:
                self.state = Enemy.State.DEAD

