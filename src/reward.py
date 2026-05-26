import pygame
import random

# --- COLORS ---
CARD_BG       = (30,  30,  50)
CARD_BORDER   = (100, 100, 150)
CARD_HOVER    = (50,  50,  80)
CARD_SELECTED = (80,  80,  120)
GOLD_COLOR    = (255, 215, 0)
WHITE         = (255, 255, 255)
GRAY          = (150, 150, 150)
BLACK         = (0,   0,   0)

# --- PLACEHOLDER ITEM POOLS ---
PLACEHOLDER_WEAPONS = [
    {"name": "Rusty Sword",     "type": "light",  "stat": "STR +1", "bonuses": {"strength": 1},      "rarity": "common"},
    {"name": "Iron Mace",       "type": "blunt",  "stat": "STR +2", "bonuses": {"strength": 2},      "rarity": "common"},
    {"name": "Oak Staff",       "type": "staff",  "stat": "INT +2", "bonuses": {"intelligence": 2},  "rarity": "common"},
    {"name": "Short Bow",       "type": "ranged", "stat": "SPD +1", "bonuses": {"speed": 1},         "rarity": "common"},
    {"name": "Dagger",          "type": "light",  "stat": "SPD +1", "bonuses": {"speed": 1},         "rarity": "common"},
    {"name": "Warhammer",       "type": "heavy",  "stat": "STR +3", "bonuses": {"strength": 3},      "rarity": "uncommon"},
    {"name": "Apprentice Wand", "type": "wand",   "stat": "INT +3", "bonuses": {"intelligence": 3},  "rarity": "uncommon"},
    {"name": "Crossbow",        "type": "ranged", "stat": "STR +2", "bonuses": {"strength": 2},      "rarity": "uncommon"},
    {"name": "Twin Daggers",    "type": "light",  "stat": "SPD +2", "bonuses": {"speed": 2},         "rarity": "uncommon"},
    {"name": "Greatsword",      "type": "heavy",  "stat": "STR +4", "bonuses": {"strength": 4},      "rarity": "rare"},
    {"name": "Arcane Staff",    "type": "staff",  "stat": "INT +5", "bonuses": {"intelligence": 5},  "rarity": "rare"},
    {"name": "Enchanted Bow",   "type": "ranged", "stat": "SPD +3", "bonuses": {"speed": 3},         "rarity": "rare"},
]

PLACEHOLDER_ARMOR = [
    {"name": "Leather Cap",       "slot": "helmet",      "type": "light", "stat": "SPD +1",  "bonuses": {"speed": 1},         "rarity": "common"},
    {"name": "Iron Helmet",       "slot": "helmet",      "type": "heavy", "stat": "CON +1",  "bonuses": {"constitution": 1},  "rarity": "common"},
    {"name": "Linen Robe Top",    "slot": "breastplate", "type": "robe",  "stat": "INT +1",  "bonuses": {"intelligence": 1},  "rarity": "common"},
    {"name": "Leather Vest",      "slot": "breastplate", "type": "light", "stat": "SPD +1",  "bonuses": {"speed": 1},         "rarity": "common"},
    {"name": "Iron Chestplate",   "slot": "breastplate", "type": "heavy", "stat": "CON +2",  "bonuses": {"constitution": 2},  "rarity": "common"},
    {"name": "Leather Gloves",    "slot": "gauntlets",   "type": "light", "stat": "STL +1",  "bonuses": {"stealth": 1},       "rarity": "common"},
    {"name": "Iron Gauntlets",    "slot": "gauntlets",   "type": "heavy", "stat": "STR +1",  "bonuses": {"strength": 1},      "rarity": "common"},
    {"name": "Cloth Bracers",     "slot": "bracers",     "type": "robe",  "stat": "INT +1",  "bonuses": {"intelligence": 1},  "rarity": "common"},
    {"name": "Leather Bracers",   "slot": "bracers",     "type": "light", "stat": "STL +1",  "bonuses": {"stealth": 1},       "rarity": "common"},
    {"name": "Iron Boots",        "slot": "boots",       "type": "heavy", "stat": "CON +1",  "bonuses": {"constitution": 1},  "rarity": "common"},
    {"name": "Soft Boots",        "slot": "boots",       "type": "light", "stat": "SPD +2",  "bonuses": {"speed": 2},         "rarity": "uncommon"},
    {"name": "Enchanted Robes",   "slot": "breastplate", "type": "robe",  "stat": "INT +3",  "bonuses": {"intelligence": 3},  "rarity": "rare"},
    {"name": "Shadow Cloak",      "slot": "breastplate", "type": "light", "stat": "STL +3",  "bonuses": {"stealth": 3},       "rarity": "rare"},
    {"name": "Dragonscale Plate", "slot": "breastplate", "type": "heavy", "stat": "CON +4",  "bonuses": {"constitution": 4},  "rarity": "rare"},
]

RARITY_COLORS = {
    "common":   (180, 180, 180),
    "uncommon": (50,  200, 50),
    "rare":     (80,  100, 220),
}

RARITY_WEIGHTS = {
    "common":   70,
    "uncommon": 25,
    "rare":     5,
}


