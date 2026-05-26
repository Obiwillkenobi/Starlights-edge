import pygame
import random
from collision import resolve_collision

# --- CONSTANTS ---
TILE_SIZE = 64

# --- COLORS ---
STONE_COLOR       = (100, 95,  90)
STONE_LINE_COLOR  = (80,  75,  70)
DIRT_COLOR        = (120, 100, 70)
DIRT_LINE_COLOR   = (100, 85,  60)
GRASS_COLOR       = (40,  80,  40)
GRASS_LINE_COLOR  = (35,  70,  35)
WOOD_COLOR        = (120, 80,  40)
WOOD_LINE_COLOR   = (100, 65,  30)
WATER_COLOR       = (40,  80,  150)
WATER_LINE_COLOR  = (30,  60,  130)
WALL_COLOR        = (80,  70,  60)
WALL_LINE_COLOR   = (60,  55,  45)
DOOR_COLOR        = (150, 100, 50)
GATE_COLOR        = (60,  50,  40)
RITUAL_COLOR      = (80,  0,   150)

# --- TILE TYPES ---
STONE  = "stone"
DIRT   = "dirt"
GRASS  = "grass"
WOOD   = "wood"
WATER  = "water"
WALL   = "wall"
DOOR   = "door"
GATE   = "gate"
RITUAL = "ritual"
EMPTY  = "empty"

WALKABLE = {STONE, DIRT, GRASS, WOOD, DOOR, GATE, RITUAL}

# --- NPC DIALOGUE ---
NPC_DIALOGUE = {
    "friend": [
        "I've almost decoded another passage from the tome!",
        "The revival ritual is ready. Don't worry — I'll bring you back.",
        "Be careful out there. The castle changes every time.",
        "I found something interesting... the BB seems afraid of something.",
    ],
    "shopkeeper": [
        "Take whatever you need, friend. On the house.",
        "I've been collecting these trinkets for years. Take your pick.",
        "Come back if you need anything. I'll keep the lights on.",
    ],
    "shop_customer_1": [
        "Terrible business, what happened to your family.",
        "I hope you find them. We're all rooting for you.",
    ],
    "shop_customer_2": [
        "The shopkeeper is a good man. He'd give you the shirt off his back.",
        "I heard the castle is different every time you enter. Spooky.",
    ],
    "wizard": [
        "Magic is patience, and patience is power.",
        "I've been studying the castle's curse. Fascinating, really.",
        "Come back when you've found more tomes. I can teach you much.",
    ],
    "blacksmith": [
        "Good steel is the difference between life and death.",
        "Invest in quality and quality will invest in you.",
        "The better your tools, the better your chances.",
    ],
    "innkeeper": [
        "Welcome to the Rusty Flagon! What'll it be?",
        "Food and rest — best things in the world.",
        "We've got stew, bread, and something the cook calls 'mystery pie'.",
    ],
    "tavern_patron_1": [
        "I'll drink to your health, friend!",
        "Another round? Don't mind if I do.",
    ],
    "tavern_patron_2": [
        "Heard you're heading to the castle again. Brave soul.",
        "The last person who went in never came back. Well... except you.",
    ],
    "tavern_patron_3": [
        "This town hasn't been the same since the BB took over.",
        "At least the ale is still good.",
    ],
    "tavern_patron_4": [
        "My brother tried to fight the castle guards once. Not recommended.",
        "You look like you could use a drink.",
    ],
    "librarian": [
        "Shh. This is a library.",
        "We have tomes on every subject. Magic, history, bestiary...",
        "Knowledge is the greatest weapon.",
    ],
    "child": [
        "Is your son okay? He's my best friend.",
        "I snuck up to the castle wall once. It was scary.",
        "Bring him back, okay? Promise?",
    ],
    "old_man": [
        "In my day, the castle was open to everyone.",
        "The BB wasn't always like this, you know. Something changed him.",
        "I've lived in Laphero my whole life. Never seen it this dark.",
        "Back when I was young, the Starlight Castle actually shone at night.",
    ],
    "mayor": [
        "Now now, let's not be hasty. The castle provides order.",
        "Violence isn't the answer. Perhaps we can negotiate...",
        "The sacrifices are... regrettable. But necessary for peace.",
        "I urge you to reconsider. The BB is a reasonable... entity.",
    ],
    "guard_1": [
        "Halt! Nobody leaves Laphero after dark.",
        "Turn back, citizen.",
    ],
    "guard_2": [
        "The gate is closed. Move along.",
        "We have our orders.",
    ],
}


