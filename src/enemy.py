import pygame
import math
import random
from collision import resolve_collision

# --- CONSTANTS ---
ENEMY_SIZE = 32
ENEMY_COLOR = (220, 50, 50)
ENEMY_PATROL_COLOR = (180, 50, 50)
ENEMY_MAX_HEALTH = 3
ENEMY_SPEED = 2
ENEMY_CHASE_SPEED = 3
ENEMY_DETECT_RANGE = 200
ENEMY_ATTACK_RANGE = 40
ENEMY_ATTACK_COOLDOWN = 60
ENEMY_DAMAGE = 1
PATROL_CHANGE_TIME = 90

PATROLLING = "patrolling"
CHASING = "chasing"
ATTACKING = "attacking"

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.health = ENEMY_MAX_HEALTH
        self.active = True
        self.state = PATROLLING
        self.attack_timer = 0
        self.patrol_timer = 0
        self.patrol_dx = random.choice([-1, 0, 1])
        self.patrol_dy = random.choice([-1, 0, 1])
        self.walls = []

    def get_distance(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        return math.sqrt(dx * dx + dy * dy)

    def update(self, player):
        if not self.active:
            return

        distance = self.get_distance(player)

        # --- STATE TRANSITIONS ---
        if distance <= ENEMY_ATTACK_RANGE:
            self.state = ATTACKING
        elif distance <= ENEMY_DETECT_RANGE:
            self.state = CHASING
        else:
            self.state = PATROLLING

        # --- STATE BEHAVIORS ---
        if self.state == PATROLLING:
            self.patrol_timer += 1
            if self.patrol_timer >= PATROL_CHANGE_TIME:
                self.patrol_timer = 0
                self.patrol_dx = random.choice([-1, 0, 1])
                self.patrol_dy = random.choice([-1, 0, 1])
            self.rect.x += self.patrol_dx * ENEMY_SPEED
            self.rect = resolve_collision(self.rect, self.walls)
            self.rect.y += self.patrol_dy * ENEMY_SPEED
            self.rect = resolve_collision(self.rect, self.walls)

        elif self.state == CHASING:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = max(1, math.sqrt(dx * dx + dy * dy))
            self.rect.x += int((dx / dist) * ENEMY_CHASE_SPEED)
            self.rect = resolve_collision(self.rect, self.walls)
            self.rect.y += int((dy / dist) * ENEMY_CHASE_SPEED)
            self.rect = resolve_collision(self.rect, self.walls)

        elif self.state == ATTACKING:
            if self.attack_timer == 0:
                player.take_damage(ENEMY_DAMAGE)
                self.attack_timer = ENEMY_ATTACK_COOLDOWN

        if self.attack_timer > 0:
            self.attack_timer -= 1

    def check_hits(self, player):
        if player.sword and player.sword.active:
            if self.rect.colliderect(player.sword.rect):
                self.health -= 1
                player.sword.active = False

        for p in player.projectiles:
            if self.rect.colliderect(p.rect):
                self.health -= 1
                p.active = False

        if self.health <= 0:
            self.active = False

    def draw(self, screen, camera):
        if self.active:
            draw_rect = camera.apply(self.rect)

            color = ENEMY_PATROL_COLOR if self.state == PATROLLING else ENEMY_COLOR
            pygame.draw.rect(screen, color, draw_rect)

            bar_width = ENEMY_SIZE
            bar_height = 6
            health_ratio = self.health / ENEMY_MAX_HEALTH
            bar_x = draw_rect.x
            bar_y = draw_rect.y - 10

            pygame.draw.rect(screen, (80, 80, 80),
                (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (50, 200, 50),
                (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

            font = pygame.font.SysFont(None, 18)
            label = font.render(self.state, True, (255, 255, 255))
            screen.blit(label, (draw_rect.x, draw_rect.y - 24))