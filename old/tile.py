import pygame

class Tile:

    pygame.font.init()

    def __init__(self, pos, tileSize, numberColour=(0,0,0)):
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.locked = False
        self.number = None
        self.numberSurface = None
        self.numberColour = numberColour
        self.connected = Tile.find_connected_tiles(self.pos)
        self.font = pygame.font.SysFont("", int(tileSize * 0.8))

    @staticmethod
    def find_connected_tiles(tile):
        connected = []
        x = tile[0]
        y = tile[1]
        area = (x // 3, y // 3)
        for c in range(3):
            for r in range(3):
                pos = (area[0] * 3 + c, area[1] * 3 + r)
                if pos != tile:
                    connected.append(pos)
        for c in range(3):
            for r in range(3):
                if (c, r) != area:
                    if c == area[0]:
                        connected += [(x, r * 3 + i) for i in range(3)] 
                    if r == area[1]:
                        connected += [(c * 3 + i, y) for i in range(3)]
        return connected

    def get_draw_rect(self, tileSize):
        area = (self.x // 3, self.y // 3)
        tile = (self.x % 3, self.y % 3)
        x = 3 + area[0] * (5 + 3 * tileSize) + tile[0] * (tileSize + 1)
        y = 3 + area[1] * (5 + 3 * tileSize) + tile[1] * (tileSize + 1)
        return (x, y, tileSize, tileSize)

    def lock(self, num):
        self.locked = False
        self.set_number(num)
        self.locked = True

    def set_number(self, num):
        if not self.locked and 1 <= num <= 9 and num != self.number:
            self.number = num
            self.numberSurface = self.font.render(f"{num}", True, self.numberColour)
    
    def clear_number(self, unlock=False):
        if not self.locked or unlock:
            self.number = None
            self.numberSurface = None
        if unlock:
            self.locked = False