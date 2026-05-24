import pygame
from room import Room, Tile, TILE_SIZE

# --- COLORS ---
STAIRCASE_COLOR = (255, 215, 0)      # Gold
STORE_COLOR = (50, 200, 100)         # Green
LIBRARY_COLOR = (100, 50, 200)       # Purple
ARMORY_COLOR = (150, 150, 150)       # Silver
DOJO_COLOR = (200, 100, 50)          # Orange
KITCHEN_COLOR = (200, 50, 50)        # Red
KENNELS_COLOR = (150, 100, 50)       # Brown
RESCUE_COLOR = (255, 50, 150)        # Pink

# --- WAYPOINT TYPES ---
STAIRCASE = "staircase"
STORE     = "store"
LIBRARY   = "library"
ARMORY    = "armory"
DOJO      = "dojo"
KITCHEN   = "kitchen"
KENNELS   = "kennels"
RESCUE    = "rescue"

# --- WAYPOINT LABELS ---
WAYPOINT_LABELS = {
    STAIRCASE: "STAIRCASE",
    STORE:     "STORE",
    LIBRARY:   "LIBRARY",
    ARMORY:    "ARMORY",
    DOJO:      "DOJO",
    KITCHEN:   "KITCHEN",
    KENNELS:   "KENNELS",
    RESCUE:    "RESCUE ROOM"
}

# --- WAYPOINT COLORS ---
WAYPOINT_COLORS = {
    STAIRCASE: STAIRCASE_COLOR,
    STORE:     STORE_COLOR,
    LIBRARY:   LIBRARY_COLOR,
    ARMORY:    ARMORY_COLOR,
    DOJO:      DOJO_COLOR,
    KITCHEN:   KITCHEN_COLOR,
    KENNELS:   KENNELS_COLOR,
    RESCUE:    RESCUE_COLOR
}

# --- WAYPOINT LIMITS (total appearances across all 12 floors) ---
WAYPOINT_LIMITS = {
    STORE:   5,
    LIBRARY: 3,
    ARMORY:  3,
    DOJO:    3,
    KITCHEN: 2,
    KENNELS: 1
}


class WaypointRoom(Room):
    def __init__(self, x, y, waypoint_type):
        super().__init__(x, y, width=12, height=10)
        self.waypoint_type = waypoint_type
        self.activated = False
        self.label = WAYPOINT_LABELS.get(waypoint_type, "WAYPOINT")
        self.color = WAYPOINT_COLORS.get(waypoint_type, (200, 200, 200))

    def build_surface(self):
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
                if tile_type == Tile.WALL:
                    pygame.draw.rect(self.surface, (30, 30, 45), tile_rect)
                    pygame.draw.rect(self.surface, (20, 20, 35), tile_rect, 1)
                elif tile_type == Tile.DOOR:
                    pygame.draw.rect(self.surface, (150, 100, 50), tile_rect)
                    pygame.draw.rect(self.surface, (120, 80, 30), tile_rect, 1)
                else:
                    r = min(60 + self.color[0] // 4, 255)
                    g = min(60 + self.color[1] // 4, 255)
                    b = min(80 + self.color[2] // 4, 255)
                    pygame.draw.rect(self.surface, (r, g, b), tile_rect)
                    pygame.draw.rect(self.surface, (50, 50, 70), tile_rect, 1)

        cx = pixel_width // 2
        cy = pixel_height // 2
        pygame.draw.circle(self.surface, self.color, (cx, cy), 40, 4)
        pygame.draw.circle(self.surface, self.color, (cx, cy), 20)

    def check_player_interaction(self, player):
        room_rect = pygame.Rect(
            self.x, self.y,
            self.get_pixel_width(),
            self.get_pixel_height()
        )
        return room_rect.collidepoint(
            player.rect.centerx, player.rect.centery
        )

    def draw_label(self, screen, camera):
        cx = self.x + self.get_pixel_width() // 2
        cy = self.y + self.get_pixel_height() // 2 - 60
        draw_pos = camera.apply(pygame.Rect(cx, cy, 0, 0))

        font = pygame.font.SysFont(None, 28)
        label = font.render(self.label, True, self.color)
        screen.blit(label, (
            draw_pos.x - label.get_width() // 2,
            draw_pos.y
        ))


class WaypointScheduler:
    """
    Decides which waypoints appear on each floor across all 12 floors.
    Staircase appears on every floor.
    Rescue appears on floors 3, 6, 9.
    All other waypoints are distributed respecting their limits.
    """
    def __init__(self):
        self.schedule = self.build_schedule()

    def build_schedule(self):
        import random

        # Start with empty lists for each floor
        schedule = {f: [STAIRCASE] for f in range(1, 13)}

        # Add rescue rooms on floors 3, 6, 9
        for f in [3, 6, 9]:
            schedule[f].append(RESCUE)

        # Build a pool of all waypoints to distribute
        pool = []
        for wtype, limit in WAYPOINT_LIMITS.items():
            pool.extend([wtype] * limit)

        # Shuffle and distribute across floors
        random.shuffle(pool)
        floors = list(range(1, 13))
        random.shuffle(floors)

        for i, wtype in enumerate(pool):
            floor = floors[i % len(floors)]
            # Don't add duplicates to the same floor
            if wtype not in schedule[floor]:
                schedule[floor].append(wtype)
            else:
                # Try other floors
                for f in range(1, 13):
                    if wtype not in schedule[f]:
                        schedule[f].append(wtype)
                        break

        return schedule

    def get_waypoints_for_floor(self, floor_number):
        return self.schedule.get(floor_number, [STAIRCASE])