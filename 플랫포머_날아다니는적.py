import pygame
import heapq

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
GREY = (128, 128, 128)

# FPS 설정
clock = pygame.time.Clock()
FPS = 60

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


class Player:
    def __init__(self, x, y, width, height, speed, tile_map):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.gravity = 0.8
        self.jump_power = -15
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.tile_map = tile_map

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
        else:
            self.velocity_x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power

        self.velocity_y += self.gravity
        self.update_position()

    def update_position(self):
        # 수평 이동
        self.rect.x += self.velocity_x
        collisions = self.check_collision()
        for tile in collisions:
            if self.velocity_x > 0:  # 오른쪽 이동 중
                self.rect.right = tile.left
            elif self.velocity_x < 0:  # 왼쪽 이동 중
                self.rect.left = tile.right

        # 수직 이동
        self.rect.y += self.velocity_y
        self.on_ground = False
        collisions = self.check_collision()
        for tile in collisions:
            if self.velocity_y > 0:  # 아래로 떨어지는 중
                self.rect.bottom = tile.top
                self.velocity_y = 0
                self.on_ground = True
            elif self.velocity_y < 0:  # 위로 점프 중
                self.rect.top = tile.bottom
                self.velocity_y = 0

    def check_collision(self):
        return [tile for tile in self.tile_map.tiles if self.rect.colliderect(tile)]

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)


class Enemy:
    def __init__(self, x, y, width, height, speed, tile_map):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.tile_map = tile_map
        self.path = []

    def move(self, player):
        start = (int(self.rect.x // TILE_SIZE), int(self.rect.y // TILE_SIZE))
        goal = (int(player.rect.x // TILE_SIZE), int(player.rect.y // TILE_SIZE))
        if not self.path or start != self.path[-1]:  # 경로가 없거나 목표 위치가 변경된 경우
            self.path = self.astar(start, goal)

        if self.path:
            next_tile = self.path[0]
            target_x = next_tile[0] * TILE_SIZE
            target_y = next_tile[1] * TILE_SIZE

            # 수평 이동
            if self.rect.x < target_x:
                self.rect.x += self.speed
            elif self.rect.x > target_x:
                self.rect.x -= self.speed

            # 수직 이동
            if self.rect.y < target_y:
                self.rect.y += self.speed
            elif self.rect.y > target_y:
                self.rect.y -= self.speed

            # 경로를 따라 이동 중에 목표 타일에 도달한 경우 경로 업데이트
            if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
                self.rect.x, self.rect.y = target_x, target_y
                self.path.pop(0)  # 경로의 첫 번째 타일 제거

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
        pygame.draw.rect(surface, RED, self.rect)


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
        self.enemy = Enemy(200, 200, TILE_SIZE, TILE_SIZE * 2, 2, self.tile_map)

    def run(self):
        running = True
        while running:
            screen.fill(WHITE)
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.enemy.move(self.player)

            self.tile_map.draw(screen)
            self.player.draw(screen)
            self.enemy.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()


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
