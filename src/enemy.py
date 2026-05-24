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
ENEMY_DETECT_RANGE = 250
ENEMY_ATTACK_RANGE = 40
ENEMY_ATTACK_COOLDOWN = 60
ENEMY_DAMAGE = 1
PATROL_CHANGE_TIME = 90

PATROLLING = "patrolling"
CHASING = "chasing"
ATTACKING = "attacking"

class Enemy:
    def __init__(self, x, y, room=None):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.health = ENEMY_MAX_HEALTH
        self.active = True
        self.state = PATROLLING
        self.attack_timer = 0
        self.patrol_timer = 0
        self.patrol_dx = random.choice([-1, 0, 1])
        self.patrol_dy = random.choice([-1, 0, 1])
        self.walls = []
        self.player_in_room = False

        self.home_room = room
        if room:
            from room import TILE_SIZE
            self.bounds = pygame.Rect(
                room.x + TILE_SIZE,
                room.y + TILE_SIZE,
                room.get_pixel_width() - TILE_SIZE * 2,
                room.get_pixel_height() - TILE_SIZE * 2
            )
            self.home_x = room.x + room.get_pixel_width() // 2
            self.home_y = room.y + room.get_pixel_height() // 2
        else:
            self.bounds = None
            self.home_x = x
            self.home_y = y

    def get_distance_to(self, x, y):
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        return math.sqrt(dx * dx + dy * dy)

    def get_distance(self, player):
        return self.get_distance_to(
            player.rect.centerx, player.rect.centery
        )

    def clamp_to_bounds(self):
        if self.bounds:
            if self.rect.left < self.bounds.left:
                self.rect.left = self.bounds.left
            if self.rect.right > self.bounds.right:
                self.rect.right = self.bounds.right
            if self.rect.top < self.bounds.top:
                self.rect.top = self.bounds.top
            if self.rect.bottom > self.bounds.bottom:
                self.rect.bottom = self.bounds.bottom

    def move_toward(self, tx, ty, speed):
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        self.rect.x += int((dx / dist) * speed)
        self.rect = resolve_collision(self.rect, self.walls)
        self.rect.y += int((dy / dist) * speed)
        self.rect = resolve_collision(self.rect, self.walls)
        self.clamp_to_bounds()

    def update(self, player, player_in_room=True):
        if not self.active:
            return

        self.player_in_room = player_in_room

        if not player_in_room:
            # Player has left — return to patrol
            self.state = PATROLLING

            # Drift back toward room center
            dist_home = self.get_distance_to(self.home_x, self.home_y)
            if dist_home > 10:
                self.move_toward(self.home_x, self.home_y, ENEMY_SPEED)
            else:
                # Wander randomly once home
                self.patrol_timer += 1
                if self.patrol_timer >= PATROL_CHANGE_TIME:
                    self.patrol_timer = 0
                    self.patrol_dx = random.choice([-1, 0, 1])
                    self.patrol_dy = random.choice([-1, 0, 1])
                self.rect.x += self.patrol_dx * ENEMY_SPEED
                self.rect = resolve_collision(self.rect, self.walls)
                self.rect.y += self.patrol_dy * ENEMY_SPEED
                self.rect = resolve_collision(self.rect, self.walls)
                self.clamp_to_bounds()
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
            self.clamp_to_bounds()

        elif self.state == CHASING:
            self.move_toward(
                player.rect.centerx, player.rect.centery,
                ENEMY_CHASE_SPEED
            )

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