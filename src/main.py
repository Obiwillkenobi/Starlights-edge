import pygame
import sys
from player import Player

# --- CONSTANTS ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Starlight's Edge"

# --- COLORS ---
BLACK = (0, 0, 0)

def main():
    # Initialize Pygame
    pygame.init()

    # Create the window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Create the clock (controls game speed)
    clock = pygame.time.Clock()

    # Create the player (starting in the center of the screen)
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # --- MAIN LOOP ---
    running = True
    while running:

        # 1. CHECK FOR INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. UPDATE GAME STATE
        player.handle_input()

        # 3. DRAW EVERYTHING
        screen.fill(BLACK)
        player.draw(screen)

        # Flip the display
        pygame.display.flip()

        # Hold at 60 frames per second
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()