import pygame
import random
from room import Room, TILE_SIZE

# --- CONSTANTS ---
ROOM_SPACING_X = 1200
ROOM_SPACING_Y = 900
MIN_ROOMS = 8
MAX_ROOMS = 12

class Floor:
    def __init__(self, floor_number=1):
        self.floor_number = floor_number
        self.rooms = []
        self.current_room_index = 0
        self.generate()

    def generate(self):
        self.rooms = []

        start_x = 2000
        start_y = 2000
        start_room = Room(start_x, start_y)
        self.rooms.append(start_room)

        occupied = {(0, 0): start_room}
        frontier = [(0, 0)]

        num_rooms = random.randint(MIN_ROOMS, MAX_ROOMS)

        attempts = 0
        while len(self.rooms) < num_rooms and attempts < 100:
            attempts += 1

            grid_pos = random.choice(frontier)
            parent_room = occupied[grid_pos]

            direction = random.choice(["north", "south", "east", "west"])
            offsets = {
                "north": (0, -1),
                "south": (0, 1),
                "east":  (1, 0),
                "west":  (-1, 0)
            }
            opposite = {
                "north": "south",
                "south": "north",
                "east":  "west",
                "west":  "east"
            }

            dx, dy = offsets[direction]
            new_grid = (grid_pos[0] + dx, grid_pos[1] + dy)

            if new_grid in occupied:
                continue

            new_x = start_x + new_grid[0] * ROOM_SPACING_X
            new_y = start_y + new_grid[1] * ROOM_SPACING_Y

            new_room = Room(new_x, new_y)

            parent_room.doors[direction] = True
            new_room.doors[opposite[direction]] = True
            parent_room.add_doors()
            new_room.add_doors()

            self.rooms.append(new_room)
            occupied[new_grid] = new_room
            frontier.append(new_grid)

        self.current_room_index = 0

    def get_current_room(self):
        return self.rooms[self.current_room_index]

    def draw(self, screen, camera):
        for room in self.rooms:
            room_rect = pygame.Rect(
                room.x, room.y,
                room.get_pixel_width(),
                room.get_pixel_height()
            )
            visible_rect = pygame.Rect(
                camera.offset_x - 200,
                camera.offset_y - 200,
                1360, 940
            )
            if room_rect.colliderect(visible_rect):
                room.draw(screen, camera)

    def draw_minimap(self, screen):
        minimap_x = screen.get_width() - 180
        minimap_y = screen.get_height() - 180
        minimap_scale = 12

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            (minimap_x - 5, minimap_y - 5, 170, 170)
        )

        for i, room in enumerate(self.rooms):
            rx = (room.x - 2000) // ROOM_SPACING_X
            ry = (room.y - 2000) // ROOM_SPACING_Y

            mx = minimap_x + rx * minimap_scale * 4 + 80
            my = minimap_y + ry * minimap_scale * 4 + 80

            color = (0, 200, 255) if i == self.current_room_index else (150, 150, 150)
            pygame.draw.rect(
                screen,
                color,
                (mx, my, minimap_scale, minimap_scale)
            )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (minimap_x - 5, minimap_y - 5, 170, 170),
            2
        )