import pygame
from room import Room, Tile, TILE_SIZE

# --- COLORS ---
STAIRCASE_COLOR = (255, 215, 0)
STORE_COLOR     = (50,  200, 100)
LIBRARY_COLOR   = (100, 50,  200)
ARMORY_COLOR    = (150, 150, 150)
DOJO_COLOR      = (200, 100, 50)
KITCHEN_COLOR   = (200, 50,  50)
KENNELS_COLOR   = (150, 100, 50)
RESCUE_COLOR    = (255, 50,  150)
BOSS_COLOR      = (180, 0,   0)
TEMPLE_ORAKNOS_COLOR = (100, 0,   180)
TEMPLE_THANGAR_COLOR = (40,  40,  40)
TEMPLE_JERRY_COLOR   = (220, 200, 100)
TEMPLE_SQUIRREL_COLOR= (80,  160, 80)

# --- WAYPOINT TYPES ---
STAIRCASE       = "staircase"
STORE           = "store"
LIBRARY         = "library"
ARMORY          = "armory"
DOJO            = "dojo"
KITCHEN         = "kitchen"
KENNELS         = "kennels"
RESCUE          = "rescue"
BOSS            = "boss"
TEMPLE_ORAKNOS  = "temple_oraknos"
TEMPLE_THANGAR  = "temple_thangar"
TEMPLE_JERRY    = "temple_jerry"
TEMPLE_SQUIRREL = "temple_squirrel"

TEMPLE_TYPES = {
    TEMPLE_ORAKNOS, TEMPLE_THANGAR,
    TEMPLE_JERRY,   TEMPLE_SQUIRREL
}

WAYPOINT_LABELS = {
    STAIRCASE:       "STAIRCASE",
    STORE:           "STORE",
    LIBRARY:         "LIBRARY",
    ARMORY:          "ARMORY",
    DOJO:            "DOJO",
    KITCHEN:         "KITCHEN",
    KENNELS:         "KENNELS",
    RESCUE:          "RESCUE ROOM",
    BOSS:            "BOSS CHAMBER",
    TEMPLE_ORAKNOS:  "TEMPLE OF ORAKNOS",
    TEMPLE_THANGAR:  "TEMPLE OF THANGAR",
    TEMPLE_JERRY:    "TEMPLE OF JERRY",
    TEMPLE_SQUIRREL: "TEMPLE OF A SQUIRREL",
}

WAYPOINT_COLORS = {
    STAIRCASE:       STAIRCASE_COLOR,
    STORE:           STORE_COLOR,
    LIBRARY:         LIBRARY_COLOR,
    ARMORY:          ARMORY_COLOR,
    DOJO:            DOJO_COLOR,
    KITCHEN:         KITCHEN_COLOR,
    KENNELS:         KENNELS_COLOR,
    RESCUE:          RESCUE_COLOR,
    BOSS:            BOSS_COLOR,
    TEMPLE_ORAKNOS:  TEMPLE_ORAKNOS_COLOR,
    TEMPLE_THANGAR:  TEMPLE_THANGAR_COLOR,
    TEMPLE_JERRY:    TEMPLE_JERRY_COLOR,
    TEMPLE_SQUIRREL: TEMPLE_SQUIRREL_COLOR,
}

# --- WAYPOINT LIMITS ---
WAYPOINT_LIMITS = {
    STORE:           5,
    LIBRARY:         3,
    ARMORY:          3,
    DOJO:            3,
    KITCHEN:         2,
    KENNELS:         1,
    TEMPLE_ORAKNOS:  1,
    TEMPLE_THANGAR:  1,
    TEMPLE_JERRY:    1,
    TEMPLE_SQUIRREL: 1,
}

# Floors that get a boss room
BOSS_FLOORS = {3, 6, 9, 10, 11}

# Temple god mapping
TEMPLE_GOD_MAP = {
    TEMPLE_ORAKNOS:  "oraknos",
    TEMPLE_THANGAR:  "thangar",
    TEMPLE_JERRY:    "jerry",
    TEMPLE_SQUIRREL: "squirrel",
}


