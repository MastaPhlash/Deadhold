import pygame

TILE_SIZE = 32
MAP_WIDTH = 20
MAP_HEIGHT = 15

GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (50, 50, 50)
WALL_COLOR = (120, 120, 120)

class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.hp = 100

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Colonist(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
            self.x, self.y = nx, ny

class Zombie(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, RED)
        self.move_counter = 0

    def update(self, target, walls):
        self.move_counter += 1
        if self.move_counter % 4 == 0:  # Move only every 4 frames
            dx = target.x - self.x
            dy = target.y - self.y
            nx, ny = self.x, self.y
            if abs(dx) > abs(dy):
                nx += 1 if dx > 0 else -1 if dx < 0 else 0
            else:
                ny += 1 if dy > 0 else -1 if dy < 0 else 0
            # Check for wall collision
            if not any(wall.x == nx and wall.y == ny for wall in walls):
                self.x, self.y = nx, ny

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = WALL_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
