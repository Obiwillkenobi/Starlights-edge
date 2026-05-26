import pygame
import sys
import random
from player import Player
from camera import Camera
from enemy import Enemy
from floor import Floor, reset_scheduler
from floor_manager import FloorManager
from collision import get_wall_rects, get_all_walls
from graveyard import Graveyard
from laphero import Laphero
from reward import RewardPopup
from waypoints import (STAIRCASE, RESCUE, LIBRARY,
    ARMORY, DOJO, STORE, KITCHEN, KENNELS, BOSS,
    TEMPLE_ORAKNOS, TEMPLE_THANGAR, TEMPLE_JERRY,
    TEMPLE_SQUIRREL, TEMPLE_TYPES, TEMPLE_GOD_MAP)
from stats import GODS

# --- CONSTANTS ---
SCREEN_WIDTH  = 960
SCREEN_HEIGHT = 540
FPS           = 60
TITLE         = "Starlight's Edge"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (200, 50, 50)
GOLD  = (255, 215, 0)
GREEN = (50, 200, 50)

# --- GAME STATES ---
STATE_LAPHERO   = "laphero"
STATE_GRAVEYARD = "graveyard"
STATE_CASTLE    = "castle"

WAYPOINT_MESSAGES = {
    STAIRCASE:       "Press E to go to the next floor!",
    LIBRARY:         "The Magic Library! Spells await...",
    ARMORY:          "The Armory! Weapons and upgrades...",
    DOJO:            "The Dojo! Train your combat skills...",
    STORE:           "The Store! Browse the wares...",
    KITCHEN:         "The Kitchen! Something smells good...",
    KENNELS:         "The Kennels! What lurks within...",
    RESCUE:          "A family member is here! Press E to rescue.",
    BOSS:            "A powerful enemy blocks the staircase!",
    TEMPLE_ORAKNOS:  "Temple of Oraknos - Press E to pray and heal.",
    TEMPLE_THANGAR:  "Temple of Thangar - Press E to pray and heal.",
    TEMPLE_JERRY:    "Temple of Jerry - Press E to pray and heal.",
    TEMPLE_SQUIRREL: "Temple of A Squirrel - Press E to pray and heal.",
}

def spawn_enemies(floor, fm):
    from waypoints import WaypointRoom
    count  = fm.get_enemy_count()
    h_mult = fm.get_health_multiplier()
    s_mult = fm.get_speed_multiplier()
    for i, room in enumerate(floor.rooms):
        if i == 0 or isinstance(room, WaypointRoom):
            continue
        cx, cy = room.get_center()
        for _ in range(count):
            ex = cx + random.randint(-80, 80)
            ey = cy + random.randint(-80, 80)
            room.enemies.append(
                Enemy(ex, ey, room=room,
                      health_mult=h_mult,
                      speed_mult=s_mult))

def do_fade(screen, clock, fade_in=True, color=BLACK):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(color)
    steps = 20
    for i in range(steps):
        alpha = int(255 * (i / steps))
        if fade_in:
            alpha = 255 - alpha
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

def draw_hud_extras(screen, font, fm):
    mm_x = SCREEN_WIDTH  - 160 - 20
    mm_y = SCREEN_HEIGHT - 160 - 20
    floor_txt = font.render(
        f"Floor: {fm.current_floor} / 12", True, WHITE)
    screen.blit(floor_txt, (
        mm_x + 80 - floor_txt.get_width() // 2,
        mm_y - 28))
    family_status = [
        ("Son",      fm.family[3]["rescued"]),
        ("Daughter", fm.family[6]["rescued"]),
        ("Wife",     fm.family[9]["rescued"]),
    ]
    for i, (name, is_rescued) in enumerate(family_status):
        color = GREEN if is_rescued else (120, 120, 120)
        icon  = "v" if is_rescued else "x"
        screen.blit(font.render(f"{icon} {name}", True, color),
            (20, 50 + i * 22))

