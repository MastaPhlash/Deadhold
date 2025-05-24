import random
import pygame
from entities import Tree, Rock, Wall, Door

class MapGenerator:
    @staticmethod
    def generate_buildings(MAP_WIDTH, MAP_HEIGHT, count=10):
        """Generate random buildings with walls, doors, and floors"""
        walls = []
        doors = []
        floors = []
        
        for _ in range(count):
            bx = random.randint(5, MAP_WIDTH - 10)
            by = random.randint(5, MAP_HEIGHT - 10)
            bw = random.randint(3, 7)
            bh = random.randint(3, 7)
            wall_type = "stone" if random.random() < 0.5 else "wood"
            
            # Place floor tiles (interior and under top row)
            for x in range(bx + 1, bx + bw - 1):
                for y in range(by, by + bh - 1):
                    if (x, y) not in floors:
                        floors.append((x, y))
            
            # Place walls and doors on perimeter
            for x in range(bx, bx + bw):
                for y in range(by, by + bh):
                    if x == bx or x == bx + bw - 1 or y == by or y == by + bh - 1:
                        # Random door placement
                        if (random.random() < 0.08 and 
                            ((y == by or y == by + bh - 1) or (x == bx or x == bx + bw - 1))):
                            if not any(d.x == x and d.y == y for d in doors):
                                doors.append(Door(x, y))
                        else:
                            if (not any(w.x == x and w.y == y for w in walls) and 
                                not any(d.x == x and d.y == y for d in doors)):
                                walls.append(Wall(x, y, wall_type=wall_type))
        
        return walls, doors, floors

    @staticmethod
    def generate_resources(MAP_WIDTH, MAP_HEIGHT, walls, doors, floors, tree_count=300, rock_count=150):
        """Generate trees and rocks scattered across the map"""
        trees = []
        rocks = []
        
        # Generate trees
        for _ in range(tree_count):
            tx = random.randint(1, MAP_WIDTH - 2)
            ty = random.randint(1, MAP_HEIGHT - 2)
            if (not any(w.x == tx and w.y == ty for w in walls) and
                not any(d.x == tx and d.y == ty for d in doors) and
                (tx, ty) not in floors):
                trees.append(Tree(tx, ty))

        # Generate rocks
        for _ in range(rock_count):
            rx = random.randint(1, MAP_WIDTH - 2)
            ry = random.randint(1, MAP_HEIGHT - 2)
            if (not any(w.x == rx and w.y == ry for w in walls) and
                not any(d.x == rx and d.y == ry for d in doors) and
                not any(t.x == rx and t.y == ry for t in trees) and
                (rx, ry) not in floors):
                rocks.append(Rock(rx, ry))
        
        return trees, rocks

class TimeSystem:
    def __init__(self, minutes_per_step=15):
        self.minutes_per_step = minutes_per_step
        self.ticks_per_step = 10  # 5 FPS * 2
        self.total_steps = 24 * 60 // minutes_per_step
        self.current_step = (6 * 60) // minutes_per_step  # Start at 6:00 AM
        self.ticks = 0

    def update(self):
        self.ticks += 1
        if self.ticks % self.ticks_per_step == 0:
            self.current_step = (self.current_step + 1) % self.total_steps

    def get_time(self):
        hour = (self.current_step * self.minutes_per_step) // 60
        minute = (self.current_step * self.minutes_per_step) % 60
        return hour, minute

    def is_night(self):
        hour, _ = self.get_time()
        return not (6 <= hour < 21)

    def is_new_day(self):
        hour, minute = self.get_time()
        return hour == 6 and minute == 0 and self.ticks % self.ticks_per_step == 0

class WaveSystem:
    def __init__(self, fps=5, wave_interval_minutes=2, base_zombies=5):
        self.wave_timer = 0
        self.wave_interval = fps * 60 * wave_interval_minutes
        self.base_zombies = base_zombies
        self.day_count = 1

    def update(self, time_system):
        self.wave_timer += 1
        
        # New day wave
        if time_system.is_new_day():
            self.day_count += 1
            return self.base_zombies + self.day_count - 1
        
        # Timed wave
        if self.wave_timer >= self.wave_interval:
            self.wave_timer = 0
            return self.base_zombies + self.day_count - 1
        
        return 0

class ExperienceSystem:
    @staticmethod
    def check_level_up(xp, level, skill_points, xp_to_next):
        leveled = False
        while xp >= xp_to_next:
            xp -= xp_to_next
            level += 1
            skill_points += 1
            xp_to_next = int(xp_to_next * 1.5)
            leveled = True
        return xp, level, skill_points, xp_to_next, leveled

