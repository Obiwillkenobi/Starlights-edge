import pygame
import random
import math
from collision import resolve_collision

# --- CONSTANTS ---
TILE_SIZE = 64

# --- COLORS ---
STONE_COLOR      = (100, 95,  90)
STONE_LINE_COLOR = (80,  75,  70)
GRASS_COLOR      = (40,  80,  40)
GRASS_LINE_COLOR = (35,  70,  35)
WOOD_COLOR       = (120, 80,  40)
WOOD_LINE_COLOR  = (100, 65,  30)
WALL_COLOR       = (80,  70,  60)
WALL_LINE_COLOR  = (60,  55,  45)
DOOR_COLOR       = (150, 100, 50)
GATE_COLOR       = (60,  50,  40)
RITUAL_COLOR     = (80,  0,   150)
EMPTY_COLOR      = (10,  10,  10)

# --- TILE TYPES ---
STONE  = "stone"
GRASS  = "grass"
WOOD   = "wood"
WALL   = "wall"
DOOR   = "door"
GATE   = "gate"
RITUAL = "ritual"
EMPTY  = "empty"

WALKABLE = {STONE, GRASS, WOOD, DOOR, GATE, RITUAL}

# --- SHARED FONTS ---
# Created once at module level so they are never recreated per frame
_FONT_SMALL  = None
_FONT_MEDIUM = None
_FONT_LARGE  = None

def get_fonts():
    global _FONT_SMALL, _FONT_MEDIUM, _FONT_LARGE
    if _FONT_SMALL is None:
        _FONT_SMALL  = pygame.font.SysFont(None, 18)
        _FONT_MEDIUM = pygame.font.SysFont(None, 22)
        _FONT_LARGE  = pygame.font.SysFont(None, 26)
    return _FONT_SMALL, _FONT_MEDIUM, _FONT_LARGE

# --- NPC DIALOGUE ---
NPC_DIALOGUE = {
    "friend": [
        "I've almost decoded another passage from the tome!",
        "The revival ritual is ready. Don't worry, I'll bring you back.",
        "Be careful out there. The castle changes every time.",
        "I found something... the BB seems afraid of something.",
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
        "I heard the castle is different every time. Spooky.",
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
        "Food and rest, best things in the world.",
        "We've got stew, bread, and mystery pie.",
    ],
    "tavern_patron_1": [
        "I'll drink to your health, friend!",
        "Another round? Don't mind if I do.",
    ],
    "tavern_patron_2": [
        "Heard you're heading to the castle again. Brave soul.",
        "The last person who went in never came back. Well, except you.",
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
        "Bring him back okay? Promise?",
    ],
    "old_man": [
        "In my day, the castle was open to everyone.",
        "The BB wasn't always like this. Something changed him.",
        "I've lived in Laphero my whole life. Never seen it this dark.",
        "Back when I was young, the Starlight Castle shone at night.",
    ],
    "mayor": [
        "Now now, let's not be hasty. The castle provides order.",
        "Violence isn't the answer. Perhaps we can negotiate...",
        "The sacrifices are regrettable. But necessary for peace.",
        "I urge you to reconsider. The BB is a reasonable entity.",
    ],
    "guard_1": [
        "Halt! Nobody leaves Laphero.",
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
    def __init__(self, x, y, npc_id, color=(200,180,140)):
        self.rect      = pygame.Rect(x, y, 28, 28)
        self.npc_id    = npc_id
        self.color     = color
        self.dialogue  = NPC_DIALOGUE.get(npc_id, ["..."])
        self.dial_idx  = 0
        # Pre-render the name tag surface once
        self._name_surf = None

    def _get_name_surf(self):
        if self._name_surf is None:
            font, _, _ = get_fonts()
            self._name_surf = font.render(
                self.npc_id.replace("_"," ").title(),
                True, (255,255,255))
        return self._name_surf

    def get_next_line(self):
        line = self.dialogue[self.dial_idx]
        self.dial_idx = (self.dial_idx + 1) % len(self.dialogue)
        return line

    def draw(self, screen, camera):
        dr      = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, dr, border_radius=4)
        tag     = self._get_name_surf()
        screen.blit(tag, (
            dr.centerx - tag.get_width()//2,
            dr.y - 16))


class Guard(NPC):
    def __init__(self, x, y, guard_id, power_mult=1.0):
        super().__init__(x, y, guard_id, color=(150,150,180))
        self.max_health   = int(10 * power_mult)
        self.health       = self.max_health
        self.damage       = max(1, int(2 * power_mult))
        self.active       = True
        self.attack_timer = 0
        self.rect         = pygame.Rect(x, y, 32, 32)
        self._label_surf  = None

    def _get_label_surf(self):
        if self._label_surf is None:
            font, _, _ = get_fonts()
            self._label_surf = font.render(
                "Guard", True, (255,255,255))
        return self._label_surf

    def update(self, player):
        if not self.active:
            return
        dx   = player.rect.centerx - self.rect.centerx
        dy   = player.rect.centery - self.rect.centery
        dist = max(1, (dx*dx + dy*dy)**0.5)
        if dist < 200:
            speed = 2
            self.rect.x += int((dx/dist) * speed)
            self.rect.y += int((dy/dist) * speed)
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
        dr    = camera.apply(self.rect)
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, self.color, dr, border_radius=4)
        pygame.draw.rect(screen, (80,80,80),
            (dr.x, dr.y-8, 32, 5))
        pygame.draw.rect(screen, (200,50,50),
            (dr.x, dr.y-8, int(32*ratio), 5))
        tag = self._get_label_surf()
        screen.blit(tag, (
            dr.centerx - tag.get_width()//2,
            dr.y - 20))


