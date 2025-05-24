import pygame
import random
from entities import Colonist, Zombie, Wall, Tree, Rock, Spike, Turret, Bullet, Door
from hud import draw_hud
from game_systems import (MapGenerator, TimeSystem, WaveSystem, ExperienceSystem, 
                         CombatSystem, MinimapSystem, ConstructionPlanningSystem, 
                         JobSystem, GameStatistics)
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
floor_img = load_image("floor.png")

# --- Modular: Blueprints ---
def get_all_blueprints():
    return [
        {"name": "wood_wall", "display": "Wood Wall", "img": "wall.png", "cost": {"wood": 1}, "required": set()},
        {"name": "stone_wall", "display": "Stone Wall", "img": "stone_wall.png", "cost": {"stone": 2}, "required": set()},
        {"name": "spike", "display": "Spike Trap", "img": "spike.png", "cost": {"wood": 2, "stone": 1}, "required": set()},
        {"name": "turret", "display": "Turret", "img": "turret.png", "cost": {"stone": 5}, "required": set()},
        {"name": "door", "display": "Door", "img": "door.png", "cost": {"wood": 2}, "required": set()},
        {"name": "campfire", "display": "Campfire", "img": "campfire.png", "cost": {"wood": 1, "stone": 1}, "required": set()},
        {"name": "workbench", "display": "Workbench", "img": "workbench.png", "cost": {"wood": 3}, "required": set()},
        {"name": "trap_pit", "display": "Trap Pit", "img": "trap_pit.png", "cost": {"stone": 3}, "required": set()},
    ]

def get_unlocked_blueprints(all_blueprints, unlocked_set):
    return [bp for bp in all_blueprints if bp["name"] in unlocked_set]

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
    doors = []
    for d in data.get("doors", []):
        door = Door(d["x"], d["y"])
        door.hp = d.get("hp", 1)
        door.open = d.get("open", False)
        doors.append(door)
    wood = data.get("wood", 5)  # Default to 5 if not present
    stone = data.get("stone", 0)
    xp = data.get("xp", 0)
    level = data.get("level", 1)
    skill_points = data.get("skill_points", 0)
    xp_to_next = data.get("xp_to_next", 10)
    unlocked_blueprints = set(data.get("unlocked_blueprints", ["wood_wall"]))
    selected_blueprint_idx = data.get("selected_blueprint_idx", 0)
    return colonist, zombies, walls, trees, wood, rocks, stone, xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx

