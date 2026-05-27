import json
import os

# Save file location
SAVE_DIR  = os.path.join(
    os.path.dirname(__file__), "..", "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "savegame.json")


def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def save_game(player, floor_manager):
    """Save current game state to disk."""
    ensure_save_dir()

    data = {
        "version":      1,
        "floor":        floor_manager.current_floor,
        "family": {
            str(k): v for k, v in
            floor_manager.family.items()
        },
        "player": {
            "health":       player.health,
            "max_health":   player.max_health,
            "base_stats":   player.stats.base,
            "item_bonus":   player.stats.item_bonus,
            "gold":         player.stats.gold,
            "mana":         player.stats.mana,
            "worshipped_god":
                player.stats.worshipped_god,
            "current_class":
                player.stats.current_class,
        }
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return True


def load_game():
    """
    Load saved game state from disk.
    Returns the save data dict or None if no save exists.
    """
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        # Validate version
        if data.get("version") != 1:
            return None
        return data
    except (json.JSONDecodeError, KeyError):
        return None


def delete_save():
    """Delete the save file — called on a fresh new game."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def save_exists():
    """Returns True if a valid save file exists."""
    return os.path.exists(SAVE_FILE) and \
           load_game() is not None


def apply_save(data, player, floor_manager):
    """
    Apply loaded save data to player and floor manager.
    Call this after creating a fresh player and floor.
    """
    # Floor manager
    floor_manager.current_floor = data["floor"]
    for k, v in data["family"].items():
        floor_manager.family[int(k)] = v

    # Player stats
    pd = data["player"]
    player.stats.base          = pd["base_stats"]
    player.stats.item_bonus    = pd["item_bonus"]
    player.stats.gold          = pd["gold"]
    player.stats.mana          = pd["mana"]
    player.stats.worshipped_god = pd.get("worshipped_god")
    player.stats.current_class  = pd.get(
        "current_class", "none")

    # Health
    player.max_health = player.stats.get_max_health()
    player.health     = min(pd["health"], player.max_health)

    return player, floor_manager