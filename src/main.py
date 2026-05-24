import pygame
import sys
import random
from player import Player
from camera import Camera
from enemy import Enemy
from floor import Floor

# --- CONSTANTS ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Starlight's Edge"

# --- COLORS ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)

def get_current_room(floor, player):
    # Find which room the player is currently in
    for i, room in enumerate(floor.rooms):
        room_rect = pygame.Rect(
            room.x, room.y,
            room.get_pixel_width(),
            room.get_pixel_height()
        )
        if room_rect.collidepoint(player.rect.centerx, player.rect.centery):
            floor.current_room_index = i
            return room
    return floor.get_current_room()

def spawn_enemies(floor):
    for i, room in enumerate(floor.rooms):
        if i == 0:
            continue
        cx, cy = room.get_center()
        for _ in range(3):
            ex = cx + random.randint(-100, 100)
            ey = cy + random.randint(-100, 100)
            room.enemies.append(Enemy(ex, ey))

def main():
    # Initialize Pygame
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Generate the first floor
    floor = Floor(floor_number=1)
    start_room = floor.get_current_room()
    start_x, start_y = start_room.get_center()
    player = Player(start_x, start_y)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    spawn_enemies(floor)

    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 72)

    # --- MAIN LOOP ---
    running = True
    while running:

        # 1. CHECK FOR INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not player.alive:
                    floor = Floor(floor_number=1)
                    start_room = floor.get_current_room()
                    start_x, start_y = start_room.get_center()
                    player = Player(start_x, start_y)
                    spawn_enemies(floor)

        # 2. UPDATE GAME STATE
        if player.alive:
            player.handle_input()
            player.update()
            camera.update(player)

            # Only update enemies in the current room
            current_room = get_current_room(floor, player)
            for enemy in current_room.enemies:
                enemy.update(player)
                enemy.check_hits(player)
            current_room.enemies = [
                e for e in current_room.enemies if e.active
            ]

        # 3. DRAW EVERYTHING
        screen.fill(BLACK)
        floor.draw(screen, camera)

        # Only draw enemies in nearby rooms
        for room in floor.rooms:
            room_rect = pygame.Rect(
                room.x, room.y,
                room.get_pixel_width(),
                room.get_pixel_height()
            )
            visible_rect = pygame.Rect(
                camera.offset_x - 200,
                camera.offset_y - 200,
                1360, 940
            )
            if room_rect.colliderect(visible_rect):
                for enemy in room.enemies:
                    enemy.draw(screen, camera)

        player.draw(screen, camera)
        player.draw_hud(screen)
        floor.draw_minimap(screen)

        # FPS counter
        fps = int(clock.get_fps())
        fps_color = (50, 200, 50) if fps >= 50 else (200, 50, 50)
        fps_text = font.render(f"FPS: {fps}", True, fps_color)
        screen.blit(fps_text, (SCREEN_WIDTH - 80, 20))

        # Floor indicator
        floor_text = font.render(
            f"Floor: {floor.floor_number}  |  Rooms: {len(floor.rooms)}",
            True, WHITE
        )
        screen.blit(floor_text, (10, SCREEN_HEIGHT - 30))

        # Controls hint
        hint = font.render(
            "WASD: Move  |  J: Sword  |  K: Projectile  |  R: Restart",
            True, (180, 180, 180)
        )
        screen.blit(hint, (10, SCREEN_HEIGHT - 55))

        # Game over screen
        if not player.alive:
            overlay = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            game_over = big_font.render("YOU DIED", True, RED)
            restart = font.render("Press R to restart", True, WHITE)
            screen.blit(game_over,
                (SCREEN_WIDTH // 2 - game_over.get_width() // 2,
                SCREEN_HEIGHT // 2 - 60))
            screen.blit(restart,
                (SCREEN_WIDTH // 2 - restart.get_width() // 2,
                SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()