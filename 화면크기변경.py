import pygame
import sys

# Pygame 초기화
pygame.init()

# 이미지 로드
background_image = pygame.image.load('_Idle.png')

# 초기 창 크기 설정
original_width, original_height = 800, 600
screen = pygame.display.set_mode((original_width, original_height), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Window Example")

# 이미지의 원본 크기
bg_width, bg_height = background_image.get_width(), background_image.get_height()

# 초기 스케일링
scale_factor = min(original_width / bg_width, original_height / bg_height)
scaled_width = int(bg_width * scale_factor)
scaled_height = int(bg_height * scale_factor)
scaled_image = pygame.transform.scale(background_image, (scaled_width, scaled_height))

# 초기 오프셋 계산
x_offset = (original_width - scaled_width) // 2
y_offset = (original_height - scaled_height) // 2

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # 새로운 창 크기
            new_width, new_height = event.w, event.h
            screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            
            # 비율 유지하며 이미지 스케일링
            scale_factor = min(new_width / bg_width, new_height / bg_height)
            scaled_width = int(bg_width * scale_factor)
            scaled_height = int(bg_height * scale_factor)
            scaled_image = pygame.transform.scale(background_image, (scaled_width, scaled_height))
            
            # 이미지 중앙에 배치
            x_offset = (new_width - scaled_width) // 2
            y_offset = (new_height - scaled_height) // 2

    # 검은색 배경 채우기
    screen.fill((0, 0, 0))
    
    # 이미지 그리기
    screen.blit(scaled_image, (x_offset, y_offset))
    pygame.display.update()

pygame.quit()
sys.exit()
