import pygame
import random

# 초기화
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 카메라 클래스
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.shake_magnitude = 0
        self.shake_duration = 0  # 흔들림 남은 시간 (초 단위)

    def update(self, dt):
        if self.shake_duration > 0:
            self.offset.x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            self.offset.y = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            self.shake_duration -= dt  # 남은 시간을 감소
            if self.shake_duration <= 0:
                self.shake_duration = 0
                self.offset = pygame.Vector2(0, 0)
        else:
            self.offset = pygame.Vector2(0, 0)

    def shake(self, magnitude, duration):
        """흔들림 강도와 지속 시간 설정"""
        self.shake_magnitude = magnitude
        self.shake_duration = duration

# 게임 오브젝트
class GameObject:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface, camera_offset):
        # 화면에 그리기 (카메라 오프셋 반영)
        adjusted_rect = self.rect.move(-camera_offset.x, -camera_offset.y)
        pygame.draw.rect(surface, self.color, adjusted_rect)

# 게임 오브젝트 생성
player = GameObject(375, 275, 50, 50, RED)
camera = Camera()

# 게임 루프
running = True
while running:
    # 델타 타임 계산
    dt = clock.tick() / 1000  # 초 단위로 변환

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # 스페이스바로 화면 흔들기
                camera.shake(10, 0.5)  # 강도 10, 0.5초 지속

    # 카메라 업데이트
    camera.update(dt)

    # 화면 그리기
    screen.fill(BLACK)
    player.draw(screen, camera.offset)
    image = pygame.image.load("vectorart.svg")
    rect = image.get_rect()
  #  image = pygame.transform.scale(image, (rect.w*1, rect.y*1))
    screen.blit(image, (10, 10))
    pygame.display.flip()
