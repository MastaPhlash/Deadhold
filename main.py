import pygame
import random
from entities import Colonist, Zombie, Wall, Tree, Rock
from hud import draw_hud
import os

#
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

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (50, 50, 50)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deadhold Prototype")

clock = pygame.time.Clock()

# Load grass tile image
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

def main():
    colonist = Colonist(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    zombies = [Zombie(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(10)]
    walls = []
    trees = []
    rocks = []
    wood = 5  # Starting wood
    stone = 0 # Starting stone
    ticks = 0
    FPS = 5
    MINUTES_PER_STEP = 15  # Each tick of the clock is 15 in-game minutes
    TICKS_PER_STEP = FPS * 2  # 2 real seconds per in-game step
    TOTAL_STEPS = 24 * 60 // MINUTES_PER_STEP  # 96 steps in 24 hours
    # Start at 06:00 (6 AM)
    current_step = (6 * 60) // MINUTES_PER_STEP  # 6*60=360, 360//15=24

    # Place rocks randomly, avoid starting position
    for _ in range(600):
        placed = False
        for _ in range(20):  # Try more times to find a free spot
            rx = random.randint(0, MAP_WIDTH-1)
            ry = random.randint(0, MAP_HEIGHT-1)
            if (
                abs(rx - colonist.x) > 2 or abs(ry - colonist.y) > 2
            ) and not any(r.x == rx and r.y == ry for r in rocks):
                rocks.append(Rock(rx, ry))
                placed = True
                break
    print(f"Rocks placed: {len(rocks)}")
   
    for _ in range(600):
        placed = False
        for _ in range(20):
            tx = random.randint(0, MAP_WIDTH-1)
            ty = random.randint(0, MAP_HEIGHT-1)
            if (
                abs(tx - colonist.x) > 2 or abs(ty - colonist.y) > 2
            ) and not any(t.x == tx and t.y == ty for t in trees) \
              and not any(r.x == tx and r.y == ty for r in rocks):
                trees.append(Tree(tx, ty))
                placed = True
                break

    running = True
    while running:
        ticks += 1
        # Advance in-game time every TICKS_PER_STEP frames
        if ticks % TICKS_PER_STEP == 0:
            current_step = (current_step + 1) % TOTAL_STEPS

        # Calculate hour and minute
        hour = (current_step * MINUTES_PER_STEP) // 60
        minute = (current_step * MINUTES_PER_STEP) % 60

        # Day/night logic: day from 6:00 to 21:00 (6am to 9pm), night otherwise
        is_night = not (6 <= hour < 21)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Exit with Escape key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            # Save game with F5
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                save_game(colonist, zombies, walls, trees, wood, rocks, stone)
                print("Game saved.")
            # Load game with F9
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                data = load_game()
                if data:
                    # Restore colonist
                    colonist.x = data["colonist"]["x"]
                    colonist.y = data["colonist"]["y"]
                    colonist.hp = data["colonist"]["hp"]
                    colonist.facing = tuple(data["colonist"].get("facing", (0, -1)))
                    # Restore zombies
                    zombies = []
                    for z in data["zombies"]:
                        zombie = Zombie(z["x"], z["y"])
                        zombie.hp = z["hp"]
                        zombie.facing = tuple(z.get("facing", (0, 1)))
                        zombies.append(zombie)
                    # Restore walls
                    walls = []
                    for w in data["walls"]:
                        wall = Wall(w["x"], w["y"])
                        wall.hp = w["hp"]
                        walls.append(wall)
                    # Restore trees
                    trees = []
                    for t in data["trees"]:
                        tree = Tree(t["x"], t["y"])
                        tree.cut_down = t.get("cut_down", False)
                        trees.append(tree)
                    # Restore rocks
                    rocks = []
                    for r in data.get("rocks", []):
                        rock = Rock(r["x"], r["y"])
                        rock.mined = r.get("mined", False)
                        rocks.append(rock)
                    # Restore stone
                    stone = data.get("stone", 0)
                    print("Game loaded.")
                else:
                    print("No save file found.")
            # Place wall with spacebar (costs wood)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if wood > 0 and not any(w.x == colonist.x and w.y == colonist.y for w in walls) and not any(t.x == colonist.x and t.y == colonist.y for t in trees):
                    walls.append(Wall(colonist.x, colonist.y))
                    wood -= 1
            # Attack with 'A' key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                fx, fy = colonist.facing
                target_x = colonist.x + fx
                target_y = colonist.y + fy
                attacked = False
                # Attack zombie
                for zombie in zombies:
                    if zombie.x == target_x and zombie.y == target_y:
                        zombie.hp -= 50  # Damage value
                        attacked = True
                        break
                # Attack tree (get wood)
                if not attacked:
                    for tree in trees:
                        if tree.x == target_x and tree.y == target_y:
                            wood += tree.cut()
                            attacked = True
                            break
                # Attack rock (get stone)
                if not attacked:
                    for rock in rocks:
                        if rock.x == target_x and rock.y == target_y:
                            stone += rock.mine()
                            break

        keys = pygame.key.get_pressed()
        # Prepare list of impassable objects (tree bases and rocks)
        impassable = [t for t in trees if not t.cut_down] + [r for r in rocks if not r.mined]
        if keys[pygame.K_UP]:
            colonist.move(0, -1, walls, impassable)
        if keys[pygame.K_DOWN]:
            colonist.move(0, 1, walls, impassable)
        if keys[pygame.K_LEFT]:
            colonist.move(-1, 0, walls, impassable)
        if keys[pygame.K_RIGHT]:
            colonist.move(1, 0, walls, impassable)

        # Update zombies
        for zombie in zombies:
            # Zombies should also not walk through tree bases or rocks
            zombie.update(colonist, walls + impassable)
            if zombie.x == colonist.x and zombie.y == colonist.y:
                colonist.hp -= 1

        # Remove dead zombies
        zombies = [z for z in zombies if z.hp > 0]
        # Remove destroyed walls
        walls = [w for w in walls if w.hp > 0]
        # Remove cut trees and mined rocks
        trees = [t for t in trees if not t.cut_down]
        rocks = [r for r in rocks if not r.mined]

        # Camera scroll: center on colonist
        cam_x = colonist.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        cam_y = colonist.y * TILE_SIZE - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        cam_x = max(0, min(cam_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        cam_y = max(0, min(cam_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

        # Draw
        screen.fill((50, 50, 50))
        # Draw grass tiles (always the very bottom layer)
        for x in range(SCREEN_WIDTH // TILE_SIZE):
            for y in range(SCREEN_HEIGHT // TILE_SIZE):
                wx = x + cam_x // TILE_SIZE
                wy = y + cam_y // TILE_SIZE
                if 0 <= wx < MAP_WIDTH and 0 <= wy < MAP_HEIGHT:
                    if grass_img:
                        screen.blit(grass_img, (x*TILE_SIZE, y*TILE_SIZE))
                    else:
                        pygame.draw.rect(screen, (34, 139, 34), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # Draw rocks before trees
        for rock in rocks:
            rock.draw(screen, cam_x, cam_y)
        # Draw walls before trees and characters
        for wall in walls:
            wall.draw(screen, cam_x, cam_y)
        # Draw trees that are NOT covering any character (base and canopy not above colonist or any zombie)
        for tree in trees:
            covered = (tree.x == colonist.x and tree.y - 1 == colonist.y) or any(tree.x == z.x and tree.y - 1 == z.y for z in zombies)
            if not covered:
                tree.draw(screen, cam_x, cam_y)
        # Draw colonist
        colonist.draw(screen, cam_x, cam_y)
        # Draw zombies
        for zombie in zombies:
            zombie.draw(screen, cam_x, cam_y)
        # Draw trees that ARE covering any character (canopy above colonist or any zombie)
        for tree in trees:
            covered = (tree.x == colonist.x and tree.y - 1 == colonist.y) or any(tree.x == z.x and tree.y - 1 == z.y for z in zombies)
            if covered:
                tree.draw(screen, cam_x, cam_y)

        draw_hud(screen, colonist, wood, stone)

        # Night overlay
        if is_night:
            night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            night_overlay.fill((0, 0, 40, 120))  # RGBA: blue-black, alpha for darkness
            screen.blit(night_overlay, (0, 0))

        # Draw day/night indicator
        font = pygame.font.SysFont(None, 32)
        dn_text = font.render("Night" if is_night else "Day", True, (200, 200, 255) if is_night else (255, 255, 0))
        screen.blit(dn_text, (SCREEN_WIDTH - 110, 5))

        # Draw conventional clock at the top center
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
