# --- BASE STATS ---
# All stats start at 1
BASE_STATS = {
    "constitution": 1,
    "speed":        1,
    "stealth":      1,
    "strength":     1,
    "intelligence": 1
}

# --- STAT EFFECTS ---
# How each stat point translates into gameplay
# These are multipliers/additions applied on top of base values
STAT_EFFECTS = {
    "constitution": {
        "description": "Increases max health",
        "health_per_point": 5       # Each point = +5 max HP
    },
    "speed": {
        "description": "Increases movement speed",
        "speed_per_point": 0.5      # Each point = +0.5 move speed
    },
    "stealth": {
        "description": "Reduces enemy detection range",
        "detection_reduction_per_point": 20  # Each point = -20px detection
    },
    "strength": {
        "description": "Increases melee damage",
        "damage_per_point": 1       # Each point = +1 melee damage
    },
    "intelligence": {
        "description": "Increases max mana and mana regen",
        "mana_per_point": 10,       # Each point = +10 max mana
        "regen_per_point": 0.1      # Each point = +0.1 mana/sec
    }
}

# --- CLASS DEFINITIONS ---
# Stat bonuses/penalties applied when a class is active
CLASS_STATS = {
    "barbarian": {
        "name":         "Barbarian",
        "color":        (180, 50,  50),
        "constitution": +3,
        "speed":        0,
        "stealth":      -2,
        "strength":     +2,
        "intelligence": -2,
        "description":  "Blunt weapons, no armor"
    },
    "wizard": {
        "name":         "Wizard",
        "color":        (150, 100, 255),
        "constitution": -2,
        "speed":        0,
        "stealth":      0,
        "strength":     -2,
        "intelligence": +3,
        "description":  "Wand or staff, robes"
    },
    "knight": {
        "name":         "Knight",
        "color":        (150, 150, 180),
        "constitution": +2,
        "speed":        0,
        "stealth":      -2,
        "strength":     +1,
        "intelligence": 0,
        "description":  "Heavy weapons, heavy armor"
    },
    "rogue": {
        "name":         "Rogue",
        "color":        (50,  200, 100),
        "constitution": 0,
        "speed":        +1,
        "stealth":      +3,
        "strength":     -2,
        "intelligence": 0,
        "description":  "Light weapons, light armor"
    },
    "ranger": {
        "name":         "Ranger",
        "color":        (100, 180, 80),
        "constitution": 0,
        "speed":        +2,
        "stealth":      0,
        "strength":     0,
        "intelligence": +1,
        "description":  "Ranged weapons, light armor"
    },
    "warlock": {
        "name":         "Warlock",
        "color":        (100, 0,   180),
        "constitution": -2,
        "speed":        0,
        "stealth":      0,
        "strength":     -2,
        "intelligence": +5,   # Wizard +3, Warlock +2
        "description":  "Wizard who worships Oraknos"
    },
    "paladin": {
        "name":         "Paladin",
        "color":        (220, 200, 100),
        "constitution": +2,
        "speed":        0,
        "stealth":      -2,
        "strength":     +1,
        "intelligence": +1,   # Knight + Jerry worship
        "description":  "Knight who worships Jerry"
    },
    "druid": {
        "name":         "Druid",
        "color":        (80,  160, 80),
        "constitution": 0,
        "speed":        +2,
        "stealth":      0,
        "strength":     0,
        "intelligence": +2,   # Ranger + Squirrel worship
        "description":  "Ranger who worships A Squirrel"
    },
    "none": {
        "name":         "Adventurer",
        "color":        (0,   200, 255),
        "constitution": 0,
        "speed":        0,
        "stealth":      0,
        "strength":     0,
        "intelligence": 0,
        "description":  "No class yet"
    }
}

# --- GOD DEFINITIONS ---
GODS = {
    "oraknos": {
        "name":        "Oraknos",
        "title":       "The Wise and Unfathomable",
        "color":       (100, 0, 180),
        "unlocks":     "warlock",
        "base_class":  "wizard",
        "description": "God of Magic"
    },
    "thangar": {
        "name":        "Thangar",
        "title":       "Dark Lord of All That Hides in the Shadow",
        "color":       (40,  40,  40),
        "unlocks":     None,          # No multiclass — standalone worship
        "base_class":  None,
        "description": "God of Death"
    },
    "jerry": {
        "name":        "Jerry",
        "title":       "God of Life",
        "color":       (220, 200, 100),
        "unlocks":     "paladin",
        "base_class":  "knight",
        "description": "God of Life"
    },
    "squirrel": {
        "name":        "A Squirrel",
        "title":       "God of Nature",
        "color":       (80,  160, 80),
        "unlocks":     "druid",
        "base_class":  "ranger",
        "description": "God of Nature"
    }
}

# --- WEAPON CLASS REQUIREMENTS ---
# Which weapon types grant which classes
WEAPON_CLASS_MAP = {
    "blunt":   "barbarian",
    "staff":   "wizard",
    "wand":    "wizard",
    "heavy":   "knight",
    "light":   "rogue",
    "ranged":  "ranger"
}

# --- ARMOR CLASS REQUIREMENTS ---
ARMOR_CLASS_MAP = {
    "heavy": ["knight", "paladin"],
    "light": ["rogue", "ranger", "druid"],
    "robe":  ["wizard", "warlock"],
    "none":  ["barbarian"]
}