class CombatSystem:
    @staticmethod
    def update_turrets(turrets, zombies, bullets, Bullet):
        """Optimized turret AI with spatial optimization"""
        # Pre-filter zombies that are alive
        alive_zombies = [z for z in zombies if z.hp > 0]
        
        for turret in turrets:
            if turret.hp <= 0 or turret.cooldown > 0:
                if turret.cooldown > 0:
                    turret.cooldown -= 1
                continue
            
            # Quick distance check - only consider zombies within rough range first
            nearby_zombies = [z for z in alive_zombies 
                            if abs(z.x - turret.x) <= 5 and abs(z.y - turret.y) <= 5]
            
            if not nearby_zombies:
                continue
                
            # Find nearest zombie in exact range
            min_dist = 999
            target_z = None
            for z in nearby_zombies:
                dist = abs(z.x - turret.x) + abs(z.y - turret.y)
                if dist <= 5 and dist < min_dist:
                    min_dist = dist
                    target_z = z
            
            if target_z:
                dx = target_z.x - turret.x
                dy = target_z.y - turret.y
                # Normalize direction
                if abs(dx) > abs(dy):
                    dx = 1 if dx > 0 else -1
                    dy = 0
                else:
                    dy = 1 if dy > 0 else -1
                    dx = 0
                bullets.append(Bullet(turret.x, turret.y, dx, dy))
                turret.cooldown = 10

    @staticmethod
    def update_bullets(bullets, zombies, MAP_WIDTH, MAP_HEIGHT):
        """Optimized bullet collision detection"""
        alive_zombies = [z for z in zombies if z.hp > 0]
        
        for bullet in bullets[:]:
            bullet.update()
            
            # Remove if out of bounds or expired
            if (bullet.x < 0 or bullet.y < 0 or 
                bullet.x >= MAP_WIDTH or bullet.y >= MAP_HEIGHT or 
                bullet.timer > 20):
                bullets.remove(bullet)
                continue
            
            # Optimized collision - only check nearby zombies
            hit = False
            for z in alive_zombies:
                if z.x == bullet.x and z.y == bullet.y:
                    z.hp -= 50
                    bullets.remove(bullet)
                    hit = True
                    break
            
            if hit:
                break

    @staticmethod
    def update_spikes(spikes, zombies):
        """Optimized spike damage with spatial optimization"""
        alive_zombies = [z for z in zombies if z.hp > 0]
        
        # Create a position lookup for faster collision detection
        zombie_positions = {(z.x, z.y): z for z in alive_zombies}
        
        for spike in spikes:
            if spike.hp <= 0:
                continue
            zombie = zombie_positions.get((spike.x, spike.y))
            if zombie:
                zombie.hp -= 10

