import pygame
import heapq
from utils import manhattan_distance, can_move_diagonal

# 색상 정의
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

class Enemy:
    def __init__(self, x, y, enemy_type, tile_map):
        if enemy_type == 'basic':
            self.rect = pygame.Rect(x, y, 50, 100)
            self.color = RED
            self.speed = 2
        elif enemy_type == 'fast':
            self.rect = pygame.Rect(x, y, 40, 80)
            self.color = YELLOW
            self.speed = 4
        elif enemy_type == 'strong':
            self.rect = pygame.Rect(x, y, 60, 120)
            self.color = PURPLE
            self.speed = 1

        self.tile_map = tile_map
        self.path = []

    def move(self, player):
        start = (int(self.rect.x // self.tile_map.tile_size), int(self.rect.y // self.tile_map.tile_size))
        goal = (int(player.rect.x // self.tile_map.tile_size), int(player.rect.y // self.tile_map.tile_size))

        if self.get_distance_to_player(player) > self.tile_map.tile_size:
            if not self.path or start != self.path[-1]:
                self.path = self.astar(start, goal)

            if self.path:
                next_tile = self.path[0]
                target_x = next_tile[0] * self.tile_map.tile_size
                target_y = next_tile[1] * self.tile_map.tile_size

                if self.rect.x < target_x:
                    self.rect.x += self.speed
                elif self.rect.x > target_x:
                    self.rect.x -= self.speed

                if self.rect.y < target_y:
                    self.rect.y += self.speed
                elif self.rect.y > target_y:
                    self.rect.y -= self.speed

                if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
                    self.rect.x, self.rect.y = target_x, target_y
                    self.path.pop(0)

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
        pygame.draw.rect(surface, self.color, self.rect)
