import pygame
import random
from entities import Colonist, Zombie, Wall, Tree
from hud import draw_hud
from savegame import save_game, load_game
import os

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
    wood = 5  # Starting wood

    # Place trees randomly
    for _ in range(600):
        tx = random.randint(0, MAP_WIDTH-1)
        ty = random.randint(0, MAP_HEIGHT-1)
        # Avoid starting position
        if abs(tx - colonist.x) > 2 or abs(ty - colonist.y) > 2:
            trees.append(Tree(tx, ty))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Exit with Escape key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            # Save game with F5
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                save_game(colonist, zombies, walls, trees, wood)
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
                    # Restore wood
                    wood = data.get("wood", 0)
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
                            break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            colonist.move(0, -1, walls, trees)
        if keys[pygame.K_DOWN]:
            colonist.move(0, 1, walls, trees)
        if keys[pygame.K_LEFT]:
            colonist.move(-1, 0, walls, trees)
        if keys[pygame.K_RIGHT]:
            colonist.move(1, 0, walls, trees)

        # Update zombies
        for zombie in zombies:
            zombie.update(colonist, walls)
            if zombie.x == colonist.x and zombie.y == colonist.y:
                colonist.hp -= 1

        # Remove dead zombies
        zombies = [z for z in zombies if z.hp > 0]
        # Remove destroyed walls
        walls = [w for w in walls if w.hp > 0]
        # Remove cut trees
        trees = [t for t in trees if not t.cut_down]

        # Camera scroll: center on colonist
        cam_x = colonist.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        cam_y = colonist.y * TILE_SIZE - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        cam_x = max(0, min(cam_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        cam_y = max(0, min(cam_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

        # Draw
        screen.fill((50, 50, 50))
        # Draw grass tiles (only visible area)
        for x in range(SCREEN_WIDTH // TILE_SIZE):
            for y in range(SCREEN_HEIGHT // TILE_SIZE):
                wx = x + cam_x // TILE_SIZE
                wy = y + cam_y // TILE_SIZE
                if 0 <= wx < MAP_WIDTH and 0 <= wy < MAP_HEIGHT:
                    if grass_img:
                        screen.blit(grass_img, (x*TILE_SIZE, y*TILE_SIZE))
                    else:
                        pygame.draw.rect(screen, (34, 139, 34), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # Draw grid (optional, comment out to hide)
        # for x in range(SCREEN_WIDTH // TILE_SIZE):
        #     for y in range(SCREEN_HEIGHT // TILE_SIZE):
        #         wx = x + cam_x // TILE_SIZE
        #         wy = y + cam_y // TILE_SIZE
        #         if 0 <= wx < MAP_WIDTH and 0 <= wy < MAP_HEIGHT:
        #             pygame.draw.rect(screen, WHITE, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        # Draw trees
        for tree in trees:
            tree.draw(screen, cam_x, cam_y)
        # Draw walls
        for wall in walls:
            wall.draw(screen, cam_x, cam_y)
        colonist.draw(screen, cam_x, cam_y)
        for zombie in zombies:
            zombie.draw(screen, cam_x, cam_y)

        draw_hud(screen, colonist, wood)

        pygame.display.flip()
        clock.tick(5)

        if colonist.hp <= 0:
            print("Colonist died!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