def build_surface(tiles, width, height):
    pw   = width  * TILE_SIZE
    ph   = height * TILE_SIZE
    surf = pygame.Surface((pw, ph))
    color_map = {
        STONE:  (STONE_COLOR,  STONE_LINE_COLOR),
        GRASS:  (GRASS_COLOR,  GRASS_LINE_COLOR),
        WOOD:   (WOOD_COLOR,   WOOD_LINE_COLOR),
        WALL:   (WALL_COLOR,   WALL_LINE_COLOR),
        DOOR:   (DOOR_COLOR,   DOOR_COLOR),
        GATE:   (GATE_COLOR,   GATE_COLOR),
        RITUAL: (RITUAL_COLOR, RITUAL_COLOR),
        EMPTY:  (EMPTY_COLOR,  EMPTY_COLOR),
    }
    for row_idx, row in enumerate(tiles):
        for col_idx, tile in enumerate(row):
            fill, line = color_map.get(
                tile.tile_type, (GRASS_COLOR, GRASS_LINE_COLOR))
            rect = pygame.Rect(
                col_idx * TILE_SIZE,
                row_idx * TILE_SIZE,
                TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surf, fill, rect)
            pygame.draw.rect(surf, line, rect, 1)

            if tile.tile_type == RITUAL:
                cx = col_idx * TILE_SIZE + TILE_SIZE // 2
                cy = row_idx * TILE_SIZE + TILE_SIZE // 2
                pygame.draw.circle(surf,(150,50,255),(cx,cy),28,3)
                pygame.draw.circle(surf,(100,0,200), (cx,cy),16,2)
                for angle in range(0, 360, 60):
                    rx = cx + int(22*math.cos(math.radians(angle)))
                    ry = cy + int(22*math.sin(math.radians(angle)))
                    pygame.draw.circle(surf,(180,80,255),(rx,ry),4)
    return surf


def parse_layout(layout, ox, oy):
    char_map = {
        "S": STONE, "G": GRASS, "W": WALL,
        "O": WOOD,  "A": DOOR,  "T": GATE,
        "R": RITUAL,"E": EMPTY,
    }
    cleaned = []
    for row in layout:
        cleaned.append(row.replace(" ", ""))
    height = len(cleaned)
    width  = max(len(r) for r in cleaned)
    for i in range(len(cleaned)):
        cleaned[i] = (cleaned[i] + "E" * width)[:width]
    tiles = []
    for row in cleaned:
        tile_row = []
        for ch in row:
            tile_row.append(LapheroTile(char_map.get(ch, EMPTY)))
        tiles.append(tile_row)
    return tiles, width, height


def get_wall_rects_from_tiles(tiles, ox, oy):
    walls = []
    for row_idx, row in enumerate(tiles):
        for col_idx, tile in enumerate(row):
            if not tile.walkable:
                walls.append(pygame.Rect(
                    ox + col_idx * TILE_SIZE,
                    oy + row_idx * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE))
    return walls


