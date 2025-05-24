import json
import os

SAVE_FILE = os.path.join(os.path.dirname(__file__), "savegame.json")

def save_game(colonist, zombies, walls, trees, wood):
    data = {
        "colonist": {
            "x": colonist.x,
            "y": colonist.y,
            "hp": colonist.hp,
            "facing": colonist.facing
        },
        "zombies": [
            {"x": z.x, "y": z.y, "hp": z.hp, "facing": z.facing}
            for z in zombies
        ],
        "walls": [
            {"x": w.x, "y": w.y, "hp": w.hp}
            for w in walls
        ],
        "trees": [
            {"x": t.x, "y": t.y, "cut_down": t.cut_down}
            for t in trees
        ],
        "wood": wood
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    return data
