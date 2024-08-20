import pygame

# 색상 정의
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Player:
    def __init__(self, x, y, player_type, tile_map):
        if player_type == 'basic':
            self.rect = pygame.Rect(x, y, 50, 60)
            self.color = BLUE
            self.speed = 5
            self.gravity = 0.8
            self.jump_power = -15
        elif player_type == 'speedy':
            self.rect = pygame.Rect(x, y, 50, 60)
            self.color = GREEN
            self.speed = 8
            self.gravity = 0.8
            self.jump_power = -12
        elif player_type == 'strong':
            self.rect = pygame.Rect(x, y, 60, 70)
            self.color = RED
            self.speed = 4
            self.gravity = 0.9
            self.jump_power = -18

        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.tile_map = tile_map

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
        else:
            self.velocity_x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power

        self.velocity_y += self.gravity
        self.update_position()

    def update_position(self):
        # 수평 이동
        self.rect.x += self.velocity_x
        collisions = self.check_collision()
        for tile in collisions:
            if self.velocity_x > 0:  # 오른쪽 이동 중
                self.rect.right = tile.left
            elif self.velocity_x < 0:  # 왼쪽 이동 중
                self.rect.left = tile.right

        # 수직 이동
        self.rect.y += self.velocity_y
        self.on_ground = False
        collisions = self.check_collision()
        for tile in collisions:
            if self.velocity_y > 0:  # 아래로 떨어지는 중
                self.rect.bottom = tile.top
                self.velocity_y = 0
                self.on_ground = True
            elif self.velocity_y < 0:  # 위로 점프 중
                self.rect.top = tile.bottom
                self.velocity_y = 0

    def check_collision(self):
        return [tile for tile in self.tile_map.tiles if self.rect.colliderect(tile)]

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
