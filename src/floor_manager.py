# --- FAMILY MEMBERS ---
FAMILY = {
    3:  {"name": "Son",   "rescued": False},
    6:  {"name": "Daughter", "rescued": False},
    9:  {"name": "Wife",  "rescued": False},
}

# --- ENEMY SCALING PER FLOOR ---
# Each entry is (enemy_count, health_multiplier, speed_multiplier)
FLOOR_SCALING = {
    1:  (3,  1.0, 1.0),
    2:  (3,  1.0, 1.0),
    3:  (4,  1.2, 1.0),
    4:  (4,  1.2, 1.1),
    5:  (4,  1.4, 1.1),
    6:  (5,  1.4, 1.2),
    7:  (5,  1.6, 1.2),
    8:  (5,  1.8, 1.3),
    9:  (6,  1.8, 1.3),
    10: (6,  2.0, 1.4),
    11: (7,  2.2, 1.5),
    12: (8,  2.5, 1.6),
}

class FloorManager:
    def __init__(self):
        self.current_floor  = 1
        self.family         = {k: dict(v) for k, v in FAMILY.items()}
        self.game_won       = False
        self.bb_defeated    = False

    def get_scaling(self):
        return FLOOR_SCALING.get(
            self.current_floor, FLOOR_SCALING[12])

    def get_enemy_count(self):
        return self.get_scaling()[0]

    def get_health_multiplier(self):
        return self.get_scaling()[1]

    def get_speed_multiplier(self):
        return self.get_scaling()[2]

    def advance_floor(self):
        if self.current_floor < 12:
            self.current_floor += 1
            return True
        return False

    def try_rescue(self, floor_number):
        """
        Call when player enters a rescue room.
        Returns the rescued family member's name or None.
        """
        if floor_number in self.family:
            member = self.family[floor_number]
            if not member["rescued"]:
                member["rescued"] = True
                return member["name"]
        return None

    def get_rescued(self):
        return [m["name"] for m in self.family.values()
                if m["rescued"]]

    def all_rescued(self):
        return all(m["rescued"] for m in self.family.values())

    def check_win(self):
        return self.bb_defeated

    def reset(self):
        self.current_floor = 1
        self.family        = {k: dict(v) for k, v in FAMILY.items()}
        self.game_won      = False
        self.bb_defeated   = False