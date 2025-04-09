GRID_SIZE = (10, 5)

DIRECTIONS = [
    (0, 1), (1, 0), (0, -1), (-1, 0),  # 수직 및 수평 방향 (상, 우, 하, 좌)
    (1, 1), (-1, -1), (1, -1), (-1, 1)  # 대각선 방향 (우하, 좌상, 우상, 좌하)
]

# MinHeap이라는 이름의 클래스를 만듭니다.
# MinHeap은 숫자들을 모아서 가장 작은 숫자를 쉽게 꺼낼 수 있도록 해줍니다.
class MinHeap:
    def __init__(self):
        self.heap = []# (f, Node_position) 형태로 저장

    def push(self, value):
        # 새로운 숫자를 리스트의 끝에 추가합니다.
        self.heap.append(value)
        # 새로 추가한 숫자가 제자리를 찾도록 위
        # 
        # 
        # 로 올립니다.
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        # 리스트에 숫자가 여러 개 있을 때, 가장 작은 숫자를 꺼내고 리스트를 정리합니다.
        if len(self.heap) > 1:
            # 가장 작은 숫자와 마지막 숫자의 자리를 바꿉니다.
            self._swap(0, len(self.heap) - 1)
            # 마지막에 있는 숫자를 리스트에서 꺼냅니다. 이것이 우리가 원하는 가장 작은 숫자입니다.
            min_value = self.heap.pop()
            # 그리고 리스트를 다시 정리합니다.
            self._heapify_down(0)
        elif self.heap:
            # 리스트에 숫자가 하나만 있다면, 그것을 꺼내서 반환합니다.
            min_value = self.heap.pop()
        else:
            # 만약 리스트가 비어 있다면, None을 반환합니다.
            min_value = None
        return min_value

    def _heapify_up(self, index):
        # 이 함수는 새로 추가된 숫자가 제자리를 찾도록 위로 올라가게 합니다.
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index] < self.heap[parent_index]:
            # 부모와 자식의 위치를 바꿉니다.
            self._swap(index, parent_index)
            # 그리고 부모의 위치에서 다시 위로 올라갑니다.
            self._heapify_up(parent_index)

    def _heapify_down(self, index):
        # 이 함수는 작은 숫자가 위로 가도록 아래로 내려가면서 정리합니다.
        left_child_index = 2 * index + 1
        right_child_index = 2 * index + 2
        smallest = index

        if left_child_index < len(self.heap) and self.heap[left_child_index] < self.heap[smallest]:
            smallest = left_child_index
        if right_child_index < len(self.heap) and self.heap[right_child_index] < self.heap[smallest]:
            smallest = right_child_index

        if smallest != index:
            # 현재 위치의 숫자가 자식들보다 크면 자리를 바꿉니다.
            self._swap(index, smallest)
            # 그리고 그 자식 자리에서 다시 아래로 내려가면서 정리합니다.
            self._heapify_down(smallest)

    def _swap(self, i, j):
        # 리스트에서 두 숫자의 위치를 바꿉니다.
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def is_empty(self):
        # 리스트가 비어 있는지 확인합니다.
        return len(self.heap) == 0


