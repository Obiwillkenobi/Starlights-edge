import pygame
import math
import random
from collision import resolve_collision

# --- CONSTANTS ---
ENEMY_SIZE           = 32
ENEMY_COLOR          = (220, 50,  50)
ENEMY_PATROL_COLOR   = (180, 50,  50)
ENEMY_BASE_HEALTH    = 3
ENEMY_BASE_SPEED     = 2
ENEMY_CHASE_SPEED    = 3
ENEMY_DETECT_RANGE   = 250
ENEMY_ATTACK_RANGE   = 40
ENEMY_ATTACK_COOLDOWN = 60
ENEMY_DAMAGE         = 1
PATROL_CHANGE_TIME   = 90

PATROLLING = "patrolling"
CHASING    = "chasing"
ATTACKING  = "attacking"


class Enemy:
    def __init__(self, x, y, room=None,
                 health_mult=1.0, speed_mult=1.0):
        self.rect   = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.health = max(1, int(ENEMY_BASE_HEALTH * health_mult))
        self.max_health = self.health
        self.speed       = max(1, int(ENEMY_BASE_SPEED  * speed_mult))
        self.chase_speed = max(2, int(ENEMY_CHASE_SPEED * speed_mult))
        self.active = True
        self.state  = PATROLLING
        self.attack_timer  = 0
        self.patrol_timer  = 0
        self.patrol_dx     = random.choice([-1, 0, 1])
        self.patrol_dy     = random.choice([-1, 0, 1])
        self.walls         = []
        self.player_in_room = False

        self.home_room = room
        if room:
            from room import TILE_SIZE
            self.bounds = pygame.Rect(
                room.x + TILE_SIZE,
                room.y + TILE_SIZE,
                room.get_pixel_width()  - TILE_SIZE * 2,
                room.get_pixel_height() - TILE_SIZE * 2
            )
            self.home_x = room.x + room.get_pixel_width()  // 2
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
            player.rect.centerx, player.rect.centery)

    def clamp_to_bounds(self):
        if self.bounds:
            self.rect.left   = max(self.rect.left,   self.bounds.left)
            self.rect.right  = min(self.rect.right,  self.bounds.right)
            self.rect.top    = max(self.rect.top,    self.bounds.top)
            self.rect.bottom = min(self.rect.bottom, self.bounds.bottom)

    def move_toward(self, tx, ty, speed):
        dx   = tx - self.rect.centerx
        dy   = ty - self.rect.centery
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        self.rect.x += int((dx / dist) * speed)
        self.rect    = resolve_collision(self.rect, self.walls)
        self.rect.y += int((dy / dist) * speed)
        self.rect    = resolve_collision(self.rect, self.walls)
        self.clamp_to_bounds()

    def update(self, player, player_in_room=True):
        if not self.active:
            return

        self.player_in_room = player_in_room

        if not player_in_room:
            self.state = PATROLLING
            dist_home  = self.get_distance_to(self.home_x, self.home_y)
            if dist_home > 10:
                self.move_toward(self.home_x, self.home_y, self.speed)
            else:
                self.patrol_timer += 1
                if self.patrol_timer >= PATROL_CHANGE_TIME:
                    self.patrol_timer = 0
                    self.patrol_dx = random.choice([-1, 0, 1])
                    self.patrol_dy = random.choice([-1, 0, 1])
                self.rect.x += self.patrol_dx * self.speed
                self.rect    = resolve_collision(self.rect, self.walls)
                self.rect.y += self.patrol_dy * self.speed
                self.rect    = resolve_collision(self.rect, self.walls)
                self.clamp_to_bounds()
            return

        distance = self.get_distance(player)

        if distance <= ENEMY_ATTACK_RANGE:
            self.state = ATTACKING
        elif distance <= ENEMY_DETECT_RANGE:
            self.state = CHASING
        else:
            self.state = PATROLLING

        if self.state == PATROLLING:
            self.patrol_timer += 1
            if self.patrol_timer >= PATROL_CHANGE_TIME:
                self.patrol_timer = 0
                self.patrol_dx = random.choice([-1, 0, 1])
                self.patrol_dy = random.choice([-1, 0, 1])
            self.rect.x += self.patrol_dx * self.speed
            self.rect    = resolve_collision(self.rect, self.walls)
            self.rect.y += self.patrol_dy * self.speed
            self.rect    = resolve_collision(self.rect, self.walls)
            self.clamp_to_bounds()

        elif self.state == CHASING:
            self.move_toward(
                player.rect.centerx, player.rect.centery,
                self.chase_speed)

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
        if not self.active:
            return

        draw_rect = camera.apply(self.rect)

        # Darken color as health drops
        health_ratio = self.health / self.max_health
        r = int(ENEMY_COLOR[0] * health_ratio)
        g = int(ENEMY_COLOR[1] * health_ratio)
        b = int(ENEMY_COLOR[2] * health_ratio)
        color = (max(r, 80), g, b) if self.state != PATROLLING \
                else ENEMY_PATROL_COLOR

        pygame.draw.rect(screen, color, draw_rect)

        # Health bar
        bar_w = ENEMY_SIZE
        bar_h = 6
        bx    = draw_rect.x
        by    = draw_rect.y - 10
        pygame.draw.rect(screen, (80, 80, 80),
            (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, (50, 200, 50),
            (bx, by, int(bar_w * health_ratio), bar_h))