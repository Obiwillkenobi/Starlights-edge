import pygame
from combat import SwordAttack, Projectile

# --- CONSTANTS ---
PLAYER_SPEED = 4
PLAYER_SIZE = 32
PLAYER_COLOR = (0, 200, 255)
ATTACK_COOLDOWN = 20
SHOOT_COOLDOWN = 30

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.direction = "right"

        # Combat
        self.sword = None
        self.projectiles = []
        self.attack_timer = 0
        self.shoot_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # --- MOVEMENT ---
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
            self.direction = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.direction = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = "right"

        # --- MELEE ATTACK (J key) ---
        if keys[pygame.K_j] and self.attack_timer == 0:
            self.sword = SwordAttack(self.rect, self.direction)
            self.attack_timer = ATTACK_COOLDOWN

        # --- RANGED ATTACK (K key) ---
        if keys[pygame.K_k] and self.shoot_timer == 0:
            self.projectiles.append(
                Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    self.direction
                )
            )
            self.shoot_timer = SHOOT_COOLDOWN

    def update(self):
        # Count down timers
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Update sword
        if self.sword and self.sword.active:
            self.sword.update()

        # Update projectiles
        for p in self.projectiles:
            p.update()

        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, screen, camera):
        # Draw player
        draw_rect = camera.apply(self.rect)
        pygame.draw.rect(screen, PLAYER_COLOR, draw_rect)

        # Draw sword
        if self.sword and self.sword.active:
            self.sword.draw(screen, camera)

        # Draw projectiles
        for p in self.projectiles:
            p.draw(screen, camera)