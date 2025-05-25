import pygame
import os

TILE_SIZE = 64
MAP_WIDTH = 200
MAP_HEIGHT = 150

# Ensure the assets folder exists at this path:
# x:\Coding\Python\Deadhold-1\assets\
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
if not os.path.exists(ASSET_DIR):
    os.makedirs(ASSET_DIR)
    # Place your images in this folder:
    #   colonist.png
    #   zombie.png
    #   wall.png
    #   tree.png
    #   (optional) facing_indicator.png

GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (50, 50, 50)
WALL_COLOR = (120, 120, 120)
TREE_COLOR = (34, 139, 34)
ROCK_COLOR = (100, 100, 100)

def load_image(filename):
    path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
        return img
    except Exception:
        return None

def get_direction_name(dx, dy):
    if dx == 0 and dy == -1:
        return "up"
    elif dx == 0 and dy == 1:
        return "down"
    elif dx == -1 and dy == 0:
        return "left"
    elif dx == 1 and dy == 0:
        return "right"
    return "down"  # Default

class Entity:
    image = None  # To be set in subclasses

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.hp = 100

    def draw(self, surface, cam_x=0, cam_y=0):
        if self.image:
            surface.blit(self.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y, TILE_SIZE, TILE_SIZE))

class Colonist(Entity):
    images = {}

    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        self.facing = (0, -1)  # Default facing up (dx, dy)
        self.movement_delay = 0  # Delay before movement starts
        self.key_hold_time = {}  # Track how long each direction key is held
        # Load directional images once
        if not Colonist.images:
            for dir_name in ["up", "down", "left", "right"]:
                img = load_image(f"colonist_{dir_name}.png")
                if img:
                    Colonist.images[dir_name] = img
            # Fallback to colonist.png if directional missing
            fallback = load_image("colonist.png")
            for dir_name in ["up", "down", "left", "right"]:
                if dir_name not in Colonist.images and fallback:
                    Colonist.images[dir_name] = fallback

    def update_movement(self, keys):
        """Update movement based on key states, allowing quick taps to change facing only"""
        # Check which direction keys are pressed
        directions = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0)
        }
        
        pressed_direction = None
        for key, direction in directions.items():
            if keys[key]:
                pressed_direction = direction
                # Track how long this key has been held
                if key not in self.key_hold_time:
                    self.key_hold_time[key] = 0
                self.key_hold_time[key] += 1
                break
        
        # Clear hold times for keys that aren't pressed
        for key in list(self.key_hold_time.keys()):
            if not keys[key]:
                del self.key_hold_time[key]
        
        if pressed_direction:
            # Always update facing direction immediately
            self.facing = pressed_direction
            
            # Only move if key has been held for more than 1 frame (faster response)
            for key, direction in directions.items():
                if keys[key] and direction == pressed_direction:
                    if self.key_hold_time[key] > 1:  # Reduced from 2 to 1 for faster movement
                        return direction
            
        return (0, 0)  # No movement, just facing change

    def move(self, dx, dy, walls, trees_and_rocks):
        if dx == 0 and dy == 0:
            return
            
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
            # Prevent moving into walls, uncut trees, or unmined rocks
            if any(w.x == nx and w.y == ny for w in walls):
                return
            if any((t.x == nx and t.y == ny) for t in trees_and_rocks):
                return
            self.x, self.y = nx, ny

    def draw(self, surface, cam_x=0, cam_y=0):
        # Draw directional image
        dir_name = get_direction_name(*self.facing)
        img = Colonist.images.get(dir_name)
        if img:
            surface.blit(img, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            super().draw(surface, cam_x, cam_y)

class Zombie(Entity):
    images = {}

    def __init__(self, x, y):
        super().__init__(x, y, RED)
        self.move_counter = 0
        self.facing = (0, 1)
        # Load directional images once
        if not Zombie.images:
            for dir_name in ["up", "down", "left", "right"]:
                img = load_image(f"zombie_{dir_name}.png")
                if img:
                    Zombie.images[dir_name] = img
            fallback = load_image("zombie.png")
            for dir_name in ["up", "down", "left", "right"]:
                if dir_name not in Zombie.images and fallback:
                    Zombie.images[dir_name] = fallback
            # If still missing any direction, use any loaded image as a last resort
            for dir_name in ["up", "down", "left", "right"]:
                if dir_name not in Zombie.images:
                    for img in Zombie.images.values():
                        Zombie.images[dir_name] = img
                        break
            # Print warning if no image loaded at all
            if not Zombie.images:
                print("Warning: No zombie images found. Zombies will be red squares.")

    def update(self, target, walls):
        self.move_counter += 1
        if self.move_counter % 4 == 0:  # Move only every 4 frames
            # Always calculate movement toward target (removed optimization that was breaking AI)
            dx = target.x - self.x
            dy = target.y - self.y
            nx, ny = self.x, self.y
            
            # Determine facing direction for image
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.facing = (1, 0)
                elif dx < 0:
                    self.facing = (-1, 0)
                nx += self.facing[0]
            else:
                if dy > 0:
                    self.facing = (0, 1)
                elif dy < 0:
                    self.facing = (0, -1)
                ny += self.facing[1]
            
            # Check for wall collision - NOTE: spikes removed from walls list in main.py
            for wall in walls:
                if wall.x == nx and wall.y == ny:
                    wall.damage(25)
                    return  # Don't move, just damage wall
            
            # Move if no collision (zombies now walk through spikes)
            self.x, self.y = nx, ny

    def draw(self, surface, cam_x=0, cam_y=0):
        dir_name = get_direction_name(*self.facing)
        img = Zombie.images.get(dir_name)
        if img:
            surface.blit(img, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            super().draw(surface, cam_x, cam_y)
        # Draw zombie HP bar
        if self.hp < 100:
            bar_width = int(TILE_SIZE * (self.hp / 100))
            pygame.draw.rect(
                surface,
                (0, 255, 0),
                (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5)
            )

class Wall:
    images = {}

    def __init__(self, x, y, wall_type="wood"):
        self.x = x
        self.y = y
        self.type = wall_type  # "wood" or "stone"
        if self.type == "stone":
            self.color = (150, 150, 150)
            self.hp = 300
            img_name = "stone_wall.png"
        else:
            self.color = WALL_COLOR
            self.hp = 100
            img_name = "wall.png"
        # Load images for both wall types
        if img_name not in Wall.images:
            Wall.images[img_name] = load_image(img_name)
        self.image = Wall.images[img_name]

    def draw(self, surface, cam_x=0, cam_y=0):
        if self.image:
            surface.blit(self.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y, TILE_SIZE, TILE_SIZE))
        # Draw wall HP bar
        if self.hp < (300 if self.type == "stone" else 100):
            max_hp = 300 if self.type == "stone" else 100
            bar_width = int(TILE_SIZE * (self.hp / max_hp))
            pygame.draw.rect(surface, (255, 0, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5))

    def damage(self, amount):
        self.hp -= amount

class Tree:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = TREE_COLOR
        self.cut_down = False
        if Tree.image is None:
            # Load a 1x2 tile image, or scale a 1x1 image to 1x2 tiles
            img = load_image("tree.png")
            if img and img.get_height() != TILE_SIZE * 2:
                img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE * 2))
            Tree.image = img

    def draw(self, surface, cam_x=0, cam_y=0):
        if Tree.image:
            # Draw the tree image so its base is at (self.x, self.y)
            surface.blit(Tree.image, (self.x * TILE_SIZE - cam_x, (self.y - 1) * TILE_SIZE - cam_y))
        else:
            # Draw a tall rectangle as a placeholder
            pygame.draw.rect(
                surface,
                self.color,
                (self.x * TILE_SIZE - cam_x + 4, (self.y - 1) * TILE_SIZE - cam_y + 4, TILE_SIZE - 8, TILE_SIZE * 2 - 8)
            )

    def cut(self):
        self.cut_down = True
        return 2  # Amount of wood per tree

    def damage(self, amount):
        # Trees are not damaged by zombies, so do nothing
        pass

