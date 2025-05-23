import pygame
import random

# Game settings
TILE_SIZE = 32
MAP_WIDTH = 20
MAP_HEIGHT = 15
SCREEN_WIDTH = TILE_SIZE * MAP_WIDTH
SCREEN_HEIGHT = TILE_SIZE * MAP_HEIGHT

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (50, 50, 50)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deadhold Prototype")

clock = pygame.time.Clock()

class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.hp = 100

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Colonist(Entity):
    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
            self.x, self.y = nx, ny

class Zombie(Entity):
    def update(self, target):
        # Move toward the colonist
        dx = target.x - self.x
        dy = target.y - self.y
        if abs(dx) > abs(dy):
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
        else:
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0

def main():
    colonist = Colonist(MAP_WIDTH // 2, MAP_HEIGHT // 2, GREEN)
    zombies = [Zombie(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1), RED) for _ in range(3)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            colonist.move(0, -1)
        if keys[pygame.K_DOWN]:
            colonist.move(0, 1)
        if keys[pygame.K_LEFT]:
            colonist.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            colonist.move(1, 0)

        # Update zombies
        for zombie in zombies:
            zombie.update(colonist)
            if zombie.x == colonist.x and zombie.y == colonist.y:
                colonist.hp -= 1

        # Draw
        screen.fill(GRAY)
        # Draw grid
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                pygame.draw.rect(screen, WHITE, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        colonist.draw(screen)
        for zombie in zombies:
            zombie.draw(screen)

        pygame.display.flip()
        clock.tick(5)

        if colonist.hp <= 0:
            print("Colonist died!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
