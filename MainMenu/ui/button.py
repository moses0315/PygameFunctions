import pygame

# 색상 정의
BLACK = (0, 0, 0)
HOVER_COLOR = (200, 200, 200)
CLICK_COLOR = (150, 150, 150)

class Button:
    def __init__(self, text, pos, font, bg=BLACK):
        self.x, self.y = pos
        self.font = pygame.font.Font(None, font)
        self.bg = bg
        self.hovered = False
        self.clicked = False
        self.change_text(text)

    def change_text(self, text):
        self.text = self.font.render(text, True, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self, screen):
        bg = self.bg
        if self.clicked:
            bg = CLICK_COLOR
        elif self.hovered:
            bg = HOVER_COLOR
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        screen.blit(self.surface, (self.x, self.y))

    def check_hover(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            self.hovered = True
        else:
            self.hovered = False

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.clicked = True
            return True
        if event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
        return False
