import pygame
import sys
from player import Player
from camera import Camera

# --- CONSTANTS ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Starlight's Edge"

# --- COLORS ---
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
GRID_COLOR = (50, 50, 50)

def draw_grid(screen, camera):
    # Draws a grid so we can SEE the camera moving
    grid_size = 64
    for x in range(0, 3000, grid_size):
        for y in range(0, 3000, grid_size):
            rect = pygame.Rect(x, y, grid_size, grid_size)
            draw_rect = camera.apply(rect)
            pygame.draw.rect(screen, GRID_COLOR, draw_rect, 1)

def main():
    # Initialize Pygame
    pygame.init()

    # Create the window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Create the clock
    clock = pygame.time.Clock()

    # Create the player (starting in the center of the world)
    player = Player(1500, 1500)

    # Create the camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # --- MAIN LOOP ---
    running = True
    while running:

        # 1. CHECK FOR INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. UPDATE GAME STATE
        player.handle_input()
        camera.update(player)

        # 3. DRAW EVERYTHING
        screen.fill(BLACK)
        draw_grid(screen, camera)

        # Draw player through the camera
        player_draw_rect = camera.apply(player.rect)
        pygame.draw.rect(screen, (0, 200, 255), player_draw_rect)

        # Flip the display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()