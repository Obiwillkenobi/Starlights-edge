import pygame

# --- CONSTANTS ---
SWORD_COLOR = (255, 220, 50)    # Yellow
PROJECTILE_COLOR = (255, 100, 0) # Orange
PROJECTILE_SPEED = 8
PROJECTILE_SIZE = 8
SWORD_DURATION = 10  # Frames the sword stays active

class SwordAttack:
    def __init__(self, player_rect, direction):
        self.duration = SWORD_DURATION
        self.active = True

        # Place the sword hitbox in front of the player
        offset = 40
        if direction == "up":
            self.rect = pygame.Rect(
                player_rect.centerx - 16,
                player_rect.top - offset,
                32, 32)
        elif direction == "down":
            self.rect = pygame.Rect(
                player_rect.centerx - 16,
                player_rect.bottom + offset - 32,
                32, 32)
        elif direction == "left":
            self.rect = pygame.Rect(
                player_rect.left - offset,
                player_rect.centery - 16,
                32, 32)
        elif direction == "right":
            self.rect = pygame.Rect(
                player_rect.right + offset - 32,
                player_rect.centery - 16,
                32, 32)

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.active = False

    def draw(self, screen, camera):
        if self.active:
            draw_rect = camera.apply(self.rect)
            pygame.draw.rect(screen, SWORD_COLOR, draw_rect)


class Projectile:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.active = True
        self.direction = direction

        if direction == "up":
            self.dx, self.dy = 0, -PROJECTILE_SPEED
        elif direction == "down":
            self.dx, self.dy = 0, PROJECTILE_SPEED
        elif direction == "left":
            self.dx, self.dy = -PROJECTILE_SPEED, 0
        elif direction == "right":
            self.dx, self.dy = PROJECTILE_SPEED, 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen, camera):
        if self.active:
            draw_rect = camera.apply(self.rect)
            pygame.draw.rect(screen, PROJECTILE_COLOR, draw_rect)