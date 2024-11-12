import pygame
import sys

# 초기 설정
pygame.init()
logical_width, logical_height = 640, 480  # 논리적 해상도
window = pygame.display.set_mode((800, 600), pygame.RESIZABLE)  # 창 생성
pygame.display.set_caption("Pygame Logical Size with Aspect Ratio")

# 논리적 해상도에 맞춘 가상 Surface 생성
logical_surface = pygame.Surface((logical_width, logical_height))

# 두 개의 이미지 로드 및 크기 조정
try:
    image1 = pygame.image.load("image1.bmp")  # 첫 번째 이미지 경로
    image2 = pygame.image.load("image2.bmp")  # 두 번째 이미지 경로
    
    # 논리적 해상도에 맞게 각 이미지 크기 조정 (필요 시 크기를 조정)
    image1 = pygame.transform.scale(image1, (200, 150))  # 원하는 크기로 변경
except pygame.error as e:
    print(f"이미지를 불러오는 중 오류 발생: {e}")
    pygame.quit()
    sys.exit()

# 캐릭터 설정
character_color = (255, 0, 0)  # 빨간색
character_size = 20  # 캐릭터 크기
character_x, character_y = logical_width // 2, logical_height // 2  # 캐릭터 초기 위치
character_speed = 200  # 캐릭터 이동 속도 (초당 200 픽셀)

# 시간 설정
clock = pygame.time.Clock()

# 메인 루프
running = True
while running:
    delta_time = clock.tick(120) / 1000.0  # 델타타임을 초 단위로 계산 (60 FPS로 설정)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:  # 창 크기 변경 이벤트 처리
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:  # 위로 이동
        character_y -= character_speed * delta_time
    if keys[pygame.K_s]:  # 아래로 이동
        character_y += character_speed * delta_time
    if keys[pygame.K_a]:  # 왼쪽으로 이동
        character_x -= character_speed * delta_time
    if keys[pygame.K_d]:  # 오른쪽으로 이동
        character_x += character_speed * delta_time

    # 논리적 Surface에 이미지와 캐릭터 그리기
    logical_surface.fill((0, 0, 0))  # 배경색 설정 (검정색으로 클리핑)
    logical_surface.blit(image1, (150, 50))  # 이미지1 위치 설정
    logical_surface.blit(image2, (0, 0))  # 이미지2 위치 설정
    pygame.draw.rect(logical_surface, character_color, (character_x, character_y, character_size, character_size))

    # 창 비율 계산
    window_width, window_height = window.get_size()
    aspect_ratio = logical_width / logical_height
    window_ratio = window_width / window_height

    # 비율에 맞춰 논리적 Surface 크기 조정
    if window_ratio > aspect_ratio:
        # 창이 더 넓은 경우 - 높이를 기준으로 스케일링
        scale_height = window_height
        scale_width = int(scale_height * aspect_ratio)
    else:
        # 창이 더 좁은 경우 - 너비를 기준으로 스케일링
        scale_width = window_width
        scale_height = int(scale_width / aspect_ratio)

    # 중앙 정렬을 위해 위치 계산
    x_offset = (window_width - scale_width) // 2
    y_offset = (window_height - scale_height) // 2

    # 창의 비율에 맞춰 논리적 Surface의 일부분만 표시
    scaled_surface = pygame.transform.scale(logical_surface, (scale_width, scale_height))
    window.fill((0, 0, 0))  # 검은색으로 배경을 채움
    window.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.flip()

pygame.quit()
sys.exit()
