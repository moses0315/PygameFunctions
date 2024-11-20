import pygame
import time

class Animation:
    def __init__(self, texture, num_frames, frame_length, loop=True):
        """
        애니메이션 클래스 초기화
        :param texture: 애니메이션 스프라이트 시트
        :param num_frames: 프레임 수
        :param frame_length: 각 프레임의 지속 시간 (초)
        :param loop: 애니메이션 반복 여부
        """
        self.texture = texture
        self.num_frames = num_frames
        self.frame_length = frame_length
        self.loop = loop

        self.current_frame = 0
        self.frame_timer = 0

        self.frame_width = texture.get_width() // num_frames
        self.frame_height = texture.get_height()
        self.finished = False

    def update(self, dt):
        """
        애니메이션 업데이트
        :param dt: 델타 시간 (초)
        """
        if self.finished:
            return

        self.frame_timer += dt
        if self.frame_timer > self.frame_length:
            self.current_frame += 1
            self.frame_timer = 0

            # 프레임 종료 처리
            if self.current_frame == self.num_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.finished = True
                    self.current_frame = self.num_frames - 1

    def get_current_frame(self):
        """
        현재 프레임 Rect 가져오기
        :return: pygame.Rect
        """
        return pygame.Rect(
            self.current_frame * self.frame_width, 0, self.frame_width, self.frame_height
        )

    def reset(self):
        """
        애니메이션 초기화
        """
        self.current_frame = 0
        self.frame_timer = 0
        self.finished = False