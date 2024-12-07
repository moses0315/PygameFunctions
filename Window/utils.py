import pygame
from enum import Enum, auto
import json
import os
from game_data import SAVE_FILE, default_data

def save_game(data, file_path=SAVE_FILE):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("Game data saved!")


def load_game(file_path=SAVE_FILE):
    if not os.path.exists(file_path):
        print("Game DEFAULT data loaded!")
        return default_data
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print("Game data loaded!")
        return data


class Button:
    class State(Enum):
        NORMAL = auto()
        HOVER = auto()
        PRESS = auto()
        FOCUS = auto()

    def __init__(self, rect, color, text="", text_size=32, text_color=(0, 0, 0)):
        self.rect = rect
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.surface_rect = self.surface.get_rect()
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, text_size)
        self.state = Button.State.NORMAL

    def handle_event_and_check_clicked(self, event, mouse_position):
        if event.type == pygame.MOUSEMOTION:
            if self.state in (Button.State.PRESS, Button.State.FOCUS):
                pass
            elif self.rect.collidepoint(mouse_position):
                self.state = Button.State.HOVER
            else:
                self.state = Button.State.NORMAL
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_position):
                self.state = Button.State.PRESS
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == Button.State.PRESS and self.rect.collidepoint(mouse_position):
                self.state = Button.State.FOCUS
                return True
            self.state = Button.State.NORMAL
        return False

    def draw(self, surface):
        if self.state == Button.State.NORMAL:
            draw_color = self.color
        elif self.state == Button.State.HOVER:
            r = min(self.color[0] + 40, 255)
            g = min(self.color[1] + 40, 255)
            b = min(self.color[2] + 40, 255)
            a = min(self.color[3] + 40, 255)
            draw_color = (r, g, b, a)
        elif self.state == Button.State.PRESS:
            r = max(self.color[0] - 40, 0)
            g = max(self.color[1] - 40, 0)
            b = max(self.color[2] - 40, 0)
            a = max(self.color[3] + 40, 0)
            draw_color = (r, g, b, a)
        elif self.state == Button.State.FOCUS:
            draw_color = (255, 255, 255, 255)
        self.surface.fill(draw_color)
        if self.text:
            text_surface = self.font.render(self.text, False, self.text_color)
            text_rect = text_surface.get_rect(center=self.surface_rect.center)
            self.surface.blit(text_surface, text_rect)
        surface.blit(self.surface, self.rect)


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def update(self, target_rect, map_width, map_height):
        self.x = target_rect.centerx - self.width // 2
        self.y = target_rect.centery - self.height // 2
        self.x = max(0, min(self.x, map_width - self.width))
        self.y = max(0, min(self.y, map_height - self.height))


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
            frame_rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame = self.sprite_sheet.subsurface(frame_rect)
            frames.append(frame)
        return frames

    def update(self, delta_time):
        if self.finished:
            return

        self.accumulated_time += delta_time

        if self.accumulated_time >= self.frame_length:
            self.accumulated_time -= self.frame_length
            self.current_frame += 1

            if self.current_frame == self.num_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.finished = True
                    self.current_frame = self.num_frames - 1

    def draw(self, surface, rect, flip):
        current_frame_image = self.frames[self.current_frame]
        current_frame_image = pygame.transform.flip(current_frame_image, flip, False)
        self.rect.midbottom = rect.midbottom
        surface.blit(current_frame_image, self.rect)

    def reset(self):
        self.current_frame = 0
        self.accumulated_time = 0
        self.finished = False
        return self

  
class Timer:
    def __init__(self, duration, loop=False):
        self.duration = duration  # 타이머 지속 시간 (초 단위)
        self.loop = loop
        self.accumulated_time = 0
        self.is_running = False

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False
        self.accumulated_time = 0

    def pause(self):
        self.is_running = False

    def resume(self):
        self.is_running = True

    def update(self, delta_time):
        if self.is_running:
            self.accumulated_time += delta_time
            if self.accumulated_time >= self.duration:
                self.accumulated_time -= self.duration
                if self.loop:
                    self.start()
                else:
                    self.is_running = False
