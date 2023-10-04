"""Solves sudoku puzzles by representing them as an exact cover problem."""

import numpy as np
import sys

class SudokuConstraints:
    """A class which uses a 2 dimensional doubly circular linked list to represent the constraints for solving a sudoku."""

    def __init__(self, sudoku: np.ndarray) -> None:
        """Constructs a new table of constraints to solve a given sudoku.""" 
        # Calculates the dimensions and amount of nodes needed to represent the constraints table
        columns_n = 324                     # There are always 324 constraints for a sudoku puzzle
        rows_n = 9 * (sudoku == 0).sum()    # There can be at most 9 rows per empty cell
        nodes = 4 * rows_n + columns_n      # Each row has 4 nodes, and there's a header node for each constraint

        # Arrays to store each column's size and whether they've been covered
        self.sizes = np.full(columns_n, 0)
        self.covered = np.full(columns_n, 0)        

        # The max size a column can be
        self.max_size = rows_n

        # Array to store which column each node belongs to
        self.columns = np.arange(nodes)

        # Array to hold the sudoku action that each row represents
        self.actions = np.full(nodes, np.nonzero)

        # Creates basic up and down pointers, where each node points to itself
        self.up = np.arange(nodes)
        self.down = np.arange(nodes)

        # Creates and links left and right pointers
        self.left = np.arange(-1, nodes - 1)
        self.right = np.arange(1, nodes + 1)
        self.left[range(columns_n, nodes, 4)] += 4
        self.right[range(columns_n + 3, nodes, 4)] -= 4
        
        # Mark already satisfied constraints as covered
        rows, cols = np.where(sudoku != 0)
        for row, col in zip(rows, cols):
            for constraint in self.get_constraints(row, col, sudoku[row, col]):
                self.covered[constraint] = 1

        # Add remaining necessary rows to the table
        next_index = columns_n
        last_nodes = np.arange(columns_n)
        rows, cols = np.where(sudoku == 0)
        for row, col in zip(rows, cols):
            for n in range(1, 10):
                next_index = self.add_row(next_index, row, col, n, last_nodes)
                
        # Finishes linking the columns in a circle
        for c in range(columns_n):
            if not self.covered[c]:
                self.link_below(last_nodes[c], c)

    def get_constraints(self, row: int, col: int, n: int) -> tuple[int, int, int, int]:
        """Gets the constraints for a given row, column and number in the sudoku grid."""
        # Stores multiplied row and adjusted n to speed up constraint creation 
        multiplied_row = row * 9
        adjusted_n = n - 1

        # Creates the 4 constraint indexes 
        constraint_0 = multiplied_row + col
        constraint_1 = 81 + multiplied_row + adjusted_n
        constraint_2 = 162 + col * 9 + adjusted_n
        constraint_3 = 243 + (col // 3 + 3 * (row // 3)) * 9 + adjusted_n

        # Returns the indexes as a tuple
        return (constraint_0, constraint_1, constraint_2, constraint_3)

    def add_row(self, index: int, row: int, col: int, n: int, last_nodes: np.ndarray):
        """Adds new nodes to the constraints table for a given sudoku action."""
        # Gets constraints for the action
        constraints = self.get_constraints(row, col, n)

        # Checks if the constraint has already been satisfied and if so returns
        for i in range(4):
            if self.covered[constraints[i]]:
                return index

        # Loops through each constraint and adds a new node to them
        for i, constraint in enumerate(constraints):
            node = index + i
            self.link_below(last_nodes[constraint], node)
            last_nodes[constraint] = node
            self.sizes[constraint] += 1
            self.columns[node] = constraint
            self.actions[node] = (row, col, n)

        return index + 4

    def link_below(self, node: int, link: int) -> None:
        """Links one node below another."""
        self.down[node] = link
        self.up[link] = node

    def cover(self, column: int) -> None:
        """Removes a column and all of its rows from the table."""
        # If a column has already been covered, it shouldn't be covered again
        if self.covered[column]:
            return

        # Marks a column as covered
        self.covered[column] = 1

        # Loops through all of the column's rows
        i = column
        while (j := (i := self.down[i])) != column:
            # Removes links for every element in the row
            while (j := self.right[j]) != i:
                self.up[self.down[j]] = self.up[j]
                self.down[self.up[j]] = self.down[j]
                self.sizes[self.columns[j]] -= 1        

    def uncover(self, column: int) -> None:
        """Recovers a removed column, relinking all its rows."""
        # If a column is currently not covered, then it shouldn't be uncovered again.
        if not self.covered[column]:
            return

        # Marks a column as not covered
        self.covered[column] = 0

        # Loops through all of the column's rows in reverse to relink them correctly
        i = column
        while (j := (i := self.up[i])) != column:
            # Relinks every element in the row
            while (j := self.left[j]) != i:
                self.sizes[self.columns[j]] += 1
                self.down[self.up[j]] = j
                self.up[self.down[j]] = j        

    def solve(self, solution: list[int]) -> bool:
        """Implements Donald Knuth's 'Algorithm X' for solving the exact cover problem,
        using the dancing links method to find a solution which satisfies all of the constraints.

        Args:
            solution (list[int]): a list passed by reference, in which the action
            to reach the solution will be stored if one is found.

        Returns:
            bool: whether a solution was found.
        """
        # If all constraints have been covered, a solution has been found
        if self.covered.all():
            return True

        # The next best column is one which hasn't yet been covered, and has the smallest size
        row = column = np.argmin(np.where(self.covered, self.max_size, self.sizes))
        
        # Covers the column to remove it from the table
        self.cover(column)

        # Goes through each row in the column nondeterministically
        while (node := (row := self.down[row])) != column:
            # Covers all columns in the row
            while (node := self.right[node]) != row:
                self.cover(self.columns[node])

            # Recursively calls solve using the adjusted table
            if self.solve(solution):
                # If a solution was found, adds the action for the row to the solution
                solution.append(self.actions[row])
                return True

            # Reverts changes by uncovering all columns in the row
            while (node := self.left[node]) != row:
                self.uncover(self.columns[node])
        
        # Uncovers the column to restore the original state, and returns that no solution was found
        self.uncover(column)
        return False

class SudokuSolver():
    def __call__(self, sudoku: np.ndarray) -> np.ndarray:
        """Solves a given sudoku puzzle and returns its solution.

        Args:
            sudoku (np.ndarray): 9x9 numpy array representing the sudku grid.
            Empty cells are stored as 0.

        Returns:
            np.ndarray: 9x9 numpy array containing the solution if one was found. 
            If there is no solution, all array entries are -1.
        """

        # Creates the constraints for the sudoku puzzle
        constraints = SudokuConstraints(sudoku)

        # Attempts to find a solution that satisfies the constraints
        solution_actions = []
        if constraints.solve(solution_actions):
            # If a solution was found, the actions are carried out to complete the sudoku
            for row, col, n in solution_actions:
                sudoku[row, col] = n
        else:
            # Otherwise, if no solution was found, the grid is filled with -1
            sudoku[:] = -1
        
        return sudoku
    
if __name__ == '__main__':
    argv = sys.argv[1:]
    
    # Ensures command line argument for the sudoku puzzle to be solved is specified
    if len(argv) == 0:
        print(f"You must specify a sudoku puzzle to be solved as a command line argument.")
        exit()

    # Ensures the correct amount of command line arguments are specified
    if len(argv) > 2:
        print("There should be at most 2 command line arguments specified.")
        exit()

    # Gets the sudoku string from command line arguments
    sudoku_string = argv[0]

    # Ensures sudoku string is of the correct format
    if len(sudoku_string) != 81 or not sudoku_string.isnumeric():
        print("The sudoku puzzle must be represented as a string of 81 digits from 0-9.")
        exit()

    # Parses the optional print mode argument
    print_mode = 0
    if len(argv) > 1:
        print_mode = argv[1]
        if print_mode != '0' and print_mode != '1':
            print("The second command line argument must be '0' or '1' specifying the output print mode.")
            exit()
        else:
            print_mode = int(print_mode)

    # Converts string input to a numpy array containing the sudoku
    sudoku = np.array(list(sudoku_string), dtype=int).reshape((9, 9))

    # Solves the given sudoku
    solver = SudokuSolver()
    solution = solver(sudoku)

    # Outputs solution as a string in the same format as the input if print mode is 0
    if print_mode == 0:
        print(''.join(map(str, solution.reshape(-1))))
        exit()

    # Pretty prints the sudoku grid for easy reading
    for y in range(9):
        for x in range(9):
            if x % 3 == 0 and x > 0:
                print("|", end="")
            print(f" {solution[y, x]} ", end="")
        if y == 8:
            continue
        if (y + 1) % 3 == 0:
            print("\n---------+---------+---------")
        else:
            print("\n         |         |         ")
    
