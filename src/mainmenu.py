import pygame

# --- COLORS ---
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GOLD       = (255, 215, 0)
GRAY       = (150, 150, 150)
DARK_GRAY  = (40,  40,  40)
HIGHLIGHT  = (80,  80,  120)
DIM        = (20,  20,  40)

class MainMenu:
    def __init__(self, screen_width, screen_height, has_save):
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.has_save      = has_save
        self.selected      = 0
        self.done          = False
        self.choice        = None  # "new", "continue", "quit"

        self.title_font  = pygame.font.SysFont(None, 96)
        self.option_font = pygame.font.SysFont(None, 48)
        self.sub_font    = pygame.font.SysFont(None, 28)

        self.options = self._build_options()

        # Pre-render title
        self.title_surf = self.title_font.render(
            "STARLIGHT'S EDGE", True, GOLD)
        self.sub_surf   = self.sub_font.render(
            "A tale of love, loss, and an everchanging castle",
            True, GRAY)

        # Animated star particles
        import random
        self.stars = [
            (random.randint(0, screen_width),
             random.randint(0, screen_height),
             random.random() * 2 + 0.5)
            for _ in range(80)
        ]
        self.star_timer = 0

    def _build_options(self):
        options = []
        if self.has_save:
            options.append(("Continue", "continue"))
        options.append(("New Game", "new"))
        options.append(("Quit",     "quit"))
        return options

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % \
                                len(self.options)
            if event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % \
                                len(self.options)
            if event.key in (pygame.K_RETURN, pygame.K_e,
                             pygame.K_SPACE):
                self.choice = self.options[self.selected][1]
                self.done   = True

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self._option_rects):
                if rect.collidepoint(mx, my):
                    self.selected = i

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self._option_rects):
                if rect.collidepoint(mx, my):
                    self.choice = self.options[i][1]
                    self.done   = True

    def draw(self, screen):
        screen.fill(DIM)
        self.star_timer += 1

        # Animated stars
        for i, (sx, sy, speed) in enumerate(self.stars):
            ny = (sy + speed) % self.screen_height
            self.stars[i] = (sx, ny, speed)
            brightness = int(150 + 105 *
                abs(__import__('math').sin(
                    self.star_timer * 0.02 + i)))
            pygame.draw.circle(screen,
                (brightness, brightness, brightness),
                (int(sx), int(ny)), 1)

        # Title
        tx = self.screen_width  // 2 - \
             self.title_surf.get_width()  // 2
        ty = self.screen_height // 4 - \
             self.title_surf.get_height() // 2
        screen.blit(self.title_surf, (tx, ty))

        # Subtitle
        sx = self.screen_width  // 2 - \
             self.sub_surf.get_width()  // 2
        screen.blit(self.sub_surf,
            (sx, ty + self.title_surf.get_height() + 10))

        # Options
        self._option_rects = []
        start_y = self.screen_height // 2
        for i, (label, _) in enumerate(self.options):
            color  = GOLD  if i == self.selected else WHITE
            surf   = self.option_font.render(label, True, color)
            ox     = self.screen_width  // 2 - \
                     surf.get_width()   // 2
            oy     = start_y + i * 70

            # Highlight box
            if i == self.selected:
                box = pygame.Rect(
                    ox - 20, oy - 8,
                    surf.get_width() + 40,
                    surf.get_height() + 16)
                pygame.draw.rect(screen, HIGHLIGHT,
                    box, border_radius=6)
                pygame.draw.rect(screen, GOLD,
                    box, 2, border_radius=6)
                self._option_rects.append(box)
            else:
                self._option_rects.append(pygame.Rect(
                    ox - 20, oy - 8,
                    surf.get_width() + 40,
                    surf.get_height() + 16))

            screen.blit(surf, (ox, oy))

        # Controls hint
        hint = self.sub_font.render(
            "W/S or Arrow Keys to navigate   |   E or Enter to select",
            True, GRAY)
        screen.blit(hint, (
            self.screen_width  // 2 - hint.get_width()  // 2,
            self.screen_height - 40))


class PauseMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.selected      = 0
        self.done          = False
        self.choice        = None  # "resume", "save", "quit"
        self.options       = [
            ("Resume",       "resume"),
            ("Save Game",    "save"),
            ("Quit to Menu", "quit"),
        ]
        self.title_font  = pygame.font.SysFont(None, 64)
        self.option_font = pygame.font.SysFont(None, 42)
        self.sub_font    = pygame.font.SysFont(None, 24)
        self._option_rects = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.choice = "resume"
                self.done   = True
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % \
                                len(self.options)
            if event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % \
                                len(self.options)
            if event.key in (pygame.K_RETURN, pygame.K_e,
                             pygame.K_SPACE):
                self.choice = self.options[self.selected][1]
                self.done   = True

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self._option_rects):
                if rect.collidepoint(mx, my):
                    self.selected = i

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self._option_rects):
                if rect.collidepoint(mx, my):
                    self.choice = self.options[i][1]
                    self.done   = True

    def draw(self, screen):
        # Dim overlay
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height),
            pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Panel
        panel_w = 400
        panel_h = 320
        panel_x = self.screen_width  // 2 - panel_w // 2
        panel_y = self.screen_height // 2 - panel_h // 2
        pygame.draw.rect(screen, (20, 20, 40),
            (panel_x, panel_y, panel_w, panel_h),
            border_radius=12)
        pygame.draw.rect(screen, GOLD,
            (panel_x, panel_y, panel_w, panel_h),
            2, border_radius=12)

        # Title
        title = self.title_font.render("PAUSED", True, GOLD)
        screen.blit(title, (
            self.screen_width // 2 - title.get_width() // 2,
            panel_y + 20))

        # Options
        self._option_rects = []
        start_y = panel_y + 110
        for i, (label, _) in enumerate(self.options):
            color = GOLD if i == self.selected else WHITE
            surf  = self.option_font.render(label, True, color)
            ox    = self.screen_width // 2 - surf.get_width() // 2
            oy    = start_y + i * 60

            if i == self.selected:
                box = pygame.Rect(
                    ox - 15, oy - 6,
                    surf.get_width() + 30,
                    surf.get_height() + 12)
                pygame.draw.rect(screen, HIGHLIGHT,
                    box, border_radius=6)
                pygame.draw.rect(screen, GOLD,
                    box, 2, border_radius=6)
                self._option_rects.append(box)
            else:
                self._option_rects.append(pygame.Rect(
                    ox - 15, oy - 6,
                    surf.get_width() + 30,
                    surf.get_height() + 12))

            screen.blit(surf, (ox, oy))

        # Hint
        hint = self.sub_font.render(
            "ESC to resume", True, GRAY)
        screen.blit(hint, (
            self.screen_width  // 2 - hint.get_width()  // 2,
            panel_y + panel_h - 30))