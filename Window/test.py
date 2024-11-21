import pygame

class Animation:
    def __init__(self, sprite_sheet_path, num_frames, frame_length, loop=True):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.num_frames = num_frames
        self.frame_length = frame_length
        self.loop = loop

        self.frame_width = self.sprite_sheet.get_width() // num_frames
        self.frame_height = self.sprite_sheet.get_height()
        self.frames = self.load_frames()

        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False

        self.rect = pygame.rect.Rect(0, 0, self.frame_width, self.frame_height)

    def load_frames(self):
        frames = []
        for i in range(self.num_frames):
            frame_rect = pygame.Rect(
                i * self.frame_width, 0, self.frame_width, self.frame_height
            )
            frame = self.sprite_sheet.subsurface(frame_rect)
            frames.append(frame)
        return frames

    def update(self, dt):
        if self.finished:
            return

        self.accumulated_time += dt

        while self.accumulated_time >= self.frame_length:
            self.accumulated_time -= self.frame_length
            self.current_frame += 1

            if self.current_frame == self.num_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.finished = True
                    self.current_frame = self.num_frames - 1

    def draw(self, surface, rect):
        current_frame_image = self.frames[self.current_frame]
        self.rect.midbottom = rect.midbottom
        surface.blit(current_frame_image, self.rect)

    def reset(self):
        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False
        return self


class Player:
    def __init__(self, idle_sheet, attack_sheet):
        self.idle_animation = Animation(idle_sheet, num_frames=4, frame_length=0.15)
        self.attack_animation = Animation(attack_sheet, num_frames=5, frame_length=0.1, loop=False)
        self.current_animation = self.idle_animation
        self.rect = pygame.Rect(100, 100, 50, 50)  # 플레이어 위치와 크기
        self.is_attacking = False
        self.attack_frame_active = False

    def update(self, dt):
        if self.is_attacking:
            self.current_animation.update(dt)

            # 공격 애니메이션 판정 처리
            if self.current_animation.current_frame == 2 and not self.attack_frame_active:
                self.attack_frame_active = True
                self.perform_attack()

            # 공격 종료 처리
            if self.current_animation.finished:
                self.is_attacking = False
                self.attack_frame_active = False
                self.current_animation = self.idle_animation
                self.current_animation.reset()
        else:
            self.current_animation.update(dt)

    def draw(self, surface):
        self.current_animation.draw(surface, self.rect)

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_animation = self.attack_animation.reset()

    def perform_attack(self):
        print("Attack hit!")  # 공격 판정 발생


# Pygame 실행 예제
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 애니메이션 시트 경로 (이미지 경로를 올바르게 설정하세요)
idle_sheet = "anim.png"
attack_sheet = "attack.png"

player = Player(idle_sheet, attack_sheet)

running = True
while running:
    dt = clock.tick(60) / 1000.0  # FPS에 따른 델타 타임 계산

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                player.attack()

    player.update(dt)

    screen.fill((0, 0, 0))
    player.draw(screen)
    pygame.display.flip()

pygame.quit()
