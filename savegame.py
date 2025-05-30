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
            "hp": wall.hp,
            "type": getattr(wall, "type", "wood")
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

    @staticmethod
    def serialize_spike(spike):
        return {
            "x": spike.x,
            "y": spike.y,
            "hp": spike.hp
        }

    @staticmethod
    def serialize_turret(turret):
        return {
            "x": turret.x,
            "y": turret.y,
            "hp": turret.hp,
            "cooldown": getattr(turret, "cooldown", 0)
        }

    @staticmethod
    def serialize_door(door):
        return {
            "x": door.x,
            "y": door.y,
            "hp": door.hp,
            "open": getattr(door, "open", False)
        }

    @staticmethod
    def serialize_trap_pit(trap_pit):
        return {
            "x": trap_pit.x,
            "y": trap_pit.y,
            "hp": trap_pit.hp
        }

    @staticmethod
    def serialize_workbench(workbench):
        return {
            "x": workbench.x,
            "y": workbench.y,
            "hp": workbench.hp,
            "in_use": workbench.in_use,
            "craft_timer": workbench.craft_timer
        }

    @staticmethod
    def serialize_campfire(campfire):
        return {
            "x": campfire.x,
            "y": campfire.y,
            "hp": campfire.hp,
            "lit": campfire.lit,
            "fuel": campfire.fuel
        }

    @classmethod
    def save(cls, colonist, zombies, walls, trees, wood, rocks=None, stone=0,
             xp=0, level=1, skill_points=0, xp_to_next=10, unlocked_blueprints=None, selected_blueprint_idx=0,
             spikes=None, turrets=None, doors=None, floors=None, trap_pits=None, workbenches=None, campfires=None):
        try:
            data = {
                "colonist": cls.serialize_colonist(colonist),
                "zombies": [cls.serialize_zombie(z) for z in zombies],
                "walls": [cls.serialize_wall(w) for w in walls],
                "trees": [cls.serialize_tree(t) for t in trees],
                "rocks": [cls.serialize_rock(r) for r in (rocks or [])],
                "spikes": [cls.serialize_spike(s) for s in (spikes or [])],
                "turrets": [cls.serialize_turret(t) for t in (turrets or [])],
                "doors": [cls.serialize_door(d) for d in (doors or [])],
                "trap_pits": [cls.serialize_trap_pit(tp) for tp in (trap_pits or [])],
                "workbenches": [cls.serialize_workbench(wb) for wb in (workbenches or [])],
                "campfires": [cls.serialize_campfire(cf) for cf in (campfires or [])],
                "floors": list(floors or []),
                "wood": wood,
                "stone": stone,
                "xp": xp,
                "level": level,
                "skill_points": skill_points,
                "xp_to_next": xp_to_next,
                "unlocked_blueprints": list(unlocked_blueprints) if unlocked_blueprints else [],
                "selected_blueprint_idx": selected_blueprint_idx
            }
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=2)
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
def save_game(colonist, zombies, walls, trees, wood, rocks=None, stone=0,
              xp=0, level=1, skill_points=0, xp_to_next=10, unlocked_blueprints=None, selected_blueprint_idx=0,
              spikes=None, turrets=None, doors=None, floors=None, trap_pits=None, workbenches=None, campfires=None):
    return SaveGame.save(colonist, zombies, walls, trees, wood, rocks, stone,
                         xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx,
                         spikes, turrets, doors, floors, trap_pits, workbenches, campfires)

def load_game():
    return SaveGame.load()