def pick_weighted_item(pool):
    weights = [RARITY_WEIGHTS[item["rarity"]] for item in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def generate_reward_cards():
    all_items = []
    all_items.append(dict(pick_weighted_item(PLACEHOLDER_WEAPONS),
                          category="weapon"))
    all_items.append(dict(pick_weighted_item(PLACEHOLDER_ARMOR),
                          category="armor"))
    if random.random() < 0.5:
        all_items.append(dict(pick_weighted_item(PLACEHOLDER_WEAPONS),
                              category="weapon"))
    else:
        all_items.append(dict(pick_weighted_item(PLACEHOLDER_ARMOR),
                              category="armor"))
    random.shuffle(all_items)
    return all_items


class RewardCard:
    def __init__(self, item, x, y, width, height):
        self.item     = item
        self.rect     = pygame.Rect(x, y, width, height)
        self.hovered  = False
        self.selected = False

    def draw(self, screen, font, small_font):
        if self.selected:
            color = CARD_SELECTED
        elif self.hovered:
            color = CARD_HOVER
        else:
            color = CARD_BG

        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        rarity       = self.item.get("rarity", "common")
        border_color = RARITY_COLORS.get(rarity, CARD_BORDER)
        border_width = 3 if self.selected else 2
        pygame.draw.rect(screen, border_color, self.rect,
                         border_width, border_radius=8)

        cat       = self.item.get("category", "")
        cat_color = (100, 180, 255) if cat == "weapon" else (180, 130, 80)
        tag       = small_font.render(cat.upper(), True, cat_color)
        screen.blit(tag, (self.rect.x + 10, self.rect.y + 10))

        name      = self.item.get("name", "Unknown")
        name_surf = font.render(name, True, WHITE)
        screen.blit(name_surf, (
            self.rect.centerx - name_surf.get_width() // 2,
            self.rect.y + 40))

        itype     = self.item.get("type", self.item.get("slot", ""))
        type_surf = small_font.render(itype.upper(), True, GRAY)
        screen.blit(type_surf, (
            self.rect.centerx - type_surf.get_width() // 2,
            self.rect.y + 70))

        stat      = self.item.get("stat", "")
        stat_surf = font.render(stat, True, (100, 220, 100))
        screen.blit(stat_surf, (
            self.rect.centerx - stat_surf.get_width() // 2,
            self.rect.y + 100))

        rar_surf  = small_font.render(rarity.upper(), True, border_color)
        screen.blit(rar_surf, (
            self.rect.centerx - rar_surf.get_width() // 2,
            self.rect.y + 130))

        if self.selected:
            check = font.render("SELECTED", True, (100, 220, 100))
            screen.blit(check, (
                self.rect.centerx - check.get_width() // 2,
                self.rect.bottom - 35))


class RewardPopup:
    def __init__(self, screen_width, screen_height):
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.active        = False
        self.cards         = []
        self.selected_card = None
        self.gold_reward   = 0
        self.confirmed     = False

        self.font       = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)
        self.big_font   = pygame.font.SysFont(None, 42)

    def show(self):
        self.active        = True
        self.confirmed     = False
        self.selected_card = None
        self.gold_reward   = random.randint(1, 100)

        items   = generate_reward_cards()
        card_w  = 180
        card_h  = 220
        padding = 30
        total_w = card_w * 3 + padding * 2
        start_x = self.screen_width  // 2 - total_w // 2
        card_y  = self.screen_height // 2 - card_h // 2 + 20

        self.cards = []
        for i, item in enumerate(items):
            cx = start_x + i * (card_w + padding)
            self.cards.append(
                RewardCard(item, cx, card_y, card_w, card_h))

    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for card in self.cards:
                card.hovered = card.rect.collidepoint(mx, my)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for card in self.cards:
                if card.rect.collidepoint(mx, my):
                    for c in self.cards:
                        c.selected = False
                    card.selected      = True
                    self.selected_card = card.item

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.selected_card:
                self.confirmed = True
                self.active    = False

    def apply_to_player(self, player):
        """
        Apply the selected item's stat bonuses to the player.
        Called from main.py after confirmation.
        """
        if not self.selected_card:
            return

        bonuses = self.selected_card.get("bonuses", {})
        for stat, value in bonuses.items():
            if stat in player.stats.item_bonus:
                player.stats.item_bonus[stat] += value

        # Refresh health in case constitution changed
        player.refresh_max_health()

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface(
            (self.screen_width, self.screen_height),
            pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.big_font.render(
            "Room Cleared! Choose a Reward", True, GOLD_COLOR)
        screen.blit(title, (
            self.screen_width  // 2 - title.get_width()  // 2,
            self.screen_height // 2 - 160))

        gold_txt = self.font.render(
            f"+ {self.gold_reward} Gold", True, GOLD_COLOR)
        screen.blit(gold_txt, (
            self.screen_width  // 2 - gold_txt.get_width()  // 2,
            self.screen_height // 2 - 120))

        for card in self.cards:
            card.draw(screen, self.font, self.small_font)

        if self.selected_card:
            confirm = self.font.render(
                "Press E to confirm selection", True, WHITE)
        else:
            confirm = self.font.render(
                "Click a card to select it", True, GRAY)
        screen.blit(confirm, (
            self.screen_width  // 2 - confirm.get_width()  // 2,
            self.screen_height // 2 + 150))