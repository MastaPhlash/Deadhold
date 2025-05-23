import pygame

font = pygame.font.SysFont(None, 28)

def draw_hud(surface, colonist):
    hp_text = font.render(f"HP: {colonist.hp}", True, (255, 255, 0))
    surface.blit(hp_text, (10, 5))
