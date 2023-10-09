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

ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))
MINIMUM_DIMENSIONS = 200
DEFAULT_DIMENSIONS = 800
MINIMUM_FRAMERATE = 24
DEFAULT_FRAMERATE = 60

# Methods
def set_sudoku(board: SudokuBoard, sudoku=None) -> tuple[np.ndarray, np.ndarray]:
    """Sets the sudoku for the board or generates a new puzzle."""
    if sudoku is None:
        sudoku = SudokuGenerator.generate_puzzle()
    solution = SudokuSolver.solve(sudoku.copy())
    board.set_sudoku(sudoku)
    return sudoku, solution

def sudoku_argument(arg: str) -> np.ndarray | None:
    if arg is None:
        return arg

    # Gets the sudoku string from command line arguments
    sudoku_string = arg.replace('.', '0')

    # Ensures sudoku string is of the correct format
    if len(sudoku_string) != 81 or not sudoku_string.isnumeric():
        raise argparse.ArgumentTypeError(
            "sudoku puzzle must be represented as a string of 81 digits from 0-9")

    # Converts string input to a numpy array containing the sudoku
    sudoku = np.array(list(sudoku_string), dtype=int).reshape((9, 9))

    # Ensures the sudoku only has one solution
    if SudokuSolver.count_solutions(sudoku, 2) != 1:
        raise argparse.ArgumentTypeError(
            "sudoku puzzle must have a single solution to be valid")

    return sudoku

def dimensions_argument(arg: str) -> int:
    value = int(arg)
    if value < MINIMUM_DIMENSIONS:
        raise argparse.ArgumentTypeError(
            f"value must be greater than {MINIMUM_DIMENSIONS}")
    return value

def framerate_argument(arg: str) -> int:
    value = int(arg)
    if value < MINIMUM_FRAMERATE:
        raise argparse.ArgumentTypeError(
            f"value must be greater than {MINIMUM_FRAMERATE}")
    return value

# Main Loop
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Adds command line arguments to be parsed
    parser.add_argument("-s", "--sudoku", type=sudoku_argument, default=None, 
        help="sudoku string to initialise the program with")
    parser.add_argument("-a", "--appearance", type=int, choices=[0, 1], default=0,
        help="the appearance of the program, 0 is light mode and 1 is dark mode")
    parser.add_argument("-d", "--dimensions", type=dimensions_argument, default=DEFAULT_DIMENSIONS, 
        help="the size of the square display window in pixels")
    parser.add_argument("-f", "--framerate", type=framerate_argument, default=DEFAULT_FRAMERATE,
        help="the maximum framerate of the program")

    # Parses the command line arguments
    args = parser.parse_args()
    sudoku = args.sudoku
    appearance = [SudokuBoard.LIGHT_MODE, SudokuBoard.DARK_MODE][args.appearance]
    win_size = args.dimensions
    framerate = args.framerate

    # Calculates values for the board's tile size and position
    tile_size = win_size // 15
    board_size = 9 * (tile_size + 2)
    board_screen_pos = (win_size - board_size) // 2
    board_pos = (board_screen_pos, board_screen_pos)

    # Pygame setup
    window = pygame.display.set_mode((win_size, win_size))
    pygame.display.set_caption("Sudoku")
    pygame.display.set_icon(ICON_IMG)
    clock = pygame.time.Clock()

    # Creates font to be displayed when you win
    if not pygame.font.get_init():
        pygame.font.init()
    win_text_font = pygame.font.SysFont("", int(tile_size * 0.8))

    # Sets up the board and creates the starting sudoku
    start_time = time.time()
    board = SudokuBoard(tile_size, board_pos, appearance)
    sudoku, solution = set_sudoku(board, sudoku)

    # Initialises loop variables
    running = True
    over = False

    # Main game loop
    while running:
        clock.tick(framerate)
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
                    sudoku, solution = set_sudoku(board)
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
        if over: 
            board.deselect_all()
        
        # Update the display after everything has been drawn
        pygame.display.update()