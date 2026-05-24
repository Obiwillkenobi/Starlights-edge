import pygame
from combat import SwordAttack, Projectile

# --- CONSTANTS ---
PLAYER_SPEED = 4
PLAYER_SIZE = 32
PLAYER_COLOR = (0, 200, 255)
PLAYER_MAX_HEALTH = 10
ATTACK_COOLDOWN = 20
SHOOT_COOLDOWN = 30
INVINCIBILITY_FRAMES = 60  # Player can't be hit again for 1 second after taking damage

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.direction = "right"

        # Health
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.invincibility_timer = 0
        self.alive = True

        # Combat
        self.sword = None
        self.projectiles = []
        self.attack_timer = 0
        self.shoot_timer = 0

    def take_damage(self, amount):
        if self.invincibility_timer == 0 and self.alive:
            self.health -= amount
            self.invincibility_timer = INVINCIBILITY_FRAMES
            if self.health <= 0:
                self.health = 0
                self.alive = False

    def handle_input(self):
        if not self.alive:
            return

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
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # Update sword
        if self.sword and self.sword.active:
            self.sword.update()

        # Update projectiles
        for p in self.projectiles:
            p.update()

        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, screen, camera):
        draw_rect = camera.apply(self.rect)

        # Flash white when invincible
        if self.invincibility_timer > 0 and self.invincibility_timer % 6 < 3:
            color = (255, 255, 255)
        else:
            color = (0, 200, 255) if self.alive else (100, 100, 100)

        pygame.draw.rect(screen, color, draw_rect)

        # Draw sword
        if self.sword and self.sword.active:
            self.sword.draw(screen, camera)

        # Draw projectiles
        for p in self.projectiles:
            p.draw(screen, camera)

    def draw_hud(self, screen):
        # Draw health bar in top left corner
        bar_x, bar_y = 20, 20
        bar_width, bar_height = 200, 20
        health_ratio = self.health / self.max_health

        # Background
        pygame.draw.rect(screen, (80, 80, 80),
            (bar_x, bar_y, bar_width, bar_height))
        # Health
        pygame.draw.rect(screen, (200, 50, 50),
            (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        # Border
        pygame.draw.rect(screen, (255, 255, 255),
            (bar_x, bar_y, bar_width, bar_height), 2)

        # Health text
        font = pygame.font.SysFont(None, 24)
        text = font.render(
            f"HP: {self.health} / {self.max_health}",
            True, (255, 255, 255)
        )
        screen.blit(text, (bar_x + 5, bar_y + 3))