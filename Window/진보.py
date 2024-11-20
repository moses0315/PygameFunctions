import pygame
import sys
import os

#pyinstaller --onefile --noconsole --add-data "assets/*;assets" 진보.py
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

pygame.init()
DEFAULT_WIDTH = 320
DEFAULT_HEIGHT = 160
MONITOR_WIDTH = pygame.display.Info().current_w
MONITOR_HEIGHT = pygame.display.Info().current_h
if MONITOR_WIDTH / MONITOR_HEIGHT < (16 / 9):
    MONITOR_WIDTH = MONITOR_HEIGHT * (16 / 9)
else:
    MONITOR_HEIGHT = MONITOR_WIDTH * (9 / 16)

is_fullscreen = False
scale = 0.0

key_bindings = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_z,
    "attack": pygame.K_x
}

clock = pygame.time.Clock()
pygame.display.set_caption("Tilemap Platformer")

font_path = resource_path("assets/GowunBatang-Regular.ttf")


class Player:
    def __init__(self, tilemap):

        self.idle_animation = Animation(pygame.image.load(resource_path("assets/player/idle.png")).convert_alpha(), 4, 0.15)
        self.run_animation = Animation(pygame.image.load(resource_path("assets/player/run.png")).convert_alpha(), 4, 0.1)
        self.jump_animation = Animation(pygame.image.load(resource_path("assets/player/jump.png")).convert_alpha(), 2, 0.15)
        self.fall_animation = Animation(pygame.image.load(resource_path("assets/player/fall.png")).convert_alpha(), 2, 0.15)
        self.attack_animation = Animation(pygame.image.load(resource_path("assets/player/attack.png")).convert_alpha(), 5, 0.07, False)
        self.dash_animation = Animation(pygame.image.load(resource_path("assets/player/dash.png")).convert_alpha(), 3, 0.1, False)
        
        self.current_animation = self.idle_animation

        self.rect = pygame.Rect(20*scale, 0, 16*scale, 32*scale)

        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

        self.speed = 75 * scale  # pixels per second
        self.jump_strength = 250 * scale  # pixels per second
        self.gravity = 750 * scale  # pixels per second squared

        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        
        self.pressed_keys = []
        
        self.tilemap = tilemap

        self.facing_right = True
        self.is_attacking = False
        self.is_dashing = False
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == key_bindings["left"]:
                self.pressed_keys.append("left")
            elif event.key == key_bindings["right"]:
                self.pressed_keys.append("right")
       
        elif event.type == pygame.KEYUP:
            if event.key == key_bindings["left"]:
                self.pressed_keys.remove("left")
            elif event.key == key_bindings["right"]:
                self.pressed_keys.remove("right")

    def update(self, delta_time):
        self.move(delta_time)
        self.attack()
        self.handle_animation(delta_time)
        pygame.draw.rect(screen, (30, 30, 30), self.rect, 1)
        
    def move(self, delta_time):
        if self.is_attacking:
            if self.pressed_keys == []:
                self.velocity_x = 0
            elif self.pressed_keys[-1] == "left" and self.current_animation.current_frame_index == 1:
                self.velocity_x = -self.speed*2
            elif self.pressed_keys[-1] == "right" and self.current_animation.current_frame_index ==1:
                self.velocity_x = self.speed*2
            else:
                self.velocity_x = 0
        elif self.is_dashing:
            if self.pressed_keys == []:
                self.velocity_x = 0
            elif self.pressed_keys[-1] == "left" and self.current_animation.current_frame_index <= 2:
                self.velocity_x = -self.speed*2
            elif self.pressed_keys[-1] == "right" and self.current_animation.current_frame_index <= 2:
                self.velocity_x = self.speed*2
            else:
                self.velocity_x = 0            
        else:
            if self.pressed_keys == []:
                self.velocity_x = 0
            elif self.pressed_keys[-1] == "left":
                self.velocity_x = -self.speed
            elif self.pressed_keys[-1] == "right":
                self.velocity_x = self.speed

        self.float_x += self.velocity_x * delta_time
        self.rect.x = int(self.float_x)        
        for tile in self.tilemap.tilemap:
            if self.rect.colliderect(tile.rect):
                if self.velocity_x > 0 and self.rect.x < tile.rect.x:  # Right collision
                    self.rect.right = tile.rect.left
                    self.float_x = self.rect.x
                elif self.velocity_x < 0 and self.rect.x > tile.rect.x:  # Left collision
                    self.rect.left = tile.rect.right
                    self.float_x = self.rect.x
        
        if self.on_ground and not self.is_attacking:
            keys = pygame.key.get_pressed()            
            if keys[key_bindings["jump"]]:
                self.velocity_y = -self.jump_strength
                self.on_ground = False              
        self.velocity_y += self.gravity * delta_time
        
        self.float_y += self.velocity_y * delta_time
        self.rect.y = int(self.float_y)
        self.on_ground = False
        for tile in self.tilemap.tilemap:
            if pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h + 1).colliderect(tile.rect):
                if self.velocity_y > 0 and self.rect.y < tile.rect.y:  # Down collision
                    self.rect.bottom = tile.rect.top
                    self.float_y = self.rect.y
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0 and self.rect.y > tile.rect.y:  # Up collision
                    self.rect.top = tile.rect.bottom
                    self.float_y = self.rect.y
                    self.velocity_y = 0
                    
    def attack(self):
        if self.is_attacking:
            if self.current_animation != self.attack_animation or self.current_animation.is_finished:
                self.is_attacking = False
        elif not self.is_attacking:
            keys = pygame.key.get_pressed()            
            if keys[key_bindings["attack"]]:   
                self.is_attacking = True
                self.current_animation = self.attack_animation.reset_state()
            
    def handle_animation(self, delta_time):
        if self.velocity_x < 0:
            self.current_animation = self.run_animation
            self.facing_right = False
        elif self.velocity_x > 0:
            self.current_animation = self.run_animation
            self.facing_right = True
        else:
            self.current_animation = self.idle_animation
            
        if self.velocity_y < 0:
            self.current_animation = self.jump_animation
        elif self.velocity_y > 0:
            self.current_animation = self.fall_animation
        
        if self.is_attacking:
            self.current_animation = self.attack_animation
            
        self.current_animation.update(delta_time)        
        self.current_frame = self.current_animation.get_current_frame()
        
        if not self.facing_right:
            self.current_frame = pygame.transform.flip(self.current_frame, True, False)
        else:
            self.current_frame = pygame.transform.flip(self.current_frame, False, False)
            
        screen.blit(self.current_frame, self.current_frame.get_rect(midbottom=self.rect.midbottom).topleft)
        
        