class WaypointRoom(Room):
    def __init__(self, x, y, waypoint_type):
        if waypoint_type == BOSS:
            super().__init__(x, y, width=16, height=12)
        elif waypoint_type in TEMPLE_TYPES:
            super().__init__(x, y, width=14, height=12)
        else:
            super().__init__(x, y, width=12, height=10)

        self.waypoint_type  = waypoint_type
        self.activated      = False
        self.label          = WAYPOINT_LABELS.get(waypoint_type, "WAYPOINT")
        self.color          = WAYPOINT_COLORS.get(waypoint_type, (200,200,200))
        self.boss_defeated  = False

    def build_surface(self):
        pixel_width  = self.width  * TILE_SIZE
        pixel_height = self.height * TILE_SIZE
        self.surface = pygame.Surface((pixel_width, pixel_height))

        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.tiles[row][col]
                tile_rect = pygame.Rect(
                    col * TILE_SIZE, row * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE)

                if tile_type == Tile.WALL:
                    pygame.draw.rect(self.surface, (30,30,45), tile_rect)
                    pygame.draw.rect(self.surface, (20,20,35), tile_rect, 1)
                elif tile_type == Tile.DOOR:
                    pygame.draw.rect(self.surface, (150,100,50), tile_rect)
                    pygame.draw.rect(self.surface, (120,80,30),  tile_rect, 1)
                else:
                    if self.waypoint_type == BOSS:
                        r = min(80  + self.color[0] // 4, 255)
                        g = min(20  + self.color[1] // 4, 255)
                        b = min(20  + self.color[2] // 4, 255)
                    elif self.waypoint_type in TEMPLE_TYPES:
                        r = min(40  + self.color[0] // 3, 255)
                        g = min(40  + self.color[1] // 3, 255)
                        b = min(40  + self.color[2] // 3, 255)
                    else:
                        r = min(60  + self.color[0] // 4, 255)
                        g = min(60  + self.color[1] // 4, 255)
                        b = min(80  + self.color[2] // 4, 255)
                    pygame.draw.rect(self.surface, (r,g,b), tile_rect)
                    pygame.draw.rect(self.surface, (50,50,70), tile_rect, 1)

        cx = pixel_width  // 2
        cy = pixel_height // 2

        if self.waypoint_type == BOSS:
            points_outer = [
                (cx, cy-60),(cx+60,cy),(cx,cy+60),(cx-60,cy)]
            points_inner = [
                (cx, cy-30),(cx+30,cy),(cx,cy+30),(cx-30,cy)]
            pygame.draw.polygon(
                self.surface, self.color, points_outer, 4)
            pygame.draw.polygon(
                self.surface, self.color, points_inner, 3)
            pygame.draw.circle(
                self.surface, self.color, (cx, cy), 8)

        elif self.waypoint_type in TEMPLE_TYPES:
            # Draw altar symbol — two pillars and an arch
            pillar_w = 16
            pillar_h = 80
            # Left pillar
            pygame.draw.rect(self.surface, self.color,
                (cx - 50, cy - pillar_h//2,
                 pillar_w, pillar_h))
            # Right pillar
            pygame.draw.rect(self.surface, self.color,
                (cx + 50 - pillar_w, cy - pillar_h//2,
                 pillar_w, pillar_h))
            # Arch top
            pygame.draw.arc(self.surface, self.color,
                (cx - 50, cy - pillar_h//2 - 30, 100, 60),
                0, 3.14159, 4)
            # Altar base
            pygame.draw.rect(self.surface, self.color,
                (cx - 20, cy + 10, 40, 25))
            # Flame on altar
            pygame.draw.circle(self.surface, (255, 200, 50),
                (cx, cy + 5), 10)
            pygame.draw.circle(self.surface, (255, 100, 0),
                (cx, cy + 8), 6)

        else:
            pygame.draw.circle(
                self.surface, self.color, (cx, cy), 40, 4)
            pygame.draw.circle(
                self.surface, self.color, (cx, cy), 20)

    def check_player_interaction(self, player):
        room_rect = pygame.Rect(
            self.x, self.y,
            self.get_pixel_width(),
            self.get_pixel_height())
        return room_rect.collidepoint(
            player.rect.centerx, player.rect.centery)

    def draw_label(self, screen, camera):
        cx  = self.x + self.get_pixel_width()  // 2
        cy  = self.y + self.get_pixel_height() // 2 - 70
        pos = camera.apply(pygame.Rect(cx, cy, 0, 0))
        font  = pygame.font.SysFont(None, 28)
        label = font.render(self.label, True, self.color)
        screen.blit(label, (
            pos.x - label.get_width() // 2,
            pos.y))

        if self.waypoint_type == BOSS and self.boss_defeated:
            cleared = font.render("CLEARED", True, (50, 200, 50))
            screen.blit(cleared, (
                pos.x - cleared.get_width() // 2,
                pos.y + 20))

        if self.waypoint_type in TEMPLE_TYPES:
            from stats import GODS
            god_key  = TEMPLE_GOD_MAP.get(self.waypoint_type)
            god_data = GODS.get(god_key, {})
            subtitle = font.render(
                god_data.get("title", ""), True,
                self.color)
            screen.blit(subtitle, (
                pos.x - subtitle.get_width() // 2,
                pos.y + 22))
            hint = pygame.font.SysFont(None, 22).render(
                "Press E to pray and heal", True,
                (180, 180, 180))
            screen.blit(hint, (
                pos.x - hint.get_width() // 2,
                pos.y + 44))


class WaypointScheduler:
    def __init__(self):
        self.schedule = self.build_schedule()

    def build_schedule(self):
        import random
        schedule = {f: [STAIRCASE] for f in range(1, 13)}

        for f in [3, 6, 9]:
            schedule[f].append(RESCUE)

        for f in BOSS_FLOORS:
            schedule[f].append(BOSS)

        pool = []
        for wtype, limit in WAYPOINT_LIMITS.items():
            pool.extend([wtype] * limit)

        random.shuffle(pool)
        floors = list(range(1, 13))
        random.shuffle(floors)

        for i, wtype in enumerate(pool):
            floor = floors[i % len(floors)]
            if wtype not in schedule[floor]:
                schedule[floor].append(wtype)
            else:
                for f in range(1, 13):
                    if wtype not in schedule[f]:
                        schedule[f].append(wtype)
                        break

        return schedule

    def get_waypoints_for_floor(self, floor_number):
        return self.schedule.get(floor_number, [STAIRCASE])