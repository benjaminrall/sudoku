"""A board object to allow interactions with a sudoku puzzle stored as a numpy array."""

import pygame
import copy
import numpy as np
from solver import SudokuSolver

BLACK = (0, 0, 0)

class SudokuBoard:
    """A class that can be used to play a sudoku puzzle and draw it to a pygame surface."""

    # Light mode colour scheme
    LIGHT_MODE = {
        "background": (240, 240, 240),
        "default": (255, 255, 255),
        "hovering": (180, 180, 180),
        "selected": (120, 120, 160),
        "connected": (200, 200, 200),
        "text": (0, 0, 0),
        "incorrect": (255, 150, 150),
    }

    # Dark mode colour scheme
    DARK_MODE = {
        "background": (10, 10, 10),
        "default": (50, 50, 60),
        "hovering": (43, 43, 55),
        "selected": (35, 75, 80),
        "connected": (38, 38, 50),
        "text": (200, 200, 200),
        "incorrect": (100, 20, 20),
    }

    def __init__(self, cell_size: int, pos: tuple[int, int], colours: dict = DARK_MODE):
        # Stores the cell size and position
        self.cell_size = int(cell_size)
        self.pos = pos

        # Ensures the provided colours is a dictionary containing all required keys
        if type(colours) == dict and all([key in colours for key in self.DARK_MODE]):
            self.colours = colours
        else:
            self.colours = self.DARK_MODE

        # Initialises pygame font if necessary
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("", int(cell_size * 0.8))
        self.text_surfaces = [self.font.render(" ", True, self.colours["text"])]
        self.text_surfaces += [self.font.render(f"{i}", True, self.colours["text"]) for i in range(1, 10)]

        # Calculates the total size of the board
        self.size = 9 * (cell_size + 2)

        # Renders and stores the board background surface
        self.board = self.render_board()

        # Creates an array containing the rects for filling each cell
        self.cell_rects = np.zeros((9, 9, 4), dtype=int)
        self.cell_rects[:, :, :2] = self.generate_cell_positions()
        self.cell_rects[:, :, 2:] = self.cell_size

        # Creates attributes to store cells to be coloured differently
        self.selected = None
        self.hovering = None
        self.connected = set()
        self.incorrect = set()

        # Stack to store all moves made on the sudoku
        self.moves = []

    def render_board(self) -> pygame.Surface:
        surface = pygame.Surface((self.size, self.size))

        # Fills the grid with the default background colour
        surface.fill(self.colours["default"])

        # Draws the lines that display between cells in a block
        for block in range(0, self.size - 3, 5 + 3 * self.cell_size):
            for cell in [3 + self.cell_size, 4 + 2 * self.cell_size]:
                # Calculate position of the line
                pos = cell + block

                # Draws vertical cell lines
                pygame.draw.line(surface, BLACK, (pos, 0), (pos, self.size))
                
                # Draws horizontal cell lines
                pygame.draw.line(surface, BLACK, (0, pos), (self.size, pos))

        # Draws the lines that separate blocks and form the grid's outline
        for pos in range(1, self.size, 5 + 3 * self.cell_size):
            # Draws vertical block lines
            pygame.draw.line(surface, BLACK, (pos, 0), (pos, self.size), 3)

            # Draws horizontal block lines
            pygame.draw.line(surface, BLACK, (0, pos), (self.size, pos), 3)

        return surface
    
    def generate_cell_positions(self) -> np.ndarray:
        """Generates the pixel positions of each cell in the grid."""
        # Creates cell position array
        cell_positions = np.zeros((9, 9, 2), dtype=int)

        # Fills cell positions with their indices
        cell_positions[:, :, 0] = np.arange(9)[:, None]
        cell_positions[:, :, 1] = np.arange(9)[None, :]

        # Uses a vectorised function to convert the cell indices to pixel coordinates
        converted_positions = np.vectorize(lambda i : 
            (i // 3) * (5 + self.cell_size * 3) 
            + 3 + (i % 3) * (1 + self.cell_size)
        )(cell_positions)

        # Returns the converted cell positions
        return converted_positions
    
    def convert_surface_pos(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Converts a given surface pos to an index for the sudoku grid if possible."""
        # Shifts position to be relative to the board's upper left tile
        x, y = pos[0] - self.pos[0] - 3, pos[1] - self.pos[1] - 3

        # Ensures the position is within the board's boundaries
        if x < 0 or x > self.size - 6 or y < 0 or y > self.size - 6:
            return None
        
        # Finds the indices of the block and cell containing the position
        block_size = 3 * self.cell_size + 5
        bx, by = x // block_size, y // block_size

        # Shifts the position to be relative to the block
        x, y = x - bx * block_size, y - by * block_size

        # Finds the indices of the cell containing the position in the block
        cx, cy = x // (self.cell_size + 1), y // (self.cell_size + 1)

        # Ensures the cell is within the block
        if cx < 0 or cx > 2 or cy < 0 or cy > 2:
            return None
        
        # Shifts the position to be relative to the cell
        x, y = x - cx * (self.cell_size + 1), y - cy * (self.cell_size + 1)

        # Ensures position is within the cell's bounds
        if x < 0 or x >= self.cell_size or y < 0 or y >= self.cell_size:
            return None
        
        # Calculates and returns the row and column index of the position
        return bx * 3 + cx, by * 3 + cy

    def set_sudoku(self, sudoku: np.ndarray) -> bool:
        """Sets the sudoku puzzle to render on the board."""
        # Checks that the sudoku is valid and possible
        if SudokuSolver.count_solutions(sudoku, 2) != 1:
            return False

        # Sets the sudoku and stores its solution
        self.sudoku = sudoku
        self.solution = SudokuSolver.solve(sudoku.copy())

        # Creates a mask of the locked cells on the sudoku grid
        self.locked = (sudoku > 0).astype(bool)

        # Resets selected, connected, and hovered cells
        self.hovering = None
        self.selected = None
        self.connected = set()
        self.incorrect = set()

        # Resets moves stack
        self.moves = []
        return True

    def check_solution(self) -> bool:
        """Checks whether the current state of the sudoku matches the solution."""
        return (self.sudoku == self.solution).all()
    
    def check_valid(self, pos: tuple[int, int]) -> bool:
        """Checks whether a given position in the sudoku is currently correct."""
        return self.sudoku[pos] == self.solution[pos]
    
    def calculate_incorrect(self) -> set[tuple]:
        """Calculates the positions of all incorrect cells in the sudoku."""
        condition = np.logical_and(self.sudoku != self.solution, self.sudoku != 0)
        return [(x, y) for y, x in zip(*np.where(condition))]

    def clear(self) -> None:
        """Clears the current sudoku puzzle, resetting it to its starting value."""
        # Stores the 'clear' move on the stack and reverts the board to only contain locked values
        self.moves.append((1, copy.copy(self.sudoku)))
        self.sudoku[np.logical_not(self.locked)] = 0

        # Recalculates incorrect cells
        self.incorrect = self.calculate_incorrect()


    def undo(self) -> None:
        """Undoes actions in the reverse order to which they were taken."""
        # Ensures no error is caused by attempting to undo a move that doesn't exist
        if len(self.moves) == 0:
            return
        
        # Pops the last move off the stack
        last_move = self.moves.pop()

        if last_move[0] == 0:
            # Undoes regular set/remove moves
            self.sudoku[last_move[1]] = last_move[2]
        else:
            # Undoes the 'clear' move, resetting the entire board
            self.sudoku[:, :] = last_move[1]

        # Recalculates incorrect cells
        self.incorrect = self.calculate_incorrect()
        
    def calculate_connected(self, pos: tuple[int, int]) -> set[tuple]:
        """Calculates the positions of all cells connected to a given cell."""
        connected = set()

        # A None position has no connections
        if pos is None:
            return connected
    
        # Adds all cells in the same column
        for col in range(9):
            connected.add((pos[0], col))

        # Adds all cells in the same row
        for row in range(9):
            connected.add((row, pos[1]))

        # Adds all cells in the same block
        bx, by = pos[0] // 3 * 3, pos[1] // 3 * 3
        for row in range(3):
            for col in range(3):
                connected.add((bx + row, by + col))

        return connected

    def select(self, pos: tuple[int, int]) -> None:
        """Selects the cell at the given surface position."""
        self.selected = self.convert_surface_pos(pos) if pos else None
        self.connected = self.calculate_connected(self.selected)

    def hover(self, pos: tuple[int, int]) -> None:
        """Hovers the cell at the given surface position."""
        self.hovering = self.convert_surface_pos(pos) if pos else None

    def deselect_all(self) -> None:
        """Deselects the currently selected cell and removes its connected cells."""
        self.selected = None
        self.hovering = None
        self.connected = set()

    def clear_selected_cell(self) -> None:
        """Clears the currently selected cell if it isn't locked."""
        # Sets the cell's value to 0 in the sudoku
        si = (self.selected[1], self.selected[0])
        if self.selected is not None and not self.locked[si]:
            self.moves.append((0, si, self.sudoku[si]))
            self.sudoku[si] = 0

            # Recalculates incorrect cells
            self.incorrect = self.calculate_incorrect()
    
    def set_selected_cell(self, i: int) -> bool:
        """Sets the currently selected cell to a given value if it isn't locked."""
        # Ensures the value is valid
        if i < 1 or i > 9:
            return

        # Sets the cell's value to the given integer in the sudoku
        si = (self.selected[1], self.selected[0])
        if self.selected is not None and not self.locked[si]:
            self.moves.append((0, si, self.sudoku[si]))
            self.sudoku[si] = i

            # Recalculates incorrect cells
            self.incorrect = self.calculate_incorrect()

            # Checks if the move was valid
            if not self.check_valid(si):
                return False
        
        return True

    def move_selection(self, movement: tuple[int, int]) -> None:
        """Moves the selection by a given amount"""
        # Nothing can happen if there is no current selection
        if self.selected is None:
            return

        # Calculates the adjusted x and y values
        x, y = self.selected[0] + movement[0], self.selected[1] + movement[1]

        # Clips values to be within the grid and sets it to be the new selected cell
        self.selected = tuple(np.clip((x, y), 0, 8))
        self.connected = self.calculate_connected(self.selected)


    def draw(self, surface: pygame.Surface) -> None:
        """Draws a sudoku to the given surface at a specified position.
        
        Args:
            sudoku (np.ndarray): the sudoku to be drawn.
            pos (tuple[int, int]): the position at which the board will be displayed.
            surface (pygame.Surface): the surface on which the board will be drawn.
        """
        surface.fill(self.colours["background"])
        surface.blit(self.render(), self.pos)

    def centre(self, row, col, surface: pygame.Surface):
        """Centres a surface in the cell at the given row and column indices."""
        crow = self.cell_rects[row, col, 1] + (self.cell_size - surface.get_width()) / 2 
        ccol = self.cell_rects[row, col, 0] + (self.cell_size - surface.get_height()) / 2
        return (crow, ccol)

    def render(self) -> pygame.Surface: 
        """Creates a surface containing the board which shows the given sudoku."""
        surface = pygame.Surface((self.size, self.size))
        
        # Draws the empty board onto the surface
        surface.blit(self.board, (0, 0))

        # Fills in connected cells
        for pos in self.connected:
            pygame.draw.rect(surface, self.colours["connected"], self.cell_rects[pos])

        # Fills in the cell that's being hovered over
        if self.hovering is not None:
            pygame.draw.rect(surface, self.colours["hovering"], self.cell_rects[self.hovering])
        
        # Fills in selected cells
        if self.selected is not None:
            pygame.draw.rect(surface, self.colours["selected"], self.cell_rects[self.selected])

        # Fills in incorrect cells
        for pos in self.incorrect:
            pygame.draw.rect(surface, self.colours["incorrect"], self.cell_rects[pos])
        
        # Draws text surfaces to the grid
        for row in range(9):
            for col in range(9):
                digit = self.text_surfaces[self.sudoku[row, col]]
                surface.blit(digit, self.centre(row, col, digit))
        
        return surface