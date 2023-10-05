import random
import pygame
import os
import time
from personallib.camera import Camera
from personallib.canvas import *

from board import Board

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 800
FRAMERATE = 60
TILE_SIZE = 50
BOARD_SIZE = 9 * (TILE_SIZE + 2)
BOARD_POS = (-BOARD_SIZE / 2, -BOARD_SIZE / 2)
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))

# Pygame Setup
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Sudoku")
pygame.display.set_icon(ICON_IMG)
clock = pygame.time.Clock()
pygame.font.init()

# Objects
cam = Camera(win, 0, 0, 1)
ui = Canvas(WIN_WIDTH, WIN_HEIGHT)
board = Board(BOARD_POS, TILE_SIZE, Board.DIFFICULTIES["easy"], Board.LIGHT_MODE)

# Variables
running = True
won = False

# Methods

# UI
ui.add_element(Text("winText", (WIN_WIDTH / 2, WIN_HEIGHT - 100), "georgia", 40, "You Win! Press 'R' to restart.", (255, 255, 255), "centre"))
ui.set_visible(False)

# Main Loop
if __name__ == '__main__':
    while running:
        
        clock.tick(FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEMOTION and not won:
                board.hover(cam)
            elif event.type == pygame.MOUSEBUTTONDOWN and not won:
                if event.button == 1:
                    board.select(cam)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and won:
                    won = False
                    ui.set_visible(False)
                    board = SudokuBoard(BOARD_POS, TILE_SIZE, SudokuBoard.DIFFICULTIES["hard"], SudokuBoard.DARK_MODE)
                elif board.selected:
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        board.selectedTile.clear_number()
                    else:
                        board.selectedTile.set_number(event.key - 48)

        if board.solution == board.toDict():
            board.selected = None
            board.hovering = None
            won = True
            ui.set_visible(True)

        win.fill((240, 240, 240))

        board.draw(cam)
        ui.update(cam)

        pygame.display.update()