import pygame
import sys
from utils import Button, Camera, Animation, Timer, save_game, load_game
from characters import Player, Enemy
from game_data import *



class MainScene:
    def __init__(self, game_data):
        self.game_data = game_data

        self.buttons = [
            Button(pygame.Rect(0, 0, 200, 50), pygame.Color(50, 50, 50, 0), text="Play"),
            Button(pygame.Rect(0, 50, 200, 50), pygame.Color(50, 50, 50, 0), text="Settings"),
            Button(pygame.Rect(0, 100, 200, 50), pygame.Color(200, 0, 0, 0), text="Quit"),
        ]
        self.background = pygame.image.load("main_scene_bg.png").convert()
        self.layer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

    def handle_event(self, event, mouse_position):
        for button in self.buttons:
            if button.handle_event_and_check_clicked(event, mouse_position):
                if button.text == "Play":
                    return PlayScene(self.game_data)
                elif button.text == "Settings":
                    return SettingsScene(self.game_data)
                elif button.text == "Quit":
                    save_game(self.game_data)
                    pygame.quit()
                    sys.exit()
        return None

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        self.layer.blit(self.background, (0, 0))
        for button in self.buttons:
            button.draw(self.layer)
        logical_surface.blit(self.layer, (0, 0))


class PlayScene:
    def __init__(self, game_data):
        self.game_data = game_data
        self.camera = Camera(LOGICAL_WIDTH, LOGICAL_HEIGHT)
        self.background_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT))
        self.midground_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.foreground_layer = pygame.Surface((LOGICAL_WIDTH * 2, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.canvas_layer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")
        self.player = Player(100, 110, self.game_data["controls"])
        self.enemies = [Enemy(200, 110)]
        self.background = pygame.image.load("assets/background/background.png").convert_alpha()
        self.background1 = pygame.image.load("assets/background/midground.png").convert_alpha()
        self.background2 = pygame.image.load("assets/background/foreground.png").convert_alpha()

        for x in range(0, LOGICAL_WIDTH * 2, self.background.get_width()):
            self.background_layer.blit(self.background, (x, 0))
        for x in range(0, LOGICAL_WIDTH * 2, self.background.get_width()):
            self.midground_layer.blit(self.background1, (x, 0))

    def handle_event(self, event, mouse_position):
        if self.back_button.handle_event_and_check_clicked(event, mouse_position):
            return MainScene(self.game_data)
        self.player.handle_event(event)
        return None

    def update(self, delta_time):
        self.player.update(self.enemies, delta_time)
        for enemy in self.enemies:
            enemy.update(self.player, delta_time)
            if enemy.state == Enemy.State.DEAD:
                self.enemies.remove(enemy)
        self.camera.update(self.player.rect, LOGICAL_WIDTH * 2, LOGICAL_HEIGHT)

    def draw(self, logical_surface):
        self.foreground_layer.fill((0, 0, 0, 0))
        self.canvas_layer.fill((0, 0, 0, 0))

        self.foreground_layer.blit(self.background2, (0, 0))
        for enemy in self.enemies:
            enemy.draw(self.foreground_layer)
        self.player.draw(self.foreground_layer)
        self.back_button.draw(self.canvas_layer)

        logical_surface.blit(self.background_layer, (-self.camera.x, 0))
        logical_surface.blit(self.midground_layer, (-self.camera.x, 0))
        logical_surface.blit(self.foreground_layer, (-self.camera.x, 0))
        logical_surface.blit(self.canvas_layer, (0, 0))


class SettingsScene:
    def __init__(self, game_data):
        self.game_data = game_data
        self.controls = self.game_data["controls"]
        self.back_button = Button(pygame.Rect(10, 10, 100, 50), pygame.Color(200, 200, 0, 0), text="Back")
        self.background = pygame.image.load("settings_scene_bg.png").convert()
        self.selected_action = None
        self.action_buttons = {
            "move_left": Button(pygame.Rect(100, 50, 200, 50), pygame.Color(100, 100, 200, 0), text=f"move_left: {pygame.key.name(self.controls['move_left'])}"),
            "move_right": Button(pygame.Rect(100, 100, 200, 50), pygame.Color(100, 100, 200, 0), text=f"move_right: {pygame.key.name(self.controls['move_right'])}"),
            "attack": Button(pygame.Rect(100, 150, 200, 50), pygame.Color(100, 100, 200, 0), text=f"attack: {pygame.key.name(self.controls['attack'])}"),
            "dash": Button(pygame.Rect(100, 200, 200, 50), pygame.Color(100, 100, 200, 0), text=f"dash: {pygame.key.name(self.controls['dash'])}"),
        }

    def handle_event(self, event, mouse_position):
        for action, button in self.action_buttons.items():
            if button.handle_event_and_check_clicked(event, mouse_position):
                self.selected_action = action
        if event.type == pygame.KEYDOWN:
            self.controls[self.selected_action] = event.key
            self.action_buttons[self.selected_action].text = f"{self.selected_action}: {pygame.key.name(event.key)}"
            self.action_buttons[self.selected_action].state = Button.State.NORMAL
            save_game(self.game_data)
            self.selected_action = None
        if self.back_button.handle_event_and_check_clicked(event, mouse_position):
            self.game_data["controls"] = self.controls
            save_game(self.game_data)
            return MainScene(self.game_data)
        return None

    def update(self, delta_time):
        pass

    def draw(self, logical_surface):
        logical_surface.blit(self.background, (0, 0))
        for button in self.action_buttons.values():
            button.draw(logical_surface)
        self.back_button.draw(logical_surface)
