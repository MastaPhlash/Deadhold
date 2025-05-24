import pygame
import random
from entities import Colonist, Zombie, Wall, Tree, Rock, Spike, Turret, Bullet
from hud import draw_hud
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

try:
    from savegame import save_game, load_game
except ImportError:
    import importlib.util
    savegame_path = os.path.join(os.path.dirname(__file__), "savegame.py")
    spec = importlib.util.spec_from_file_location("savegame", savegame_path)
    savegame = importlib.util.module_from_spec(spec)
    sys.modules["savegame"] = savegame
    spec.loader.exec_module(savegame)
    save_game = savegame.save_game
    load_game = savegame.load_game

# Game settings
TILE_SIZE = 64
MAP_WIDTH = 200
MAP_HEIGHT = 150
SCREEN_WIDTH = TILE_SIZE * 15
SCREEN_HEIGHT = TILE_SIZE * 10
FPS = 5

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (50, 50, 50)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deadhold Prototype")
clock = pygame.time.Clock()

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
def load_image(filename):
    path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
        return img
    except Exception:
        return None

grass_img = load_image("grass.png")

# --- Modular: Blueprints ---
def get_all_blueprints():
    return [
        {"name": "wood_wall", "display": "Wood Wall", "img": "wall.png", "cost": {"wood": 1}, "required": set()},
        {"name": "stone_wall", "display": "Stone Wall", "img": "stone_wall.png", "cost": {"stone": 2}, "required": {"wood_wall"}},
        {"name": "spike", "display": "Spike Trap", "img": "spike.png", "cost": {"wood": 2, "stone": 1}, "required": {"wood_wall"}},
        {"name": "turret", "display": "Turret", "img": "turret.png", "cost": {"stone": 5}, "required": {"spike"}},
    ]

def get_unlocked_blueprints(all_blueprints, unlocked_set):
    return [bp for bp in all_blueprints if bp["name"] in unlocked_set]

# --- Modular: XP/Level System ---
def gain_xp(xp, amount):
    return xp + amount

def check_level_up(xp, level, skill_points, xp_to_next):
    leveled = False
    while xp >= xp_to_next:
        xp -= xp_to_next
        level += 1
        skill_points += 1
        xp_to_next = int(xp_to_next * 1.5)
        leveled = True
    return xp, level, skill_points, xp_to_next, leveled

# --- Modular: Impassable Tiles ---
def get_impassable(trees, rocks):
    return [t for t in trees if not t.cut_down] + [r for r in rocks if not r.mined]

# --- Modular: Save/Load State ---
def get_game_state(colonist, zombies, walls, trees, wood, rocks, stone, xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx):
    return {
        "colonist": colonist,
        "zombies": zombies,
        "walls": walls,
        "trees": trees,
        "wood": wood,
        "rocks": rocks,
        "stone": stone,
        "xp": xp,
        "level": level,
        "skill_points": skill_points,
        "xp_to_next": xp_to_next,
        "unlocked_blueprints": list(unlocked_blueprints),
        "selected_blueprint_idx": selected_blueprint_idx
    }

def set_game_state(data, all_blueprints):
    colonist = Colonist(data["colonist"]["x"], data["colonist"]["y"])
    colonist.hp = data["colonist"]["hp"]
    colonist.facing = tuple(data["colonist"].get("facing", (0, -1)))
    zombies = []
    for z in data["zombies"]:
        zombie = Zombie(z["x"], z["y"])
        zombie.hp = z["hp"]
        zombie.facing = tuple(z.get("facing", (0, 1)))
        zombies.append(zombie)
    walls = []
    for w in data["walls"]:
        wall_type = w.get("type", "wood")
        wall = Wall(w["x"], w["y"], wall_type=wall_type)
        wall.hp = w["hp"]
        walls.append(wall)
    trees = []
    for t in data["trees"]:
        tree = Tree(t["x"], t["y"])
        tree.cut_down = t.get("cut_down", False)
        trees.append(tree)
    rocks = []
    for r in data.get("rocks", []):
        rock = Rock(r["x"], r["y"])
        rock.mined = r.get("mined", False)
        rocks.append(rock)
    spikes = []
    for s in data.get("spikes", []):
        spike = Spike(s["x"], s["y"])
        spike.hp = s.get("hp", 1)
        spikes.append(spike)
    turrets = []
    for t in data.get("turrets", []):
        turret = Turret(t["x"], t["y"])
        turret.hp = t.get("hp", 1)
        turret.cooldown = t.get("cooldown", 0)
        turrets.append(turret)
    wood = data.get("wood", 0)
    stone = data.get("stone", 0)
    xp = data.get("xp", 0)
    level = data.get("level", 1)
    skill_points = data.get("skill_points", 0)
    xp_to_next = data.get("xp_to_next", 10)
    unlocked_blueprints = set(data.get("unlocked_blueprints", ["wood_wall"]))
    selected_blueprint_idx = data.get("selected_blueprint_idx", 0)
    return colonist, zombies, walls, trees, wood, rocks, stone, xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx

