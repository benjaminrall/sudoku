import pygame
import random
import copy
from tile import Tile

class Board:

    LIGHT_MODE = {
        "default": (255, 255, 255),
        "hovering": (180, 180, 180),
        "selected": (120, 120, 160),
        "connected": (200, 200, 200),
        "text": (0, 0, 0)
    }

    DARK_MODE = {
        "default": (50, 50, 60),
        "hovering": (43, 43, 55),
        "selected": (35, 75, 80),
        "connected": (38, 38, 50),
        "text": (200, 200, 200)
    }

    DIFFICULTIES = {
        "easy": 50,
        "normal": 42,
        "hard": 34,
        "expert": 25,
    }

    def __init__(self, pos, tileSize, startSize = None, colours = None):
        self.pos = pos
        self.tileSize = tileSize
        self.colours = colours
        self.startSize = startSize
        if not self.colours or False in [key in colours for key in Board.LIGHT_MODE]:
            self.colours = Board.LIGHT_MODE
        if not startSize:
            self.startSize = Board.DIFFICULTIES["hard"]
        self.boardSize = 9 * (tileSize + 2)
        self.surface = pygame.Surface((self.boardSize, self.boardSize))
        self.tiles = [[Tile((x, y), tileSize, self.colours["text"]) for x in range(9)] for y in range(9)]
        self.drawRects = [[tile.get_draw_rect(tileSize) for tile in row] for row in self.tiles]
        self.hovering = None
        self.selected = None
        self.selectedTile = None
        print("CREATING BOARD")
        self.solution = self.generate_solution()
        print("SOLUTION GENERATED")
        self.generate_start()
        print("BOARD GENERATED")

    def toDict(self):
        return {(c, r): self.tiles[r][c].number for c in range(9) for r in range(9) if self.tiles[r][c].number is not None}

    def fromDict(self, board, locked=False):
        for r in range(9):
            for c in range(9):
                self.tiles[r][c].clear_number(True)
                key = (c, r)
                if key in board:
                    if locked:
                        self.tiles[key[1]][key[0]].lock(board[key])
                    else:
                        self.tiles[key[1]][key[0]].set_number(board[key])
            
    def draw(self, cam):
        self.surface.fill(self.colours["default"])
        for c in range(0, self.boardSize - (5 + 3 * self.tileSize), 5 + 3 * self.tileSize):
            for x in range(3 + self.tileSize, 5 + 3 * self.tileSize, 1 + self.tileSize):
                pygame.draw.line(self.surface, (0, 0, 0), (c + x, 0), (c + x, self.boardSize))
                pygame.draw.line(self.surface, (0, 0, 0), (0, c + x), (self.boardSize, c + x))
        for x in range(1, self.boardSize, 5 + 3 * self.tileSize):
            pygame.draw.line(self.surface, (0, 0, 0), (x, 0), (x, self.boardSize), 3)
            pygame.draw.line(self.surface, (0, 0, 0), (0, x), (self.boardSize, x), 3)
        if self.selected:
            for pos in self.tiles[self.selected[1]][self.selected[0]].connected:
                pygame.draw.rect(self.surface, self.colours["connected"], self.drawRects[pos[1]][pos[0]])
        if self.hovering:
            pygame.draw.rect(self.surface, self.colours["hovering"], self.drawRects[self.hovering[1]][self.hovering[0]])
        if self.selected:
            pygame.draw.rect(self.surface, self.colours["selected"], self.drawRects[self.selected[1]][self.selected[0]])
        for r, row in enumerate(self.tiles):
            for c, tile in enumerate(row):
                if tile.numberSurface:
                    x = self.drawRects[r][c][0] + self.tileSize / 2 - tile.numberSurface.get_width() / 2
                    y = self.drawRects[r][c][1] + self.tileSize / 2 - tile.numberSurface.get_height() / 2
                    self.surface.blit(tile.numberSurface, (x, y))
        cam.blit(self.surface, self.pos)

    def get_pos(self, mPos):
        x = mPos[0] - self.pos[0]
        y = mPos[1] - self.pos[1]
        if 3 <= x < self.boardSize - 3 and 3 <= y < self.boardSize - 3:
            x -= 3
            y -= 3
            area = (x // (3 * self.tileSize + 5), y // (3 * self.tileSize + 5))
            x -= area[0] * (3 * self.tileSize + 5)
            y -= area[1] * (3 * self.tileSize + 5)
            tile = (x // (self.tileSize + 1), y // (self.tileSize + 1))
            if 0 <= tile[0] <= 2 and 0 <= tile[1] <= 2:
                x -= tile[0] * (self.tileSize + 1)
                y -= tile[1] * (self.tileSize + 1)
                if 0 <= x < self.tileSize and 0 <= y < self.tileSize:
                    i = (int(area[0] * 3 + tile[0]), int(area[1] * 3 + tile[1]))
                    return i
        return None

    def hover(self, cam):
        self.hovering = self.get_pos(cam.get_world_coord(pygame.mouse.get_pos()))

    def select(self, cam):
        self.selected = self.get_pos(cam.get_world_coord(pygame.mouse.get_pos()))
        if self.selected:
            self.selectedTile = self.tiles[self.selected[1]][self.selected[0]]
        else:
            self.selectedTile = None
            
    def generate_start(self):
        board = copy.copy(self.solution)
        solutions = Board.backtrack(board)
        validTiles = [(c, r) for c in range(9) for r in range(9)]
        random.shuffle(validTiles)
        i = 0
        while solutions == 1 or len(board) > self.startSize:
            print(len(board))
            key = validTiles[i]
            if key in board:
                x = board[key]
                board.pop(key)
                validTiles.pop(i)
            solutions = Board.backtrack(board)
            if len(board) > self.startSize and solutions > 1:
                board[key] = x
                validTiles.append(x)
            i = (i + 1) % len(validTiles)
        board[key] = x
        self.fromDict(board, True)

    def generate_solution(self, board = {}):
        validTiles = [(c, r) for c in range(9) for r in range(9) if (c, r) not in board]
        while len(validTiles) > 0:
            random.shuffle(validTiles)
            tile = validTiles[0]
            numbers = [i for i in range(1, 10)]
            for connection in Tile.find_connected_tiles(tile):
                if connection in board and board[connection] in numbers:
                    numbers.remove(board[connection])
            for number in numbers:
                tempBoard = copy.copy(board)
                tempBoard[tile] = number
                if Board.backtrack(tempBoard, 0) > 0:
                    board = tempBoard
                    validTiles.pop(0)
                    break
        return board

    @staticmethod
    def backtrack(board, limit = 1, start = (0, 0)):
        if type(board) == Board:
            board = board.toDict()
        if not type(board) == dict:
            return 0
        if len(board) == 81:
            return 1
        # Finding operative tile
        tile = None
        for r in range(start[1], 9):
            for c in range(start[0], 9):
                if (c, r) not in board:
                    tile = (c, r)
                    break
            start = (0, 0)
            if tile:
                break
        if not tile:
            return 0
        # Finding valid numbers for tile
        numbers = [i for i in range(1, 10)]
        for connection in Tile.find_connected_tiles(tile):
            if connection in board and board[connection] in numbers:
                numbers.remove(board[connection])
        if len(numbers) < 1:
            return 0
        # Recursive search
        total = 0
        for number in numbers:
            tempBoard = copy.copy(board)
            tempBoard[tile] = number
            total += Board.backtrack(tempBoard, limit, tile)
            if total > limit:
                break
        return total
