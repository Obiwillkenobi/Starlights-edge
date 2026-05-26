import pygame
from combat import SwordAttack, Projectile
from collision import resolve_collision
from stats import PlayerStats

# --- CONSTANTS ---
PLAYER_SIZE          = 32
ATTACK_COOLDOWN_BASE = 15
SHOOT_COOLDOWN_BASE  = 20
INVINCIBILITY_FRAMES = 90
STEALTH_RADIUS       = 300   # Pixels — only affects enemies within this range


class Player:
    def __init__(self, x, y):
        self.rect        = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.direction   = "right"
        self.alive       = True

        # Stats system
        self.stats = PlayerStats()

        # Health derived from stats
        self.max_health = self.stats.get_max_health()
        self.health     = self.max_health

        # Timers
        self.invincibility_timer = 0
        self.attack_timer        = 0
        self.shoot_timer         = 0

        # Combat
        self.sword       = None
        self.projectiles = []
        self.walls       = []

        # Stealth
        self.stealthed        = False
        self.stealth_radius   = STEALTH_RADIUS
        self.stealth_timer    = 0   # Visual pulse timer

    # ── stat-derived values ───────────────────────────────────────────
    @property
    def speed(self):
        return self.stats.get_speed()

    @property
    def melee_damage(self):
        return self.stats.get_melee_damage()

    @property
    def detection_reduction(self):
        # Only applies when stealthed
        if self.stealthed:
            return self.stats.get_detection_reduction()
        return 0

    # ── health ────────────────────────────────────────────────────────
    def take_damage(self, amount):
        if self.invincibility_timer == 0 and self.alive:
            # Taking damage breaks stealth
            self.stealthed = False
            self.health   -= amount
            self.invincibility_timer = INVINCIBILITY_FRAMES
            if self.health <= 0:
                self.health = 0
                self.alive  = False
                self.stats.on_death()

    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)

    def full_heal(self):
        self.max_health = self.stats.get_max_health()
        self.health     = self.max_health
        self.stats.restore_mana()

    def refresh_max_health(self):
        new_max = self.stats.get_max_health()
        diff    = new_max - self.max_health
        self.max_health = new_max
        if diff > 0:
            self.health = min(self.health + diff, self.max_health)

    # ── stealth ───────────────────────────────────────────────────────
    def toggle_stealth(self):
        if not self.stealthed:
            # Only activate if we have mana
            if self.stats.mana > 0:
                self.stealthed = True
        else:
            self.stealthed = False

    def is_enemy_in_stealth_range(self, enemy):
        """Returns True if this enemy is close enough to be affected."""
        dx   = enemy.rect.centerx - self.rect.centerx
        dy   = enemy.rect.centery - self.rect.centery
        dist = (dx * dx + dy * dy) ** 0.5
        return dist <= self.stealth_radius

    # ── input ─────────────────────────────────────────────────────────
    def handle_input(self):
        if not self.alive:
            return
        keys = pygame.key.get_pressed()
        spd  = int(self.speed)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= spd
            self.rect    = resolve_collision(self.rect, self.walls)
            self.direction = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += spd
            self.rect    = resolve_collision(self.rect, self.walls)
            self.direction = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= spd
            self.rect    = resolve_collision(self.rect, self.walls)
            self.direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += spd
            self.rect    = resolve_collision(self.rect, self.walls)
            self.direction = "right"

        if keys[pygame.K_j] and self.attack_timer == 0:
            self.sword        = SwordAttack(self.rect, self.direction,
                                            damage=self.melee_damage)
            self.attack_timer = ATTACK_COOLDOWN_BASE
            # Attacking breaks stealth
            self.stealthed    = False

        if keys[pygame.K_k] and self.shoot_timer == 0:
            self.projectiles.append(
                Projectile(self.rect.centerx, self.rect.centery,
                           self.direction))
            self.shoot_timer = SHOOT_COOLDOWN_BASE
            # Attacking breaks stealth
            self.stealthed   = False

    # ── update ────────────────────────────────────────────────────────
    def update(self):
        if self.attack_timer        > 0: self.attack_timer        -= 1
        if self.shoot_timer         > 0: self.shoot_timer         -= 1
        if self.invincibility_timer > 0: self.invincibility_timer -= 1

        # Stealth timer for visual pulse only
        if self.stealthed:
            self.stealth_timer += 1
        else:
            self.stealth_timer = 0

        # Mana always regenerates
        self.stats.update_mana()

        if self.sword and self.sword.active:
            self.sword.update()

        for p in self.projectiles:
            p.update()
        self.projectiles = [p for p in self.projectiles if p.active]

    # ── draw ──────────────────────────────────────────────────────────
    def draw(self, screen, camera):
        draw_rect = camera.apply(self.rect)

        # Flash white when invincible
        if self.invincibility_timer > 0 and \
                self.invincibility_timer % 6 < 3:
            color = (255, 255, 255)
        elif self.stealthed:
            # Pulse dark blue when stealthed
            pulse = abs(math.sin(self.stealth_timer * 0.05))
            r = int(20  * pulse)
            g = int(80  * pulse)
            b = int(180 * pulse + 40)
            color = (r, g, b)
        else:
            cls_color = self.stats.get_class_info()["color"]
            color     = cls_color if self.alive else (100, 100, 100)

        pygame.draw.rect(screen, color, draw_rect)

        # Draw stealth radius ring
        if self.stealthed:
            pulse_alpha = int(40 + 30 * abs(
                math.sin(self.stealth_timer * 0.05)))
            center = (draw_rect.centerx, draw_rect.centery)
            scaled_radius = int(self.stealth_radius *
                (screen.get_width() / (camera.width * 2 + 1)))
            # Draw as a simple circle outline
            pygame.draw.circle(screen, (50, 100, 200),
                center,
                int(self.stealth_radius * 0.15),
                1)

        if self.sword and self.sword.active:
            self.sword.draw(screen, camera)
        for p in self.projectiles:
            p.draw(screen, camera)

    def draw_hud(self, screen):
        font         = pygame.font.SysFont(None, 24)
        bar_x, bar_y = 20, 20
        bar_w, bar_h = 200, 20

        # Health bar
        health_ratio = self.health / max(1, self.max_health)
        pygame.draw.rect(screen, (80, 80, 80),
            (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, (200, 50, 50),
            (bar_x, bar_y, int(bar_w * health_ratio), bar_h))
        pygame.draw.rect(screen, (255, 255, 255),
            (bar_x, bar_y, bar_w, bar_h), 2)
        screen.blit(
            font.render(
                f"HP: {self.health} / {self.max_health}",
                True, (255, 255, 255)),
            (bar_x + 5, bar_y + 3))

        # Mana bar
        max_mana   = self.stats.get_max_mana()
        mana_ratio = self.stats.mana / max(1, max_mana)
        bar_y2     = bar_y + bar_h + 6
        pygame.draw.rect(screen, (80, 80, 80),
            (bar_x, bar_y2, bar_w, bar_h))
        pygame.draw.rect(screen, (50, 80, 200),
            (bar_x, bar_y2, int(bar_w * mana_ratio), bar_h))
        pygame.draw.rect(screen, (255, 255, 255),
            (bar_x, bar_y2, bar_w, bar_h), 2)
        screen.blit(
            font.render(
                f"MP: {int(self.stats.mana)} / {max_mana}",
                True, (255, 255, 255)),
            (bar_x + 5, bar_y2 + 3))

        # Stealth indicator
        if self.stealthed:
            screen.blit(font.render(
                "STEALTH ACTIVE", True, (50, 100, 220)),
                (bar_x, bar_y2 + bar_h + 6))

        # Stats panel
        self.stats.draw_stats_hud(screen, font)

    def draw_stealth_radius(self, screen, camera):
        """
        Draw the stealth radius in world space so it scales
        correctly with the camera.
        """
        if not self.stealthed:
            return
        center_world = self.rect.center
        # Draw 8 points around the radius to approximate a circle
        import math
        points = []
        for i in range(16):
            angle = (i / 16) * 2 * math.pi
            wx    = center_world[0] + \
                    int(math.cos(angle) * self.stealth_radius)
            wy    = center_world[1] + \
                    int(math.sin(angle) * self.stealth_radius)
            draw  = camera.apply(pygame.Rect(wx, wy, 1, 1))
            points.append((draw.x, draw.y))
        if len(points) > 2:
            pygame.draw.polygon(screen, (30, 60, 150), points, 1)


import math