class LapheroTile:
    def __init__(self, tile_type):
        self.tile_type = tile_type
        self.walkable  = tile_type in WALKABLE


class NPC:
    def __init__(self, x, y, npc_id, color=(200, 180, 140)):
        self.rect      = pygame.Rect(x, y, 28, 28)
        self.npc_id    = npc_id
        self.color     = color
        self.dialogue  = NPC_DIALOGUE.get(npc_id, ["..."])
        self.dial_idx  = 0
        self.talking   = False

    def get_next_line(self):
        line = self.dialogue[self.dial_idx]
        self.dial_idx = (self.dial_idx + 1) % len(self.dialogue)
        return line

    def draw(self, screen, camera):
        dr = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, dr, border_radius=4)
        # Name tag
        font = pygame.font.SysFont(None, 18)
        tag  = font.render(self.npc_id.replace("_", " ").title(),
                           True, (255, 255, 255))
        screen.blit(tag, (dr.x - tag.get_width()//2 + 14,
                          dr.y - 16))


class Guard(NPC):
    def __init__(self, x, y, guard_id, power_mult=1.0):
        super().__init__(x, y, guard_id, color=(150, 150, 180))
        self.max_health  = int(10 * power_mult)
        self.health      = self.max_health
        self.damage      = max(1, int(2 * power_mult))
        self.active      = True
        self.attack_timer = 0
        self.rect        = pygame.Rect(x, y, 32, 32)

    def update(self, player):
        if not self.active:
            return
        dx   = player.rect.centerx - self.rect.centerx
        dy   = player.rect.centery - self.rect.centery
        dist = max(1, (dx*dx + dy*dy)**0.5)
        if dist < 200:
            # Move toward player
            speed = 2
            self.rect.x += int((dx/dist) * speed)
            self.rect.y += int((dy/dist) * speed)
            # Attack
            if dist < 40 and self.attack_timer == 0:
                player.take_damage(self.damage)
                self.attack_timer = 60
        if self.attack_timer > 0:
            self.attack_timer -= 1

    def check_hits(self, player):
        if player.sword and player.sword.active:
            if self.rect.colliderect(player.sword.rect):
                self.health -= player.sword.damage
                player.sword.active = False
        for p in player.projectiles:
            if self.rect.colliderect(p.rect):
                self.health -= p.damage
                p.active = False
        if self.health <= 0:
            self.active = False

    def draw(self, screen, camera):
        if not self.active:
            return
        dr = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, dr, border_radius=4)
        # Health bar
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, (80,80,80),   (dr.x, dr.y-8, 32, 5))
        pygame.draw.rect(screen, (200,50,50),  (dr.x, dr.y-8,
                                                int(32*ratio), 5))
        font = pygame.font.SysFont(None, 18)
        tag  = font.render("Guard", True, (255,255,255))
        screen.blit(tag, (dr.x, dr.y - 20))


