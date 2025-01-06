import ctypes
import pygame

# Windows DPI 인식 활성화
ctypes.windll.user32.SetProcessDPIAware()

pygame.init()

# 화면 크기 설정
screen_width = 1200
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))

# 폰트 로드
font = pygame.font.SysFont(None, 48)

# 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 화면 색상 채우기
    screen.fill((0, 0, 0))
    
    # 텍스트 표시
    text = font.render("Hello, Pygame!", True, (255, 255, 255))
    screen.blit(text, (50, 50))
    pygame.draw.circle(screen, "red", (500, 400), 300)
    
    pygame.display.flip()

pygame.quit()
