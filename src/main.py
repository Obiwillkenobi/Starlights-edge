import pygame
import sys
import random
from player import Player
from camera import Camera
from enemy import Enemy
from floor import Floor, reset_scheduler
from collision import get_wall_rects, get_all_walls
from waypoints import (STAIRCASE, RESCUE, LIBRARY,
    ARMORY, DOJO, STORE, KITCHEN, KENNELS)

# --- CONSTANTS ---
SCREEN_WIDTH  = 960
SCREEN_HEIGHT = 540
FPS           = 60
TITLE         = "Starlight's Edge"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (200, 50, 50)
GOLD  = (255, 215, 0)

WAYPOINT_MESSAGES = {
    STAIRCASE: "Press E to go to the next floor!",
    LIBRARY:   "The Magic Library! Spells await...",
    ARMORY:    "The Armory! Weapons and upgrades...",
    DOJO:      "The Dojo! Train your combat skills...",
    STORE:     "The Store! Browse the wares...",
    KITCHEN:   "The Kitchen! Something smells good...",
    KENNELS:   "The Kennels! What lurks within...",
    RESCUE:    "A family member is here!"
}

def spawn_enemies(floor):
    from waypoints import WaypointRoom
    for i, room in enumerate(floor.rooms):
        if i == 0 or isinstance(room, WaypointRoom):
            continue
        cx, cy = room.get_center()
        for _ in range(3):
            ex = cx + random.randint(-80, 80)
            ey = cy + random.randint(-80, 80)
            room.enemies.append(Enemy(ex, ey, room=room))

def do_fade(screen, clock, fade_in=True):
    """Quick 20-frame fade to/from black."""
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    floor_number = 1
    reset_scheduler()
    floor      = Floor(floor_number=floor_number)
    start_room = floor.get_current_room()
    sx, sy     = start_room.get_center()
    player     = Player(sx, sy)
    camera     = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    camera.update(player)
    spawn_enemies(floor)

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
                if event.key == pygame.K_r and not player.alive:
                    floor_number = 1
                    reset_scheduler()
                    floor      = Floor(floor_number=floor_number)
                    start_room = floor.get_current_room()
                    sx, sy     = start_room.get_center()
                    player     = Player(sx, sy)
                    camera.update(player)
                    spawn_enemies(floor)
                    notification       = ""
                    last_waypoint_type = None

                if event.key == pygame.K_e and floor.staircase_reached:
                    if floor_number < 12:
                        floor_number += 1
                        floor      = Floor(floor_number=floor_number)
                        start_room = floor.get_current_room()
                        sx, sy     = start_room.get_center()
                        player.rect.center = (sx, sy)
                        player.walls = []
                        camera.update(player)
                        spawn_enemies(floor)
                        notification       = f"Floor {floor_number}!"
                        notification_timer = 180
                        last_waypoint_type = None
                    else:
                        notification       = "You have reached the top floor!"
                        notification_timer = 180

        # 2. UPDATE
        if player.alive and not transitioning:
            player.handle_input()
            player.update()
            camera.update(player)

            current_room = floor.get_current_room()
            walls        = get_all_walls(current_room)
            player.walls = walls

            # Enemy updates
            for enemy in current_room.enemies:
                enemy.walls = walls
                enemy.update(player, player_in_room=True)
                enemy.check_hits(player)
            current_room.enemies = [
                e for e in current_room.enemies if e.active]

            # Door transition check
            neighbor, entry_dir = floor.check_door_transition(player)
            if neighbor is not None:
                transitioning = True

                # Fade out
                do_fade(screen, clock, fade_in=False)

                # Move player to new room
                floor.set_current_room(neighbor)
                sx, sy = floor.get_spawn_point(neighbor, entry_dir)
                player.rect.center = (sx, sy)
                player.walls = get_all_walls(neighbor)
                camera.update(player)

                # Fade in
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

        # 3. DRAW
        screen.fill(BLACK)
        floor.draw(screen, camera)

        current_room = floor.get_current_room()
        for enemy in current_room.enemies:
            enemy.draw(screen, camera)

        player.draw(screen, camera)
        player.draw_hud(screen)
        floor.draw_minimap(screen, player)

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
            f"Floor: {floor.floor_number}  |  "
            f"Rooms: {len(floor.rooms)}", True, WHITE),
            (10, SCREEN_HEIGHT - 30))
        screen.blit(font.render(
            "WASD: Move  |  J: Sword  |  K: Projectile"
            "  |  E: Interact  |  R: Restart",
            True, (180, 180, 180)),
            (10, SCREEN_HEIGHT - 55))

        if not player.alive:
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            game_over = big_font.render("YOU DIED", True, RED)
            restart   = font.render("Press R to restart", True, WHITE)
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