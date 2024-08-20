import pygame
import heapq
import sys

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
    def __init__(self, image, num_frames, frame_duration=0.1):
        self.sprite_sheet = image
        self.num_frames = num_frames
        self.frame_width = self.sprite_sheet.get_width() // self.num_frames
        self.frame_height = self.sprite_sheet.get_height()
        self.frames = []
        self.current_frame = 0
        self.frame_duration = frame_duration  # 각 프레임의 지속 시간 (초)
        self.frame_timer = 0
        self.load_frames()

    def load_frames(self):
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
        self.gravity = 20 * 60
        self.jump_power = -800
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.tile_map = tile_map

        # 애니메이션 설정
        self.idle_animation = Animation(pygame.image.load('_Idle.png'), num_frames=10, frame_duration=0.1)
        self.run_animation = Animation(pygame.image.load('_Run.png'), num_frames=10, frame_duration=0.1)
        self.jump_animation = Animation(pygame.image.load('_Jump.png'), num_frames=3, frame_duration=0.1)
        self.fall_animation = Animation(pygame.image.load('_Fall.png'), num_frames=3, frame_duration=0.1)
        self.current_animation = self.idle_animation
        self.facing_right = True

        # 초기 on_ground 상태 설정
        self.check_on_ground()

    def move(self, keys, delta_time):
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed * delta_time
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed * delta_time
            self.facing_right = True
        else:
            self.velocity_x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        self.velocity_y += self.gravity * delta_time
        self.update_position(delta_time)
        self.update_animation(delta_time)

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

    def check_collision(self):
        return [tile for tile in self.tile_map.tiles if self.rect.colliderect(tile)]

    def draw(self, surface):
        image = self.current_animation.get_image()
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        image_rect = image.get_rect(midbottom=self.rect.midbottom)
        surface.blit(image, image_rect.topleft)



class Enemy:
    def __init__(self, x, y, width, height, speed, tile_map):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed * 60  # 속도 보정
        self.tile_map = tile_map
        self.path = []

        # 애니메이션 설정 (이미 각각의 파일로 제공된 애니메이션 프레임 사용)
        idle_frames = [
            pygame.image.load('LightBandit_Idle_0.png'),
            pygame.image.load('LightBandit_Idle_1.png'),
            pygame.image.load('LightBandit_Idle_2.png'),
            pygame.image.load('LightBandit_Idle_3.png')
        ]
        self.idle_animation = Animation(idle_frames, frame_rate=10)  # 초당 10 프레임

        run_frames = [
            pygame.image.load('LightBandit_Run_0.png'),
            pygame.image.load('LightBandit_Run_1.png'),
            pygame.image.load('LightBandit_Run_2.png'),
            pygame.image.load('LightBandit_Run_3.png'),
            pygame.image.load('LightBandit_Run_4.png'),
            pygame.image.load('LightBandit_Run_5.png'),
            pygame.image.load('LightBandit_Run_6.png'),
            pygame.image.load('LightBandit_Run_7.png')
        ]
        self.run_animation = Animation(run_frames, frame_rate=10)  # 초당 10 프레임

        self.current_animation = self.idle_animation
        self.facing_left = True

    def move(self, player, delta_time):
        start = (int(self.rect.x // TILE_SIZE), int(self.rect.y // TILE_SIZE))
        goal = (int(player.rect.x // TILE_SIZE), int(player.rect.y // TILE_SIZE))

        if self.get_distance_to_player(player) > MIN_DISTANCE_TO_PLAYER:
            if not self.path or start != self.path[-1]:  # 경로가 없거나 목표 위치가 변경된 경우
                self.path = self.astar(start, goal)

            if self.path:
                next_tile = self.path[0]
                target_x = next_tile[0] * TILE_SIZE
                target_y = next_tile[1] * TILE_SIZE

                moving_horizontally = False
                moving_vertically = False

                # 수평 이동
                if self.rect.x < target_x:
                    self.rect.x += self.speed * delta_time
                    moving_horizontally = True
                    self.facing_left = False
                elif self.rect.x > target_x:
                    self.rect.x -= self.speed * delta_time
                    moving_horizontally = True
                    self.facing_left = True

                # 수직 이동
                if self.rect.y < target_y:
                    self.rect.y += self.speed * delta_time
                    moving_vertically = True
                elif self.rect.y > target_y:
                    self.rect.y -= self.speed * delta_time
                    moving_vertically = True

                # 경로를 따라 이동 중에 목표 타일에 도달한 경우 경로 업데이트
                if abs(self.rect.x - target_x) < self.speed * delta_time and abs(self.rect.y - target_y) < self.speed * delta_time:
                    self.rect.x, self.rect.y = target_x, target_y
                    self.path.pop(0)  # 경로의 첫 번째 타일 제거

                # 애니메이션 업데이트
                if moving_horizontally or moving_vertically:
                    self.current_animation = self.run_animation
                else:
                    self.current_animation = self.idle_animation

        self.current_animation.update(delta_time)

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
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
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
        if not self.facing_left:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, self.rect.topleft)


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
        self.player = Player(100, SCREEN_HEIGHT - 60 - 10, 50, 60, 5, self.tile_map)
        self.enemy = Enemy(200, 200, TILE_SIZE, TILE_SIZE * 2, 2, self.tile_map)  # 날아다니는 적
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
                self.player.move(keys, delta_time)
                self.enemy.move(self.player, delta_time)

                self.tile_map.draw(screen)
                self.player.draw(screen)
                self.enemy.draw(screen)

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
