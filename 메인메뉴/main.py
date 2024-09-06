import pygame
import heapq
import os
import sys

def resource_path(relative_path):
    """ 리소스를 실행 파일 내에서 접근 가능하도록 경로를 변환 """
    try:
        # PyInstaller가 빌드하는 실행 파일 내부에서 리소스를 찾을 때
        base_path = sys._MEIPASS
    except Exception:
        # 개발 환경에서 리소스를 찾을 때
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Pygame 초기화
pygame.init()

# 화면 크기 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
TILE_SIZE = 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("플랫포머 게임")

# 색상 정의
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
HOVER_COLOR = (200, 200, 200)
CLICK_COLOR = (150, 150, 150)

# FPS 설정
clock = pygame.time.Clock()
FPS = 60

# 적과 플레이어 사이의 최소 거리 설정
MIN_DISTANCE_TO_PLAYER = TILE_SIZE

#플립이 연속해서 일어나는 버그 제어
FLIP_THRESHOLD = 0.5


class TileMap:
    def __init__(self, tile_size, tile_map):
        self.tile_size = tile_size
        self.tile_map = tile_map
        self.tiles = self.create_tiles()

    def create_tiles(self):
        tiles = []
        for row_index, row in enumerate(self.tile_map):
            for col_index, col in enumerate(row):
                if col == "#":
                    tile = pygame.Rect(col_index * self.tile_size, row_index * self.tile_size, self.tile_size, self.tile_size)
                    tiles.append(tile)
        return tiles

    def draw(self, surface):
        for tile in self.tiles:
            pygame.draw.rect(surface, GREEN, tile)

    def is_obstacle(self, x, y):
        if 0 <= y < len(self.tile_map) and 0 <= x < len(self.tile_map[0]):
            return self.tile_map[y][x] == "#"
        return False

