class Board:
    def __init__(self, pos, tileSize, difficulty, colours):
        self.pos = pos
        self.tileSize = tileSize
        self.difficulty = difficulty
        self.colours = colours

        self.boardSize = 9 * (tileSize + 2)