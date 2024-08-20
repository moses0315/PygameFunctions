from entities.player import Player
from entities.enemy import Enemy
from entities.tilemap import TileMap
from ui.button import Button
import pygame

# Pygame 초기화
pygame.init()

# 화면 크기 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
TILE_SIZE = 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("플랫포머 게임")

# 색상 정의
WHITE = (255, 255, 255)

# FPS 설정
clock = pygame.time.Clock()
FPS = 60

class Game:
    def __init__(self):
        self.tile_map = TileMap(TILE_SIZE, 'basic')  # 'basic' 맵 사용
        self.player = Player(100, SCREEN_HEIGHT - 60 - 10, 'basic', self.tile_map)  # 'basic' 플레이어 사용
        self.enemy = Enemy(200, 200, 'basic', self.tile_map)  # 'basic' 적 사용
        self.current_scene = "menu"  # 초기 화면은 메뉴로 설정
        self.play_button = Button("Play", (350, 300), font=50)
        self.options_button = Button("Options", (350, 400), font=50)
        self.quit_button = Button("Quit", (350, 500), font=50)

    def run(self):
        running = True
        while running:
            screen.fill(WHITE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.current_scene == "menu":
                    if self.play_button.click(event):
                        self.current_scene = "play"
                    elif self.quit_button.click(event):
                        running = False

            if self.current_scene == "menu":
                self.render_menu()
            elif self.current_scene == "play":
                keys = pygame.key.get_pressed()
                self.player.move(keys)
                self.enemy.move(self.player)

                self.tile_map.draw(screen)
                self.player.draw(screen)
                self.enemy.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()

    def render_menu(self):
        self.play_button.check_hover()
        self.play_button.show(screen)
        self.options_button.check_hover()
        self.options_button.show(screen)
        self.quit_button.check_hover()
        self.quit_button.show(screen)

if __name__ == "__main__":
    game = Game()
    game.run()