class LapheroRoom:
    def __init__(self, room_id, layout, npc_list, ox, oy):
        self.room_id = room_id
        self.ox      = ox
        self.oy      = oy
        self.tiles, self.width, self.height = \
            parse_layout(layout, ox, oy)
        self.surface = build_surface(
            self.tiles, self.width, self.height)
        self.npcs    = []
        # Pre-compute wall rects once
        self.walls   = get_wall_rects_from_tiles(
            self.tiles, ox, oy)

        for entry in npc_list:
            col, row, npc_id = entry[:3]
            color = entry[3] if len(entry) > 3 else (200,180,140)
            nx = ox + col * TILE_SIZE + TILE_SIZE // 4
            ny = oy + row * TILE_SIZE + TILE_SIZE // 4
            self.npcs.append(NPC(nx, ny, npc_id, color))

        # Pre-render door label surfaces
        self._door_label_surfs = {}

    def pixel_w(self): return self.width  * TILE_SIZE
    def pixel_h(self): return self.height * TILE_SIZE

    def get_nearby_npc(self, player, radius=80):
        for npc in self.npcs:
            dx = npc.rect.centerx - player.rect.centerx
            dy = npc.rect.centery - player.rect.centery
            if (dx*dx + dy*dy)**0.5 < radius:
                return npc
        return None

    def draw(self, screen, camera):
        dp = camera.apply(pygame.Rect(
            self.ox, self.oy, self.pixel_w(), self.pixel_h()))
        screen.blit(self.surface, dp.topleft)
        for npc in self.npcs:
            npc.draw(screen, camera)


