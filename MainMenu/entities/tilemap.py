import pygame

# 색상 정의
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
GREY = (128, 128, 128)

class TileMap:
    def __init__(self, tile_size, map_type):
        if map_type == 'basic':
            self.tile_map = [
                "################",
                "#..............#",
                "#..............#",
                "#..............#",
                "#......##......#",
                "#..............#",
                "#..............#",
                "#..............#",
                "#.............##",
                "######.....#...#",
                "#........###...#",
                "#.......#......#",
                "########......##",
                "#............###",
                "################",
            ]
            self.color = GREEN
        elif map_type == 'desert':
            self.tile_map = [
                "################",
                "#..............#",
                "#..............#",
                "#..............#",
                "#......##......#",
                "#..............#",
                "#..............#",
                "#..............#",
                "#.............##",
                "######.....#...#",
                "#........###...#",
                "#.......#......#",
                "########......##",
                "#............###",
                "################",
            ]
            self.color = BROWN
        elif map_type == 'industrial':
            self.tile_map = [
                "################",
                "#..............#",
                "#..............#",
                "#..............#",
                "#......##......#",
                "#..............#",
                "#..............#",
                "#..............#",
                "#.............##",
                "######.....#...#",
                "#........###...#",
                "#.......#......#",
                "########......##",
                "#............###",
                "################",
            ]
            self.color = GREY

        self.tile_size = tile_size
        self.tiles = self.create_tiles()

    def create_tiles(self):
        tiles = []
        for row_index, row in enumerate(self.tile_map):
            for col_index, col in enumerate(row):
                if col == "#":
                    tile = pygame.Rect(col_index * self.tile_size, row_index * self.tile_size, self.tile_size, self.tile_size)
                    tiles.append(tile)
        return tiles

    def draw(self, surface):
        for tile in self.tiles:
            pygame.draw.rect(surface, self.color, tile)

    def is_obstacle(self, x, y):
        """
        주어진 좌표에 장애물(타일)이 있는지 확인합니다.
        """
        if 0 <= x < len(self.tile_map[0]) and 0 <= y < len(self.tile_map):
            return self.tile_map[y][x] == "#"
        return False