# A* 알고리즘을 사용하여 최단 경로를 찾는 함수입니다.
def a_star(start, goal, grid_map):
    open_set = MinHeap()
    open_set.push((0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    closed_set = set()
    
    while not open_set.is_empty():
        current = open_set.pop()[1]

        # 경로를 모두 찾았으면 경로를 return
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        
        closed_set.add(current)
        
        # 이웃 노드들을 살펴봅니다.
        for neighbor in get_neighbors(current, grid_map, closed_set):
            if current[0] != neighbor[0] and current[1] != neighbor[1]:
                movement_cost = 14
            else:
                movement_cost = 10
            tentative_g_score = g_score[current] + movement_cost
            
            # 이웃 노드가 처음 방문되었거나 더 좋은 경로가 발견되면 정보를 갱신합니다.
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                open_set.push((f_score[neighbor], neighbor))
    
    return []  # 목표점에 도달할 수 없는 경우 None을 반환합니다.
    

def get_neighbors(node, grid_map, closed_set):
    neighbors = []
    
    for direction in DIRECTIONS:
        neighbor = (node[0] + direction[0], node[1] + direction[1])

        # 대각선 이동을 할 때, 직선 이동이 모두 가능한지 확인
        if abs(direction[0]) == 1 and abs(direction[1]) == 1:
            adjacent1 = (node[0] + direction[0], node[1])
            adjacent2 = (node[0], node[1] + direction[1])

            # 만약 직선 방향의 둘 중 하나라도 벽(장애물)이라면, 대각선 이동을 막습니다.
            if not (is_walkable(adjacent1, grid_map) and is_walkable(adjacent2, grid_map)):
                continue

        if is_walkable(neighbor, grid_map) and neighbor not in closed_set:
            neighbors.append(neighbor)
    
    return neighbors


# 휴리스틱 함수입니다. 이 함수는 노드에서 목표점까지의 예상 거리를 계산합니다.
# 여기서는 맨해튼 거리와 대각선 거리를 섞어서 사용합니다.
def heuristic(node, goal):
    dx = abs(node[0] - goal[0])
    dy = abs(node[1] - goal[1])
    return 10 * (dx + dy) + (14 - 2 * 10) * min(dx, dy)


# 그리드에서 해당 노드가 맵 안에 있고 장애물이 아닌지 검사
def is_walkable(node, grid_map):
    x, y = node
    return 0 <= x < GRID_SIZE[0] and 0 <= y < GRID_SIZE[1] and not grid_map[node]["wall"]



"""----------------출력을 위한 코드들입니다.---------------"""

def print_grid(grid_map, path=None):
    for y in range(GRID_SIZE[1]):
        for x in range(GRID_SIZE[0]):
            if path and (x, y) in path:
                print("P", end=" ")  # 경로가 지나가는 곳은 'P'로 표시
            elif grid_map[(x, y)]["wall"]:
                print("#", end=" ")  # 장애물은 '#'으로 표시
            else:
                print(".", end=" ")  # 이동 가능한 곳은 '.'로 표시
        print()

# 사용 예시:
grid_map = {
    (0, 0): {"wall": False},
    (1, 0): {"wall": False},
    (2, 0): {"wall": False},
    (3, 0): {"wall": False},
    (4, 0): {"wall": False},
    (5, 0): {"wall": False},
    (6, 0): {"wall": False},
    (7, 0): {"wall": False},
    (8, 0): {"wall": False},
    (9, 0): {"wall": True},  # 오른쪽 끝에 벽 추가
    (0, 1): {"wall": False},
    (1, 1): {"wall": True},   # 중간에 벽 추가
    (2, 1): {"wall": False},
    (3, 1): {"wall": False},
    (4, 1): {"wall": False},
    (5, 1): {"wall": True},   # 중간에 벽 추가
    (6, 1): {"wall": False},
    (7, 1): {"wall": False},
    (8, 1): {"wall": False},
    (9, 1): {"wall": True},   # 오른쪽 끝에 벽 추가
    (0, 2): {"wall": False},
    (1, 2): {"wall": False},
    (2, 2): {"wall": False},
    (3, 2): {"wall": True},   # 중간에 벽 추가
    (4, 2): {"wall": False},
    (5, 2): {"wall": False},
    (6, 2): {"wall": True},   # 중간에 벽 추가
    (7, 2): {"wall": False},
    (8, 2): {"wall": False},
    (9, 2): {"wall": True},   # 오른쪽 끝에 벽 추가
    (0, 3): {"wall": False},
    (1, 3): {"wall": False},
    (2, 3): {"wall": False},
    (3, 3): {"wall": False},
    (4, 3): {"wall": True},   # 중간에 벽 추가
    (5, 3): {"wall": False},
    (6, 3): {"wall": False},
    (7, 3): {"wall": False},
    (8, 3): {"wall": False},
    (9, 3): {"wall": True},   # 오른쪽 끝에 벽 추가
    (0, 4): {"wall": True},   # 왼쪽 끝에 벽 추가
    (1, 4): {"wall": True},   # 왼쪽 끝에 벽 추가
    (2, 4): {"wall": True},   # 왼쪽 끝에 벽 추가
    (3, 4): {"wall": True},   # 중간에 벽 추가
    (4, 4): {"wall": True},   # 중간에 벽 추가
    (5, 4): {"wall": True},   # 중간에 벽 추가
    (6, 4): {"wall": False},
    (7, 4): {"wall": False},
    (8, 4): {"wall": False},
    (9, 4): {"wall": True}    # 오른쪽 끝에 벽 추가
}

start = (3, 3)  # 시작점
goal = (7, 4)  # 목표점

path = a_star(start, goal, grid_map)
print_grid(grid_map, path)
