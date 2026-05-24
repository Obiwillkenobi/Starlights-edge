import pygame
import random
from room import Room, Tile, TILE_SIZE

# --- CONSTANTS ---
ROOM_SPACING_X = 1200
ROOM_SPACING_Y = 900
MIN_ROOMS = 8
MAX_ROOMS = 12
CORRIDOR_WIDTH = 3  # Width in tiles

# --- COLORS ---
CORRIDOR_COLOR = (60, 60, 80)
CORRIDOR_LINE_COLOR = (50, 50, 70)

class Corridor:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.surface = None
        self.build_surface()

    def build_surface(self):
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(CORRIDOR_COLOR)
        pygame.draw.rect(self.surface, CORRIDOR_LINE_COLOR,
            (0, 0, self.width, self.height), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, camera):
        draw_pos = camera.apply(
            pygame.Rect(self.x, self.y, self.width, self.height)
        )
        screen.blit(self.surface, (draw_pos.x, draw_pos.y))


class Floor:
    def __init__(self, floor_number=1):
        self.floor_number = floor_number
        self.rooms = []
        self.corridors = []
        self.current_room_index = 0
        self.generate()

    def generate(self):
        self.rooms = []
        self.corridors = []

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

            # Build corridor aligned to door positions
            corridor = self.build_corridor(
                parent_room, new_room, direction
            )
            if corridor:
                self.corridors.append(corridor)

            self.rooms.append(new_room)
            occupied[new_grid] = new_room
            frontier.append(new_grid)

        self.current_room_index = 0

    def get_door_position(self, room, direction):
        # Returns the world pixel position of the door center
        mid_col = room.width // 2
        mid_row = room.height // 2
        corridor_pixels = CORRIDOR_WIDTH * TILE_SIZE

        if direction == "east":
            x = room.x + room.get_pixel_width()
            y = room.y + mid_row * TILE_SIZE - corridor_pixels // 2
            return x, y
        elif direction == "west":
            x = room.x
            y = room.y + mid_row * TILE_SIZE - corridor_pixels // 2
            return x, y
        elif direction == "south":
            x = room.x + mid_col * TILE_SIZE - corridor_pixels // 2
            y = room.y + room.get_pixel_height()
            return x, y
        elif direction == "north":
            x = room.x + mid_col * TILE_SIZE - corridor_pixels // 2
            y = room.y
            return x, y

    def build_corridor(self, room_a, room_b, direction):
        corridor_pixels = CORRIDOR_WIDTH * TILE_SIZE
        ax, ay = self.get_door_position(room_a, direction)

        opposite = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        bx, by = self.get_door_position(room_b, opposite[direction])

        if direction == "east":
            width = bx - ax
            height = corridor_pixels
            if width > 0:
                return Corridor(ax, ay, width, height)

        elif direction == "west":
            width = ax - bx
            height = corridor_pixels
            if width > 0:
                return Corridor(bx, by, width, height)

        elif direction == "south":
            width = corridor_pixels
            height = by - ay
            if height > 0:
                return Corridor(ax, ay, width, height)

        elif direction == "north":
            width = corridor_pixels
            height = ay - by
            if height > 0:
                return Corridor(bx, by, width, height)

        return None

    def get_current_room(self):
        return self.rooms[self.current_room_index]

    def get_nearby_corridors(self, player):
        # Returns corridors close to the player
        nearby = []
        for corridor in self.corridors:
            expanded = corridor.get_rect().inflate(200, 200)
            if expanded.collidepoint(player.rect.centerx, player.rect.centery):
                nearby.append(corridor)
        return nearby

    def get_all_walkable_rects(self):
        rects = []
        for room in self.rooms:
            rects.append(pygame.Rect(
                room.x, room.y,
                room.get_pixel_width(),
                room.get_pixel_height()
            ))
        for corridor in self.corridors:
            rects.append(corridor.get_rect())
        return rects

    def draw(self, screen, camera):
        visible_rect = pygame.Rect(
            camera.offset_x - 200,
            camera.offset_y - 200,
            1360, 940
        )

        for corridor in self.corridors:
            if corridor.get_rect().colliderect(visible_rect):
                corridor.draw(screen, camera)

        for room in self.rooms:
            room_rect = pygame.Rect(
                room.x, room.y,
                room.get_pixel_width(),
                room.get_pixel_height()
            )
            if room_rect.colliderect(visible_rect):
                room.draw(screen, camera)

    def draw_minimap(self, screen):
        minimap_x = screen.get_width() - 180
        minimap_y = screen.get_height() - 180
        minimap_scale = 12

        pygame.draw.rect(screen, (20, 20, 20),
            (minimap_x - 5, minimap_y - 5, 170, 170))

        for i, room in enumerate(self.rooms):
            rx = (room.x - 2000) // ROOM_SPACING_X
            ry = (room.y - 2000) // ROOM_SPACING_Y

            mx = minimap_x + rx * minimap_scale * 4 + 80
            my = minimap_y + ry * minimap_scale * 4 + 80

            color = (0, 200, 255) if i == self.current_room_index else (150, 150, 150)
            pygame.draw.rect(screen, color,
                (mx, my, minimap_scale, minimap_scale))

        pygame.draw.rect(screen, (255, 255, 255),
            (minimap_x - 5, minimap_y - 5, 170, 170), 2)