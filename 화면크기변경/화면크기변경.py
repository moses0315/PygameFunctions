import pygame
import sys

# Pygame 초기화
pygame.init()

# 이미지 로드
background_image = pygame.image.load('background.png')
character_image = pygame.image.load('character.png')
enemy_image = pygame.image.load('enemy.png')

# 초기 창 크기 설정
original_width, original_height = 800, 600
screen = pygame.display.set_mode((original_width, original_height), pygame.RESIZABLE)
pygame.display.set_caption("Resizable Window Example")

# 이미지의 원본 크기
bg_width, bg_height = background_image.get_width(), background_image.get_height()
char_width, char_height = character_image.get_width(), character_image.get_height()
enemy_width, enemy_height = enemy_image.get_width(), enemy_image.get_height()

# 초기 스케일링
scale_factor = min(original_width / bg_width, original_height / bg_height)
scaled_bg_width = int(bg_width * scale_factor)
scaled_bg_height = int(bg_height * scale_factor)
scaled_bg_image = pygame.transform.scale(background_image, (scaled_bg_width, scaled_bg_height))

# 초기 오프셋 계산
x_offset = (original_width - scaled_bg_width) // 2
y_offset = (original_height - scaled_bg_height) // 2

# 전체 화면 상태 변수
fullscreen = False

# 현재 창 크기 변수
current_width, current_height = original_width, original_height

# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            # 새로운 창 크기
            current_width, current_height = event.w, event.h
            screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
            
            # 비율 유지하며 배경 이미지 스케일링
            scale_factor = min(current_width / bg_width, current_height / bg_height)
            scaled_bg_width = int(bg_width * scale_factor)
            scaled_bg_height = int(bg_height * scale_factor)
            scaled_bg_image = pygame.transform.scale(background_image, (scaled_bg_width, scaled_bg_height))
            
            # 이미지 중앙에 배치
            x_offset = (current_width - scaled_bg_width) // 2
            y_offset = (current_height - scaled_bg_height) // 2
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((original_width, original_height), pygame.RESIZABLE)
                    current_width, current_height = original_width, original_height
            elif event.key == pygame.K_ESCAPE and fullscreen:
                fullscreen = False
                screen = pygame.display.set_mode((original_width, original_height), pygame.RESIZABLE)
                current_width, current_height = original_width, original_height

    # 검은색 배경 채우기
    screen.fill((0, 0, 0))
    
    # 배경 이미지 그리기
    screen.blit(scaled_bg_image, (x_offset, y_offset))
    
    # 클리핑 영역 설정
    clip_rect = pygame.Rect(x_offset, y_offset, scaled_bg_width, scaled_bg_height)
    screen.set_clip(clip_rect)
    
    # 캐릭터와 적 이미지 스케일링 및 위치 조정
    scaled_char_image = pygame.transform.scale(character_image, (int(char_width * scale_factor), int(char_height * scale_factor)))
    scaled_enemy_image = pygame.transform.scale(enemy_image, (int(enemy_width * scale_factor), int(enemy_height * scale_factor)))
    
    char_x = x_offset + 50 * scale_factor
    char_y = y_offset + 50 * scale_factor
    enemy_x = x_offset + 200 * scale_factor
    enemy_y = y_offset + 200 * scale_factor
    
    screen.blit(scaled_char_image, (char_x, char_y))  # 캐릭터 이미지 위치
    screen.blit(scaled_enemy_image, (enemy_x, enemy_y))  # 적 이미지 위치
    
    # 클리핑 영역 해제
    screen.set_clip(None)
    
    # 사각형 그리기
    rect_x = x_offset + 300 * scale_factor
    rect_y = y_offset + 300 * scale_factor
    rect_width = 100 * scale_factor
    rect_height = 50 * scale_factor
    pygame.draw.rect(screen, (255, 0, 0), (rect_x, rect_y, rect_width, rect_height))  # 빨간색 사각형
    
    pygame.display.update()

pygame.quit()
sys.exit()
