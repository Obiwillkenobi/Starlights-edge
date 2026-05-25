import pygame
import random
from room import Room, Tile, TILE_SIZE
from waypoints import (WaypointRoom, WaypointScheduler,
    STAIRCASE, LIBRARY, ARMORY, DOJO,
    RESCUE, STORE, KITCHEN, KENNELS, BOSS,
    BOSS_FLOORS)

GRID_CELL_W = 900
GRID_CELL_H = 700

_scheduler = None

def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = WaypointScheduler()
    return _scheduler

def reset_scheduler():
    global _scheduler
    _scheduler = None

def rooms_for_floor(floor_number):
    base     = 7
    extra    = int((floor_number - 1) * (22 - 7) / 11)
    variance = random.randint(-1, 2)
    return max(5, base + extra + variance)


class Floor:
    def __init__(self, floor_number=1):
        self.floor_number       = floor_number
        self.rooms              = []
        self.waypoint_rooms     = []
        self.current_room_index = 0
        self.staircase_reached  = False
        self.discovered_rooms   = {0}
        self.room_grid          = {}
        self.grid_to_room       = {}
        self.connections        = {}
        self.boss_room          = None
        self.generate()

    # ── helpers ───────────────────────────────────────────────────────
    def room_pixel_origin(self, room, gx, gy):
        cx = 2000 + gx * GRID_CELL_W + GRID_CELL_W // 2
        cy = 2000 + gy * GRID_CELL_H + GRID_CELL_H // 2
        return (cx - room.get_pixel_width()  // 2,
                cy - room.get_pixel_height() // 2)

    def find_farthest_grid(self, start=(0, 0)):
        from collections import deque
        visited  = {start: 0}
        queue    = deque([start])
        farthest = start
        max_dist = 0
        for dx, dy in [(0,-1),(0,1),(1,0),(-1,0)]:
            pass
        offsets = [(0,-1),(0,1),(1,0),(-1,0)]
        while queue:
            pos  = queue.popleft()
            dist = visited[pos]
            if dist > max_dist:
                max_dist = dist
                farthest = pos
            for dx, dy in offsets:
                nb = (pos[0]+dx, pos[1]+dy)
                if nb in self.grid_to_room and nb not in visited:
                    visited[nb] = dist + 1
                    queue.append(nb)
        return farthest

    def connect(self, room_a, direction, room_b):
        opp = {"north":"south","south":"north",
               "east":"west",  "west":"east"}
        room_a.doors[direction]      = True
        room_b.doors[opp[direction]] = True
        room_a.add_doors()
        room_b.add_doors()
        self.connections.setdefault(id(room_a), {})[direction]        = room_b
        self.connections.setdefault(id(room_b), {})[opp[direction]]   = room_a

    def place_room(self, room, gx, gy):
        px, py = self.room_pixel_origin(room, gx, gy)
        room.x, room.y = px, py
        self.rooms.append(room)
        self.room_grid[id(room)]    = (gx, gy)
        self.grid_to_room[(gx, gy)] = room
        self.connections[id(room)]  = {}

    # ── generation ────────────────────────────────────────────────────
    def generate(self):
        self.rooms            = []
        self.waypoint_rooms   = []
        self.discovered_rooms = {0}
        self.room_grid        = {}
        self.grid_to_room     = {}
        self.connections      = {}
        self.boss_room        = None

        offsets  = {"north":(0,-1),"south":(0,1),
                    "east":(1,0),  "west":(-1,0)}
        opposite = {"north":"south","south":"north",
                    "east":"west",  "west":"east"}

        # Starting room
        start_room = Room(0, 0)
        self.place_room(start_room, 0, 0)
        frontier = [(0, 0)]

        # Grow random rooms
        target   = rooms_for_floor(self.floor_number)
        attempts = 0
        while len(self.rooms) < target and attempts < 500:
            attempts += 1
            grid_pos  = random.choice(frontier)
            direction = random.choice(list(offsets.keys()))
            dx, dy    = offsets[direction]
            new_grid  = (grid_pos[0]+dx, grid_pos[1]+dy)
            if new_grid in self.grid_to_room:
                continue
            new_room = Room(0, 0)
            self.place_room(new_room, *new_grid)
            self.connect(self.grid_to_room[grid_pos],
                         direction, new_room)
            frontier.append(new_grid)

        # Find farthest point
        farthest = self.find_farthest_grid()

        # On boss floors: insert boss room between farthest and staircase
        if self.floor_number in BOSS_FLOORS:
            # Boss room goes one step beyond farthest
            boss_grid = None
            boss_dir  = None
            for direction, (dx, dy) in offsets.items():
                candidate = (farthest[0]+dx, farthest[1]+dy)
                if candidate not in self.grid_to_room:
                    boss_grid = candidate
                    boss_dir  = direction
                    break

            if boss_grid:
                boss_room = WaypointRoom(0, 0, BOSS)
                self.place_room(boss_room, *boss_grid)
                self.waypoint_rooms.append(boss_room)
                self.boss_room = boss_room
                self.connect(
                    self.grid_to_room[farthest],
                    boss_dir, boss_room)

                # Staircase goes one step beyond boss room
                stair_grid = None
                stair_dir  = None
                for direction, (dx, dy) in offsets.items():
                    candidate = (boss_grid[0]+dx, boss_grid[1]+dy)
                    if candidate not in self.grid_to_room:
                        stair_grid = candidate
                        stair_dir  = direction
                        break

                if stair_grid:
                    stair_room = WaypointRoom(0, 0, STAIRCASE)
                    self.place_room(stair_room, *stair_grid)
                    self.waypoint_rooms.append(stair_room)
                    self.connect(boss_room, stair_dir, stair_room)
                else:
                    # No space — attach staircase to boss room anyway
                    stair_room = WaypointRoom(0, 0, STAIRCASE)
                    alt_dir = list(offsets.keys())[0]
                    alt_grid = (boss_grid[0]+offsets[alt_dir][0],
                                boss_grid[1]+offsets[alt_dir][1])
                    self.place_room(stair_room, *alt_grid)
                    self.waypoint_rooms.append(stair_room)
                    self.connect(boss_room, alt_dir, stair_room)
            else:
                # No space for boss — fall back to staircase only
                self._place_staircase_at(farthest, offsets)
        else:
            self._place_staircase_at(farthest, offsets)

        # Place other waypoints
        scheduler      = get_scheduler()
        waypoint_types = scheduler.get_waypoints_for_floor(
                             self.floor_number)
        non_special    = [w for w in waypoint_types
                          if w not in (STAIRCASE, BOSS)]

        wp_positions = [
            (2,0),(-2,0),(0,2),(0,-2),
            (3,0),(-3,0),(0,3),(0,-3)
        ]

        for i, wtype in enumerate(non_special):
            if i >= len(wp_positions):
                break
            gx, gy = wp_positions[i]
            if (gx, gy) in self.grid_to_room:
                found = False
                for d, (ddx, ddy) in offsets.items():
                    alt = (gx+ddx, gy+ddy)
                    if alt not in self.grid_to_room:
                        gx, gy = alt
                        found  = True
                        break
                if not found:
                    continue
            wroom = WaypointRoom(0, 0, wtype)
            self.place_room(wroom, gx, gy)
            self.waypoint_rooms.append(wroom)
            for direction, (ddx, ddy) in offsets.items():
                ngrid = (gx-ddx, gy-ddy)
                if ngrid in self.grid_to_room:
                    self.connect(
                        self.grid_to_room[ngrid],
                        direction, wroom)
                    break

        self.current_room_index = 0

    def _place_staircase_at(self, farthest, offsets):
        """Place staircase one step beyond farthest room."""
        opposite = {"north":"south","south":"north",
                    "east":"west",  "west":"east"}
        stair_grid = None
        stair_dir  = None
        for direction, (dx, dy) in offsets.items():
            candidate = (farthest[0]+dx, farthest[1]+dy)
            if candidate not in self.grid_to_room:
                stair_grid = candidate
                stair_dir  = direction
                break

        stair_room = WaypointRoom(0, 0, STAIRCASE)
        if stair_grid:
            self.place_room(stair_room, *stair_grid)
            self.connect(
                self.grid_to_room[farthest],
                stair_dir, stair_room)
        else:
            # Convert farthest room to staircase
            existing = self.grid_to_room[farthest]
            idx = self.rooms.index(existing)
            stair_room = WaypointRoom(
                existing.x, existing.y, STAIRCASE)
            stair_room.doors   = existing.doors.copy()
            stair_room.tiles   = existing.tiles
            stair_room.surface = None
            self.rooms[idx]                  = stair_room
            self.room_grid[id(stair_room)]   = farthest
            self.grid_to_room[farthest]      = stair_room
            self.connections[id(stair_room)] = \
                self.connections.pop(id(existing))
            for room in self.rooms:
                for d, nb in self.connections.get(
                        id(room), {}).items():
                    if nb is existing:
                        self.connections[id(room)][d] = stair_room

        self.waypoint_rooms.append(stair_room)

    # ── door transition helpers ───────────────────────────────────────
    def get_door_rect(self, room, direction):
        cp      = 3 * TILE_SIZE
        mid_col = room.width  // 2
        mid_row = room.height // 2
        if direction == "north":
            return pygame.Rect(
                room.x + (mid_col-1) * TILE_SIZE,
                room.y, cp, TILE_SIZE)
        if direction == "south":
            return pygame.Rect(
                room.x + (mid_col-1) * TILE_SIZE,
                room.y + room.get_pixel_height() - TILE_SIZE,
                cp, TILE_SIZE)
        if direction == "west":
            return pygame.Rect(
                room.x,
                room.y + (mid_row-1) * TILE_SIZE,
                TILE_SIZE, cp)
        if direction == "east":
            return pygame.Rect(
                room.x + room.get_pixel_width() - TILE_SIZE,
                room.y + (mid_row-1) * TILE_SIZE,
                TILE_SIZE, cp)

    def get_spawn_point(self, room, entry_direction):
        mid_col = room.width  // 2
        mid_row = room.height // 2
        pad     = TILE_SIZE * 2
        if entry_direction == "south":
            return (room.x + mid_col * TILE_SIZE,
                    room.y + room.get_pixel_height() - pad)
        if entry_direction == "north":
            return (room.x + mid_col * TILE_SIZE,
                    room.y + pad)
        if entry_direction == "east":
            return (room.x + room.get_pixel_width() - pad,
                    room.y + mid_row * TILE_SIZE)
        if entry_direction == "west":
            return (room.x + pad,
                    room.y + mid_row * TILE_SIZE)

    def check_door_transition(self, player):
        current_room     = self.get_current_room()
        room_connections = self.connections.get(id(current_room), {})
        opp = {"north":"south","south":"north",
               "east":"west",  "west":"east"}
        for direction, neighbor in room_connections.items():
            # Block entry to staircase from boss room if boss not defeated
            if (isinstance(neighbor, WaypointRoom) and
                    neighbor.waypoint_type == STAIRCASE and
                    self.boss_room is not None and
                    not self.boss_room.boss_defeated):
                continue
            door_rect = self.get_door_rect(current_room, direction)
            if door_rect and player.rect.colliderect(door_rect):
                return neighbor, opp[direction]
        return None, None

    # ── runtime ───────────────────────────────────────────────────────
    def get_current_room(self):
        return self.rooms[self.current_room_index]

    def get_nearby_corridors(self, player):
        return []

    def discover_room(self, idx):
        self.discovered_rooms.add(idx)

    def set_current_room(self, room):
        for i, r in enumerate(self.rooms):
            if r is room:
                self.current_room_index = i
                self.discover_room(i)
                return

    def check_waypoints(self, player):
        for wroom in self.waypoint_rooms:
            if wroom.check_player_interaction(player):
                if wroom.waypoint_type == STAIRCASE:
                    self.staircase_reached = True
                wroom.activated = True
                return wroom
        return None

    # ── draw ─────────────────────────────────────────────────────────
    def draw(self, screen, camera):
        current_room = self.get_current_room()
        current_room.draw(screen, camera)
        if isinstance(current_room, WaypointRoom):
            current_room.draw_label(screen, camera)

    def draw_minimap(self, screen, player):
        mm_size = 160
        mm_x    = screen.get_width()  - mm_size - 20
        mm_y    = screen.get_height() - mm_size - 20
        cell    = 10

        pygame.draw.rect(screen, (20,20,20),
            (mm_x-5, mm_y-5, mm_size+10, mm_size+10))

        cur_grid   = self.room_grid.get(
                         id(self.get_current_room()), (0,0))
        cx_g, cy_g = cur_grid

        for i, room in enumerate(self.rooms):
            if i not in self.discovered_rooms:
                continue
            gp = self.room_grid.get(id(room))
            if gp is None:
                continue
            rx, ry = gp
            mx = mm_x + mm_size//2 + (rx-cx_g)*cell*3
            my = mm_y + mm_size//2 + (ry-cy_g)*cell*3
            if not (mm_x <= mx <= mm_x+mm_size and
                    mm_y <= my <= mm_y+mm_size):
                continue
            if isinstance(room, WaypointRoom):
                color = room.color
            elif i == self.current_room_index:
                color = (0,200,255)
            else:
                color = (150,150,150)
            pygame.draw.rect(screen, color, (mx,my,cell,cell))

        pygame.draw.circle(screen, (255,255,255),
            (mm_x+mm_size//2, mm_y+mm_size//2), 3)
        pygame.draw.rect(screen, (255,255,255),
            (mm_x-5, mm_y-5, mm_size+10, mm_size+10), 2)