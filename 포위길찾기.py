import pygame
import random
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target_offset):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.target_offset = target_offset

    def update(self, player):
        target_position = (player.rect.centerx + self.target_offset[0], player.rect.centery + self.target_offset[1])
        direction = pygame.math.Vector2(target_position) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
        self.rect.center += direction * self.speed

# Pygame 초기화 및 게임 루프 설정은 생략

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
enemies = pygame.sprite.Group()

# 적 생성 (플레이어의 좌우에 위치하도록 설정)
enemy1 = Enemy(100, 300, (-100, 0))  # 왼쪽
enemy2 = Enemy(700, 300, (100, 0))   # 오른쪽
enemies.add(enemy1, enemy2)

player = pygame.sprite.Sprite()
player.image = pygame.Surface((50, 50))
player.image.fill((0, 255, 0))
player.rect = player.image.get_rect(center=(400, 300))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    enemies.update(player)

    screen.fill((0, 0, 0))
    screen.blit(player.image, player.rect)
    enemies.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
