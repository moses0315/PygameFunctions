import pygame
import heapq

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 20, 20
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

    def draw(self, win, is_start_or_end=False, is_path=False):
        if is_start_or_end or is_path:
            pygame.draw.rect(win, self.color, (self.x, self.y, TILE_SIZE, TILE_SIZE * 2))
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, TILE_SIZE, TILE_SIZE))

    def can_move_diagonal(self, grid, row_offset, col_offset):
        row_check = self.row + row_offset
        col_check = self.col + col_offset

        # 그리드 경계를 벗어나지 않도록 체크
        if (
            row_check < 0 or row_check >= ROWS - 1 or
            col_check < 0 or col_check >= COLS - 1 or
            self.row + 1 >= ROWS or self.col + 1 >= COLS
        ):
            return False

        # 대각선 이동 가능 여부 확인 (모서리에 걸리지 않도록)
        if grid[self.row][col_check].is_obstacle or grid[self.row + 1][col_check].is_obstacle:
            return False
        if grid[row_check][self.col].is_obstacle or grid[row_check + 1][self.col].is_obstacle:
            return False

        # 대각선 방향으로도 장애물이 없어야 함
        if grid[row_check][col_check].is_obstacle or grid[row_check + 1][col_check].is_obstacle:
            return False

        return True

    def update_neighbors(self, grid):
        self.neighbors = []

        # Vertical & horizontal moves
        if self.row < ROWS - 2 and not grid[self.row + 2][self.col].is_obstacle:  # DOWN
            if not grid[self.row + 1][self.col].is_obstacle:
                self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle:  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < COLS - 1 and not grid[self.row][self.col + 1].is_obstacle:  # RIGHT
            if self.row < ROWS - 1 and not grid[self.row + 1][self.col + 1].is_obstacle:
                self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle:  # LEFT
            if self.row < ROWS - 1 and not grid[self.row + 1][self.col - 1].is_obstacle:
                self.neighbors.append(grid[self.row][self.col - 1])

        # Diagonal moves with obstacle checks
        if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_obstacle:  # UP-LEFT
            if self.can_move_diagonal(grid, -1, -1):
                self.neighbors.append(grid[self.row - 1][self.col - 1])

        if self.row > 0 and self.col < COLS - 1 and not grid[self.row - 1][self.col + 1].is_obstacle:  # UP-RIGHT
            if self.can_move_diagonal(grid, -1, 1):
                self.neighbors.append(grid[self.row - 1][self.col + 1])

        if self.row < ROWS - 2 and self.col > 0 and not grid[self.row + 2][self.col - 1].is_obstacle:  # DOWN-LEFT
            if self.can_move_diagonal(grid, 1, -1):
                self.neighbors.append(grid[self.row + 1][self.col - 1])

        if self.row < ROWS - 2 and self.col < COLS - 1 and not grid[self.row + 2][self.col + 1].is_obstacle:  # DOWN-RIGHT
            if self.can_move_diagonal(grid, 1, 1):
                self.neighbors.append(grid[self.row + 1][self.col + 1])

def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw(is_path=True)

def a_star_algorithm(draw, grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}

    start.g = 0
    start.f = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        # 목표 도달 여부 검사
        if current == end or (current.row + 1 == end.row and current.col == end.col):
            reconstruct_path(came_from, end, draw)
            return True

        for neighbor in current.neighbors:
            temp_g_score = current.g + 1

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

    return False

def make_grid():
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(COLS):
            node = Node(i, j)
            grid[i].append(node)
    return grid

def draw_grid(win):
    for i in range(ROWS):
        pygame.draw.line(win, GREY, (0, i * TILE_SIZE), (WIDTH, i * TILE_SIZE))
    for j in range(COLS):
        pygame.draw.line(win, GREY, (j * TILE_SIZE, 0), (j * TILE_SIZE, HEIGHT))

def draw(win, grid, start, end, is_path=False):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            if node == start or node == end:
                node.draw(win, is_start_or_end=True)
            elif is_path and node.color == BLUE:
                node.draw(win, is_path=True)
            else:
                node.draw(win)
    draw_grid(win)
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = y // TILE_SIZE
    col = x // TILE_SIZE
    return row, col

def main():
    grid = make_grid()
    start = None
    end = None

    run = True
    started = False

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
                    if row < ROWS - 1:  # Ensure the end point is not at the bottom edge where the character wouldn't fit
                        end = node
                        end.make_end()

                elif node != end and node != start:
                    node.make_obstacle()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT CLICK
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    a_star_algorithm(lambda is_path=False: draw(WIN, grid, start, end, is_path), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid()

    pygame.quit()

main()