def draw_graveyard_hud(screen, font, graveyard):
    screen.blit(font.render(
        f"Enemies remaining: {len(graveyard.enemies)}",
        True, WHITE), (20, SCREEN_HEIGHT - 80))
    if graveyard.is_cleared():
        screen.blit(font.render(
            "All enemies defeated! Head to the north gate!",
            True, GOLD), (20, SCREEN_HEIGHT - 55))
    else:
        screen.blit(font.render(
            "Defeat all enemies to open the gate!",
            True, (180, 180, 180)), (20, SCREEN_HEIGHT - 55))

def draw_laphero_hud(screen, font, town):
    if not town.gate_open:
        screen.blit(font.render(
            "Defeat the guards to open the gate!",
            True, (180, 180, 180)),
            (20, SCREEN_HEIGHT - 55))
    else:
        screen.blit(font.render(
            "The gate is open! Head north to the graveyard.",
            True, GOLD),
            (20, SCREEN_HEIGHT - 55))
    screen.blit(font.render(
        "E: Talk to NPCs",
        True, (180, 180, 180)),
        (20, SCREEN_HEIGHT - 30))

def draw_worship_status(screen, font, player):
    god = player.stats.worshipped_god
    if god:
        god_data = GODS.get(god, {})
        color    = god_data.get("color", WHITE)
        name     = god_data.get("name", god)
        screen.blit(font.render(
            f"Worships: {name}", True, color),
            (20, 310))

def handle_temple_interaction(player, waypoint_type):
    god_key  = TEMPLE_GOD_MAP.get(waypoint_type)
    god_data = GODS.get(god_key, {})
    god_name = god_data.get("name", "the deity")
    player.full_heal()
    old_god = player.stats.worshipped_god
    player.stats.worshipped_god = god_key
    player.stats.determine_class(None, None, god_key)
    player.refresh_max_health()
    if old_god == god_key:
        return f"You pray to {god_name}. You feel restored!"
    elif old_god:
        old_name = GODS.get(old_god, {}).get("name", old_god)
        return (f"You abandon {old_name} and "
                f"pledge yourself to {god_name}. Healed!")
    else:
        return (f"You pledge yourself to {god_name} "
                f"and are healed!")