class MinimapSystem:
    def __init__(self, minimap_size=150):
        self.size = minimap_size
        self.scale = 1
        self.surface = None
        self.update_counter = 0  # Only update every few frames
        
    def initialize(self, MAP_WIDTH, MAP_HEIGHT):
        self.scale = max(MAP_WIDTH // self.size, MAP_HEIGHT // self.size, 1)
        minimap_w = MAP_WIDTH // self.scale
        minimap_h = MAP_HEIGHT // self.scale
        self.surface = pygame.Surface((minimap_w, minimap_h))
        
    def update(self, MAP_WIDTH, MAP_HEIGHT, colonist, zombies, walls, trees, rocks):
        if not self.surface:
            return
        
        # Only update minimap every 5 frames for performance
        self.update_counter += 1
        if self.update_counter % 5 != 0:
            return
            
        self.surface.fill((20, 40, 20))
        
        # Batch set pixels for better performance
        pixels_to_set = []
        
        # Draw terrain features
        for tree in trees:
            if not tree.cut_down:
                px, py = tree.x // self.scale, tree.y // self.scale
                if 0 <= px < self.surface.get_width() and 0 <= py < self.surface.get_height():
                    pixels_to_set.append(((px, py), (0, 150, 0)))
                    
        for rock in rocks:
            if not rock.mined:
                px, py = rock.x // self.scale, rock.y // self.scale
                if 0 <= px < self.surface.get_width() and 0 <= py < self.surface.get_height():
                    pixels_to_set.append(((px, py), (100, 100, 100)))
                    
        for wall in walls:
            px, py = wall.x // self.scale, wall.y // self.scale
            if 0 <= px < self.surface.get_width() and 0 <= py < self.surface.get_height():
                pixels_to_set.append(((px, py), (120, 120, 120)))
        
        # Draw zombies (only nearby ones for performance)
        nearby_zombies = [z for z in zombies if abs(z.x - colonist.x) < 50 and abs(z.y - colonist.y) < 50]
        for zombie in nearby_zombies:
            px, py = zombie.x // self.scale, zombie.y // self.scale
            if 0 <= px < self.surface.get_width() and 0 <= py < self.surface.get_height():
                pixels_to_set.append(((px, py), (200, 0, 0)))
                
        # Set all pixels at once
        for pos, color in pixels_to_set:
            self.surface.set_at(pos, color)
        
        # Draw colonist last (always on top)
        cx, cy = colonist.x // self.scale, colonist.y // self.scale
        if 0 <= cx < self.surface.get_width() and 0 <= cy < self.surface.get_height():
            self.surface.set_at((cx, cy), (0, 255, 0))

    def draw(self, screen, SCREEN_WIDTH, SCREEN_HEIGHT, position="topright"):
        if self.surface:
            if position == "bottomright":
                x = SCREEN_WIDTH - self.surface.get_width() - 10
                y = SCREEN_HEIGHT - self.surface.get_height() - 10
            else:
                x = SCREEN_WIDTH - self.surface.get_width() - 10
                y = 10
            screen.blit(self.surface, (x, y))
            pygame.draw.rect(screen, (255, 255, 255), 
                           (x-1, y-1, self.surface.get_width()+2, self.surface.get_height()+2), 1)

class ConstructionPlanningSystem:
    def __init__(self):
        self.planning_mode = False
        self.planned_buildings = []  # List of (x, y, blueprint_name)
        
    def toggle_planning_mode(self):
        self.planning_mode = not self.planning_mode
        
    def add_planned_building(self, x, y, blueprint_name):
        # Remove existing plan at this location
        self.planned_buildings = [(px, py, bp) for px, py, bp in self.planned_buildings if px != x or py != y]
        self.planned_buildings.append((x, y, blueprint_name))
        
    def remove_planned_building(self, x, y):
        self.planned_buildings = [(px, py, bp) for px, py, bp in self.planned_buildings if px != x or py != y]
        
    def clear_all_plans(self):
        self.planned_buildings.clear()
        
    def get_plan_at(self, x, y):
        for px, py, bp in self.planned_buildings:
            if px == x and py == y:
                return bp
        return None
        
    def draw_plans(self, screen, cam_x, cam_y, load_image_func, TILE_SIZE):
        if not self.planning_mode:
            return
            
        # Simple fallback for now - just draw colored rectangles
        for x, y, blueprint_name in self.planned_buildings:
            screen_x = x * TILE_SIZE - cam_x
            screen_y = y * TILE_SIZE - cam_y
            
            # Only draw if on screen
            if -TILE_SIZE <= screen_x <= screen.get_width() and -TILE_SIZE <= screen_y <= screen.get_height():
                # Draw semi-transparent colored rectangle
                s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                s.fill((100, 100, 255))
                s.set_alpha(128)
                screen.blit(s, (screen_x, screen_y))

class JobSystem:
    def __init__(self):
        self.job_queue = []  # List of jobs to be done
        self.priorities = {
            "mining": 3,
            "woodcutting": 3,
            "construction": 2,
            "hauling": 1
        }
        
    def add_job(self, job_type, x, y, priority=None):
        if priority is None:
            priority = self.priorities.get(job_type, 1)
        self.job_queue.append({
            "type": job_type,
            "x": x,
            "y": y,
            "priority": priority,
            "assigned": False
        })
        # Sort by priority (higher first)
        self.job_queue.sort(key=lambda j: j["priority"], reverse=True)
        
    def get_next_job(self):
        for job in self.job_queue:
            if not job["assigned"]:
                job["assigned"] = True
                return job
        return None
        
    def complete_job(self, job):
        if job in self.job_queue:
            self.job_queue.remove(job)
            
    def cancel_job(self, x, y):
        self.job_queue = [j for j in self.job_queue if j["x"] != x or j["y"] != y]

class GameStatistics:
    def __init__(self):
        self.stats = {
            "zombies_killed": 0,
            "trees_cut": 0,
            "rocks_mined": 0,
            "buildings_built": 0,
            "wood_gathered": 0,
            "stone_gathered": 0,
            "days_survived": 0,
            "damage_taken": 0,
            "start_time": pygame.time.get_ticks()
        }
        
    def increment(self, stat_name, amount=1):
        if stat_name in self.stats:
            self.stats[stat_name] += amount
            
    def get_playtime_minutes(self):
        return (pygame.time.get_ticks() - self.stats["start_time"]) // 60000
        
    def draw_stats_overlay(self, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
        font = pygame.font.SysFont(None, 24)
        y_offset = 100
        
        # Create semi-transparent background
        overlay = pygame.Surface((250, 200))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (SCREEN_WIDTH - 260, y_offset))
        
        stats_to_show = [
            ("Days Survived", self.stats["days_survived"]),
            ("Zombies Killed", self.stats["zombies_killed"]),
            ("Trees Cut", self.stats["trees_cut"]),
            ("Rocks Mined", self.stats["rocks_mined"]),
            ("Buildings Built", self.stats["buildings_built"]),
            ("Playtime", f"{self.get_playtime_minutes()}m")
        ]
        
        for i, (label, value) in enumerate(stats_to_show):
            text = font.render(f"{label}: {value}", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH - 250, y_offset + 10 + i * 25))
