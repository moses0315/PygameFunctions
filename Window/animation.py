import pygame
import sys

class Animation:
    def __init__(self, sprite_sheet_path, num_frames, frame_length, loop=True):
        """
        애니메이션 클래스 초기화
        :param image_path: 애니메이션 이미지 파일 경로
        :param num_frames: 프레임 수
        :param frame_length: 각 프레임의 지속 시간 (초)
        :param loop: 애니메이션 반복 여부
        """
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.num_frames = num_frames
        self.frame_length = frame_length
        self.loop = loop

        # 프레임 초기화
        self.frame_width = self.sprite_sheet.get_width() // num_frames
        self.frame_height = self.sprite_sheet.get_height()
        self.frames = self.load_frames()

        # 상태 변수
        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False

        self.rect = pygame.rect.Rect(0, 0, self.frame_width, self.frame_height)

    def load_frames(self):
        """
        스프라이트 시트에서 각 프레임을 추출하여 리스트로 반환
        """
        frames = []
        for i in range(self.num_frames):
            frame_rect = pygame.Rect(
                i * self.frame_width, 0, self.frame_width, self.frame_height
            )
            frame = self.sprite_sheet.subsurface(frame_rect)
            frames.append(frame)
        return frames

    def update(self, dt):
        """
        애니메이션 업데이트
        :param dt: 델타 시간 (초)
        """
        if self.finished:
            return

        self.accumulated_time += dt

        # 누적된 시간으로 필요한 만큼의 프레임 전환
        while self.accumulated_time >= self.frame_length:
            self.accumulated_time -= self.frame_length
            self.current_frame += 1

            # 프레임 종료 처리
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
        """
        애니메이션 초기화
        """
        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False
        return self


# 초기화
pygame.init()

# 창 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 200, 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My First Game")
clock = pygame.time.Clock()

# 플레이어 설정
player_pos = pygame.Vector2(0, 0)
player_vel = pygame.Vector2(0, 0)
player_grounded = False
player_flip = False

# 애니메이션 생성
run_animation = Animation("anim.png", num_frames=4, frame_length=0.25, loop=True)

# 현재 애니메이션
current_animation = run_animation

# 색상 정의
BG_COLOR = (0, 0, 0)

# 게임 루프
running = True
while running:
    dt = clock.tick(900) / 1000  # 초 단위의 프레임 시간
    print(dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 좌우 이동
    if keys[pygame.K_LEFT]:
        player_vel.x = -400
        player_flip = True
        current_animation = run_animation
    elif keys[pygame.K_RIGHT]:
        player_vel.x = 400
        player_flip = False
        current_animation = run_animation
    else:
        player_vel.x = 0
        current_animation = run_animation

    # 플레이어 위치 업데이트
    player_pos += player_vel * dt

    # 애니메이션 업데이트
    current_animation.update(dt)

    # 화면 그리기
    screen.fill(BG_COLOR)
    rect = pygame.Rect(10, 5, 70, 90)
    rect_color = pygame.Color
    pygame.draw.rect(screen, (0, 255, 0), rect)
    # 애니메이션 프레임 그리기
    current_animation.draw(screen, rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
