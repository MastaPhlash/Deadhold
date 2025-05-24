import pygame

def draw_hud(surface, colonist, wood, stone, build_img=None):
    # Enhanced HUD background
    hud_height = 90
    hud_surface = pygame.Surface((surface.get_width(), hud_height))
    hud_surface.fill((20, 20, 30))
    hud_surface.set_alpha(200)
    surface.blit(hud_surface, (0, 0))
    
    # Main resource display
    font = pygame.font.SysFont(None, 28)
    hp_color = (255, 255, 0) if colonist.hp > 50 else (255, 100, 100)
    hp_text = font.render(f"HP: {colonist.hp}/100", True, hp_color)
    wood_text = font.render(f"Wood: {wood}", True, (222, 184, 135))
    stone_text = font.render(f"Stone: {stone}", True, (180, 180, 180))
    
    surface.blit(hp_text, (10, 5))
    surface.blit(wood_text, (140, 5))
    surface.blit(stone_text, (260, 5))
    
    # Health bar
    hp_bar_width = 100
    hp_percentage = colonist.hp / 100
    pygame.draw.rect(surface, (100, 100, 100), (10, 30, hp_bar_width, 8))
    pygame.draw.rect(surface, hp_color, (10, 30, int(hp_bar_width * hp_percentage), 8))
    
    # Build preview with enhanced info
    if build_img:
        preview_x = surface.get_width() - 150
        preview_y = 10
        
        # Background for build preview
        preview_bg = pygame.Surface((140, 75))
        preview_bg.fill((40, 40, 60))
        preview_bg.set_alpha(180)
        surface.blit(preview_bg, (preview_x - 5, preview_y - 5))
        
        # Build image
        surface.blit(build_img, (preview_x, preview_y))
        
        # Build info text
        font3 = pygame.font.SysFont(None, 18)
        build_text = font3.render("Next Build:", True, (200, 200, 200))
        surface.blit(build_text, (preview_x, preview_y + 65))
