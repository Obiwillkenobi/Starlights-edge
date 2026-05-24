import pygame

# --- CONSTANTS ---
ENEMY_SIZE = 32
ENEMY_COLOR = (220, 50, 50)  # Red
ENEMY_MAX_HEALTH = 3

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.health = ENEMY_MAX_HEALTH
        self.active = True

    def check_hits(self, player):
        # Check sword hit
        if player.sword and player.sword.active:
            if self.rect.colliderect(player.sword.rect):
                self.health -= 1
                player.sword.active = False

        # Check projectile hits
        for p in player.projectiles:
            if self.rect.colliderect(p.rect):
                self.health -= 1
                p.active = False

        # Die if out of health
        if self.health <= 0:
            self.active = False

    def draw(self, screen, camera):
        if self.active:
            draw_rect = camera.apply(self.rect)
            pygame.draw.rect(screen, ENEMY_COLOR, draw_rect)

            # Draw health bar above enemy
            bar_width = ENEMY_SIZE
            bar_height = 6
            health_ratio = self.health / ENEMY_MAX_HEALTH
            bar_x = draw_rect.x
            bar_y = draw_rect.y - 10

            # Background bar (gray)
            pygame.draw.rect(screen, (80, 80, 80),
                (bar_x, bar_y, bar_width, bar_height))
            # Health bar (green)
            pygame.draw.rect(screen, (50, 200, 50),
                (bar_x, bar_y, int(bar_width * health_ratio), bar_height))