def main():
    # Initialize game objects
    colonist = Colonist(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    zombies = [Zombie(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(10)]
    
    # Initialize game systems
    time_system = TimeSystem()
    wave_system = WaveSystem(FPS)
    minimap = MinimapSystem()
    construction_planner = ConstructionPlanningSystem()
    job_system = JobSystem()
    stats = GameStatistics()
    
    minimap.initialize(MAP_WIDTH, MAP_HEIGHT)
    
    # Generate world
    walls, doors, floors = MapGenerator.generate_buildings(MAP_WIDTH, MAP_HEIGHT)
    trees, rocks = MapGenerator.generate_resources(MAP_WIDTH, MAP_HEIGHT, walls, doors, floors)
    
    # Initialize other game objects
    spikes = []
    turrets = []
    bullets = []
    wood = 5
    stone = 0
    
    # UI state
    show_stats = False
    pause_game = False
    auto_save_timer = 0
    AUTO_SAVE_INTERVAL = FPS * 300  # Auto-save every 5 minutes
    
    # XP/Research system
    xp = 0
    level = 1
    skill_points = 0
    xp_to_next = 10
    unlocked_blueprints = {"wood_wall"}
    all_blueprints = get_all_blueprints()
    research_menu = False
    selected_blueprint_idx = 0

    # Tracking sets for XP
    last_tree_cut = set()
    last_rock_mined = set()
    last_zombie_killed = set()
    last_build_positions = set()

    running = True
    
    while running:
        if not pause_game:
            # Update game systems
            time_system.update()
            
            # Auto-save
            auto_save_timer += 1
            if auto_save_timer >= AUTO_SAVE_INTERVAL:
                auto_save_timer = 0
                # Auto-save logic here
                print("Auto-saving...")
            
            # Zombie wave spawning
            new_zombies = wave_system.update(time_system)
            for _ in range(new_zombies):
                zx, zy = random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)
                zombies.append(Zombie(zx, zy))

        hour, minute = time_system.get_time()
        is_night = time_system.is_night()
        impassable = [t for t in trees if not t.cut_down] + [r for r in rocks if not r.mined]

        # Event handling with QoL improvements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Quality of Life hotkeys
                if event.key == pygame.K_p:  # Pause
                    pause_game = not pause_game
                elif event.key == pygame.K_TAB and pygame.key.get_pressed()[pygame.K_LSHIFT]:  # Shift+Tab for stats
                    show_stats = not show_stats
                elif event.key == pygame.K_b:  # Toggle construction planning
                    construction_planner.toggle_planning_mode()
                elif event.key == pygame.K_c and construction_planner.planning_mode:  # Clear all plans
                    construction_planner.clear_all_plans()
                # --- Global keys ---
                elif event.key == pygame.K_ESCAPE:
                    if research_menu:
                        research_menu = False
                    else:
                        running = False
                elif event.key == pygame.K_r:
                    research_menu = not research_menu
                elif event.key == pygame.K_F5:
                    state = get_game_state(
                        colonist, zombies, walls, trees, wood, rocks, stone,
                        xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx
                    )
                    # Update to match savegame.py function signature
                    result = save_game(colonist, zombies, walls, trees, wood, rocks, stone,
                                     xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx)
                    if result:
                        print("Game saved.")
                    else:
                        print("Failed to save game.")
                elif event.key == pygame.K_F9:
                    data = load_game()
                    if data:
                        colonist, zombies, walls, trees, wood, rocks, stone, xp, level, skill_points, xp_to_next, unlocked_blueprints, selected_blueprint_idx = set_game_state(data, all_blueprints)
                        # Reload the world data if available
                        if 'spikes' in data:
                            spikes = []
                            for s in data['spikes']:
                                spike = Spike(s["x"], s["y"])
                                spike.hp = s.get("hp", 50)
                                spikes.append(spike)
                        if 'turrets' in data:
                            turrets = []
                            for t in data['turrets']:
                                turret = Turret(t["x"], t["y"])
                                turret.hp = t.get("hp", 100)
                                turret.cooldown = t.get("cooldown", 0)
                                turrets.append(turret)
                        if 'doors' in data:
                            doors = []
                            for d in data['doors']:
                                door = Door(d["x"], d["y"])
                                door.hp = d.get("hp", 100)
                                door.open = d.get("open", False)
                                doors.append(door)
                        if 'floors' in data:
                            floors = data['floors']
                        print("Game loaded.")
                    else:
                        print("No save file found.")
                # --- Research menu navigation ---
                elif research_menu:
                    if event.key == pygame.K_UP:
                        selected_blueprint_idx = (selected_blueprint_idx - 1) % len(all_blueprints)
                    elif event.key == pygame.K_DOWN:
                        selected_blueprint_idx = (selected_blueprint_idx + 1) % len(all_blueprints)
                    elif event.key == pygame.K_RETURN:
                        bp = all_blueprints[selected_blueprint_idx]
                        if bp["name"] not in unlocked_blueprints and skill_points > 0:
                            unlocked_blueprints.add(bp["name"])
                            skill_points -= 1
                # --- Construction planning mode ---
                elif construction_planner.planning_mode and event.key == pygame.K_SPACE:
                    # Add building to plan instead of building immediately
                    unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
                    if unlocked_list:
                        bp = unlocked_list[selected_blueprint_idx % len(unlocked_list)]
                        construction_planner.add_planned_building(colonist.x, colonist.y, bp["name"])
                # --- Game controls ---
                else:
                    if event.key == pygame.K_TAB:
                        unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
                        selected_blueprint_idx = (selected_blueprint_idx + 1) % len(unlocked_list)
                    elif event.key == pygame.K_SPACE:
                        unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
                        if unlocked_list:
                            bp = unlocked_list[selected_blueprint_idx % len(unlocked_list)]
                            can_build = all((wood if res == "wood" else stone) >= amt for res, amt in bp["cost"].items())
                            build_pos = (colonist.x, colonist.y, bp["name"])
                            blocked = any(w.x == colonist.x and w.y == colonist.y for w in walls) \
                                      or any(t.x == colonist.x and t.y == colonist.y for t in trees) \
                                      or any(s.x == colonist.x and s.y == colonist.y for s in spikes) \
                                      or any(tu.x == colonist.x and tu.y == colonist.y for tu in turrets) \
                                      or any(d.x == colonist.x and d.y == colonist.y for d in doors)
                            if can_build and not blocked:
                                if bp["name"] == "wood_wall":
                                    walls.append(Wall(colonist.x, colonist.y, wall_type="wood"))
                                elif bp["name"] == "stone_wall":
                                    walls.append(Wall(colonist.x, colonist.y, wall_type="stone"))
                                elif bp["name"] == "spike":
                                    spikes.append(Spike(colonist.x, colonist.y))
                                elif bp["name"] == "turret":
                                    turrets.append(Turret(colonist.x, colonist.y))
                                elif bp["name"] == "door":
                                    doors.append(Door(colonist.x, colonist.y))
                                # Add more buildables as needed
                                if "wood" in bp["cost"]:
                                    wood -= bp["cost"]["wood"]
                                if "stone" in bp["cost"]:
                                    stone -= bp["cost"]["stone"]
                                if build_pos not in last_build_positions:
                                    xp += 1
                                    last_build_positions.add(build_pos)
                    elif event.key == pygame.K_e:
                        for door in doors:
                            if door.x == colonist.x and door.y == colonist.y:
                                door.toggle()
                                break
                    elif event.key == pygame.K_a:
                        fx, fy = colonist.facing
                        target_x = colonist.x + fx
                        target_y = colonist.y + fy
                        # Attack or harvest anything 1 tile away (zombie, tree, rock), or open/close door
                        for zombie in zombies:
                            if zombie.x == target_x and zombie.y == target_y and zombie.hp > 0:
                                zombie.hp -= 50
                                break
                        # Try to harvest tree or rock even if no zombie was found
                        harvested = False
                        for tree in trees:
                            if tree.x == target_x and tree.y == target_y and not tree.cut_down:
                                wood += tree.cut()
                                if (tree.x, tree.y) not in last_tree_cut:
                                    xp += 1
                                    last_tree_cut.add((tree.x, tree.y))
                                harvested = True
                                break
                        if not harvested:
                            for rock in rocks:
                                if rock.x == target_x and rock.y == target_y and not rock.mined:
                                    stone += rock.mine()
                                    if (rock.x, rock.y) not in last_rock_mined:
                                        xp += 1
                                        last_rock_mined.add((rock.x, rock.y))
                                    harvested = True
                                    break
                            if not harvested:
                                # Open/close door if present
                                for door in doors:
                                    if door.x == target_x and door.y == target_y:
                                        door.toggle()
                                        break

        if research_menu:
            # ...existing research menu rendering code...
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

        # Movement (walls, closed doors, rocks, and trees block; open doors do not)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dx, dy = 0, -1
        elif keys[pygame.K_DOWN]:
            dx, dy = 0, 1
        elif keys[pygame.K_LEFT]:
            dx, dy = -1, 0
        elif keys[pygame.K_RIGHT]:
            dx, dy = 1, 0
        if dx != 0 or dy != 0:
            # Block by walls, closed doors, uncut trees, and unmined rocks
            block_walls = [w for w in walls]
            block_doors = [d for d in doors if not d.open]
            block_trees = [t for t in trees if not t.cut_down]
            block_rocks = [r for r in rocks if not r.mined]
            colonist.move(dx, dy, block_walls + block_doors + block_trees + block_rocks, [])

        # Skip game updates if paused
        if pause_game:
            # Still handle rendering
            pass
        else:
            # Combat systems
            CombatSystem.update_turrets(turrets, zombies, bullets, Bullet)
            CombatSystem.update_bullets(bullets, zombies, MAP_WIDTH, MAP_HEIGHT)
            CombatSystem.update_spikes(spikes, zombies)

            # Update zombies
            for zombie in zombies:
                zombie.update(colonist, walls + impassable + spikes + turrets + [d for d in doors if not d.open])
                if zombie.x == colonist.x and zombie.y == colonist.y:
                    colonist.hp -= 1
                    stats.increment("damage_taken", 1)

            # Cleanup and XP with statistics
            zombies_to_remove = [z for z in zombies if z.hp <= 0]
            for zombie in zombies_to_remove:
                if (zombie.x, zombie.y) not in last_zombie_killed:
                    xp += 5
                    stats.increment("zombies_killed")
                    last_zombie_killed.add((zombie.x, zombie.y))

            # Count trees and rocks cut/mined for stats before removing them
            cut_trees = [t for t in trees if t.cut_down]
            for t in cut_trees:
                stats.increment("trees_cut")
                stats.increment("wood_gathered", 2)
            mined_rocks = [r for r in rocks if r.mined]
            for r in mined_rocks:
                stats.increment("rocks_mined")
                stats.increment("stone_gathered", 2)

            zombies = [z for z in zombies if z.hp > 0]
            walls = [w for w in walls if w.hp > 0]
            spikes = [s for s in spikes if s.hp > 0]
            turrets = [t for t in turrets if t.hp > 0]
            doors = [d for d in doors if d.hp > 0]

            # Remove cut trees and mined rocks from the lists
            trees = [t for t in trees if not t.cut_down]
            rocks = [r for r in rocks if not r.mined]

            # Update minimap
            minimap.update(MAP_WIDTH, MAP_HEIGHT, colonist, zombies, walls, trees, rocks)

        # Level up
        xp, level, skill_points, xp_to_next, _ = ExperienceSystem.check_level_up(xp, level, skill_points, xp_to_next)

        # Camera scroll (no smoothing, always center on colonist)
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
                    # Draw floor tile if present, else grass
                    if (wx, wy) in floors and floor_img:
                        screen.blit(floor_img, (x*TILE_SIZE, y*TILE_SIZE))
                    elif grass_img:
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
        for door in doors:
            door.draw(screen, cam_x, cam_y)
        colonist.draw(screen, cam_x, cam_y)
        for zombie in zombies:
            zombie.draw(screen, cam_x, cam_y)
        for tree in trees:
            covered = (tree.x == colonist.x and tree.y - 1 == colonist.y) or any(tree.x == z.x and tree.y - 1 == z.y for z in zombies)
            if covered:
                tree.draw(screen, cam_x, cam_y)

        # Draw QoL overlays
        minimap.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        construction_planner.draw_plans(screen, cam_x, cam_y, load_image, TILE_SIZE)
        
        if show_stats:
            stats.draw_stats_overlay(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Draw pause indicator
        if pause_game:
            font = pygame.font.SysFont(None, 48)
            pause_text = font.render("PAUSED (P to resume)", True, (255, 255, 0))
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Draw planning mode indicator
        if construction_planner.planning_mode:
            font = pygame.font.SysFont(None, 24)
            plan_text = font.render("PLANNING MODE (B to toggle, C to clear)", True, (255, 255, 0))
            screen.blit(plan_text, (10, SCREEN_HEIGHT - 30))

        # Build preview in HUD
        build_img = None
        if not research_menu:
            unlocked_list = get_unlocked_blueprints(all_blueprints, unlocked_blueprints)
            if unlocked_list:
                bp = unlocked_list[selected_blueprint_idx % len(unlocked_list)]
                img = load_image(bp["img"])
                if img:
                    build_img = img.copy()

        # Enhanced HUD with QoL info
        draw_hud(screen, colonist, wood, stone, build_img)
        
        font = pygame.font.SysFont(None, 28)
        xp_text = font.render(f"XP: {xp}/{xp_to_next}  Level: {level}  SP: {skill_points}", True, (0, 255, 255))
        screen.blit(xp_text, (10, 35))
        day_text = font.render(f"Day: {wave_system.day_count}", True, (255, 255, 255))
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

        # Additional QoL HUD elements
        font = pygame.font.SysFont(None, 20)
        qol_hints = [
            "P: Pause  B: Plan Mode  Shift+Tab: Stats",
            f"Auto-save in: {(AUTO_SAVE_INTERVAL - auto_save_timer) // FPS}s"
        ]
        for i, hint in enumerate(qol_hints):
            text = font.render(hint, True, (200, 200, 200))
            screen.blit(text, (10, SCREEN_HEIGHT - 70 + i * 20))

        pygame.display.flip()
        clock.tick(FPS)

        if colonist.hp <= 0:
            print("Colonist died!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
