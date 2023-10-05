"""Generates random sudoku puzzles with only one solution."""

import sys
import numpy as np
from solver import SudokuSolver, SudokuConstraints

class SudokuGenerator:
    """A class that provides methods for generating random sudoku solutions and puzzles."""
    @staticmethod
    def generate_solution(seed=None) -> np.ndarray:
        """Generates a random sudoku solution.
        
        Args:
            seed: the seed for the random number generator.

        Returns:
            np.ndarray: 9x9 numpy array containing the randomly generated
            sudoku solution.
        """
        # Sets the seed for the numpy random number generator
        np.random.seed(seed)

        # Creates an empty sudoku grid
        sudoku = np.zeros((9, 9), dtype=int)

        # Fills diagonal 3x3s with random numbers for best random starting point
        for i, j in [(0, 3), (3, 6), (6, 9)]:
            sudoku[i:j, i:j] = np.random.permutation(range(1, 10)).reshape(3, 3)

        # Creates constraints for the sudoku
        constraints = SudokuConstraints(sudoku)

        # Finds a random solution to the sudoku
        solution_actions = []
        constraints.solve_randomly(solution_actions)

        # Carries out the actions to complete the sudoku
        for row, col, n in solution_actions:
            sudoku[row, col] = n
        
        # Returns the newly generated solution
        return sudoku
    
    @staticmethod
    def minimalise(sudoku):
        """Recursively removes symbols from a sudoku until it is minimal."""
        # Finds row and column indices of non-empty cells
        rows, cols = np.where(sudoku != 0)
        p = np.random.permutation(len(rows))

        # Loops through a random permutation of these rows and columns
        for row, col in zip(rows[p], cols[p]):
            # Stores the cell's value and empties it
            n = sudoku[row, col]
            sudoku[row, col] = 0

            # Tests if the sudoku still has a unique solution
            if SudokuSolver.count_solutions(sudoku, 2) == 1:
                return SudokuGenerator.minimalise(sudoku)

            # If no unique solution was found, reset the cell
            sudoku[row, col] = n
        
    @staticmethod
    def generate_puzzle(seed=None) -> np.ndarray:
        """Generates a random minimal sudoku puzzle.
        
        Args:
            seed: the seed for the random number generator.

        Returns:
            np.ndarray: 9x9 numpy array containing the randomly generated
            minimal sudoku puzzle.
        """
        # Generates a random solution
        sudoku = SudokuGenerator.generate_solution(seed)

        # Removes symbols until the puzzle is minimal
        SudokuGenerator.minimalise(sudoku)

        # Returns the complete puzzle
        return sudoku

if __name__ == '__main__':
    argv = sys.argv[1:]

    # Ensures the correct amount of command line arguments are specified
    if len(argv) > 1:
        print("There should be at most 1 command line argument specified.")
        exit()

    # Parses the optional print mode argument
    print_mode = 0
    if len(argv) > 0:
        print_mode = argv[0]
        if print_mode != '0' and print_mode != '1':
            print("The command line argument must be '0' or '1' specifying the output print mode.")
            exit()
        else:
            print_mode = int(print_mode)

    # Generates a sudoku with a random seed
    sudoku = SudokuGenerator.generate_puzzle()
    
    # Outputs sudoku in a string format if print mode is 0
    if print_mode == 0:
        print(''.join(map(str, sudoku.reshape(-1))))
        exit()

    # Pretty prints the sudoku for easy reading if print mode is 1
    for y in range(9):
        # Prints the entire current row
        for x in range(9):
            if x % 3 == 0 and x > 0:
                print("|", end="")
            print(f"{sudoku[y, x] if sudoku[y, x] != 0 else ' '}", end="")
        
        # Prints row divider if necessary
        print("\n---+---+---" if (y + 1) % 3 == 0 and y < 8 else "")
