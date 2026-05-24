import pygame
import random

# --- CONSTANTS ---
TILE_SIZE = 64
ROOM_MIN_WIDTH = 8
ROOM_MAX_WIDTH = 14
ROOM_MIN_HEIGHT = 6
ROOM_MAX_HEIGHT = 10

# --- COLORS ---
FLOOR_COLOR = (60, 60, 80)
WALL_COLOR = (30, 30, 45)
DOOR_COLOR = (150, 100, 50)
FLOOR_LINE_COLOR = (50, 50, 70)
WALL_LINE_COLOR = (20, 20, 35)
DOOR_LINE_COLOR = (120, 80, 30)

class Tile:
    FLOOR = "floor"
    WALL = "wall"
    DOOR = "door"

class Room:
    def __init__(self, x, y, width=None, height=None):
        self.x = x
        self.y = y
        self.width = width or random.randint(ROOM_MIN_WIDTH, ROOM_MAX_WIDTH)
        self.height = height or random.randint(ROOM_MIN_HEIGHT, ROOM_MAX_HEIGHT)

        self.doors = {
            "north": False,
            "south": False,
            "east": False,
            "west": False
        }

        self.tiles = self.generate_tiles()
        self.enemies = []
        self.cleared = False

        # Surface cache — will be built after doors are added
        self.surface = None

    def generate_tiles(self):
        tiles = []
        for row in range(self.height):
            tile_row = []
            for col in range(self.width):
                if (row == 0 or row == self.height - 1 or
                        col == 0 or col == self.width - 1):
                    tile_row.append(Tile.WALL)
                else:
                    tile_row.append(Tile.FLOOR)
            tiles.append(tile_row)
        return tiles

    def add_doors(self):
        mid_col = self.width // 2
        mid_row = self.height // 2

        if self.doors["north"]:
            self.tiles[0][mid_col] = Tile.DOOR
            self.tiles[0][mid_col - 1] = Tile.DOOR

        if self.doors["south"]:
            self.tiles[self.height - 1][mid_col] = Tile.DOOR
            self.tiles[self.height - 1][mid_col - 1] = Tile.DOOR

        if self.doors["east"]:
            self.tiles[mid_row][self.width - 1] = Tile.DOOR
            self.tiles[mid_row - 1][self.width - 1] = Tile.DOOR

        if self.doors["west"]:
            self.tiles[mid_row][0] = Tile.DOOR
            self.tiles[mid_row - 1][0] = Tile.DOOR

        # Rebuild the surface after doors are added
        self.build_surface()

    def build_surface(self):
        # Draw the room once onto a surface and cache it
        pixel_width = self.width * TILE_SIZE
        pixel_height = self.height * TILE_SIZE
        self.surface = pygame.Surface((pixel_width, pixel_height))

        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.tiles[row][col]
                tile_rect = pygame.Rect(
                    col * TILE_SIZE,
                    row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                if tile_type == Tile.FLOOR:
                    pygame.draw.rect(self.surface, FLOOR_COLOR, tile_rect)
                    pygame.draw.rect(self.surface, FLOOR_LINE_COLOR, tile_rect, 1)
                elif tile_type == Tile.WALL:
                    pygame.draw.rect(self.surface, WALL_COLOR, tile_rect)
                    pygame.draw.rect(self.surface, WALL_LINE_COLOR, tile_rect, 1)
                elif tile_type == Tile.DOOR:
                    pygame.draw.rect(self.surface, DOOR_COLOR, tile_rect)
                    pygame.draw.rect(self.surface, DOOR_LINE_COLOR, tile_rect, 1)

    def get_pixel_width(self):
        return self.width * TILE_SIZE

    def get_pixel_height(self):
        return self.height * TILE_SIZE

    def get_center(self):
        return (
            self.x + self.get_pixel_width() // 2,
            self.y + self.get_pixel_height() // 2
        )

    def draw(self, screen, camera):
        if self.surface is None:
            self.build_surface()

        # Just blit the pre-rendered surface instead of redrawing every tile
        draw_pos = camera.apply(pygame.Rect(
            self.x, self.y,
            self.get_pixel_width(),
            self.get_pixel_height()
        ))
        screen.blit(self.surface, (draw_pos.x, draw_pos.y))