import pygame
from pygame.locals import *

pygame.init()

# 기본 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)

# 플레이어 속성 정의
player = pygame.Rect(100, 500, 50, 50)
player_color = (0, 0, 255)

# 공격 관련 변수
attacking = False
attack_stage = 0
attack_buffer_time = 20  # 공격 입력 버퍼 유지 프레임 수
attack_buffer_counter = 0
combo_reset_time = 30  # 콤보가 끝난 후 초기화까지의 시간
combo_reset_counter = 0

# 게임 루프
running = True
while running:
    screen.fill(WHITE)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[K_z]:
        attack_buffer_counter = attack_buffer_time  # 공격 키가 눌리면 버퍼 카운터 초기화

    # 공격 콤보 입력 처리
    if attack_buffer_counter > 0:
        attack_buffer_counter -= 1

    if not attacking and attack_buffer_counter > 0:
        # 공격이 가능한 상태이면 콤보 스테이지에 따라 공격 시작
        attacking = True
        attack_stage = (attack_stage + 1) % 3  # 콤보는 3단계로 반복됨
        attack_buffer_counter = 0
        combo_reset_counter = combo_reset_time

    # 공격 애니메이션 상태 처리
    if attacking:
        if attack_stage == 0:
            player_color = (255, 0, 0)  # 공격1 - 빨간색
        elif attack_stage == 1:
            player_color = (0, 255, 0)  # 공격2 - 초록색
        elif attack_stage == 2:
            player_color = (0, 0, 255)  # 공격3 - 파란색 (더 강한 공격)

        # 여기에서는 단순히 일정 시간 후 공격이 끝난다고 가정
        combo_reset_counter -= 1
        if combo_reset_counter <= 0:
            attacking = False
            player_color = (0, 0, 0)  # 공격이 끝나면 색상 리셋

    # 공격이 끝나고 콤보 초기화 시간 경과 시 콤보 리셋
    if not attacking and combo_reset_counter > 0:
        combo_reset_counter -= 1
    if combo_reset_counter <= 0 and attack_stage > 0:
        attack_stage = 0

    # 플레이어 그리기
    pygame.draw.rect(screen, player_color, player)

    # 화면 업데이트
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