class PlayerStats:
    def __init__(self):
        # Base stats
        self.base = dict(BASE_STATS)

        # Bonus stats from items (reset when items change)
        self.item_bonus = {k: 0 for k in BASE_STATS}

        # Current class and god
        self.current_class = "none"
        self.worshipped_god = None

        # Gold
        self.gold = 0

        # Mana
        self.mana     = self.get_max_mana()
        self.mana_regen_timer = 0

    # ── stat calculations ─────────────────────────────────────────────
    def get_stat(self, stat_name):
        """Returns final stat value including base, items, and class."""
        base    = self.base.get(stat_name, 1)
        bonus   = self.item_bonus.get(stat_name, 0)
        cls     = CLASS_STATS.get(self.current_class, CLASS_STATS["none"])
        cls_mod = cls.get(stat_name, 0)
        return max(1, base + bonus + cls_mod)

    def get_max_health(self):
        con = self.get_stat("constitution")
        return 10 + con * STAT_EFFECTS["constitution"]["health_per_point"]

    def get_speed(self):
        spd = self.get_stat("speed")
        return 3 + spd * STAT_EFFECTS["speed"]["speed_per_point"]

    def get_detection_reduction(self):
        ste = self.get_stat("stealth")
        return ste * STAT_EFFECTS["stealth"]["detection_reduction_per_point"]

    def get_melee_damage(self):
        str_ = self.get_stat("strength")
        return 1 + (str_ - 1) * STAT_EFFECTS["strength"]["damage_per_point"]

    def get_max_mana(self):
        intel = self.get_stat("intelligence")
        return intel * STAT_EFFECTS["intelligence"]["mana_per_point"]

    def get_mana_regen(self):
        intel = self.get_stat("intelligence")
        return intel * STAT_EFFECTS["intelligence"]["regen_per_point"]

    # ── mana ──────────────────────────────────────────────────────────
    def update_mana(self):
        """Call once per frame to regenerate mana."""
        max_mana = self.get_max_mana()
        if self.mana < max_mana:
            self.mana_regen_timer += 1
            # Regen speed scales with intelligence
            regen_interval = max(10, int(60 / max(0.1,
                self.get_mana_regen())))
            if self.mana_regen_timer >= regen_interval:
                self.mana = min(self.mana + 1, max_mana)
                self.mana_regen_timer = 0

    def spend_mana(self, amount):
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def restore_mana(self):
        self.mana = self.get_max_mana()

    # ── class management ──────────────────────────────────────────────
    def determine_class(self, equipped_weapon, equipped_armor,
                        worshipped_god):
        """
        Called whenever the player equips or unequips something.
        Determines the correct class based on gear and god.
        """
        self.worshipped_god = worshipped_god
        weapon_class = None
        armor_class  = None

        if equipped_weapon:
            weapon_class = WEAPON_CLASS_MAP.get(
                equipped_weapon.weapon_type)

        if equipped_armor:
            armor_type  = equipped_armor.armor_type
            valid_classes = ARMOR_CLASS_MAP.get(armor_type, [])
            if weapon_class in valid_classes:
                armor_class = weapon_class

        # Base class from weapon
        base_class = weapon_class or "none"

        # Check for multiclass upgrade
        if worshipped_god:
            god_data = GODS.get(worshipped_god)
            if god_data and god_data["unlocks"]:
                required_base = god_data["base_class"]
                if base_class == required_base:
                    base_class = god_data["unlocks"]

        self.current_class = base_class

    def apply_item_bonuses(self, items):
        """Recalculate item bonuses from all equipped items."""
        self.item_bonus = {k: 0 for k in BASE_STATS}
        for item in items:
            if hasattr(item, "stat_bonuses"):
                for stat, val in item.stat_bonuses.items():
                    if stat in self.item_bonus:
                        self.item_bonus[stat] += val

    # ── gold ──────────────────────────────────────────────────────────
    def add_gold(self, amount):
        self.gold += amount

    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def on_death(self):
        """Lose 75% of gold on death."""
        self.gold = int(self.gold * 0.25)

    # ── heal ──────────────────────────────────────────────────────────
    def full_heal(self):
        """Used at temples."""
        self.restore_mana()
        return self.get_max_health()

    # ── display ───────────────────────────────────────────────────────
    def get_class_info(self):
        return CLASS_STATS.get(
            self.current_class, CLASS_STATS["none"])

    def draw_stats_hud(self, screen, font):
        """Draw stats panel in top left under health/mana bars."""
        cls_info = self.get_class_info()
        color    = cls_info["color"]

        # Class name
        screen.blit(font.render(
            f"Class: {cls_info['name']}", True, color),
            (20, 155))

        # Gold
        screen.blit(font.render(
            f"Gold: {self.gold}", True, (255, 215, 0)),
            (20, 177))

        # Stats
        stats = [
            ("CON", "constitution"),
            ("SPD", "speed"),
            ("STL", "stealth"),
            ("STR", "strength"),
            ("INT", "intelligence"),
        ]
        for i, (label, key) in enumerate(stats):
            val = self.get_stat(key)
            screen.blit(font.render(
                f"{label}: {val}", True, (200, 200, 200)),
                (20, 199 + i * 20))