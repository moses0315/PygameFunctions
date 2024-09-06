import pygame
import heapq
import math

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 15, 16  # 맵의 행과 열 크기에 맞게 설정
TILE_SIZE = WIDTH // COLS
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Pathfinding")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)

# 노드 클래스 정의
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * TILE_SIZE
        self.y = row * TILE_SIZE
        self.color = WHITE
        self.neighbors = []
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.came_from = None
        self.is_obstacle = False

    def get_pos(self):
        return self.row, self.col

    def reset(self):
        self.color = WHITE
        self.g = float('inf')
        self.f = float('inf')
        self.came_from = None
        self.is_obstacle = False

    def make_start(self):
        self.color = GREEN

    def make_end(self):
        self.color = RED

    def make_obstacle(self):
        self.color = BLACK
        self.is_obstacle = True

    def make_path(self):
        self.color = BLUE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, TILE_SIZE, TILE_SIZE))

    def update_neighbors(self, grid):
        self.neighbors = []

        # Vertical & horizontal moves
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_obstacle:  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle:  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < COLS - 1 and not grid[self.row][self.col + 1].is_obstacle:  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle:  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        # Diagonal moves with obstacle checks
        if self.row > 0 and self.col > 0:  # UP-LEFT
            if (not grid[self.row - 1][self.col].is_obstacle and 
                not grid[self.row][self.col - 1].is_obstacle and
                not grid[self.row - 1][self.col - 1].is_obstacle):
                self.neighbors.append(grid[self.row - 1][self.col - 1])

        if self.row > 0 and self.col < COLS - 1:  # UP-RIGHT
            if (not grid[self.row - 1][self.col].is_obstacle and 
                not grid[self.row][self.col + 1].is_obstacle and
                not grid[self.row - 1][self.col + 1].is_obstacle):
                self.neighbors.append(grid[self.row - 1][self.col + 1])

        if self.row < ROWS - 1 and self.col > 0:  # DOWN-LEFT
            if (not grid[self.row + 1][self.col].is_obstacle and 
                not grid[self.row][self.col - 1].is_obstacle and
                not grid[self.row + 1][self.col - 1].is_obstacle):
                self.neighbors.append(grid[self.row + 1][self.col - 1])

        if self.row < ROWS - 1 and self.col < COLS - 1:  # DOWN-RIGHT
            if (not grid[self.row + 1][self.col].is_obstacle and 
                not grid[self.row][self.col + 1].is_obstacle and
                not grid[self.row + 1][self.col + 1].is_obstacle):
                self.neighbors.append(grid[self.row + 1][self.col + 1])

def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    D = 1  # 직선 이동 비용
    D2 = math.sqrt(2)  # 대각선 이동 비용 (약 1.414)
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]  # 역순으로 반환하여 시작점에서 끝점으로의 경로를 반환

def a_star_algorithm(draw, grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}
    
    # 시작 노드의 g와 f값 설정
    start.g = 0
    start.f = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}  # open_set에 대한 빠른 조회를 위한 해시셋
    closed_set = set()  # 이미 방문한 노드를 기록하는 셋

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        if current == end:
            return reconstruct_path(came_from, current)

        closed_set.add(current)  # 현재 노드를 closed_set에 추가

        for neighbor in current.neighbors:
            if neighbor in closed_set:
                continue  # 이미 방문한 노드는 무시

            if neighbor.row != current.row and neighbor.col != current.col:  # 대각선 이동인 경우
                temp_g_score = current.g + math.sqrt(2)  # 대각선 이동 비용 (약 1.414)
            else:  # 직선 이동인 경우
                temp_g_score = current.g + 1  # 직선 이동 비용

            if temp_g_score < neighbor.g:
                came_from[neighbor] = current
                neighbor.g = temp_g_score
                neighbor.f = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)

        draw()

        if current != start:
            current.color = GREY

    return []

def make_grid():
    grid = []
    layout = [
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
    ]
    
    for i, line in enumerate(layout):
        grid.append([])
        for j, char in enumerate(line):
            node = Node(i, j)
            if char == "#":
                node.make_obstacle()
            grid[i].append(node)
    return grid

def draw_grid(win):
    for i in range(ROWS):
        pygame.draw.line(win, GREY, (0, i * TILE_SIZE), (WIDTH, i * TILE_SIZE))
    for j in range(COLS):
        pygame.draw.line(win, GREY, (j * TILE_SIZE, 0), (j * TILE_SIZE, HEIGHT))

def draw(win, grid, start, end):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win)
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = y // TILE_SIZE
    col = x // TILE_SIZE
    return row, col

def move_along_path(win, path, grid, start, end):
    for node in path:
        start.color = WHITE  # 이전 위치를 지우기 위해 색상 리셋
        draw(win, grid, start, end)
        # 부드럽게 이동
        while start.x != node.x or start.y != node.y:
            if start.x < node.x:
                start.x += 1
            elif start.x > node.x:
                start.x -= 1

            if start.y < node.y:
                start.y += 1
            elif start.y > node.y:
                start.y -= 1

            draw(win, grid, start, end)
            pygame.time.delay(10)  # 이동 속도 조절을 위해 딜레이 추가

        start = node  # 행위자가 이동
        start.make_start()  # 현재 위치를 시작점 색상으로 변경

def main():
    grid = make_grid()
    start = None
    end = None

    run = True

    while run:
        draw(WIN, grid, start, end)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # LEFT CLICK
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    # 목표 지점의 왼쪽이나 오른쪽 타일을 목표 지점으로 변경
                    if col > 0 and not grid[row][col - 1].is_obstacle:
                        end = grid[row][col - 1]
                    elif col < COLS - 1 and not grid[row][col + 1].is_obstacle:
                        end = grid[row][col + 1]
                    else:
                        end = None  # 도달 불가능한 경우 경로 탐색 실패

                    if end:
                        end.make_end()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    path = a_star_algorithm(lambda: draw(WIN, grid, start, end), grid, start, end)
                    if path:
                        move_along_path(WIN, path, grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid()

    pygame.quit()

main()
