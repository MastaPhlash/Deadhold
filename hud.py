import pygame

def draw_hud(surface, colonist, wood, stone):
    font = pygame.font.SysFont(None, 28)
    hp_text = font.render(f"HP: {colonist.hp}", True, (255, 255, 0))
    wood_text = font.render(f"Wood: {wood}", True, (222, 184, 135))
    stone_text = font.render(f"Stone: {stone}", True, (180, 180, 180))
    surface.blit(hp_text, (10, 5))
    surface.blit(wood_text, (120, 5))
    surface.blit(stone_text, (240, 5))
