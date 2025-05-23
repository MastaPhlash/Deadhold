import pygame

def draw_hud(surface, colonist, wood):
    font = pygame.font.SysFont(None, 28)
    hp_text = font.render(f"HP: {colonist.hp}", True, (255, 255, 0))
    wood_text = font.render(f"Wood: {wood}", True, (222, 184, 135))
    surface.blit(hp_text, (10, 5))
    surface.blit(wood_text, (120, 5))
