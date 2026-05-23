import pygame

# --- CONSTANTS ---
PLAYER_SPEED = 4
PLAYER_SIZE = 32

# --- COLORS ---
PLAYER_COLOR = (0, 200, 255)  # Bright cyan placeholder

class Player:
    def __init__(self, x, y):
        # Position and size
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)