import pygame
import sys
from player import Player
from camera import Camera
from enemy import Enemy

# --- CONSTANTS ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Starlight's Edge"

# --- COLORS ---
BLACK = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (200, 50, 50)

def draw_grid(screen, camera):
    grid_size = 64
    for x in range(0, 3000, grid_size):
        for y in range(0, 3000, grid_size):
            rect = pygame.Rect(x, y, grid_size, grid_size)
            draw_rect = camera.apply(rect)
            pygame.draw.rect(screen, GRID_COLOR, draw_rect, 1)

def main():
    # Initialize Pygame
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Create player and camera
    player = Player(1500, 1500)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Spawn test enemies
    enemies = [
        Enemy(1700, 1500),
        Enemy(1400, 1450),
        Enemy(1550, 1700),
        Enemy(1800, 1600),
        Enemy(1300, 1600),
    ]

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
                    # Restart the game
                    player = Player(1500, 1500)
                    enemies = [
                        Enemy(1700, 1500),
                        Enemy(1400, 1450),
                        Enemy(1550, 1700),
                        Enemy(1800, 1600),
                        Enemy(1300, 1600),
                    ]

        # 2. UPDATE GAME STATE
        if player.alive:
            player.handle_input()
            player.update()
            camera.update(player)

            for enemy in enemies:
                enemy.update(player)
                enemy.check_hits(player)

            enemies = [e for e in enemies if e.active]

        # 3. DRAW EVERYTHING
        screen.fill(BLACK)
        draw_grid(screen, camera)

        for enemy in enemies:
            enemy.draw(screen, camera)

        player.draw(screen, camera)
        player.draw_hud(screen)

        # Controls hint
        hint = font.render(
            "WASD: Move  |  J: Sword  |  K: Projectile  |  R: Restart",
            True, (180, 180, 180)
        )
        screen.blit(hint, (10, SCREEN_HEIGHT - 30))

        # Enemy counter
        counter = font.render(
            f"Enemies remaining: {len(enemies)}",
            True, (255, 255, 255)
        )
        screen.blit(counter, (SCREEN_WIDTH - 220, 20))

        # Game over screen
        if not player.alive:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            game_over = big_font.render("YOU DIED", True, RED)
            restart = font.render("Press R to restart", True, WHITE)
            screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2,
                SCREEN_HEIGHT // 2 - 60))
            screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2,
                SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()