class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, value):
        self.heap.append(value)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        if len(self.heap) == 0:
            raise IndexError("Heap is empty")
        if len(self.heap) == 1:
            return self.heap.pop()
        
        # 교환: 루트와 마지막 요소를 바꿈
        root_value = self.heap[0]
        self.heap[0] = self.heap.pop()  # 루트에 마지막 요소를 넣음
        self._sift_down(0)  # 루트에서 시작해 힙 속성 유지
        return root_value

    def _sift_up(self, index):
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index] < self.heap[parent_index]:
            # 부모와 현재 노드 교환
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            # 재귀적으로 부모에 대해 sift-up 수행
            self._sift_up(parent_index)

    def _sift_down(self, index):
        left_child_index = 2 * index + 1
        right_child_index = 2 * index + 2
        smallest = index

        if left_child_index < len(self.heap) and self.heap[left_child_index] < self.heap[smallest]:
            smallest = left_child_index
        
        if right_child_index < len(self.heap) and self.heap[right_child_index] < self.heap[smallest]:
            smallest = right_child_index

        if smallest != index:
            # 자식 노드 중 더 작은 것과 교환
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            # 재귀적으로 자식 노드에 대해 sift-down 수행
            self._sift_down(smallest)

    def peek(self):
        if len(self.heap) == 0:
            raise IndexError("Heap is empty")
        return self.heap[0]

    def __len__(self):
        return len(self.heap)

# 사용 예제
min_heap = MinHeap()
min_heap.insert(3)
min_heap.insert(1)
min_heap.insert(6)
min_heap.insert(5)
min_heap.insert(2)
min_heap.insert(4)

print("Min Heap:", min_heap.heap)  # [1, 2, 4, 5, 3, 6]

print("Pop:", min_heap.pop())  # 1
print("Min Heap after pop:", min_heap.heap)  # [2, 3, 4, 5, 6]