def main():
    colonist = Colonist(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    zombies = [Zombie(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(10)]
    walls = []
    trees = []
    rocks = []
    spikes = []
    turrets = []
    bullets = []
    wood = 5
    stone = 0
    ticks = 0
    MINUTES_PER_STEP = 15
    TICKS_PER_STEP = FPS * 2
    TOTAL_STEPS = 24 * 60 // MINUTES_PER_STEP
    current_step = (6 * 60) // MINUTES_PER_STEP

    # Place rocks
    for _ in range(600):
        for _ in range(20):
            rx = random.randint(0, MAP_WIDTH-1)
            ry = random.randint(0, MAP_HEIGHT-1)
            if (abs(rx - colonist.x) > 2 or abs(ry - colonist.y) > 2) and not any(r.x == rx and r.y == ry for r in rocks):
                rocks.append(Rock(rx, ry))
                break

    # Place trees
    for _ in range(600):
        for _ in range(20):
            tx = random.randint(0, MAP_WIDTH-1)
            ty = random.randint(0, MAP_HEIGHT-1)
            if (abs(tx - colonist.x) > 2 or abs(ty - colonist.y) > 2) and not any(t.x == tx and t.y == ty for t in trees) and not any(r.x == tx and r.y == ty for r in rocks):
                trees.append(Tree(tx, ty))
                break

    # XP/Research system
    xp = 0
    level = 1
    skill_points = 0
    xp_to_next = 10
    unlocked_blueprints = {"wood_wall"}
    all_blueprints = get_all_blueprints()
    research_menu = False
    selected_blueprint_idx = 0

    last_tree_cut = set()
    last_rock_mined = set()
    last_zombie_killed = set()
    last_build_positions = set()

    # Zombie wave system
    day_count = 1
    wave_timer = 0
    WAVE_INTERVAL = FPS * 60 * 2  # Every 2 minutes (adjust as needed)
    zombies_per_wave = 5

    running = True
    while running:
        ticks += 1
        if ticks % TICKS_PER_STEP == 0:
            current_step = (current_step + 1) % TOTAL_STEPS

        # Calculate hour and minute
        hour = (current_step * MINUTES_PER_STEP) // 60
        minute = (current_step * MINUTES_PER_STEP) % 60
        is_night = not (6 <= hour < 21)
        impassable = get_impassable(trees, rocks)

        # --- Zombie wave timer ---
        wave_timer += 1
        # New day detection (at 6:00)
        if hour == 6 and minute == 0 and ticks % TICKS_PER_STEP == 0:
            day_count += 1
            # Optionally, spawn a wave at the start of each day
            for _ in range(zombies_per_wave + day_count - 1):
                zx, zy = random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)
                zombies.append(Zombie(zx, zy))
        # Timed wave spawn
        if wave_timer >= WAVE_INTERVAL:
            wave_timer = 0
            for _ in range(zombies_per_wave + day_count - 1):
                zx, zy = random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)
                zombies.append(Zombie(zx, zy))

        # --- Modular: Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if research_menu:
                    research_menu = False
                else:
                    running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                research_menu = not research_menu
            if research_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_blueprint_idx = (selected_blueprint_idx - 1) % len(all_blueprints)
                    if event.key == pygame.K_DOWN:
                        selected_blueprint_idx = (selected_blueprint_idx + 1) % len(all_blueprints)
                    if event.key == pygame.K_RETURN:
                        bp = all_blueprints[selected_blueprint_idx]
                        if bp["name"] not in unlocked_blueprints and bp["required"].issubset(unlocked_blueprints) and skill_points > 0:
                            unlocked_blueprints.add(bp["name"])
                            skill_points -= 1
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
                    selected_blueprint_idx = (selected_blueprint_idx + 1) % len(unlocked_list)
                # --- Unified build button: always builds the item in the HUD ---
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
                    if unlocked_list:
                        bp = unlocked_list[selected_blueprint_idx % len(unlocked_list)]
                        can_build = all((wood if res == "wood" else stone) >= amt for res, amt in bp["cost"].items())
                        build_pos = (colonist.x, colonist.y, bp["name"])
                        # Prevent building on top of other buildables
                        blocked = any(w.x == colonist.x and w.y == colonist.y for w in walls) \
                                  or any(t.x == colonist.x and t.y == colonist.y for t in trees) \
                                  or any(s.x == colonist.x and s.y == colonist.y for s in spikes) \
                                  or any(tu.x == colonist.x and tu.y == colonist.y for tu in turrets)
                        if can_build and not blocked:
                            if bp["name"] == "wood_wall":
                                walls.append(Wall(colonist.x, colonist.y, wall_type="wood"))
                            elif bp["name"] == "stone_wall":
                                walls.append(Wall(colonist.x, colonist.y, wall_type="stone"))
                            elif bp["name"] == "spike":
                                spikes.append(Spike(colonist.x, colonist.y))
                            elif bp["name"] == "turret":
                                turrets.append(Turret(colonist.x, colonist.y))
                            if "wood" in bp["cost"]:
                                wood -= bp["cost"]["wood"]
                            if "stone" in bp["cost"]:
                                stone -= bp["cost"]["stone"]
                            if build_pos not in last_build_positions:
                                xp += 1
                                last_build_positions.add(build_pos)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    fx, fy = colonist.facing
                    target_x = colonist.x + fx
                    target_y = colonist.y + fy
                    attacked = False
                    # Attack zombie
                    for zombie in zombies:
                        if zombie.x == target_x and zombie.y == target_y and zombie.hp > 0:
                            zombie.hp -= 50
                            attacked = True
                            # XP for killing zombie will be handled below when zombie is removed
                            break
                    # Attack tree (get wood)
                    if not attacked:
                        for tree in trees:
                            if tree.x == target_x and tree.y == target_y and not tree.cut_down:
                                wood += tree.cut()
                                attacked = True
                                if (tree.x, tree.y) not in last_tree_cut:
                                    xp += 1
                                    last_tree_cut.add((tree.x, tree.y))
                                break
                    # Attack rock (get stone)
                    if not attacked:
                        for rock in rocks:
                            if rock.x == target_x and rock.y == target_y and not rock.mined:
                                stone += rock.mine()
                                if (rock.x, rock.y) not in last_rock_mined:
                                    xp += 1
                                    last_rock_mined.add((rock.x, rock.y))
                                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                # Save all state
                state = get_game_state(
                    colonist, zombies, walls, trees, wood, rocks, stone,
                    xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx
                )
                save_game(**state)
                print("Game saved.")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                data = load_game()
                if data:
                    colonist, zombies, walls, trees, wood, rocks, stone, xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx = set_game_state(data, all_blueprints)
                    print("Game loaded.")
                else:
                    print("No save file found.")

        if research_menu:
            screen.fill((30, 30, 60))
            font = pygame.font.SysFont(None, 36)
            title = font.render("Research Menu", True, (255, 255, 0))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
            font2 = pygame.font.SysFont(None, 28)
            y = 80
            for idx, bp in enumerate(all_blueprints):
                unlocked = bp["name"] in unlocked_blueprints
                prereq_met = bp["required"].issubset(unlocked_blueprints)
                color = (180, 255, 180) if unlocked else ((255, 255, 255) if prereq_met and skill_points > 0 else (120, 120, 120))
                prefix = "-> " if idx == selected_blueprint_idx else "   "
                line = f"{prefix}{bp['display']} ({'Unlocked' if unlocked else 'Locked'})"
                text = font2.render(line, True, color)
                screen.blit(text, (80, y))
                y += 36
                if idx == selected_blueprint_idx:
                    cost_str = "Cost: " + ", ".join(f"{k}:{v}" for k, v in bp["cost"].items())
                    prereq_str = "Requires: " + (", ".join(allb['display'] for allb in all_blueprints if allb["name"] in bp["required"]) if bp["required"] else "None")
                    screen.blit(font2.render(cost_str, True, (200, 200, 0)), (100, y))
                    y += 28
                    screen.blit(font2.render(prereq_str, True, (200, 200, 0)), (100, y))
                    y += 28
                    img = load_image(bp["img"])
                    if img:
                        screen.blit(img, (SCREEN_WIDTH - 120, 100))
            sp_text = font2.render(f"Skill Points: {skill_points}", True, (255, 255, 0))
            screen.blit(sp_text, (80, 50))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # Movement (only trees/rocks block)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            colonist.move(0, -1, [], impassable)
        if keys[pygame.K_DOWN]:
            colonist.move(0, 1, [], impassable)
        if keys[pygame.K_LEFT]:
            colonist.move(-1, 0, [], impassable)
        if keys[pygame.K_RIGHT]:
            colonist.move(1, 0, [], impassable)

        # --- Turret logic: fire at nearest zombie if in range ---
        for turret in turrets:
            if turret.hp <= 0:
                continue
            if turret.cooldown > 0:
                turret.cooldown -= 1
                continue
            # Find nearest zombie in range (range = 5 tiles)
            min_dist = 999
            target_z = None
            for z in zombies:
                dist = abs(z.x - turret.x) + abs(z.y - turret.y)
                if dist <= 5 and dist < min_dist and z.hp > 0:
                    min_dist = dist
                    target_z = z
            if target_z:
                dx = target_z.x - turret.x
                dy = target_z.y - turret.y
                # Normalize direction
                if abs(dx) > abs(dy):
                    dx = 1 if dx > 0 else -1
                    dy = 0
                else:
                    dy = 1 if dy > 0 else -1
                    dx = 0
                bullets.append(Bullet(turret.x, turret.y, dx, dy))
                turret.cooldown = 10  # Fire every 10 frames

        # --- Bullet logic ---
        for bullet in bullets[:]:
            bullet.update()
            # Remove bullet if out of bounds or after 20 steps
            if bullet.x < 0 or bullet.y < 0 or bullet.x >= MAP_WIDTH or bullet.y >= MAP_HEIGHT or bullet.timer > 20:
                bullets.remove(bullet)
                continue
            # Hit zombie
            for z in zombies:
                if z.x == bullet.x and z.y == bullet.y and z.hp > 0:
                    z.hp -= 50
                    bullets.remove(bullet)
                    break

        # --- Spike logic: damage zombies standing on spikes ---
        for spike in spikes:
            for z in zombies:
                if z.x == spike.x and z.y == spike.y and z.hp > 0:
                    z.hp -= 10  # Damage per frame on spike

        # Update zombies
        for zombie in zombies:
            zombie.update(colonist, walls + impassable + spikes + turrets)
            if zombie.x == colonist.x and zombie.y == colonist.y:
                colonist.hp -= 1

        # Remove dead zombies, destroyed walls, cut trees, mined rocks, destroyed spikes/turrets
        zombies_to_remove = [z for z in zombies if z.hp <= 0]
        for zombie in zombies_to_remove:
            if (zombie.x, zombie.y) not in last_zombie_killed:
                xp += 5
                last_zombie_killed.add((zombie.x, zombie.y))
        zombies = [z for z in zombies if z.hp > 0]
        walls = [w for w in walls if w.hp > 0]
        spikes = [s for s in spikes if s.hp > 0]
        turrets = [t for t in turrets if t.hp > 0]
        trees = [t for t in trees if not t.cut_down]
        rocks = [r for r in rocks if not r.mined]

        # XP for actions
        for tree in trees:
            if tree.cut_down and not hasattr(tree, "_xp_given"):
                xp += 1
                tree._xp_given = True
        for rock in rocks:
            if rock.mined and not hasattr(rock, "_xp_given"):
                xp += 1
                rock._xp_given = True
        for zombie in zombies:
            if zombie.hp <= 0 and not hasattr(zombie, "_xp_given"):
                xp += 2
                zombie._xp_given = True

        # XP for killing zombies (only once per zombie, now 5 XP per kill)
        for zombie in zombies:
            if zombie.hp <= 0 and (zombie.x, zombie.y) not in last_zombie_killed:
                xp += 5
                last_zombie_killed.add((zombie.x, zombie.y))

        # Level up
        xp, level, skill_points, xp_to_next, _ = check_level_up(xp, level, skill_points, xp_to_next)

        # Camera scroll
        cam_x = colonist.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        cam_y = colonist.y * TILE_SIZE - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        cam_x = max(0, min(cam_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        cam_y = max(0, min(cam_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

        # Draw
        screen.fill((50, 50, 50))
        for x in range(SCREEN_WIDTH // TILE_SIZE):
            for y in range(SCREEN_HEIGHT // TILE_SIZE):
                wx = x + cam_x // TILE_SIZE
                wy = y + cam_y // TILE_SIZE
                if 0 <= wx < MAP_WIDTH and 0 <= wy < MAP_HEIGHT:
                    if grass_img:
                        screen.blit(grass_img, (x*TILE_SIZE, y*TILE_SIZE))
                    else:
                        pygame.draw.rect(screen, (34, 139, 34), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        for rock in rocks:
            rock.draw(screen, cam_x, cam_y)
        for wall in walls:
            wall.draw(screen, cam_x, cam_y)
        for spike in spikes:
            spike.draw(screen, cam_x, cam_y)
        for turret in turrets:
            turret.draw(screen, cam_x, cam_y)
        for bullet in bullets:
            bullet.draw(screen, cam_x, cam_y)
        for tree in trees:
            covered = (tree.x == colonist.x and tree.y - 1 == colonist.y) or any(tree.x == z.x and tree.y - 1 == z.y for z in zombies)
            if not covered:
                tree.draw(screen, cam_x, cam_y)
        colonist.draw(screen, cam_x, cam_y)
        for zombie in zombies:
            zombie.draw(screen, cam_x, cam_y)
        for tree in trees:
            covered = (tree.x == colonist.x and tree.y - 1 == colonist.y) or any(tree.x == z.x and tree.y - 1 == z.y for z in zombies)
            if covered:
                tree.draw(screen, cam_x, cam_y)

        # Build preview in HUD
        build_img = None
        if not research_menu:
            unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
            if unlocked_list:
                bp = unlocked_list[selected_blueprint_idx % len(unlocked_list)]
                img = load_image(bp["img"])
                if img:
                    build_img = img.copy()

        draw_hud(screen, colonist, wood, stone, build_img)
        font = pygame.font.SysFont(None, 28)
        xp_text = font.render(f"XP: {xp}/{xp_to_next}  Level: {level}  SP: {skill_points}", True, (0, 255, 255))
        screen.blit(xp_text, (10, 35))
        day_text = font.render(f"Day: {day_count}", True, (255, 255, 255))
        screen.blit(day_text, (10, 65))

        # Night overlay
        if is_night:
            night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            night_overlay.fill((0, 0, 40, 120))
            screen.blit(night_overlay, (0, 0))

        font = pygame.font.SysFont(None, 32)
        dn_text = font.render("Night" if is_night else "Day", True, (200, 200, 255) if is_night else (255, 255, 0))
        screen.blit(dn_text, (SCREEN_WIDTH - 110, 5))
        clock_str = f"{hour:02d}:{minute:02d}"
        clock_text = font.render(clock_str, True, (255, 255, 255))
        screen.blit(clock_text, (SCREEN_WIDTH // 2 - clock_text.get_width() // 2, 5))

        pygame.display.flip()
        clock.tick(FPS)

        if colonist.hp <= 0:
            print("Colonist died!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
