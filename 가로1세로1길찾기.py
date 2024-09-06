import pygame
import heapq
import math

# 초기화
pygame.init()
pygame.font.init()

# 화면 설정
TILE_SIZE = 32
COLS = 55  # 가로 타일 개수
ROWS = 27  # 세로 타일 개수
WIDTH = COLS * TILE_SIZE  # 가로 크기
HEIGHT = ROWS * TILE_SIZE  # 세로 크기
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Pathfinding")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
FONT = pygame.font.Font( "PretendardVariable.ttf", 10)  # 작은 폰트 사이즈로 변경
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
        self.h = 0
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
        if self.g != float('inf') and self.h != 0:
            f_text = FONT.render(f"f:{int(self.f)}", True, BLACK)
            g_text = FONT.render(f"g:{int(self.g)}", True, BLACK)
            h_text = FONT.render(f"h:{int(self.h)}", True, BLACK)
            win.blit(f_text, (self.x, self.y + 0))
            win.blit(g_text, (self.x, self.y + 100))
            win.blit(h_text, (self.x, self.y + 16))

    def update_neighbors(self, grid, closed_set):
        self.neighbors = []

        # Vertical & horizontal moves
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_obstacle and grid[self.row + 1][self.col] not in closed_set:  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle and grid[self.row - 1][self.col] not in closed_set:  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < COLS - 1 and not grid[self.row][self.col + 1].is_obstacle and grid[self.row][self.col + 1] not in closed_set:  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle and grid[self.row][self.col - 1] not in closed_set:  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        # Diagonal moves with obstacle checks
        if self.row > 0 and self.col > 0:  # UP-LEFT
            if (not grid[self.row - 1][self.col].is_obstacle and 
                not grid[self.row][self.col - 1].is_obstacle and
                not grid[self.row - 1][self.col - 1].is_obstacle and
                grid[self.row - 1][self.col - 1] not in closed_set):
                self.neighbors.append(grid[self.row - 1][self.col - 1])

        if self.row > 0 and self.col < COLS - 1:  # UP-RIGHT
            if (not grid[self.row - 1][self.col].is_obstacle and 
                not grid[self.row][self.col + 1].is_obstacle and
                not grid[self.row - 1][self.col + 1].is_obstacle and
                grid[self.row - 1][self.col + 1] not in closed_set):
                self.neighbors.append(grid[self.row - 1][self.col + 1])

        if self.row < ROWS - 1 and self.col > 0:  # DOWN-LEFT
            if (not grid[self.row + 1][self.col].is_obstacle and 
                not grid[self.row][self.col - 1].is_obstacle and
                not grid[self.row + 1][self.col - 1].is_obstacle and
                grid[self.row + 1][self.col - 1] not in closed_set):
                self.neighbors.append(grid[self.row + 1][self.col - 1])

        if self.row < ROWS - 1 and self.col < COLS - 1:  # DOWN-RIGHT
            if (not grid[self.row + 1][self.col].is_obstacle and 
                not grid[self.row][self.col + 1].is_obstacle and
                not grid[self.row + 1][self.col + 1].is_obstacle and
                grid[self.row + 1][self.col + 1] not in closed_set):
                self.neighbors.append(grid[self.row + 1][self.col + 1])



def heuristic(p1, p2, start, prefer_left, step_count):
    y1, x1 = p1  # 현재 노드의 좌표
    y2, x2 = p2  # 목표 지점의 좌표
    
    D = 1  # 직선 이동 비용
    D2 = 1.4  # 대각선 이동 비용
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)

    h_value = (D * (dx + dy) + (D2 - 2 * D) * min(dx, dy))
    start_col = start.get_pos()[1]
    
    if prefer_left:
        if start_col > x2:
            if x1 > start_col:
                h_value *= 2  # 왼쪽이 선호되므로 오른쪽 노드의 h 값을 증가시킴
        else:
            if x1 > x2:#목표점 현재노드
                h_value *= 2  # 왼쪽이 선호되므로 오른쪽 노드의 h 값을 증가시킴
    else:
        if start_col >= x2:
            if x1 < x2:#현재노드 목표점
                h_value *= 5  # 오른쪽이 선호되므로 왼쪽 노드의 h 값을 증가시킴
        else:
            if x1 < start_col:
                h_value *=3 # 오른쪽이 선호되므로 왼쪽 노드의 h 값을 증가시킴

    return h_value