class Rock:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = ROCK_COLOR
        self.mined = False

    def draw(self, surface, cam_x=0, cam_y=0):
        # Always try to load the image if not loaded yet
        if Rock.image is None and pygame.get_init():
            Rock.image = load_image("rock.png")
        if Rock.image:
            surface.blit(Rock.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            # Draw a more visible placeholder for stone
            pygame.draw.rect(
                surface,
                (180, 180, 180),
                (self.x * TILE_SIZE - cam_x + 8, self.y * TILE_SIZE - cam_y + 8, TILE_SIZE - 16, TILE_SIZE - 16)
            )
            pygame.draw.rect(
                surface,
                (80, 80, 80),
                (self.x * TILE_SIZE - cam_x + 20, self.y * TILE_SIZE - cam_y + 20, TILE_SIZE - 40, TILE_SIZE - 40)
            )
            print("Warning: rock.png not found or could not be loaded.")

    def mine(self):
        self.mined = True
        return 2  # Amount of stone per rock

    def damage(self, amount):
        # Rocks are not damaged by zombies, so do nothing
        pass

class Spike:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 50
        self.last_damage_time = 0  # Track when spike last dealt damage
        if Spike.image is None:
            Spike.image = load_image("spike.png")

    def draw(self, surface, cam_x=0, cam_y=0):
        if Spike.image:
            surface.blit(Spike.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            # More visible spike placeholder - brown spikes on darker background
            pygame.draw.rect(surface, (101, 67, 33), (self.x * TILE_SIZE - cam_x + 4, self.y * TILE_SIZE - cam_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))
            # Draw spike points
            points = [
                (self.x * TILE_SIZE - cam_x + 16, self.y * TILE_SIZE - cam_y + 8),
                (self.x * TILE_SIZE - cam_x + 24, self.y * TILE_SIZE - cam_y + 20),
                (self.x * TILE_SIZE - cam_x + 32, self.y * TILE_SIZE - cam_y + 8),
                (self.x * TILE_SIZE - cam_x + 40, self.y * TILE_SIZE - cam_y + 20),
                (self.x * TILE_SIZE - cam_x + 48, self.y * TILE_SIZE - cam_y + 8)
            ]
            for point in points:
                pygame.draw.polygon(surface, (160, 82, 45), [
                    point,
                    (point[0] - 3, point[1] + 12),
                    (point[0] + 3, point[1] + 12)
                ])
        
        # Draw HP bar if damaged
        if self.hp < 50:
            bar_width = int(TILE_SIZE * (self.hp / 50))
            pygame.draw.rect(surface, (255, 0, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5))

    def damage(self, amount):
        self.hp -= amount

class Turret:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.cooldown = 0
        if Turret.image is None:
            Turret.image = load_image("turret.png")

    def draw(self, surface, cam_x=0, cam_y=0):
        if Turret.image:
            surface.blit(Turret.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            pygame.draw.rect(surface, (100, 100, 255), (self.x * TILE_SIZE - cam_x + 8, self.y * TILE_SIZE - cam_y + 8, TILE_SIZE - 16, TILE_SIZE - 16))

    def damage(self, amount):
        self.hp -= amount

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.timer = 0  # For bullet lifetime

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.timer += 1

    def draw(self, surface, cam_x=0, cam_y=0):
        pygame.draw.circle(surface, (255, 255, 0), (self.x * TILE_SIZE + TILE_SIZE // 2 - cam_x, self.y * TILE_SIZE + TILE_SIZE // 2 - cam_y), 8)

class Door:
    image_closed = None
    image_open = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.open = False
        if Door.image_closed is None:
            Door.image_closed = load_image("door.png")
        if Door.image_open is None:
            Door.image_open = load_image("door_open.png") or Door.image_closed

    def draw(self, surface, cam_x=0, cam_y=0):
        img = Door.image_open if self.open else Door.image_closed
        if img:
            surface.blit(img, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            color = (200, 180, 80) if self.open else (120, 100, 40)
            pygame.draw.rect(surface, color, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y, TILE_SIZE, TILE_SIZE))
        # HP bar
        if self.hp < 100:
            bar_width = int(TILE_SIZE * (self.hp / 100))
            pygame.draw.rect(surface, (255, 0, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5))

    def damage(self, amount):
        self.hp -= amount

    def toggle(self):
        self.open = not self.open

class TrapPit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 75  # More durable than spikes
        self.last_damage_time = 0
        if TrapPit.image is None:
            TrapPit.image = load_image("trap_pit.png")

    def draw(self, surface, cam_x=0, cam_y=0):
        if TrapPit.image:
            surface.blit(TrapPit.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            # Dark pit placeholder with brown edges
            pygame.draw.rect(surface, (40, 30, 20), (self.x * TILE_SIZE - cam_x + 8, self.y * TILE_SIZE - cam_y + 8, TILE_SIZE - 16, TILE_SIZE - 16))
            pygame.draw.rect(surface, (20, 15, 10), (self.x * TILE_SIZE - cam_x + 16, self.y * TILE_SIZE - cam_y + 16, TILE_SIZE - 32, TILE_SIZE - 32))
            # Draw some jagged edges
            points = [
                (self.x * TILE_SIZE - cam_x + 12, self.y * TILE_SIZE - cam_y + 12),
                (self.x * TILE_SIZE - cam_x + 20, self.y * TILE_SIZE - cam_y + 8),
                (self.x * TILE_SIZE - cam_x + 28, self.y * TILE_SIZE - cam_y + 12),
                (self.x * TILE_SIZE - cam_x + 32, self.y * TILE_SIZE - cam_y + 20)
            ]
            for point in points:
                pygame.draw.circle(surface, (60, 45, 30), point, 3)
        
        # Draw HP bar if damaged
        if self.hp < 75:
            bar_width = int(TILE_SIZE * (self.hp / 75))
            pygame.draw.rect(surface, (255, 0, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5))

    def damage(self, amount):
        self.hp -= amount

class Workbench:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 150
        self.in_use = False
        self.craft_timer = 0
        if Workbench.image is None:
            Workbench.image = load_image("workbench.png")

    def draw(self, surface, cam_x=0, cam_y=0):
        if Workbench.image:
            surface.blit(Workbench.image, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            # Brown workbench with tools
            pygame.draw.rect(surface, (139, 69, 19), (self.x * TILE_SIZE - cam_x + 4, self.y * TILE_SIZE - cam_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))
            pygame.draw.rect(surface, (160, 82, 45), (self.x * TILE_SIZE - cam_x + 8, self.y * TILE_SIZE - cam_y + 8, TILE_SIZE - 16, TILE_SIZE - 16))
            # Draw some tool shapes
            pygame.draw.circle(surface, (100, 100, 100), (self.x * TILE_SIZE - cam_x + 20, self.y * TILE_SIZE - cam_y + 20), 4)
            pygame.draw.rect(surface, (100, 100, 100), (self.x * TILE_SIZE - cam_x + 35, self.y * TILE_SIZE - cam_y + 15, 8, 3))
            
        # Visual indicator when in use
        if self.in_use:
            # Glowing effect
            glow_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            glow_surface.fill((255, 255, 0, 60))
            surface.blit(glow_surface, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        
        # Draw HP bar if damaged
        if self.hp < 150:
            bar_width = int(TILE_SIZE * (self.hp / 150))
            pygame.draw.rect(surface, (255, 0, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5))

    def damage(self, amount):
        self.hp -= amount

    def start_crafting(self):
        """Start a crafting operation"""
        if not self.in_use:
            self.in_use = True
            self.craft_timer = 30  # 6 seconds at 5 FPS
            return True
        return False

    def update(self):
        """Update crafting progress"""
        if self.in_use and self.craft_timer > 0:
            self.craft_timer -= 1
            if self.craft_timer <= 0:
                self.in_use = False
                return True  # Crafting complete
        return False

class Campfire:
    image = None
    image_off = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 75
        self.lit = True
        self.fuel = 100  # Fuel level
        self.last_heal_time = 0
        if Campfire.image is None:
            Campfire.image = load_image("campfire.png")
        if Campfire.image_off is None:
            Campfire.image_off = load_image("campfire_off.png")

    def draw(self, surface, cam_x=0, cam_y=0):
        # Choose appropriate image based on lit state and fuel
        img_to_use = None
        if self.lit and self.fuel > 0:
            img_to_use = Campfire.image
        else:
            img_to_use = Campfire.image_off or Campfire.image
            
        if img_to_use:
            surface.blit(img_to_use, (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y))
        else:
            # Stone base
            pygame.draw.circle(surface, (100, 100, 100), (self.x * TILE_SIZE - cam_x + TILE_SIZE // 2, self.y * TILE_SIZE - cam_y + TILE_SIZE // 2), 20)
            if self.lit and self.fuel > 0:
                # Fire effect
                import time
                flicker = int(time.time() * 10) % 3
                colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0)]
                pygame.draw.circle(surface, colors[flicker], (self.x * TILE_SIZE - cam_x + TILE_SIZE // 2, self.y * TILE_SIZE - cam_y + TILE_SIZE // 2), 15)
                pygame.draw.circle(surface, (255, 255, 100), (self.x * TILE_SIZE - cam_x + TILE_SIZE // 2, self.y * TILE_SIZE - cam_y + TILE_SIZE // 2), 8)
            else:
                # Unlit/no fuel
                pygame.draw.circle(surface, (50, 50, 50), (self.x * TILE_SIZE - cam_x + TILE_SIZE // 2, self.y * TILE_SIZE - cam_y + TILE_SIZE // 2), 15)
        
        # Draw HP bar if damaged
        if self.hp < 75:
            bar_width = int(TILE_SIZE * (self.hp / 75))
            pygame.draw.rect(surface, (255, 0, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 6, bar_width, 5))
        
        # Draw fuel bar
        fuel_bar_width = int(TILE_SIZE * (self.fuel / 100))
        pygame.draw.rect(surface, (50, 50, 50), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 12, TILE_SIZE, 4))
        pygame.draw.rect(surface, (255, 165, 0), (self.x * TILE_SIZE - cam_x, self.y * TILE_SIZE - cam_y + TILE_SIZE - 12, fuel_bar_width, 4))

    def damage(self, amount):
        self.hp -= amount

    def add_fuel(self, amount):
        """Add fuel to keep fire burning"""
        self.fuel = min(100, self.fuel + amount)

    def update(self):
        """Update campfire - consumes fuel and can heal nearby colonist"""
        if self.lit and self.fuel > 0:
            self.fuel -= 0.1  # Slowly consume fuel
            if self.fuel <= 0:
                self.lit = False

    def heal_nearby(self, colonist):
        """Heal colonist if they're nearby and fire is lit"""
        if self.lit and self.fuel > 0:
            distance = abs(self.x - colonist.x) + abs(self.y - colonist.y)
            if distance <= 2:  # Within 2 tiles
                current_time = pygame.time.get_ticks()
                if current_time - self.last_heal_time > 2000:  # Heal every 2 seconds
                    if colonist.hp < 100:
                        colonist.hp = min(100, colonist.hp + 5)
                        self.last_heal_time = current_time
                        return True
        return False

    def toggle_light(self):
        """Toggle fire on/off if there's fuel"""
        if self.fuel > 0:
            self.lit = not self.lit
