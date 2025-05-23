import pygame
import random
from entities import Colonist, Zombie, Wall
from hud import draw_hud

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

def main():
    colonist = Colonist(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    zombies = [Zombie(random.randint(0, MAP_WIDTH-1), random.randint(0, MAP_HEIGHT-1)) for _ in range(3)]
    walls = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Place wall with spacebar
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Prevent duplicate walls
                if not any(w.x == colonist.x and w.y == colonist.y for w in walls):
                    walls.append(Wall(colonist.x, colonist.y))

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
            zombie.update(colonist, walls)
            if zombie.x == colonist.x and zombie.y == colonist.y:
                colonist.hp -= 1

        # Draw
        screen.fill((50, 50, 50))
        # Draw grid
        for x in range(20):
            for y in range(15):
                pygame.draw.rect(screen, (255, 255, 255), (x*32, y*32, 32, 32), 1)
        # Draw walls
        for wall in walls:
            wall.draw(screen)
        colonist.draw(screen)
        for zombie in zombies:
            zombie.draw(screen)

        draw_hud(screen, colonist)

        pygame.display.flip()
        clock.tick(5)

        if colonist.hp <= 0:
            print("Colonist died!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