def apply_death_penalties(player, survived_items):
    """Apply gold and inventory penalties on death."""
    player.stats.gold = int(player.stats.gold * 0.25)
    # 99% chance to lose all items
    if random.random() < 0.99:
        player.stats.item_bonus = {k: 0 for k in
                                   player.stats.item_bonus}
        player.refresh_max_health()
        return False  # Lost items
    return True  # Kept items

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    fm     = FloorManager()
    reward = RewardPopup(SCREEN_WIDTH, SCREEN_HEIGHT)
    rewarded_rooms = set()

    def new_game(kept_items=False):
        fm.reset()
        reset_scheduler()
        rewarded_rooms.clear()

        # Calculate guard power based on player stats
        power_mult = 1.0 + (
            sum(player.stats.base.values()) - 5) * 0.1 \
            if 'player' in dir() else 1.0

        town   = Laphero(power_mult=power_mult)
        sx, sy = town.player_start
        pl     = Player(sx, sy)
        cam    = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        cam.update(pl)

        return town, None, None, pl, cam, STATE_LAPHERO

    def enter_graveyard(player, camera):
        gyard  = Graveyard()
        ex, ey = gyard.entry_pos
        player.rect.center = (ex, ey)
        player.walls = []
        camera.update(player)
        gyard.spawn_enemies(fm)
        return gyard

    def enter_castle(player, camera):
        reset_scheduler()
        rewarded_rooms.clear()
        floor      = Floor(floor_number=fm.current_floor)
        start_room = floor.get_current_room()
        sx, sy     = start_room.get_center()
        player.rect.center = (sx, sy)
        player.walls = []
        camera.update(player)
        spawn_enemies(floor, fm)
        return floor

    def next_floor(player, camera):
        if not fm.advance_floor():
            return None
        rewarded_rooms.clear()
        floor      = Floor(floor_number=fm.current_floor)
        start_room = floor.get_current_room()
        sx, sy     = start_room.get_center()
        player.rect.center = (sx, sy)
        player.walls = []
        camera.update(player)
        spawn_enemies(floor, fm)
        return floor

    # Initial game start
    player = Player(0, 0)   # Temp player for power calc
    town, graveyard, floor, player, camera, game_state = \
        new_game()

    font     = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 72)
    med_font = pygame.font.SysFont(None, 42)

    notification       = ""
    notification_timer = 0
    last_waypoint_type = None
    transitioning      = False

    running = True
    while running:

        # 1. INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Reward popup gets first dibs on events
            if reward.active:
                reward.handle_event(event)
                if reward.confirmed:
                    reward.apply_to_player(player)
                    player.stats.add_gold(reward.gold_reward)
                    notification = (
                        f"Gained {reward.gold_reward} gold and "
                        f"{reward.selected_card['name']}!")
                    notification_timer = 240
                continue

            if event.type == pygame.KEYDOWN:

                # Restart on death — back to Laphero
                if event.key == pygame.K_r and not player.alive:
                    kept = apply_death_penalties(player, [])
                    town, graveyard, floor, player, camera, \
                        game_state = new_game()
                    if kept:
                        notification = (
                            "Your friend: The revival ritual "
                            "must have brought your belongings back!")
                        notification_timer = 300
                    notification       = ""
                    last_waypoint_type = None

                if event.key == pygame.K_l and player.alive:
                    player.toggle_stealth()

                # Laphero interactions
                if game_state == STATE_LAPHERO:
                    if event.key == pygame.K_e:
                        msg = town.try_interact(player)
                        if msg:
                            town.show_dialogue(msg, 240)

                # Castle interactions
                if game_state == STATE_CASTLE and floor:
                    if event.key == pygame.K_e:
                        current_room = floor.get_current_room()
                        from waypoints import WaypointRoom

                        if (floor.staircase_reached and
                                isinstance(current_room, WaypointRoom)
                                and current_room.waypoint_type
                                == STAIRCASE):
                            do_fade(screen, clock, fade_in=False)
                            new_fl = next_floor(player, camera)
                            if new_fl is None:
                                notification       = \
                                    "You have reached the top floor!"
                                notification_timer = 180
                            else:
                                floor              = new_fl
                                notification       = \
                                    f"Floor {fm.current_floor}!"
                                notification_timer = 180
                                last_waypoint_type = None
                            do_fade(screen, clock, fade_in=True)

                        elif (isinstance(current_room, WaypointRoom)
                                and current_room.waypoint_type
                                == RESCUE):
                            name = fm.try_rescue(fm.current_floor)
                            if name:
                                notification       = \
                                    f"You rescued your {name}!"
                                notification_timer = 300

                        elif (isinstance(current_room, WaypointRoom)
                                and current_room.waypoint_type
                                in TEMPLE_TYPES):
                            msg = handle_temple_interaction(
                                player,
                                current_room.waypoint_type)
                            notification       = msg
                            notification_timer = 300

        # 2. UPDATE
        if player.alive and not transitioning and not reward.active:

            # ── LAPHERO ──
            if game_state == STATE_LAPHERO:
                player.handle_input()
                player.update()
                camera.update(player)
                town.update(player)

                if town.completed:
                    do_fade(screen, clock, fade_in=False)
                    graveyard  = enter_graveyard(player, camera)
                    game_state = STATE_GRAVEYARD
                    notification       = \
                        "You enter the haunted graveyard..."
                    notification_timer = 240
                    do_fade(screen, clock, fade_in=True)

            # ── GRAVEYARD ──
            elif game_state == STATE_GRAVEYARD:
                player.handle_input()
                player.update()
                camera.update(player)
                graveyard.update(player)

                if graveyard.completed:
                    do_fade(screen, clock, fade_in=False)
                    floor      = enter_castle(player, camera)
                    game_state = STATE_CASTLE
                    notification       = \
                        "You enter the Starlight Castle..."
                    notification_timer = 240
                    do_fade(screen, clock, fade_in=True)

            # ── CASTLE ──
            elif game_state == STATE_CASTLE and floor:
                player.handle_input()
                player.update()
                camera.update(player)

                current_room = floor.get_current_room()
                walls        = get_all_walls(current_room)
                player.walls = walls

                had_enemies = len(current_room.enemies) > 0

                for enemy in current_room.enemies:
                    enemy.walls = walls
                    enemy.update(player, player_in_room=True)
                    enemy.check_hits(player)
                current_room.enemies = [
                    e for e in current_room.enemies if e.active]

                # Room reward check
                from waypoints import WaypointRoom
                room_id = id(current_room)
                if (had_enemies and
                        len(current_room.enemies) == 0 and
                        room_id not in rewarded_rooms and
                        not isinstance(current_room, WaypointRoom)):
                    rewarded_rooms.add(room_id)
                    reward.show()

                neighbor, entry_dir = \
                    floor.check_door_transition(player)
                if neighbor is not None:
                    transitioning = True
                    do_fade(screen, clock, fade_in=False)
                    floor.set_current_room(neighbor)
                    sx, sy = floor.get_spawn_point(
                        neighbor, entry_dir)
                    player.rect.center = (sx, sy)
                    player.walls = get_all_walls(neighbor)
                    camera.update(player)
                    do_fade(screen, clock, fade_in=True)
                    transitioning = False

                active_waypoint = floor.check_waypoints(player)
                if active_waypoint:
                    wtype = active_waypoint.waypoint_type
                    if wtype != last_waypoint_type:
                        notification       = \
                            WAYPOINT_MESSAGES.get(wtype, "")
                        notification_timer = 300
                        last_waypoint_type = wtype
                else:
                    last_waypoint_type = None

                if notification_timer > 0:
                    notification_timer -= 1
                else:
                    notification = ""

        # 3. DRAW
        screen.fill(BLACK)

        if game_state == STATE_LAPHERO:
            town.draw(screen, camera)
            player.draw(screen, camera)
            player.draw_stealth_radius(screen, camera)
            player.draw_hud(screen)
            draw_laphero_hud(screen, font, town)

        elif game_state == STATE_GRAVEYARD:
            graveyard.draw(screen, camera)
            player.draw(screen, camera)
            player.draw_stealth_radius(screen, camera)
            player.draw_hud(screen)
            draw_graveyard_hud(screen, font, graveyard)

        elif game_state == STATE_CASTLE and floor:
            floor.draw(screen, camera)
            current_room = floor.get_current_room()
            for enemy in current_room.enemies:
                enemy.draw(screen, camera)
            player.draw(screen, camera)
            player.draw_stealth_radius(screen, camera)
            player.draw_hud(screen)
            floor.draw_minimap(screen, player)
            draw_hud_extras(screen, font, fm)
            draw_worship_status(screen, font, player)

        # Reward popup on top
        reward.draw(screen)

        if notification and not reward.active:
            notif = med_font.render(notification, True, GOLD)
            screen.blit(notif, (
                SCREEN_WIDTH//2 - notif.get_width()//2,
                SCREEN_HEIGHT - 100))

        fps       = int(clock.get_fps())
        fps_color = (50, 200, 50) if fps >= 50 else (200, 50, 50)
        screen.blit(font.render(f"FPS: {fps}", True, fps_color),
            (SCREEN_WIDTH - 80, 20))

        screen.blit(font.render(
            "WASD: Move  |  J: Sword  |  K: Shoot"
            "  |  L: Stealth  |  E: Interact  |  R: Restart",
            True, (180, 180, 180)),
            (10, SCREEN_HEIGHT - 30))

        if not player.alive:
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            game_over = big_font.render("YOU DIED", True, RED)
            restart   = font.render(
                "Press R to return to Laphero", True, WHITE)
            screen.blit(game_over,
                (SCREEN_WIDTH//2 - game_over.get_width()//2,
                 SCREEN_HEIGHT//2 - 60))
            screen.blit(restart,
                (SCREEN_WIDTH//2 - restart.get_width()//2,
                 SCREEN_HEIGHT//2 + 20))
            if game_state == STATE_CASTLE:
                rescued = fm.get_rescued()
                if rescued:
                    resc_txt = font.render(
                        "Rescued: " + ", ".join(rescued),
                        True, GREEN)
                    screen.blit(resc_txt,
                        (SCREEN_WIDTH//2 - resc_txt.get_width()//2,
                         SCREEN_HEIGHT//2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()