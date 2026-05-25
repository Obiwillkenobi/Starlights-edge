import pygame
import sys
import random
from player import Player
from camera import Camera
from enemy import Enemy
from floor import Floor, reset_scheduler
from floor_manager import FloorManager
from collision import get_wall_rects, get_all_walls
from waypoints import (STAIRCASE, RESCUE, LIBRARY,
    ARMORY, DOJO, STORE, KITCHEN, KENNELS, BOSS)

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

WAYPOINT_MESSAGES = {
    STAIRCASE: "Press E to go to the next floor!",
    LIBRARY:   "The Magic Library! Spells await...",
    ARMORY:    "The Armory! Weapons and upgrades...",
    DOJO:      "The Dojo! Train your combat skills...",
    STORE:     "The Store! Browse the wares...",
    KITCHEN:   "The Kitchen! Something smells good...",
    KENNELS:   "The Kennels! What lurks within...",
    RESCUE:    "A family member is here! Press E to rescue them.",
    BOSS:      "A powerful enemy blocks the way to the staircase!"
}

def spawn_enemies(floor, fm):
    from waypoints import WaypointRoom
    count   = fm.get_enemy_count()
    h_mult  = fm.get_health_multiplier()
    s_mult  = fm.get_speed_multiplier()

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

def do_fade(screen, clock, fade_in=True):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
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
    """Draw floor number and rescued family members."""
    # Floor indicator top left under health bar
    screen.blit(font.render(
        f"Floor: {fm.current_floor} / 12",
        True, WHITE), (20, 50))

    # Rescued family members stacked below floor indicator
    rescued = fm.get_rescued()
    family_status = [
        ("Son",      fm.family[3]["rescued"]),
        ("Daughter", fm.family[6]["rescued"]),
        ("Wife",     fm.family[9]["rescued"]),
    ]
    for i, (name, is_rescued) in enumerate(family_status):
        color = GREEN if is_rescued else (120, 120, 120)
        icon  = "✓" if is_rescued else "✗"
        screen.blit(font.render(f"{icon} {name}", True, color),
            (20, 75 + i * 22))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    fm = FloorManager()

    def new_game():
        fm.reset()
        reset_scheduler()
        floor      = Floor(floor_number=fm.current_floor)
        start_room = floor.get_current_room()
        sx, sy     = start_room.get_center()
        pl         = Player(sx, sy)
        cam        = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        cam.update(pl)
        spawn_enemies(floor, fm)
        return floor, pl, cam

    def next_floor(player, camera):
        if not fm.advance_floor():
            return None, player, camera
        floor      = Floor(floor_number=fm.current_floor)
        start_room = floor.get_current_room()
        sx, sy     = start_room.get_center()
        player.rect.center = (sx, sy)
        player.walls = []
        camera.update(player)
        spawn_enemies(floor, fm)
        return floor, player, camera

    floor, player, camera = new_game()

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

            if event.type == pygame.KEYDOWN:
                # Restart on death
                if event.key == pygame.K_r and not player.alive:
                    floor, player, camera = new_game()
                    notification       = ""
                    last_waypoint_type = None

                # Advance floor at staircase
                if event.key == pygame.K_e and floor.staircase_reached:
                    do_fade(screen, clock, fade_in=False)
                    floor, player, camera = next_floor(player, camera)
                    if floor is None:
                        notification       = "You have reached the top floor!"
                        notification_timer = 180
                    else:
                        notification       = f"Floor {fm.current_floor}!"
                        notification_timer = 180
                        last_waypoint_type = None
                    do_fade(screen, clock, fade_in=True)

                # Rescue family member
                if event.key == pygame.K_e:
                    current_room = floor.get_current_room()
                    from waypoints import WaypointRoom
                    if (isinstance(current_room, WaypointRoom) and
                            current_room.waypoint_type == RESCUE):
                        name = fm.try_rescue(fm.current_floor)
                        if name:
                            notification       = f"You rescued your {name}!"
                            notification_timer = 300

        # 2. UPDATE
        if player.alive and not transitioning:
            player.handle_input()
            player.update()
            camera.update(player)

            current_room = floor.get_current_room()
            walls        = get_all_walls(current_room)
            player.walls = walls

            for enemy in current_room.enemies:
                enemy.walls = walls
                enemy.update(player, player_in_room=True)
                enemy.check_hits(player)
            current_room.enemies = [
                e for e in current_room.enemies if e.active]

            # Door transition
            neighbor, entry_dir = floor.check_door_transition(player)
            if neighbor is not None:
                transitioning = True
                do_fade(screen, clock, fade_in=False)
                floor.set_current_room(neighbor)
                sx, sy = floor.get_spawn_point(neighbor, entry_dir)
                player.rect.center = (sx, sy)
                player.walls = get_all_walls(neighbor)
                camera.update(player)
                do_fade(screen, clock, fade_in=True)
                transitioning = False

            # Waypoint check
            active_waypoint = floor.check_waypoints(player)
            if active_waypoint:
                wtype = active_waypoint.waypoint_type
                if wtype != last_waypoint_type:
                    notification       = WAYPOINT_MESSAGES.get(wtype, "")
                    notification_timer = 300
                    last_waypoint_type = wtype
            else:
                last_waypoint_type = None

            if notification_timer > 0:
                notification_timer -= 1
            else:
                notification = ""

            # Win condition
            if fm.current_floor == 12 and fm.bb_defeated:
                notification       = "You have defeated the Big Bad!"
                notification_timer = 9999

        # 3. DRAW
        screen.fill(BLACK)
        floor.draw(screen, camera)

        current_room = floor.get_current_room()
        for enemy in current_room.enemies:
            enemy.draw(screen, camera)

        player.draw(screen, camera)
        player.draw_hud(screen)
        floor.draw_minimap(screen, player)
        draw_hud_extras(screen, font, fm)

        if notification:
            notif = med_font.render(notification, True, GOLD)
            screen.blit(notif, (
                SCREEN_WIDTH//2 - notif.get_width()//2,
                SCREEN_HEIGHT - 100))

        fps       = int(clock.get_fps())
        fps_color = (50, 200, 50) if fps >= 50 else (200, 50, 50)
        screen.blit(font.render(f"FPS: {fps}", True, fps_color),
            (SCREEN_WIDTH - 80, 20))

        screen.blit(font.render(
            "WASD: Move  |  J: Sword  |  K: Projectile"
            "  |  E: Interact  |  R: Restart",
            True, (180, 180, 180)),
            (10, SCREEN_HEIGHT - 78))

        if not player.alive:
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            game_over = big_font.render("YOU DIED", True, RED)
            restart   = font.render("Press R to restart", True, WHITE)
            rescued   = fm.get_rescued()
            if rescued:
                resc_txt = font.render(
                    "Rescued: " + ", ".join(rescued),
                    True, GREEN)
                screen.blit(resc_txt,
                    (SCREEN_WIDTH//2 - resc_txt.get_width()//2,
                     SCREEN_HEIGHT//2 + 50))
            screen.blit(game_over,
                (SCREEN_WIDTH//2 - game_over.get_width()//2,
                 SCREEN_HEIGHT//2 - 60))
            screen.blit(restart,
                (SCREEN_WIDTH//2 - restart.get_width()//2,
                 SCREEN_HEIGHT//2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()