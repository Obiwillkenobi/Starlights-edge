import pygame
import random
from collision import resolve_collision

# --- CONSTANTS ---
TILE_SIZE = 64

# --- COLORS ---
GRASS_COLOR       = (30,  60,  30)
GRASS_LINE_COLOR  = (25,  50,  25)
PATH_COLOR        = (80,  70,  60)
PATH_LINE_COLOR   = (70,  60,  50)
GRAVE_COLOR       = (80,  80,  90)
GRAVE_LINE_COLOR  = (60,  60,  70)
FENCE_COLOR       = (50,  40,  30)
GATE_COLOR        = (150, 130, 80)
CRYPT_COLOR       = (60,  60,  70)
CRYPT_LINE_COLOR  = (40,  40,  50)
FOG_COLOR         = (200, 210, 200, 18)

# --- TILE TYPES ---
GRASS = "grass"
PATH  = "path"
GRAVE = "grave"
FENCE = "fence"
GATE  = "gate"
CRYPT = "crypt"
EMPTY = "empty"


class GraveyardTile:
    def __init__(self, tile_type):
        self.tile_type = tile_type
        self.walkable  = tile_type in (GRASS, PATH, GATE)


class Graveyard:
    def __init__(self):
        self.tile_size  = TILE_SIZE
        self.width      = 24
        self.height     = 20
        self.x          = 2000
        self.y          = 2000
        self.tiles      = []
        self.surface    = None
        self.enemies    = []
        self.completed  = False
        self.entry_pos  = None
        self.exit_pos   = None
        self.build_layout()
        self.build_surface()

    def build_layout(self):
        layout = [
            "EEEEEEEEEEEEEEEEEEEEEEEE",
            "EFFFFFFFFAAFFFFFFFFFFFFF",
            "EFGGGGGGGGGGGGGGGGGGGGFE",
            "EFGGVGGGGGGGGGGGVGGGGGFE",
            "EFGGGGGCCCCCGGGGGGGVGGFE",
            "EFGGVGGCCCCCGGGGGGGGGFFE",
            "EFGGGGGCCCCCGGGVGGGGGFFE",
            "EFGGGGGGPPPPPGGGGGGGGFFE",
            "EFGGGGGGGPGGGGGVGGGGGFFE",
            "EFGGVGGGGGPGGGGGGGGGGFFE",
            "EFGGGGGGGGGPGGGGGVGGFFE",
            "EFGGGGVGGGGPGGGGGGGGGFFE",
            "EFGGGGGGGGGPGGVGGGGGGFFE",
            "EFGGVGGGGGGGPGGGGGGGGFFE",
            "EFGGGGGGGGGGGPGGGVGGFFE",
            "EFGGGGVGGGGGGGPGGGGGFFE",
            "EFGGGGGGGVGGGGPGGGGGFFE",
            "EFGGGGGGGGGGGGPGGGGGFFE",
            "EFFFFFFFFAAFFFFFFFFFFFFF",
            "EEEEEEEEEEEEEEEEEEEEEEEE",
        ]

        cleaned = []
        for row in layout:
            row = row.replace(" ", "")
            row = (row + "E" * self.width)[:self.width]
            cleaned.append(row)

        self.tiles = []
        for row_idx, row in enumerate(cleaned):
            tile_row = []
            for col_idx, ch in enumerate(row):
                if   ch == "G": tile_row.append(GraveyardTile(GRASS))
                elif ch == "P": tile_row.append(GraveyardTile(PATH))
                elif ch == "V": tile_row.append(GraveyardTile(GRAVE))
                elif ch == "F": tile_row.append(GraveyardTile(FENCE))
                elif ch == "A": tile_row.append(GraveyardTile(GATE))
                elif ch == "C": tile_row.append(GraveyardTile(CRYPT))
                else:           tile_row.append(GraveyardTile(EMPTY))
            self.tiles.append(tile_row)

        gate_col       = self.width // 2
        self.entry_pos = (
            self.x + gate_col * TILE_SIZE,
            self.y + 18 * TILE_SIZE + TILE_SIZE // 2
        )
        self.exit_pos  = (
            self.x + gate_col * TILE_SIZE,
            self.y + 1 * TILE_SIZE + TILE_SIZE // 2
        )

    def get_wall_rects(self):
        walls = []
        for row_idx, row in enumerate(self.tiles):
            for col_idx, tile in enumerate(row):
                if not tile.walkable:
                    walls.append(pygame.Rect(
                        self.x + col_idx * TILE_SIZE,
                        self.y + row_idx * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    ))
        return walls

    def get_exit_rect(self):
        # Make exit zone generously tall so player can't miss it
        gate_col = self.width // 2
        return pygame.Rect(
            self.x + (gate_col - 2) * TILE_SIZE,
            self.y,
            TILE_SIZE * 5,
            TILE_SIZE * 3
        )

    def is_cleared(self):
        return len(self.enemies) == 0

    def build_surface(self):
        pw = self.width  * TILE_SIZE
        ph = self.height * TILE_SIZE
        self.surface = pygame.Surface((pw, ph))

        color_map = {
            GRASS: (GRASS_COLOR,  GRASS_LINE_COLOR),
            PATH:  (PATH_COLOR,   PATH_LINE_COLOR),
            GRAVE: (GRAVE_COLOR,  GRAVE_LINE_COLOR),
            FENCE: (FENCE_COLOR,  FENCE_COLOR),
            GATE:  (GATE_COLOR,   GATE_COLOR),
            CRYPT: (CRYPT_COLOR,  CRYPT_LINE_COLOR),
            EMPTY: ((10, 10, 10), (10, 10, 10))
        }

        for row_idx, row in enumerate(self.tiles):
            for col_idx, tile in enumerate(row):
                fill, line = color_map.get(
                    tile.tile_type,
                    (GRASS_COLOR, GRASS_LINE_COLOR))
                rect = pygame.Rect(
                    col_idx * TILE_SIZE,
                    row_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.surface, fill, rect)
                pygame.draw.rect(self.surface, line, rect, 1)

                if tile.tile_type == GRAVE:
                    cx = col_idx * TILE_SIZE + TILE_SIZE // 2
                    cy = row_idx * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.rect(self.surface, (100, 100, 110),
                        (cx - 10, cy - 5, 20, 18))
                    pygame.draw.ellipse(self.surface, (110, 110, 120),
                        (cx - 10, cy - 18, 20, 16))

                if tile.tile_type == CRYPT:
                    pygame.draw.rect(self.surface, (50, 50, 60),
                        (col_idx * TILE_SIZE + 8,
                         row_idx * TILE_SIZE + 8,
                         TILE_SIZE - 16, TILE_SIZE - 16), 2)

    def spawn_enemies(self, floor_manager):
        from enemy import Enemy
        self.enemies = []
        spawn_candidates = []
        for row_idx, row in enumerate(self.tiles):
            if row_idx < 5:
                continue
            for col_idx, tile in enumerate(row):
                if tile.tile_type in (GRASS, PATH):
                    spawn_candidates.append((col_idx, row_idx))

        random.shuffle(spawn_candidates)
        count = 8 + floor_manager.current_floor * 2

        for col, row in spawn_candidates[:count]:
            ex = self.x + col * TILE_SIZE + TILE_SIZE // 2
            ey = self.y + row * TILE_SIZE + TILE_SIZE // 2
            self.enemies.append(
                Enemy(ex, ey,
                      health_mult=floor_manager.get_health_multiplier(),
                      speed_mult =floor_manager.get_speed_multiplier()))

    def update(self, player):
        walls = self.get_wall_rects()
        player.walls = walls

        for enemy in self.enemies:
            enemy.walls = walls
            enemy.update(player, player_in_room=True)
            enemy.check_hits(player)
        self.enemies = [e for e in self.enemies if e.active]

        # Exit only opens when all enemies are defeated
        if self.is_cleared():
            exit_rect = self.get_exit_rect()
            if exit_rect.collidepoint(
                    player.rect.centerx, player.rect.centery):
                self.completed = True

    def draw(self, screen, camera):
        draw_pos = camera.apply(
            pygame.Rect(self.x, self.y,
                        self.width  * TILE_SIZE,
                        self.height * TILE_SIZE))
        screen.blit(self.surface, draw_pos.topleft)

        # Fog overlay
        fog = pygame.Surface(
            (self.width  * TILE_SIZE,
             self.height * TILE_SIZE),
            pygame.SRCALPHA)
        fog.fill(FOG_COLOR)
        screen.blit(fog, draw_pos.topleft)

        for enemy in self.enemies:
            enemy.draw(screen, camera)

        # Draw exit gate
        exit_rect  = self.get_exit_rect()
        draw_exit  = camera.apply(exit_rect)
        font       = pygame.font.SysFont(None, 24)

        if self.is_cleared():
            pygame.draw.rect(screen, GATE_COLOR, draw_exit, 4)
            label = font.render("OPEN", True, GATE_COLOR)
            screen.blit(label, (
                draw_exit.centerx - label.get_width() // 2,
                draw_exit.y - 24))
        else:
            pygame.draw.rect(screen, (180, 30, 30), draw_exit, 4)
            count = font.render(
                f"Defeat all enemies! ({len(self.enemies)} remaining)",
                True, (180, 30, 30))
            screen.blit(count, (
                draw_exit.centerx - count.get_width() // 2,
                draw_exit.y - 24))