class Laphero:
    """
    Hand-crafted top-down town of Laphero.
    Player starts inside the hero's home and walks out.
    """
    def __init__(self, power_mult=1.0):
        self.tile_size  = TILE_SIZE
        self.width      = 32
        self.height     = 28
        self.x          = 1000
        self.y          = 1000
        self.tiles      = []
        self.surface    = None
        self.npcs       = []
        self.guards     = []
        self.power_mult = power_mult
        self.gate_open  = False
        self.completed  = False   # True when player reaches graveyard gate

        # Dialogue state
        self.active_dialogue  = None
        self.dialogue_timer   = 0

        self.build_layout()
        self.build_surface()
        self.place_npcs()

    # ── layout ────────────────────────────────────────────────────────
    def build_layout(self):
        """
        Town layout key:
        S = stone path     D = dirt path
        G = grass          W = wall (building)
        O = wood floor     A = door
        T = gate           R = ritual circle
        ~ = water          E = empty/border
        """
        layout = [
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",  # 0
            "EGGGGGGGGGGGGGGGGGGGGGGGGGGGGGE",   # 1
            "EGGGGGGGGGGGGGGGGGGGGGGGGGGGGGE",   # 2
            "EGGSSSSSSSSSSSSSSSSSSSSSSSGGGE",    # 3  north road
            "EGGSWWWAWWWSSSSSSWWWAWWWSGGGE",    # 4  wizard+library
            "EGGSWOOOOOWSSSSSSWOOOOOWSGGGE",    # 5
            "EGGSWOOOOOWSSSSSSWOOOOOWSGGGE",    # 6
            "EGGSWWWWWWWSSSSSSWWWWWWWSGGGE",    # 7
            "EGGSSSSSSSSSSSSSSSSSSSSSSSGGGE",    # 8  mid road
            "EGGSWWWAWWWSSSSSSWWWWWWWSGGGE",    # 9  tavern+blacksmith
            "EGGSWOOOOOWSSSSSSWOOOOOWSGGGE",    # 10
            "EGGSWOOOOOWSSSSSSWOOOOOWSGGGE",    # 11
            "EGGSWWWWWWWSSSSSSWWWAWWWSGGGE",    # 12
            "EGGSSSSSSSSSSSSSSSSSSSSSSSGGGE",    # 13 mid road
            "EGGSWWWAWWWSSSSSSSSSSSSSSGGGE",    # 14 store
            "EGGSWOOOOOWSSSSSSSSSSSSSSGGGE",    # 15
            "EGGSWOOOOOWSSSSSSSSSSSSSSGGGE",    # 16
            "EGGSWWWWWWWSSSSSSSSSSSSSSGGGE",    # 17
            "EGGSSSSSSSSSSSSSSSSSSSSSSSGGGE",    # 18 south road
            "EGGSWWWAWWWSSSSSSSWWWAWWWSGGGE",   # 19 home+shop
            "EGGSWOORROWSSSSSSSWOOOOOWSGGGE",   # 20 ritual circle
            "EGGSWOOOOOWSSSSSSSWOOOOOWSGGGE",   # 21
            "EGGSWWWWWWWSSSSSSSWWWWWWWSGGGE",   # 22
            "EGGSSSSSSSSSSSSSSSSSSSSSSSGGGE",    # 23 south road
            "EGGGGGGGSSSSSTTTSSSSGGGGGGGGE",    # 24 gate row
            "EEEEEEEESSSSSSSSSSSEEEEEEEEEE",    # 25 outside gate
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",  # 26
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",  # 27
        ]

        cleaned = []
        for row in layout:
            row = row.replace(" ", "")
            row = (row + "E" * self.width)[:self.width]
            cleaned.append(row)

        self.tiles = []
        char_map = {
            "S": STONE, "D": DIRT,  "G": GRASS,
            "W": WALL,  "O": WOOD,  "A": DOOR,
            "T": GATE,  "R": RITUAL,"~": WATER,
            "E": EMPTY
        }
        for row_idx, row in enumerate(cleaned):
            tile_row = []
            for col_idx, ch in enumerate(row):
                tile_row.append(
                    LapheroTile(char_map.get(ch, EMPTY)))
            self.tiles.append(tile_row)

        # Player starts just inside the hero's home door (row 19 col 9)
        self.player_start = (
            self.x + 9 * TILE_SIZE + TILE_SIZE // 2,
            self.y + 21 * TILE_SIZE
        )

        # Gate exit position
        self.gate_exit = (
            self.x + 15 * TILE_SIZE,
            self.y + 25 * TILE_SIZE
        )

    def get_wall_rects(self):
        walls = []
        for row_idx, row in enumerate(self.tiles):
            for col_idx, tile in enumerate(row):
                if not tile.walkable:
                    walls.append(pygame.Rect(
                        self.x + col_idx * TILE_SIZE,
                        self.y + row_idx * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE))
        return walls

    def get_gate_rect(self):
        return pygame.Rect(
            self.x + 13 * TILE_SIZE,
            self.y + 24 * TILE_SIZE,
            TILE_SIZE * 4, TILE_SIZE * 2)

    # ── NPC placement ─────────────────────────────────────────────────
    def place_npcs(self):
        self.npcs   = []
        self.guards = []

        def npc(col, row, npc_id, color=(200,180,140)):
            nx = self.x + col * TILE_SIZE + TILE_SIZE // 4
            ny = self.y + row * TILE_SIZE + TILE_SIZE // 4
            self.npcs.append(NPC(nx, ny, npc_id, color))

        def guard(col, row, gid):
            gx = self.x + col * TILE_SIZE + TILE_SIZE // 4
            gy = self.y + row * TILE_SIZE + TILE_SIZE // 4
            self.guards.append(
                Guard(gx, gy, gid, self.power_mult))

        # Friend — inside hero's home near ritual circle
        npc(10, 20, "friend", (100, 180, 255))

        # Wizard — inside wizard tower (top left building row 4-7)
        npc(4,  6,  "wizard", (150, 100, 255))

        # Library — top right building row 4-7
        npc(21, 6,  "librarian", (200, 200, 150))

        # Tavern — left building row 9-12
        npc(4,  10, "innkeeper",     (220, 160, 80))
        npc(3,  11, "tavern_patron_1",(180,140,100))
        npc(5,  11, "tavern_patron_2",(190,150,110))
        npc(3,  10, "tavern_patron_3",(170,130, 90))
        npc(5,  10, "tavern_patron_4",(185,145,105))

        # Blacksmith — right building row 9-12
        npc(21, 10, "blacksmith", (160, 120, 80))

        # Store — left building row 14-17
        npc(4,  15, "shopkeeper",     (80, 200, 120))
        npc(3,  16, "shop_customer_1",(190,160,130))
        npc(5,  16, "shop_customer_2",(195,165,135))

        # Town square NPCs — center area
        npc(14, 13, "child",   (220, 200, 150))
        npc(15, 13, "old_man", (160, 150, 140))
        npc(14, 8,  "mayor",   (180, 160, 200))

        # Guards at gate
        guard(13, 24, "guard_1")
        guard(16, 24, "guard_2")

    # ── surface ───────────────────────────────────────────────────────
    def build_surface(self):
        pw = self.width  * TILE_SIZE
        ph = self.height * TILE_SIZE
        self.surface = pygame.Surface((pw, ph))

        color_map = {
            STONE:  (STONE_COLOR,  STONE_LINE_COLOR),
            DIRT:   (DIRT_COLOR,   DIRT_LINE_COLOR),
            GRASS:  (GRASS_COLOR,  GRASS_LINE_COLOR),
            WOOD:   (WOOD_COLOR,   WOOD_LINE_COLOR),
            WATER:  (WATER_COLOR,  WATER_LINE_COLOR),
            WALL:   (WALL_COLOR,   WALL_LINE_COLOR),
            DOOR:   (DOOR_COLOR,   DOOR_COLOR),
            GATE:   (GATE_COLOR,   GATE_COLOR),
            RITUAL: (RITUAL_COLOR, RITUAL_COLOR),
            EMPTY:  ((10,10,10),   (10,10,10)),
        }

        for row_idx, row in enumerate(self.tiles):
            for col_idx, tile in enumerate(row):
                fill, line = color_map.get(
                    tile.tile_type, (GRASS_COLOR, GRASS_LINE_COLOR))
                rect = pygame.Rect(
                    col_idx * TILE_SIZE,
                    row_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.surface, fill, rect)
                pygame.draw.rect(self.surface, line, rect, 1)

                # Ritual circle decoration
                if tile.tile_type == RITUAL:
                    cx = col_idx * TILE_SIZE + TILE_SIZE // 2
                    cy = row_idx * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.circle(
                        self.surface, (150, 50, 255),
                        (cx, cy), 28, 3)
                    pygame.draw.circle(
                        self.surface, (100, 0, 200),
                        (cx, cy), 16, 2)
                    # Rune marks
                    for angle in range(0, 360, 60):
                        import math
                        rx = cx + int(22 * math.cos(
                            math.radians(angle)))
                        ry = cy + int(22 * math.sin(
                            math.radians(angle)))
                        pygame.draw.circle(
                            self.surface, (180, 80, 255),
                            (rx, ry), 4)

                # Gate decoration
                if tile.tile_type == GATE:
                    pygame.draw.rect(
                        self.surface, (100, 80, 50),
                        (col_idx * TILE_SIZE + 4,
                         row_idx * TILE_SIZE + 4,
                         TILE_SIZE - 8,
                         TILE_SIZE - 8), 3)

    # ── interaction ───────────────────────────────────────────────────
    def get_nearby_npc(self, player, radius=80):
        for npc in self.npcs:
            dx = npc.rect.centerx - player.rect.centerx
            dy = npc.rect.centery - player.rect.centery
            if (dx*dx + dy*dy)**0.5 < radius:
                return npc
        return None

    def try_interact(self, player):
        """
        Call when player presses E.
        Returns dialogue string or None.
        """
        npc = self.get_nearby_npc(player)
        if npc:
            return f"{npc.npc_id.replace('_',' ').title()}: " \
                   f"{npc.get_next_line()}"
        return None

    def check_gate_exit(self, player):
        """Returns True if player walks through the open gate."""
        if self.gate_open:
            if self.get_gate_rect().collidepoint(
                    player.rect.centerx, player.rect.centery):
                self.completed = True
        return self.completed

    # ── update ────────────────────────────────────────────────────────
    def update(self, player):
        walls = self.get_wall_rects()
        player.walls = walls

        # Update guards
        all_defeated = True
        for guard in self.guards:
            if guard.active:
                all_defeated = False
                guard.update(player)
                guard.check_hits(player)

        # Gate opens when both guards are defeated
        if all_defeated:
            self.gate_open = True

        self.check_gate_exit(player)

        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
        else:
            self.active_dialogue = None

    # ── draw ─────────────────────────────────────────────────────────
    def draw(self, screen, camera):
        draw_pos = camera.apply(
            pygame.Rect(self.x, self.y,
                        self.width  * TILE_SIZE,
                        self.height * TILE_SIZE))
        screen.blit(self.surface, draw_pos.topleft)

        # Gate status
        gate_rect  = self.get_gate_rect()
        draw_gate  = camera.apply(gate_rect)
        font       = pygame.font.SysFont(None, 22)
        if self.gate_open:
            pygame.draw.rect(screen, (100,200,100), draw_gate, 3)
            lbl = font.render("OPEN", True, (100,200,100))
        else:
            pygame.draw.rect(screen, (200,50,50), draw_gate, 3)
            lbl = font.render("GUARDED", True, (200,50,50))
        screen.blit(lbl, (
            draw_gate.centerx - lbl.get_width()//2,
            draw_gate.y - 20))

        # NPCs
        for npc in self.npcs:
            npc.draw(screen, camera)

        # Guards
        for guard in self.guards:
            guard.draw(screen, camera)

        # Active dialogue box
        if self.active_dialogue:
            self.draw_dialogue(screen, self.active_dialogue)

    def draw_dialogue(self, screen, text):
        box_w = 700
        box_h = 70
        box_x = screen.get_width()  // 2 - box_w // 2
        box_y = screen.get_height() - box_h - 50
        pygame.draw.rect(screen, (20,20,40),
            (box_x, box_y, box_w, box_h),
            border_radius=8)
        pygame.draw.rect(screen, (100,100,160),
            (box_x, box_y, box_w, box_h), 2,
            border_radius=8)
        font = pygame.font.SysFont(None, 26)
        surf = font.render(text, True, (255,255,255))
        screen.blit(surf, (box_x + 15,
                           box_y + box_h//2 - surf.get_height()//2))

    def show_dialogue(self, text, duration=180):
        self.active_dialogue = text
        self.dialogue_timer  = duration