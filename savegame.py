import os
import json

SAVE_FILE = os.path.join(os.path.dirname(__file__), "savegame.json")

class SaveGame:
    @staticmethod
    def serialize_colonist(colonist):
        return {
            "x": colonist.x,
            "y": colonist.y,
            "hp": colonist.hp,
            "facing": tuple(colonist.facing)
        }

    @staticmethod
    def serialize_zombie(zombie):
        return {
            "x": zombie.x,
            "y": zombie.y,
            "hp": zombie.hp,
            "facing": tuple(getattr(zombie, "facing", (0, 1)))
        }

    @staticmethod
    def serialize_wall(wall):
        return {
            "x": wall.x,
            "y": wall.y,
            "hp": wall.hp
        }

    @staticmethod
    def serialize_tree(tree):
        return {
            "x": tree.x,
            "y": tree.y,
            "cut_down": getattr(tree, "cut_down", False)
        }

    @staticmethod
    def serialize_rock(rock):
        return {
            "x": rock.x,
            "y": rock.y,
            "mined": getattr(rock, "mined", False)
        }

    @classmethod
    def save(cls, colonist, zombies, walls, trees, wood, rocks=None, stone=0):
        try:
            data = {
                "colonist": cls.serialize_colonist(colonist),
                "zombies": [cls.serialize_zombie(z) for z in zombies],
                "walls": [cls.serialize_wall(w) for w in walls],
                "trees": [cls.serialize_tree(t) for t in trees],
                "rocks": [cls.serialize_rock(r) for r in (rocks or [])],
                "wood": wood,
                "stone": stone
            }
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    @classmethod
    def load(cls):
        if not os.path.exists(SAVE_FILE):
            print("No save file found.")
            return None
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            # Validate essential fields
            if "colonist" not in data or "zombies" not in data or "walls" not in data or "trees" not in data:
                print("Save file is missing required data.")
                return None
            return data
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None

# For backward compatibility with existing code
def save_game(colonist, zombies, walls, trees, wood, rocks=None, stone=0):
    return SaveGame.save(colonist, zombies, walls, trees, wood, rocks, stone)

def load_game():
    return SaveGame.load()
