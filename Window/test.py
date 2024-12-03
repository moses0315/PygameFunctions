import pygame
import sys

# 초기화
pygame.init()
screen = pygame.display.set_mode((1200, 600))
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 플레이어 설정
player = pygame.Rect(400, 300, 50, 50)
player_pos = [1100.0, 300.0]  # 실수로 위치를 관리
velocity = [0.0, 0.0]  # x, y 속도
friction = 0.001  # 감속 계수 (1에 가까울수록 느리게 감속)

# 게임 루프
running = True
while running:
    delta_time = clock.tick(900) / 1000  # 초 단위로 델타 타임 계산 (밀리초 -> 초)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 넉백 발생 테스트: 스페이스바를 누르면 넉백 시작
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                velocity = [-1500, 0]  # 초기 속도 (x, y, 픽셀/초)
            elif event.key == pygame.K_a:
                player_pos[0] = 1100

    # 속도 적용 (델타 타임 사용)
    player_pos[0] += velocity[0] * delta_time
    player_pos[1] += velocity[1] * delta_time

    # 감속 적용 (마찰력처럼)
    velocity[0] *= (friction ** delta_time)
    velocity[1] *= (friction ** delta_time)

    # 매우 느린 속도는 0으로 처리
    if abs(velocity[0]) < 300:
        velocity[0] = 0
    if abs(velocity[1]) < 300:
        velocity[1] = 0

    # 실수 위치를 정수로 변환해 Rect 업데이트
    player.x = int(player_pos[0])
    player.y = int(player_pos[1])

    # 화면 그리기
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, player)

    pygame.display.flip()

pygame.quit()
sys.exit()
