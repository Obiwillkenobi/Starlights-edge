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

    # Spawn a few test enemies near the player
    enemies = [
        Enemy(1600, 1500),
        Enemy(1400, 1450),
        Enemy(1550, 1600),
    ]

    # --- MAIN LOOP ---
    running = True
    while running:

        # 1. CHECK FOR INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. UPDATE GAME STATE
        player.handle_input()
        player.update()
        camera.update(player)

        # Update enemies
        for enemy in enemies:
            enemy.check_hits(player)

        # Remove dead enemies
        enemies = [e for e in enemies if e.active]

        # 3. DRAW EVERYTHING
        screen.fill(BLACK)
        draw_grid(screen, camera)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, camera)

        # Draw player on top
        player.draw(screen, camera)

        # Display controls hint
        font = pygame.font.SysFont(None, 28)
        hint = font.render(
            "WASD: Move  |  J: Sword  |  K: Projectile",
            True, (180, 180, 180)
        )
        screen.blit(hint, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()