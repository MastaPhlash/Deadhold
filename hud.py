import pygame

def draw_hud(surface, colonist):
    font = pygame.font.SysFont(None, 28)
    hp_text = font.render(f"HP: {colonist.hp}", True, (255, 255, 0))
    surface.blit(hp_text, (10, 5))
