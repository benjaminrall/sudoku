import random
import pygame
import os
import time
from personallib.camera import Camera
from personallib.canvas import *

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 800
FRAMERATE = 60
TILE_SIZE = 50
BOARD_SIZE = 9 * (TILE_SIZE + 2)
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))

# Pygame Setup
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Sudoku")
pygame.display.set_icon(ICON_IMG)
clock = pygame.time.Clock()
pygame.font.init()

# Objects
cam = Camera(win, 0, 0, 1)
boardSurface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
ui = Canvas(WIN_WIDTH, WIN_HEIGHT)

# Variables
running = True

# Methods
def draw_board(cam, surface):
    surface.fill((255, 255, 255))
    # (3 + x, 0) (3 + x, n)
    # (4 + 2x, 0) (4 + 2x, n)
    # 
    # ((5 + 3x) + 3 + x))
    for c in range(0, BOARD_SIZE - (5 + 3 * TILE_SIZE), 5 + 3 * TILE_SIZE):
        for x in range(3 + TILE_SIZE, 5 + 3 * TILE_SIZE, 1 + TILE_SIZE):
            pygame.draw.line(surface, (0, 0, 0), (c + x, 0), (c + x, BOARD_SIZE))
            pygame.draw.line(surface, (0, 0, 0), (0, c + x), (BOARD_SIZE, c + x))
    for x in range(1, BOARD_SIZE, 5 + 3 * TILE_SIZE):
        pygame.draw.line(surface, (0, 0, 0), (x, 0), (x, BOARD_SIZE), 3)
        pygame.draw.line(surface, (0, 0, 0), (0, x), (BOARD_SIZE, x), 3)
    cam.blit(surface, (-BOARD_SIZE / 2, -BOARD_SIZE / 2))

# UI

# Main Loop
if __name__ == '__main__':
    while running:
        
        clock.tick(FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass

        win.fill((200, 200, 200))

        draw_board(cam, boardSurface)

        pygame.display.update()