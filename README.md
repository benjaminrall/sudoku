# Python Sudoku

This project provides the ability to solve and generate sudoku puzzles using an efficient implementation of the Dancing Links method, as presented by Donald Knuth in [this paper](https://arxiv.org/abs/cs/0011047).

There are 3 ways to interact with the scripts in the repository:
- Solving sudokus with `solver.py`
- Generating sudokus with `generator.py`
- Playing sudokus with `main.py`

## Solving Sudokus

To solve any sudoku, it can be passed as a command line argument when running the `solver.py` script. The sudoku must be formatted as a sudoku string, with 81 digits from 0-9 in a string (where 0 represents empty cells). The string should be created by reading the cells of a sudoku puzzle row by row from left to right and then top to bottom. Empty cells can also be represented by a '.'.

By default, the result will be another sudoku string in the same form as the input. A second optional command line argument can be specified to change the printing style - 0 (default) will result in a sudoku string, and 1 will result in a pretty printed grid, making the solution easily readable.

#### Examples
```
>>> py solver.py 000000010400000000020000000000050407008000300001090000300400200050100000000806000
693784512487512936125963874932651487568247391741398625319475268856129743274836159
```

```
>>> py solver.py 000801000000000043700000000000050800020030000000000100600000075003400000000200600 1
235|841|796
186|597|243
794|326|518
---+---+---
417|652|839
528|139|467
369|784|152
---+---+---
642|918|375
873|465|921
951|273|684
```

## Generating Sudokus

Random sudokus can be generated using the `generator.py` script. No command line arguments are required, but an optional display mode argument can be provided which works identically to `solver.py`.

Sudokus generated tend to have between 20 and 28 clues, but this can vary. The sudokus are not graded in any way, and can vary hugely in difficulty since they are just completely random. However, it is guaranteed that all sudokus will be minimal (removing any more clues will result in more than 1 possible solution).

#### Examples

```
>>> py generator.py
004100008010034050030000000000060705000400000069870000203000000001950307000002800
```

```
>>> py generator.py 1
  5|  8|  9
79 |  4|   
  6|   |7
---+---+---
   |  9|  8
 53|   | 1
 4 |   |  6
---+---+---
   | 87|
   | 53| 21
9 2|1  | 5
```

## Playing Sudokus

Randomly generated sudokus can be played through a graphical interface created using Pygame. Command line arguments for running the `main.py` script are as follows:

```
usage: main.py [-h] [-s SUDOKU] [-a {0,1}] [-d DIMENSIONS] [-f FRAMERATE]

options:
  -h, --help            show this help message and exit
  -s SUDOKU, --sudoku SUDOKU
                        sudoku string to initialise the program with
  -a {0,1}, --appearance {0,1}
                        the appearance of the program, 0 is light mode and 1 is dark mode
  -d DIMENSIONS, --dimensions DIMENSIONS
                        the size of the square display window in pixels
  -f FRAMERATE, --framerate FRAMERATE
                        the maximum framerate of the program
```

When run without any of the optional arguments, a random sudoku grid is automatically generated and displayed. The default appearance is light mode, default display size is 800 pixels, and default framerate is 60.

To use the sudoku grid, you can simply click on a cell in the grid to select it and then type a number (1-9) to enter it into the cell. Backspace or Delete can be pressed to remove the contents of the selected cell, and Space can be used to clear all cells on the grid. The starting cells are locked, and are not affected by any of these methods.

When a cell is selected, the selection can be moved around the grid using the arrow keys. Pressing the Z key allows any changes made to be undone.

When an incorrect value is entered, the cell is highlighted in red. There is no limit to the amount of incorrect values that can be edited, but for the best experience solving the sudoku should still be attempted with as few mistakes as possible.

When the complete solution is entered, congratulations text will appear along with the time that it took to complete the puzzle. You can start a new puzzle by pressing the R key to generate a new random sudoku.

#### Examples

```
py main.py -s 000801000000000043700000000000050800020030000000000100600000075003400000000200600
```

![Example 1](/imgs/example_1.png)

```
py main.py -a 1
```

![Example 2](/imgs/example_2.png)

#### Gameplay Examples

![Example 3](/imgs/example_3.png)
![Example 4](/imgs/example_4.png)
