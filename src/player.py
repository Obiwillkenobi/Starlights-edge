import pygame
from combat import SwordAttack, Projectile
from collision import resolve_collision
from stats import PlayerStats

# --- CONSTANTS ---
PLAYER_SIZE          = 32
PLAYER_COLOR         = (0, 200, 255)
ATTACK_COOLDOWN_BASE = 15
SHOOT_COOLDOWN_BASE  = 20
INVINCIBILITY_FRAMES = 90


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

    # ── stat-derived values ───────────────────────────────────────────
    @property
    def speed(self):
        return self.stats.get_speed()

    @property
    def melee_damage(self):
        return self.stats.get_melee_damage()

    @property
    def detection_reduction(self):
        return self.stats.get_detection_reduction()

    # ── health ────────────────────────────────────────────────────────
    def take_damage(self, amount):
        if self.invincibility_timer == 0 and self.alive:
            self.health -= amount
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
        """Call after equipping items to update max health."""
        new_max = self.stats.get_max_health()
        diff    = new_max - self.max_health
        self.max_health = new_max
        if diff > 0:
            self.health = min(self.health + diff, self.max_health)

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

        if keys[pygame.K_k] and self.shoot_timer == 0:
            self.projectiles.append(
                Projectile(self.rect.centerx, self.rect.centery,
                           self.direction))
            self.shoot_timer = SHOOT_COOLDOWN_BASE

    # ── update ────────────────────────────────────────────────────────
    def update(self):
        if self.attack_timer        > 0: self.attack_timer        -= 1
        if self.shoot_timer         > 0: self.shoot_timer         -= 1
        if self.invincibility_timer > 0: self.invincibility_timer -= 1

        # Mana regeneration
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
        else:
            cls_color = self.stats.get_class_info()["color"]
            color     = cls_color if self.alive else (100, 100, 100)

        pygame.draw.rect(screen, color, draw_rect)

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

        # Stats panel
        self.stats.draw_stats_hud(screen, font)