class Animation:
    def __init__(self, frames, num_frames=None, frame_duration=0.1, is_sprite_sheet=False):
        if is_sprite_sheet:
            self.sprite_sheet = frames
            self.num_frames = num_frames
            self.frame_width = self.sprite_sheet.get_width() // self.num_frames
            self.frame_height = self.sprite_sheet.get_height()
            self.frames = []
            self.load_frames_from_sprite_sheet()
        else:
            self.frames = frames
            self.num_frames = len(frames)
            self.frame_width = self.frames[0].get_width()
            self.frame_height = self.frames[0].get_height()
            
        self.current_frame = 0
        self.frame_duration = frame_duration  # 각 프레임의 지속 시간 (초)
        self.frame_timer = 0

    def load_frames_from_sprite_sheet(self):
        for i in range(self.num_frames):
            frame = self.sprite_sheet.subsurface((i * self.frame_width, 0, self.frame_width, self.frame_height))
            self.frames.append(frame)

    def update(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.num_frames

    def reset(self):
        self.current_frame = 0
        self.frame_timer = 0

    def get_image(self):
        return self.frames[self.current_frame]


class Player:
    def __init__(self, x, y, width, height, speed, tile_map):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed * 60
        self.gravity = 30 * 60
        self.jump_power = -800
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.tile_map = tile_map

        # 공격 관련 설정
        self.attacking = False
        self.attack_cooldown = 0.5  # 공격 쿨타임 (초)
        self.attack_timer = 0
        self.attack_range = pygame.Rect(0, 0, 80, 80)  # 공격 범위 Rect

        # 애니메이션 설정
        self.idle_animation = Animation(pygame.image.load(resource_path('images/_Idle.png')), num_frames=10, frame_duration=0.1, is_sprite_sheet=True)
        self.run_animation = Animation(pygame.image.load(resource_path('images/_Run.png')), num_frames=10, frame_duration=0.1, is_sprite_sheet=True)
        self.jump_animation = Animation(pygame.image.load(resource_path('images/_Jump.png')), num_frames=3, frame_duration=0.1, is_sprite_sheet=True)
        self.fall_animation = Animation(pygame.image.load(resource_path('images/_Fall.png')), num_frames=3, frame_duration=0.1, is_sprite_sheet=True)
        self.attack_animation = Animation(pygame.image.load(resource_path('images/_Attack.png')), num_frames=4, frame_duration=0.1, is_sprite_sheet=True)

        self.current_animation = self.idle_animation
        self.facing_right = True

        # 초기 on_ground 상태 설정
        self.check_on_ground()

    def move(self, keys, delta_time, enemies):
        self.attack_timer -= delta_time
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed * delta_time
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed * delta_time
            self.facing_right = True
        else:
            self.velocity_x = 0

        if keys[pygame.K_c] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        if keys[pygame.K_x] and self.attack_timer <= 0:
            self.attacking = True
            self.attack_timer = self.attack_cooldown
            self.current_animation = self.attack_animation
            self.current_animation.reset()

        self.velocity_y += self.gravity * delta_time
        self.update_position(delta_time)
        self.update_animation(delta_time)

        if self.attacking:
            if self.current_animation == self.attack_animation and self.current_animation.current_frame == 1:
                self.update_attack_range()
                for enemy in enemies:
                    if self.attack_range.colliderect(enemy.rect):
                        enemy.take_damage(10)
            else:
                # 공격하지 않는 프레임에서는 공격 범위를 무효화 (화면 밖으로 보내기)
                self.attack_range.topleft = (-100, -100)



    def update_position(self, delta_time):
        # 수평 이동
        self.rect.x += self.velocity_x
        collisions = self.check_collision()
        for tile in collisions:
            if self.velocity_x > 0:
                self.rect.right = tile.left
            elif self.velocity_x < 0:
                self.rect.left = tile.right

        # 수직 이동
        self.rect.y += self.velocity_y * delta_time
        collisions = self.check_collision()
        if collisions:  # 바닥과 충돌한 경우
            if self.velocity_y > 0:  # 떨어지는 중이었다면
                self.rect.bottom = collisions[0].top
                self.on_ground = True
                self.velocity_y = 0
            elif self.velocity_y < 0:  # 위로 점프 중이었다면
                self.rect.top = collisions[0].bottom
                self.velocity_y = 0

    def check_on_ground(self):
        # 캐릭터의 바로 아래 타일이 있는지 확인하여 초기 on_ground 상태 설정
        self.rect.y += 1  # 살짝 아래로 이동시켜 충돌 검사
        collisions = self.check_collision()
        if collisions:
            self.on_ground = True
        else:
            self.on_ground = False
        self.rect.y -= 1  # 원래 위치로 복구

    def update_animation(self, delta_time):
        previous_animation = self.current_animation
        if self.attacking:
            if self.current_animation == self.attack_animation and self.current_animation.current_frame == 1:
                pass  # 공격 애니메이션의 특정 프레임에서 공격 판정이 발생하도록 처리
            if self.current_animation != self.attack_animation or self.current_animation.current_frame == self.attack_animation.num_frames - 1:
                self.attacking = False

        if not self.attacking:
            if self.on_ground:
                if self.velocity_x != 0:
                    self.current_animation = self.run_animation
                else:
                    self.current_animation = self.idle_animation
            else:
                if self.velocity_y < 0:
                    self.current_animation = self.jump_animation
                else:
                    self.current_animation = self.fall_animation

        if self.current_animation != previous_animation:
            self.current_animation.reset()

        self.current_animation.update(delta_time)

    def update_attack_range(self):
        if self.facing_right:
            self.attack_range.midleft = self.rect.midright
        else:
            self.attack_range.midright = self.rect.midleft

    def check_collision(self):
        return [tile for tile in self.tile_map.tiles if self.rect.colliderect(tile)]

    def draw(self, surface):
        image = self.current_animation.get_image()
        image = pygame.transform.scale(image, (image.get_width()*2, image.get_height()*2))

        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        image_rect = image.get_rect(midbottom=self.rect.midbottom)
        surface.blit(image, image_rect.topleft)
        
        # 공격 범위를 시각적으로 표시
        if self.attacking:
            pygame.draw.rect(surface, BLUE, self.attack_range, 2)
        
        pygame.draw.rect(surface, RED, self.rect, 2)


class Enemy:
    def __init__(self, x, y, width, height, speed, tile_map):
        self.FLIP_THRESHOLD = 0.5
        self.previous_velocity_x = 0  # 이전 프레임의 velocity_x를 저장할 변수

        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed * 60  # 속도 보정
        self.tile_map = tile_map
        self.velocity_x = 0
        self.velocity_y = 0
        self.path = []
        self.is_dead = False
        self.health = 100
        self.damage_taken = False

        # 애니메이션 설정
        idle_frames = [
            pygame.image.load(resource_path('images/LightBandit_Idle_0.png')),
            pygame.image.load(resource_path('images/LightBandit_Idle_1.png')),
            pygame.image.load(resource_path('images/LightBandit_Idle_2.png')),
            pygame.image.load(resource_path('images/LightBandit_Idle_3.png'))
        ]
        self.idle_animation = Animation(idle_frames, frame_duration=0.1)

        run_frames = [
            pygame.image.load(resource_path('images/LightBandit_Run_0.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_1.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_2.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_3.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_4.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_5.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_6.png')),
            pygame.image.load(resource_path('images/LightBandit_Run_7.png'))
        ]
        self.run_animation = Animation(run_frames, frame_duration=0.1)

        self.death_animation = Animation([
            pygame.image.load(resource_path('images/tile032.png')),
            pygame.image.load(resource_path('images/tile033.png')),
            pygame.image.load(resource_path('images/tile034.png')),
            pygame.image.load(resource_path('images/tile035.png')),
            pygame.image.load(resource_path('images/tile036.png'))
        ], frame_duration=0.15)

        self.current_animation = self.idle_animation
        self.facing_left = True

    def move(self, player, delta_time):
        global a

        
        if self.is_dead:
            self.current_animation.update(delta_time)
            if self.current_animation.current_frame == self.current_animation.num_frames - 1:
                return False
            return True
        
        # 이동하기 전에 이전 velocity_x를 저장합니다.
        self.previous_velocity_x = self.velocity_x
        
        start = (int(self.rect.x // TILE_SIZE), int(self.rect.y // TILE_SIZE))
        goal = (int(player.rect.x // TILE_SIZE), int(player.rect.y // TILE_SIZE))

        if self.get_distance_to_player(player) > MIN_DISTANCE_TO_PLAYER:
            if not self.path or start != self.path[-1]:
                self.path = self.astar(start, goal)

            if self.path:
                next_tile = self.path[0]
                target_x = next_tile[0] * TILE_SIZE
                target_y = next_tile[1] * TILE_SIZE

                # 수평 이동을 위한 속도 설정
                if self.rect.x < target_x:
                    self.velocity_x = self.speed * delta_time
                elif self.rect.x > target_x:
                    self.velocity_x = -self.speed * delta_time
                else:
                    self.velocity_x = 0

                # 수직 이동을 위한 속도 설정
                if self.rect.y < target_y:
                    self.velocity_y = self.speed * delta_time
                elif self.rect.y > target_y:
                    self.velocity_y = -self.speed * delta_time
                else:
                    self.velocity_y = 0

                # 목표 타일에 도달하면 경로 갱신
                if abs(self.rect.x - target_x) < self.speed * delta_time and abs(self.rect.y - target_y) < self.speed * delta_time:
                    self.rect.x, self.rect.y = target_x, target_y
                    self.path.pop(0)
                    
            if abs(self.velocity_x + self.previous_velocity_x) > self.FLIP_THRESHOLD:
                if self.velocity_x > 0:
                    self.facing_left = False
                elif self.velocity_x < 0:
                    self.facing_left = True
                
            if self.velocity_x != 0 or self.velocity_y != 0:
                self.current_animation = self.run_animation
            else:
                self.current_animation = self.idle_animation

        self.current_animation.update(delta_time)
        self.update_position()

        if not player.attacking or not self.rect.colliderect(player.attack_range):
            self.damage_taken = False
        
        return True


    def update_position(self):
        # 수평 및 수직 이동 적용
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    def take_damage(self, damage):
        if not self.damage_taken:  # 아직 데미지를 받지 않았을 때만 실행
            self.health -= damage
            self.damage_taken = True  # 데미지를 받은 상태로 설정
            if self.health <= 0 and not self.is_dead:
                self.is_dead = True
                self.current_animation = self.death_animation
                self.current_animation.reset()

    def get_distance_to_player(self, player):
        return ((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2) ** 0.5

    def astar(self, start, goal):
        open_list = []
        heapq.heappush(open_list, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: manhattan_distance(start, goal)}
        
        while open_list:
            _, current = heapq.heappop(open_list)
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            x, y = current
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x-1, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1)
            ]
            
            for nx, ny in neighbors:
                if 0 <= nx < len(self.tile_map.tile_map[0]) and 0 <= ny < len(self.tile_map.tile_map):
                    if (ny + 1 < len(self.tile_map.tile_map) and not self.tile_map.is_obstacle(nx, ny) and not self.tile_map.is_obstacle(nx, ny+1)):
                        if (abs(nx - x) == 1 and abs(ny - y) == 1):  # 대각선 이동 체크
                            if not can_move_diagonal(self.tile_map, current, ny - y, nx - x):
                                continue
                        tentative_g_score = g_score[current] + 1
                        if (nx, ny) not in g_score or tentative_g_score < g_score[(nx, ny)]:
                            came_from[(nx, ny)] = current
                            g_score[(nx, ny)] = tentative_g_score
                            f_score[(nx, ny)] = tentative_g_score + manhattan_distance((nx, ny), goal)
                            heapq.heappush(open_list, (f_score[(nx, ny)], (nx, ny)))
        
        return []

    def draw(self, surface):
        image = self.current_animation.get_image()
        image = pygame.transform.scale(image, (image.get_width()*2, image.get_height()*2))

        image_rect = image.get_rect(midbottom=self.rect.midbottom)

        if not self.facing_left:  # 오른쪽을 바라보는 경우에만 flip
            image = pygame.transform.flip(image, True, False)
        
        surface.blit(image, image_rect.topleft)
        pygame.draw.rect(surface, RED, self.rect, 2)

        # 체력 바 그리기
        health_bar_width = self.rect.width
        health_bar_height = 5
        health_ratio = self.health / 100
        current_health_bar_width = int(health_bar_width * health_ratio)

        health_bar_rect = pygame.Rect(self.rect.left, self.rect.bottom + 5, health_bar_width, health_bar_height)
        current_health_bar_rect = pygame.Rect(self.rect.left, self.rect.bottom + 5, current_health_bar_width, health_bar_height)

        pygame.draw.rect(surface, BLACK, health_bar_rect)
        pygame.draw.rect(surface, RED, current_health_bar_rect)




class Button:
    def __init__(self, text, pos, font, bg="black"):
        self.x, self.y = pos
        self.font = pygame.font.Font(None, font)
        self.bg = bg
        self.hovered = False
        self.clicked = False
        self.click_released = False
        self.change_text(text)

    def change_text(self, text):
        self.text = self.font.render(text, True, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self, screen):
        bg = self.bg
        if self.clicked:
            bg = CLICK_COLOR
        elif self.hovered:
            bg = HOVER_COLOR
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        screen.blit(self.surface, (self.x, self.y))

    def check_hover(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            self.hovered = True
        else:
            self.hovered = False

    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.clicked = True
            self.click_released = False
        if event.type == pygame.MOUSEBUTTONUP:
            if self.clicked and self.hovered:
                self.click_released = True
            self.clicked = False

        return self.click_released


class Game:
    def __init__(self):
        self.tile_map = TileMap(TILE_SIZE, [
            "################",
            "#..............#",
            "#..............#",
            "#..............#",
            "#......##......#",
            "#..............#",
            "#..............#",
            "#..............#",
            "#.............##",
            "######.....#...#",
            "#........###...#",
            "#.......#......#",
            "########......##",
            "#............###",
            "################",
        ])
        self.player = Player(100, SCREEN_HEIGHT - 60 - 10, 30, 60, 6, self.tile_map) #순서: x, y, width, height, speed, tile_map
        self.enemies = [
            Enemy(200, 200, 30, 40, 2, self.tile_map),
           # Enemy(400, 200, 30, 40, 2, self.tile_map),  # 추가된 적
            #Enemy(600, 200, 30, 40, 2, self.tile_map)   # 추가된 적
        ]  # 여러 적을 포함하는 리스트로 변경
        self.current_scene = "menu"  # 초기 화면은 메뉴로 설정
        self.play_button = Button("Play", (350, 300), font=50)
        self.options_button = Button("Options", (350, 400), font=50)
        self.quit_button = Button("Quit", (350, 500), font=50)

    def run(self):
        running = True
        while running:
            delta_time = clock.tick(FPS) / 1000.0  # 델타 타임을 초 단위로 계산
            screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.current_scene == "menu":
                    if self.play_button.click(event):
                        self.current_scene = "play"
                    elif self.quit_button.click(event):
                        running = False

            if self.current_scene == "menu":
                self.render_menu()
            elif self.current_scene == "play":
                keys = pygame.key.get_pressed()
                self.player.move(keys, delta_time, self.enemies)
                
                # 적의 리스트를 순회하며, 사라질 적을 필터링하여 제거
                self.enemies = [enemy for enemy in self.enemies if enemy.move(self.player, delta_time)]

                self.tile_map.draw(screen)
                self.player.draw(screen)
                
                for enemy in self.enemies:
                    enemy.draw(screen)

            pygame.display.flip()
        
        pygame.quit()

    def render_menu(self):
        self.play_button.check_hover()
        self.play_button.show(screen)
        self.options_button.check_hover()
        self.options_button.show(screen)
        self.quit_button.check_hover()
        self.quit_button.show(screen)



def manhattan_distance(start, goal):
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

def can_move_diagonal(tile_map, current, row_offset, col_offset):
    row_check = current[1] + row_offset
    col_check = current[0] + col_offset

    # 적의 위쪽과 아래쪽 타일이 모두 장애물에 부딪히지 않도록 검사
    if (
        row_check < 0 or row_check >= len(tile_map.tile_map) - 1 or
        col_check < 0 or col_check >= len(tile_map.tile_map[0]) - 1
    ):
        return False

    # 이동 후 대각선의 두 타일이 모두 장애물에 걸리지 않도록 체크
    if tile_map.is_obstacle(col_check, row_check) or tile_map.is_obstacle(col_check, row_check + 1):
        return False
    if tile_map.is_obstacle(current[0], row_check) or tile_map.is_obstacle(current[0], row_check + 1):
        return False
    if tile_map.is_obstacle(col_check, current[1]) or tile_map.is_obstacle(col_check, current[1] + 1):
        return False

    return True

if __name__ == "__main__":
    game = Game()
    game.run()