class Laphero:
    OX = 2000
    OY = 2000

    def __init__(self, power_mult=1.0):
        self.power_mult      = power_mult
        self.rooms           = {}
        self.current_room_id = "exterior"
        self.guards          = []
        self.gate_open       = False
        self.completed       = False
        self.active_dialogue = None
        self.dialogue_timer  = 0

        self._build_rooms()
        self._place_guards()
        self._build_triggers()

        self.player_start = (
            self.OX + 16 * TILE_SIZE,
            self.OY + 11 * TILE_SIZE
        )

        # Pre-render all overlay surfaces
        self._pre_render_overlays()

    def _pre_render_overlays(self):
        """Pre-render gate labels and door labels."""
        _, med, _ = get_fonts()
        self._gate_open_surf    = med.render(
            "OPEN", True, (100,200,100))
        self._gate_closed_surf  = med.render(
            "GUARDED — Fight or Sneak!", True, (200,50,50))

        _, small, _ = get_fonts()
        door_names = [
            "Wizard's Tower", "Library",
            "Tavern",         "Blacksmith",
            "Store",          "Hero's Home",
        ]
        self._door_label_surfs = []
        for name in door_names:
            self._door_label_surfs.append(
                med.render(name, True, DOOR_COLOR))

        # Pre-render dialogue box background
        self._dialogue_bg = pygame.Surface((700, 70), pygame.SRCALPHA)
        self._dialogue_bg.fill((20,20,40,230))
        pygame.draw.rect(self._dialogue_bg, (100,100,160),
            (0, 0, 700, 70), 2, border_radius=8)

    def _build_rooms(self):
        ox = self.OX
        oy = self.OY

        ext_layout = [
            "EEEEEEEEEEEEEEEEEEEEEEE",
            "EGGGGGGGGGGGGGGGGGGGGGE",
            "EGSSSSSSSSSSSSSSSSSSGGE",
            "EGSWWWAWWWSSSSSWWWAWWGE",
            "EGSWWWWWWWSSSSSWWWWWWGE",
            "EGSSSSSSSSSSSSSSSSSSGGE",
            "EGSWWWAWWWSSSSSWWWAWWGE",
            "EGSWWWWWWWSSSSSWWWWWWGE",
            "EGSSSSSSSSSSSSSSSSSSGGE",
            "EGSWWWAWWWSSSSSWWWAWWGE",
            "EGSWWWWWWWSSSSSWWWWWWGE",
            "EGSSSSSSSSSSSSSSSSSSGGE",
            "EGGGGGGGSTTTSGGGGGGGGGE",
            "EEEEEEEESSSSSEEEEEEEEEE",
            "EEEEEEEEEEEEEEEEEEEEEEE",
        ]
        ext_npcs = [
            (10, 2, "child",   (220,200,150)),
            (11, 2, "old_man", (160,150,140)),
            (12, 2, "mayor",   (180,160,200)),
        ]
        self.rooms["exterior"] = LapheroRoom(
            "exterior", ext_layout, ext_npcs, ox, oy)

        home_layout = [
            "WWWWWWWWW",
            "WOOOOOOOW",
            "WOORROOW",
            "WOOOOOOOW",
            "WOOOOOOOW",
            "WWWWAWWWW",
        ]
        self.rooms["home"] = LapheroRoom("home", home_layout,
            [(3, 2, "friend", (100,180,255))], ox, oy)

        wizard_layout = [
            "WWWWWWWWW",
            "WOOOOOOOW",
            "WOOOOOOOW",
            "WOOOOOOOW",
            "WOOOOOOOW",
            "WWWWAWWWW",
        ]
        self.rooms["wizard"] = LapheroRoom("wizard", wizard_layout,
            [(4, 2, "wizard", (150,100,255))], ox, oy)

        library_layout = [
            "WWWWWWWWWWW",
            "WOOOOOOOOOW",
            "WOOOOOOOOOW",
            "WOOOOOOOOOW",
            "WOOOOOOOOOW",
            "WWWWWAWWWWW",
        ]
        self.rooms["library"] = LapheroRoom("library", library_layout,
            [(5, 2, "librarian", (200,200,150))], ox, oy)

        tavern_layout = [
            "WWWWWWWWWWWWW",
            "WOOOOOOOOOOOW",
            "WOOOOOOOOOOOW",
            "WOOOOOOOOOOOW",
            "WOOOOOOOOOOOW",
            "WWWWWAWWWWWWW",
        ]
        self.rooms["tavern"] = LapheroRoom("tavern", tavern_layout, [
            (4,  2, "innkeeper",      (220,160,80)),
            (2,  3, "tavern_patron_1",(180,140,100)),
            (6,  3, "tavern_patron_2",(190,150,110)),
            (2,  2, "tavern_patron_3",(170,130,90)),
            (8,  2, "tavern_patron_4",(185,145,105)),
        ], ox, oy)

        blacksmith_layout = [
            "WWWWWWWWWWW",
            "WOOOOOOOOOW",
            "WOOOOOOOOOW",
            "WOOOOOOOOOW",
            "WOOOOOOOOOW",
            "WWWWWAWWWWW",
        ]
        self.rooms["blacksmith"] = LapheroRoom(
            "blacksmith", blacksmith_layout,
            [(5, 2, "blacksmith", (160,120,80))], ox, oy)

        store_layout = [
            "WWWWWWWWWWWWW",
            "WOOOOOOOOOOOW",
            "WOOOOOOOOOOOW",
            "WOOOOOOOOOOOW",
            "WOOOOOOOOOOOW",
            "WWWWWAWWWWWWW",
        ]
        self.rooms["store"] = LapheroRoom("store", store_layout, [
            (4,  2, "shopkeeper",     (80,200,120)),
            (2,  3, "shop_customer_1",(190,160,130)),
            (7,  3, "shop_customer_2",(195,165,135)),
        ], ox, oy)

    def _build_triggers(self):
        ox = self.OX
        oy = self.OY
        T  = TILE_SIZE

        self.door_triggers = [
            (pygame.Rect(ox+6*T,  oy+3*T, T, T), "wizard"),
            (pygame.Rect(ox+18*T, oy+3*T, T, T), "library"),
            (pygame.Rect(ox+6*T,  oy+6*T, T, T), "tavern"),
            (pygame.Rect(ox+18*T, oy+6*T, T, T), "blacksmith"),
            (pygame.Rect(ox+6*T,  oy+9*T, T, T), "store"),
            (pygame.Rect(ox+18*T, oy+9*T, T, T), "home"),
        ]

        self.exit_spawns = {
            "wizard":     (ox + 6*T  + T//2, oy + 5*T),
            "library":    (ox + 15*T + T//2, oy + 5*T),
            "tavern":     (ox + 6*T  + T//2, oy + 8*T),
            "blacksmith": (ox + 15*T + T//2, oy + 8*T),
            "store":      (ox + 6*T  + T//2, oy + 11*T),
            "home":       (ox + 15*T + T//2, oy + 11*T),
        }

        # Door label world positions for drawing
        self._door_label_positions = [
            (ox+6*T,  oy+3*T),
            (ox+15*T, oy+3*T),
            (ox+6*T,  oy+6*T),
            (ox+15*T, oy+6*T),
            (ox+6*T,  oy+9*T),
            (ox+15*T, oy+9*T),
        ]

        self.gate_trigger = pygame.Rect(
            ox + 8*T, oy + 12*T, T*4, T)

    def _place_guards(self):
        ox = self.OX
        oy = self.OY
        self.guards = [
            Guard(ox + 8*TILE_SIZE,  oy + 11*TILE_SIZE,
                  "guard_1", self.power_mult),
            Guard(ox + 11*TILE_SIZE, oy + 11*TILE_SIZE,
                  "guard_2", self.power_mult),
        ]

    def get_current_room(self):
        return self.rooms[self.current_room_id]

    def is_exterior(self):
        return self.current_room_id == "exterior"

    def check_door_transition(self, player):
        px = player.rect.centerx
        py = player.rect.centery

        if self.is_exterior():
            for trigger_rect, dest in self.door_triggers:
                if trigger_rect.collidepoint(px, py):
                    return dest, "south"
            if (self.gate_trigger.collidepoint(px, py) and
                    (self.gate_open or player.stealthed)):
                self.completed = True
        else:
            room   = self.get_current_room()
            exit_y = room.oy + (room.height - 1) * TILE_SIZE
            exit_x_min = room.ox + (room.width//2 - 1) * TILE_SIZE
            exit_x_max = room.ox + (room.width//2 + 1) * TILE_SIZE
            if (py >= exit_y and exit_x_min <= px <= exit_x_max):
                return "exterior", "north"

        return None, None

    def try_interact(self, player):
        room = self.get_current_room()
        npc  = room.get_nearby_npc(player)
        if npc:
            name = npc.npc_id.replace("_"," ").title()
            return f"{name}: {npc.get_next_line()}"
        return None

    def show_dialogue(self, text, duration=200):
        self.active_dialogue = text
        self.dialogue_timer  = duration

    def get_spawn_inside(self, room_id):
        room = self.rooms[room_id]
        return (room.ox + (room.width  // 2) * TILE_SIZE,
                room.oy + (room.height - 2)  * TILE_SIZE)

    def get_spawn_outside(self, from_room_id):
        return self.exit_spawns.get(
            from_room_id,
            (self.OX + 10*TILE_SIZE, self.OY + 10*TILE_SIZE))

    def update(self, player):
        room         = self.get_current_room()
        player.walls = room.walls

        if self.is_exterior():
            all_defeated = all(not g.active for g in self.guards)
            if all_defeated:
                self.gate_open = True
            for guard in self.guards:
                if guard.active:
                    guard.update(player)
                    guard.check_hits(player)

        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
        else:
            self.active_dialogue = None

    def draw(self, screen, camera):
        room = self.get_current_room()
        room.draw(screen, camera)

        if self.is_exterior():
            for guard in self.guards:
                guard.draw(screen, camera)

            # Gate indicator — use pre-rendered surfaces
            draw_gate = camera.apply(self.gate_trigger)
            if self.gate_open:
                pygame.draw.rect(screen,(100,200,100),draw_gate,3)
                lbl = self._gate_open_surf
            else:
                pygame.draw.rect(screen,(200,50,50),draw_gate,3)
                lbl = self._gate_closed_surf
            screen.blit(lbl,(
                draw_gate.centerx - lbl.get_width()//2,
                draw_gate.y - 22))

            # Door labels — use pre-rendered surfaces
            for i, (wx, wy) in enumerate(
                    self._door_label_positions):
                dr  = camera.apply(
                    pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE))
                lbl = self._door_label_surfs[i]
                screen.blit(lbl,(
                    dr.centerx - lbl.get_width()//2,
                    dr.y - 18))

        if self.active_dialogue:
            self._draw_dialogue(screen)

    def _draw_dialogue(self, screen):
        box_w = 700
        box_h = 70
        box_x = screen.get_width()  // 2 - box_w // 2
        box_y = screen.get_height() - box_h - 50
        screen.blit(self._dialogue_bg, (box_x, box_y))
        _, _, large = get_fonts()
        surf = large.render(
            self.active_dialogue, True, (255,255,255))
        screen.blit(surf,(
            box_x + 15,
            box_y + box_h//2 - surf.get_height()//2))