class Enemy:
    def __init__(self, tilemap):
        # 적의 이미지를 불러오고 크기를 조정
        self.image = pygame.image.load(resource_path("assets/enemy.png")).convert_alpha()
        self.width, self.height = self.image.get_size()
        self.width = int(self.width * scale)
        self.height = int(self.height * scale)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        # 적의 초기 위치 설정
        self.rect = self.image.get_rect()
        self.rect.x = 35 * scale
        self.rect.y = 36

        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)
        
        self.speed = 100 * scale  # 픽셀 단위로 초당 이동 속도

        # 초기 속도 및 방향 설정
        self.velocity_x = 0
        self.velocity_y = 0
        self.directions = (
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (-1, -1), (1, -1), (-1, 1)
        )
        
        self.tilemap = tilemap
        self.facing_right = True
        self.detection_range = 100000

    def update(self, player, delta_time):
        # 플레이어와 적의 거리 계산
        distance_to_player = ((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2) ** 0.5
        
        # 플레이어가 탐지 범위 내에 있는지 확인
        if distance_to_player <= self.detection_range:
            start = (round(self.rect.x / self.tilemap.tile_size), round(self.rect.y / self.tilemap.tile_size))
            goal = (round(player.rect.x / self.tilemap.tile_size), round(player.rect.y / self.tilemap.tile_size))

            # A* 알고리즘을 사용해 경로 계산
            path = self.a_star(start, goal)[:-1]
            if path:
                # 경로상의 다음 타일로 이동
                next_tile = path[-1]
                if next_tile[0] * self.tilemap.tile_size > self.rect.x:
                    self.velocity_x = self.speed
                elif next_tile[0] * self.tilemap.tile_size < self.rect.x:
                    self.velocity_x = -self.speed
                else:
                    self.velocity_x = 0
                if next_tile[1] * self.tilemap.tile_size > self.rect.y:
                    self.velocity_y = self.speed
                elif next_tile[1] * self.tilemap.tile_size < self.rect.y:
                    self.velocity_y = -self.speed
                else:
                    self.velocity_y = 0
                if self.velocity_x != 0 and self.velocity_y != 0:
                    self.velocity_x *= 0.707
                    self.velocity_y *= 0.707
            else:
                self.velocity_x = 0
                self.velocity_y = 0  
        
        # X 축 이동 및 충돌 처리
        self.float_x += self.velocity_x * delta_time
        self.rect.x = int(self.float_x)
        for tile in self.tilemap.tilemap:
            if self.rect.colliderect(tile.rect):
                if self.velocity_x > 0 and self.rect.x < tile.rect.x:  # 우측 충돌
                    self.rect.right = tile.rect.left
                elif self.velocity_x < 0 and self.rect.x > tile.rect.x:  # 좌측 충돌
                    self.rect.left = tile.rect.right
                self.float_x = self.rect.x

        # Y 축 이동 및 충돌 처리
        self.float_y += self.velocity_y * delta_time
        self.rect.y = int(self.float_y)
        for tile in self.tilemap.tilemap:
            if self.rect.colliderect(tile.rect):
                if self.velocity_y > 0 and self.rect.y < tile.rect.y:  # 아래 충돌
                    self.rect.bottom = tile.rect.top
                elif self.velocity_y < 0 and self.rect.y > tile.rect.y:  # 위 충돌
                    self.rect.top = tile.rect.bottom
                self.float_y = self.rect.y


    def a_star(self, start, goal):
        # 휴리스틱 계산 함수
        def heuristic(node, goal):
            dx = abs(node[0] - goal[0])
            dy = abs(node[1] - goal[1])
            return 10 * (dx + dy) + (14 - 2 * 10) * min(dx, dy)

        # 노드가 이동 가능한지 확인하는 함수
        def is_walkable(node):
            x, y = node
            index = y * self.tilemap.width + x
            return 0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height and self.tilemap.tilemap_data[index] == 0
        
        # A* 알고리즘 실행
        open_set = MinHeap()
        open_set.push((0, start))

        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        closed_set = set()

        while not open_set.is_empty():
            current = open_set.pop()[1]

            # 목표에 도달하면 경로 반환
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path

            closed_set.add(current)

            # 이웃 노드 계산
            neighbors = []
            for direction in self.directions:
                neighbor = (current[0] + direction[0], current[1] + direction[1])

                # 대각선 이동시 벽에 걸리지 않도록 처리
                if abs(direction[0]) == 1 and abs(direction[1]) == 1:
                    adjacent1 = (current[0] + direction[0], current[1])
                    adjacent2 = (current[0], current[1] + direction[1])
                    if not (is_walkable(adjacent1) and is_walkable(adjacent2)):
                        continue

                if is_walkable(neighbor) and neighbor not in closed_set:
                    neighbors.append(neighbor)

            # 이웃 노드에 대한 점수 계산 및 경로 설정
            for neighbor in neighbors:
                movement_cost = 14 if current[0] != neighbor[0] and current[1] != neighbor[1] else 10
                tentative_g_score = g_score[current] + movement_cost

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.push((f_score[neighbor], neighbor))

        return []


class Animation:
    def __init__(self, sprite_sheet, num_frames, frame_duration, roop = True):
        self.sprite_sheet = sprite_sheet
        self.num_frames = num_frames
        self.frame_duration = frame_duration
        self.frames = self.load_frames()
        self.current_frame_index = 0
        self.frame_timer = 0
        self.roop = roop
        self.is_finished = False

    def load_frames(self):
        self.frame_width = self.sprite_sheet.get_width() // self.num_frames
        self.frame_height = self.sprite_sheet.get_height()

        frames = []
        for i in range(self.num_frames):
            frame = self.sprite_sheet.subsurface(
                pygame.Rect(
                    i * self.frame_width,
                    0,  # 행은 항상 0으로 고정
                    self.frame_width,
                    self.frame_height
                )
            )
            # 전역 변수 scale을 이용하여 프레임 크기 조정
            frame = pygame.transform.scale(frame, (int(self.frame_width * scale), int(self.frame_height * scale)))
            frames.append(frame)
        return frames

    def update(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.current_frame_index += 1
            if self.current_frame_index == self.num_frames:
                if not self.roop:
                    self.current_frame_index = self.num_frames - 1
                    self.is_finished = True
                    return
                self.current_frame_index = 0

    def get_current_frame(self):
        return self.frames[self.current_frame_index]
    
    def reset_state(self):
        self.frame_timer = 0
        self.is_finished = False
        self.current_frame_index = 0
        return self
    
class TileMap:
    def __init__(self, tilemap_data, tile_data, width=20, height=23):
        """
        tile_data: {tile_type: {"image": image_path, "collision": boolean}} 형식의 딕셔너리
        """
        self.tilemap_data = tilemap_data
        self.tile_data = {key: {"image": pygame.image.load(resource_path(value["image"])).convert_alpha(),
                                "collision": value["collision"]}
                          for key, value in tile_data.items()}
        print(self.tile_data)
        self.width = width
        self.height = height
        self.tile_size = int(16 * scale)

        # 타일 이미지를 스케일링
        for key in self.tile_data:
            self.tile_data[key]["image"] = pygame.transform.scale(self.tile_data[key]["image"], (self.tile_size, self.tile_size))

        self.tilemap_surface = pygame.Surface((self.width * self.tile_size, self.height * self.tile_size), pygame.SRCALPHA)
        self.tilemap = self.create_tilemap()

    def create_tilemap(self):
        self.tilemap = []
        for index, tile_type in enumerate(self.tilemap_data):
            if tile_type in self.tile_data:  # 유효한 타일 타입만 처리
                row_index = index // self.width  # y 좌표 계산
                col_index = index % self.width   # x 좌표 계산
                rect = self.tile_data[tile_type]["image"].get_rect()
                rect.x = col_index * self.tile_size
                rect.y = row_index * self.tile_size
                
                if self.tile_data[tile_type]["collision"]:      
                    # 타일 객체 생성
                    tile = type("Tile", (object,), {"image": self.tile_data[tile_type]["image"], "rect": rect})
                    self.tilemap.append(tile)

                # 충돌 여부와 관계없이 타일을 맵에 그리기
                self.tilemap_surface.blit(self.tile_data[tile_type]["image"], rect.topleft)

        return self.tilemap



class Button:
    def __init__(self, text, action, rect, font_size):
        self.action = action
        self.font = pygame.font.Font(font_path, int(font_size * scale))
        self.rect = pygame.Rect(
            rect[0] * scale,  # x
            rect[1] * scale,  # y
            rect[2] * scale,  # width
            rect[3] * scale   # height
        )
        self.bg = (0, 0, 0)
        self.hovered = False
        self.clicked = False
        self.hover_color = (200, 200, 200)
        self.click_color = (100, 100, 100)
        self.change_text(text)

    def change_text(self, text):
        self.text = self.font.render(text, True, pygame.Color("White"))
        self.size = self.text.get_size()
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def draw(self):
        bg_color = self.click_color if self.clicked else self.hover_color if self.hovered else self.bg
        pygame.draw.rect(screen, bg_color, self.rect)
        screen.blit(self.text, self.text_rect)

    def handle_event(self, event):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.clicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            if self.clicked and self.hovered:
                self.action()  # 클릭 후 동작 실행
            self.clicked = False


class MainMenu:
    def __init__(self):
        self.is_running = True
        self.menu_buttons = [
            Button("Play", PlayScene().run, (640, 50, 50, 20), 16),
            Button("Settings", SettingsScene().run, (640, 100, 50, 20), 16),
            Button("Quit", self.quit_game, (640, 150, 50, 20), 16)
        ]
        for button in self.menu_buttons:
            button.rect.centerx = DEFAULT_WIDTH/2 * scale
            button.text_rect.centerx = DEFAULT_WIDTH/2 * scale
    
    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while self.is_running:
            screen.fill(pygame.Color(87,102,240))

            # 이벤트 처리 및 버튼 상태 업데이트
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                for button in self.menu_buttons:
                    button.handle_event(event)

            # 버튼 그리기
            for button in self.menu_buttons:
                button.draw()
            
            font = pygame.font.Font(font_path, int(5 * scale))
            text = font.render("You will fight with your Enemy. Good luck.", True, pygame.Color("White"))
            text_rect = text.get_rect(midtop=(screen.get_width()/2, 0))
            screen.blit(text, text_rect)

            pygame.display.update()

class PlayScene:
    def __init__(self):
        tile_data = {
            1: {"image": "assets/tiles/tile.png", "collision": True},   # 벽 타일
            2: {"image": "assets/tiles/flower.png", "collision": False}, # 바닥 타일
            3: {"image": "assets/tiles/grass.png", "collision": False}  # 물 타일
        }
        self.tilemap = TileMap(tilemap_data, tile_data, 20, 10)
        self.player = Player(self.tilemap)
        self.enemy = Enemy(self.tilemap)
        self.is_running = True
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        
        self.background_image = pygame.image.load(resource_path("assets/background.png")).convert_alpha()
        self.background_image_width, self.background_image_height = self.background_image.get_size()
        self.background_image_width = int(self.background_image_width * scale)
        self.background_image_height = int(self.background_image_height * scale)        
        self.background_image = pygame.transform.scale(self.background_image, (self.background_image_width, self.background_image_height))
        self.background_surface = pygame.Surface((self.background_image_width, self.background_image_height))
        self.background_surface.blit(self.background_image, (0, 0))  # 여기에서 이미지 그리기

    def update_camera(self):
        # 화면의 절반 크기만큼 카메라를 플레이어 위치에 맞춰 이동
        self.camera_offset_x = self.player.rect.centerx - DEFAULT_WIDTH // 2
        self.camera_offset_y = self.player.rect.centery - DEFAULT_HEIGHT // 2

        # 카메라가 타일맵 영역을 벗어나지 않도록 제한
        self.camera_offset_x = max(0, min(self.camera_offset_x, self.tilemap.width * self.tilemap.tile_size - DEFAULT_WIDTH))
        self.camera_offset_y = max(0, min(self.camera_offset_y, self.tilemap.height * self.tilemap.tile_size - DEFAULT_HEIGHT))

    def run(self):
        while self.is_running:
            delta_time = min(0.03, clock.tick(300) / 1000)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                        MainMenu().run()
                self.player.handle_event(event)

            self.update_camera()  # 카메라 업데이트
            screen.blit(self.background_surface, (-self.camera_offset_x, -self.camera_offset_y))
            screen.blit(self.tilemap.tilemap_surface, (-self.camera_offset_x, -self.camera_offset_y))
            self.player.update(delta_time)

            player_position = self.player.rect.move(-self.camera_offset_x, -self.camera_offset_y)
            screen.blit(self.player.current_frame, player_position.topleft)

            pygame.display.flip()



class SettingsScene:
    def __init__(self):
        self.is_running = True
        self.back_button = Button("Back", self.go_back, (100, 600, 150, 60), 50)
        self.resolution_buttons = []
        self.create_resolution_buttons()

    def create_resolution_buttons(self):
        resolutions = [
            (640, 360),
            (960, 540),
            (1280, 720),
            (1600, 900),
            (1920, 1080),
        ]
        y_position = 200
        button = Button("Fullscreen", self.toggle_fullscreen, (640, y_position, 450, 60), 50)
        self.resolution_buttons.append(button)
        y_position += 75
        for resolution in resolutions:
            resolution_text = f"{resolution[0]} x {resolution[1]}"
            button = Button(resolution_text, lambda res=resolution: self.change_resolution(res), (640, y_position, 450, 60), 50)
            self.resolution_buttons.append(button)
            y_position += 75
        
    def toggle_fullscreen(self):
        global screen, scale, is_fullscreen
        if not is_fullscreen:
            resolution = (MONITOR_WIDTH, MONITOR_HEIGHT)
            screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            scale = min(resolution[0] / DEFAULT_WIDTH, resolution[1] / DEFAULT_HEIGHT)
            is_fullscreen = True
            self.__init__()
            self.resolution_buttons[0].change_text("Windowed")#나중에 해상도 목록을 딕셔너리로 바꾸기
        else:
            resolution = (MONITOR_WIDTH/2, MONITOR_HEIGHT/2)
            screen = pygame.display.set_mode(resolution)
            scale = min(resolution[0] / DEFAULT_WIDTH, resolution[1] / DEFAULT_HEIGHT)
            is_fullscreen = False
            self.__init__()
            self.resolution_buttons[0].change_text("Fullscreen")

    def change_resolution(self, resolution):
        global screen, scale
        if not is_fullscreen:
            screen = pygame.display.set_mode(resolution)
            scale = min(resolution[0] / DEFAULT_WIDTH, resolution[1] / DEFAULT_HEIGHT)
            self.__init__()  # 스케일이 바뀌었으므로 다시 초기화
        else:
            for button in self.resolution_buttons[1:]:
                button.change_text("Turn off Fullscreen")
                
    def change_keys(self):
        pass
                      
    def go_back(self):
        self.is_running = False
        MainMenu().run()

    def run(self):
        while self.is_running:
            screen.fill((87,102,24))
            self.handle_events()
            
            # 버튼 그리기
            self.back_button.draw()
            for button in self.resolution_buttons:
                button.draw()
            
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            self.back_button.handle_event(event)
            for button in self.resolution_buttons:
                button.handle_event(event)


class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, value):
        self.heap.append(value)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if len(self.heap) > 1:
            self._swap(0, len(self.heap) - 1)
            min_value = self.heap.pop()
            self._heapify_down(0)
        elif self.heap:
            min_value = self.heap.pop()
        else:
            min_value = None
        return min_value

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index] < self.heap[parent_index]:
            self._swap(index, parent_index)
            self._heapify_up(parent_index)

    def _heapify_down(self, index):
        left_child_index = 2 * index + 1
        right_child_index = 2 * index + 2
        smallest = index

        if left_child_index < len(self.heap) and self.heap[left_child_index] < self.heap[smallest]:
            smallest = left_child_index
        if right_child_index < len(self.heap) and self.heap[right_child_index] < self.heap[smallest]:
            smallest = right_child_index

        if smallest != index:
            self._swap(index, smallest)
            self._heapify_down(smallest)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def is_empty(self):
        return len(self.heap) == 0


tilemap_data = [
1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
1, 0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0,
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1,
]



SettingsScene().change_resolution((int(DEFAULT_WIDTH)*3, int(DEFAULT_HEIGHT)*3))


MainMenu().run()
