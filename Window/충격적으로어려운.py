import pygame
import random

pygame.init()

# define screen size
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sprite Groups")

# frame rate
clock = pygame.time.Clock()
FPS = 60

# colours (including HEX codes converted to colors)
colours = [

    pygame.Color("#422424"),  # HEX color
    pygame.Color("#501516")  , # HEX color
    pygame.Color("#900020")   # HEX color

    
]

# create class for squares
class Square(pygame.sprite.Sprite):
    def __init__(self, col, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill(col)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.move_ip(0, 5)
        # check if sprite has gone off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# create sprite group for squares
squares = pygame.sprite.Group()

# create square and add to squares group
square = Square("crimson", 500, 300)
squares.add(square)

# game loop
run = True

while run:
    clock.tick(FPS)
    # update background
    screen.fill("white")

    # update sprite group
    squares.update()

    # draw sprite group
    squares.draw(screen)

    # event handler
    for event in pygame.event.get():

        # quit program
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:


            # get mouse coordinates
            pos = pygame.mouse.get_pos()
            # create square
            square = Square(random.choice(colours), pos[0], pos[1])
            squares.add(square)

    # update display
    pygame.display.flip()

pygame.quit()
