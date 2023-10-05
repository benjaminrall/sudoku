"""Playable sudoku game."""

import pygame
import os
import copy
import numpy as np
from solver import SudokuSolver
from board import SudokuBoard
from generator import SudokuGenerator

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 800
FRAMERATE = 120
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))

TILE_SIZE = 70
BOARD_SIZE = 9 * (TILE_SIZE + 2)
BOARD_POS = ((WIN_WIDTH - BOARD_SIZE) // 2, (WIN_HEIGHT - BOARD_SIZE) // 2)

# Pygame Setup
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Sudoku")
pygame.display.set_icon(ICON_IMG)
clock = pygame.time.Clock()

# Objects
board = SudokuBoard(TILE_SIZE, BOARD_POS, SudokuBoard.DARK_MODE)

# Methods
def create_new_sudoku(board: SudokuBoard) -> tuple[np.ndarray, np.ndarray]:
    """Returns a new sudoku and its solution."""
    sudoku = SudokuGenerator.generate_puzzle()
    solution = SudokuSolver.solve(copy.copy(sudoku))
    board.set_sudoku(sudoku)
    return sudoku, solution

# Variables
running = True
won = False
sudoku, solution = create_new_sudoku(board)

# Main Loop
if __name__ == '__main__':
    while running:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Ensures safe exiting from the application
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEMOTION and not won:
                # Detects mouse motion and updates the board's hovered cell
                mouse_pos = pygame.mouse.get_pos()
                board.hover(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and not won:
                # Detects mouse clicks and updates the board's selected cell
                mouse_pos = pygame.mouse.get_pos()
                board.select(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Resets the sudoku when the 'R' key is pressed
                    won = False
                    sudoku, solution = create_new_sudoku(board)
                elif event.key == pygame.K_SPACE and not won:
                    # Allows the board to be cleared using the space key
                    board.clear()
                elif event.key == pygame.K_z and not won:
                    # Allows changes to be undone using the 'Z' key
                    board.undo()
                elif board.selected:
                    # Allows the selected cell to be cleared and set using the keyboard
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        board.clear_selected_cell()
                    elif event.key > ord('0') and event.key <= ord('9'):
                        board.set_selected_cell(event.key - ord('0'))
                
                    
        # Draws the sudoku board to the window
        board.draw(win)

        # Detects a win
        if (sudoku == solution).all():
            print("WON")
        
        pygame.display.update()