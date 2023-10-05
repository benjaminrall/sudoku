"""Playable sudoku game."""

import pygame
import os
import copy
import numpy as np
import argparse
import time
from solver import SudokuSolver
from board import SudokuBoard
from generator import SudokuGenerator

# Constants
WIN_SIZE = 800
FRAMERATE = 60
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))

TILE_SIZE = WIN_SIZE // 15
BOARD_SIZE = 9 * (TILE_SIZE + 2)
BOARD_SCREEN_POS = (WIN_SIZE - BOARD_SIZE) // 2
BOARD_POS = (BOARD_SCREEN_POS, BOARD_SCREEN_POS)

# Methods
def create_new_sudoku(board: SudokuBoard) -> tuple[np.ndarray, np.ndarray]:
    """Returns a new sudoku and its solution."""
    sudoku = SudokuGenerator.generate_puzzle()
    solution = SudokuSolver.solve(sudoku.copy())
    board.set_sudoku(sudoku)
    return sudoku, solution

# Main Loop
if __name__ == '__main__':
    """
    Args:

    sudoku (str): sudoku string to initialise the program with. default None.
    appearance (int): 0 for dark mode, 1 for light mode. default 0.
    
    """

    # Pygame Setup
    window = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
    pygame.display.set_caption("Sudoku")
    pygame.display.set_icon(ICON_IMG)
    clock = pygame.time.Clock()

    # Creates font to be displayed when you win
    if not pygame.font.get_init():
        pygame.font.init()
    win_text_font = pygame.font.SysFont("", int(TILE_SIZE * 0.8))

    # Sets up the board and creates the starting sudoku
    start_time = time.time()
    board = SudokuBoard(TILE_SIZE, BOARD_POS, SudokuBoard.DARK_MODE)
    sudoku, solution = create_new_sudoku(board)

    # Initialises loop variables
    running = True
    over = False

    # Main game loop
    while running:
        clock.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Ensures safe exiting from the application
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEMOTION and not over:
                # Detects mouse motion and updates the board's hovered cell
                mouse_pos = pygame.mouse.get_pos()
                board.hover(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and not over:
                # Detects mouse clicks and updates the board's selected cell
                mouse_pos = pygame.mouse.get_pos()
                board.select(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Resets the sudoku when the 'R' key is pressed
                    over = False
                    sudoku, solution = create_new_sudoku(board)
                elif event.key == pygame.K_SPACE and not over:
                    # Allows the board to be cleared using the space key
                    board.clear()
                elif event.key == pygame.K_z and not over:
                    # Allows changes to be undone using the 'Z' key
                    board.undo()
                elif board.selected and not over:
                    # Allows the selected cell to be cleared and set using the keyboard
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        board.clear_selected_cell()
                    elif event.key > ord('0') and event.key <= ord('9'):
                        board.set_selected_cell(event.key - ord('0'))
                    # Allows the selection to be moved using the arrow keys
                    elif event.key == pygame.K_RIGHT:
                        board.move_selection((1, 0))
                    elif event.key == pygame.K_LEFT:
                        board.move_selection((-1, 0))
                    elif event.key == pygame.K_DOWN:
                        board.move_selection((0, 1))
                    elif event.key == pygame.K_UP:
                        board.move_selection((0, -1))
                    
        # Draws the sudoku board to the window
        board.draw(window)

        # Detects if the game is over
        over = board.check_solution()
        if over: board.deselect_all()
        
        # Update the display after everything has been drawn
        pygame.display.update()