def _heuristic(p1, p2, start, prefer_left, step_count):
    y1, x1 = p1  # 현재 노드의 좌표
    y2, x2 = p2  # 목표 지점의 좌표
    
    D = 1  # 직선 이동 비용
    D2 = 1.4  # 대각선 이동 비용
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)

    h_value = (D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)) 
    
    start_col = start.get_pos()[1]  # 열 (col) 좌표(=x좌표)를 사용해야 함
    
    if not prefer_left and x1 < start_col:
        h_value *=3 # 오른쪽이 선호되므로 왼쪽 노드의 h 값을 증가시킴
    elif prefer_left and x1 > start_col:
        h_value *= 2  # 왼쪽이 선호되므로 오른쪽 노드의 h 값을 증가시킴

    return h_value

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]  # 역순으로 반환하여 시작점에서 끝점으로의 경로를 반환

def a_star_algorithm(draw, grid, start, end, step_by_step=False):
    count = 0
    step_count = 0  # 탐색 단계 카운트
    open_set = []
    closed_set = set()  # 닫힌 목록 추가
    heapq.heappush(open_set, (0, count, start))
    came_from = {}

    start.g = 0
    start.h = heuristic(start.get_pos(), end.get_pos(), start, False, step_count)
    start.f = start.g + start.h

    open_set_hash = set()
    open_set_hash.add(start)

    while open_set:

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)
        closed_set.add(current)  # 현재 노드를 닫힌 목록에 추가

        if current == end:
            return reconstruct_path(came_from, current)

        for neighbor in current.neighbors:
            temp_g_score = current.g + (math.sqrt(2) if neighbor.row != current.row and neighbor.col != current.col else 1)

            if temp_g_score < neighbor.g:
                came_from[neighbor] = current
                neighbor.g = temp_g_score
                neighbor.h = heuristic(neighbor.get_pos(), end.get_pos(), start, False, step_count)
                neighbor.f = neighbor.g + neighbor.h

                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)

        draw()

        if current != start:
            current.color = GREY

        step_count += 1  # 탐색 단계 증가

    return []

def make_grid():
    grid = []
    layout = [
        "#######################################################",
        "#.....................................................#",
        "#.....................................................#",
        "#.....................................................#",
        "#.....................................................#",
        "#.....................................................#",
        "#.........########....................................#",
        "#......................................######.........#",
        "#.....................................................#",
        "#.....................................................#",
        "#######...................#################...........#",
        "#.........#######.....................................#",
        "#.....................................................#",
        "#............................................########.#",
        "#................###..###.............................#",
        "#............................###...###................#",
        "#..........................................#..........#",
        "#..........................................#..........#",
        "#..................#####...................#..........#",
        "#..........................................#..........#",
        "#...................................#####.............#",
        "#.......#########.....................................#",
        "#.....................................................#",
        "#.....................................................#",
        "#.....................................................#",
        "#....................................................##",
        "#######################################################",
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
        #start.color = WHITE  # 이전 위치를 지우기 위해 색상 리셋
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
                    closed_set = set()  # 여기에 closed_set을 정의합니다.
                    
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid, closed_set)  # 닫힌 목록 전달

                    path = a_star_algorithm(lambda: draw(WIN, grid, start, end), grid, start, end, step_by_step=True)
                    if path:
                        move_along_path(WIN, path, grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid()

    pygame.quit()

main()
