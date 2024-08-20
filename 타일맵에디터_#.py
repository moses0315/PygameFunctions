import pygame
import tkinter as tk
from tkinter import simpledialog

# 초기화
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# 타일맵 크기 및 타일 크기
TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 20, 15

# 타일맵 초기화
tile_map = [['.' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# 타일 이미지 로드
wall_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
wall_image.fill((255, 0, 0))  # 빨간색 벽 타일
floor_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
floor_image.fill((0, 255, 0))  # 초록색 바닥 타일

def draw_tilemap(screen, tile_map):
    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            if tile == '#':
                screen.blit(wall_image, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '.':
                screen.blit(floor_image, (x * TILE_SIZE, y * TILE_SIZE))

def save_tilemap(tile_map):
    root = tk.Tk()
    root.withdraw()
    file_path = simpledialog.askstring("Save Tilemap", "Enter file name:")
    if file_path:
        with open(file_path + ".txt", "w") as file:
            file.write("[\n")
            for row in tile_map:
                file.write(f'    "{''.join(row)}",\n')
            file.write("]\n")
    root.destroy()

# 드래그 상태 변수
dragging = False
current_tile = '.'

# 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
            x, y = event.pos
            grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
            current_tile = '#' if tile_map[grid_y][grid_x] == '.' else '.'
            tile_map[grid_y][grid_x] = current_tile
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            x, y = event.pos
            grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE
            tile_map[grid_y][grid_x] = current_tile
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_tilemap(tile_map)

    screen.fill((0, 0, 0))
    draw_tilemap(screen, tile_map)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
