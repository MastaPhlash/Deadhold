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
                        # Check if this is a corner position
                        is_corner = ((x == bx or x == bx + bw - 1) and 
                                   (y == by or y == by + bh - 1))
                        
                        # Random door placement (only if not a corner)
                        if (not is_corner and random.random() < 0.08 and 
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
        """Spikes damage zombies and slowly degrade when stepped on"""
        alive_zombies = [z for z in zombies if z.hp > 0]
        
        # Create a position lookup for faster collision detection
        zombie_positions = {(z.x, z.y): z for z in alive_zombies}
        
        for spike in spikes:
            if spike.hp <= 0:
                continue
            zombie = zombie_positions.get((spike.x, spike.y))
            if zombie:
                # Deal damage to zombie standing on spike
                zombie.hp -= 10
                
                # Slowly degrade the spike from use (1 damage per frame a zombie is on it)
                spike.hp -= 1
                
                # Visual feedback when spike deals damage
                spike.last_damage_time = pygame.time.get_ticks()

    @staticmethod
    def update_trap_pits(trap_pits, zombies):
        """Trap pits deal heavy damage and slow zombies, plus degrade slowly"""
        alive_zombies = [z for z in zombies if z.hp > 0]
        
        # Create a position lookup for faster collision detection
        zombie_positions = {(z.x, z.y): z for z in alive_zombies}
        
        for trap_pit in trap_pits:
            if trap_pit.hp <= 0:
                continue
            zombie = zombie_positions.get((trap_pit.x, trap_pit.y))
            if zombie:
                # Deal heavy damage every frame (20 damage per frame at 5 FPS = 100 DPS)
                zombie.hp -= 20
                # Slow down zombie movement by resetting move counter
                zombie.move_counter = 0
                
                # Trap pits degrade slower than spikes (0.5 damage per frame)
                trap_pit.hp -= 0.5
                
                # Visual feedback when trap pit deals damage
                trap_pit.last_damage_time = pygame.time.get_ticks()

class MinimapSystem:
    def __init__(self, minimap_size=150):
        self.size = minimap_size
        self.scale = 3  # 3x zoom: each minimap pixel = 3x3 world tiles
        self.surface = None
        self.update_counter = 0  # Only update every few frames
    
    def initialize(self, MAP_WIDTH, MAP_HEIGHT):
        minimap_w = self.size
        minimap_h = self.size
        self.surface = pygame.Surface((minimap_w, minimap_h))
    
    def update(self, MAP_WIDTH, MAP_HEIGHT, colonist, zombies, walls, trees, rocks):
        # Store latest state for draw()
        self.last_map_width = MAP_WIDTH
        self.last_map_height = MAP_HEIGHT
        self.last_colonist = colonist
        self.last_zombies = zombies
        self.last_walls = walls
        self.last_trees = trees
        self.last_rocks = rocks
        # No need to update self.surface anymore (draw handles rendering)
        self.update_counter += 1
        # Optionally, skip some updates for performance
        # if self.update_counter % 5 != 0:
        #     return
        # self.surface.fill((20, 40, 20))
        # ...old code removed...

    def draw(self, screen, SCREEN_WIDTH, SCREEN_HEIGHT, position="topright"):
        if self.surface:
            # --- Begin new zoomed minimap scaling logic ---
            # The minimap surface is always self.size x self.size
            # But the zoomed-in area (view) is smaller, then scaled up to fill the minimap
            view_size = self.size // self.scale  # e.g. 150//3 = 50
            if view_size < 1:
                view_size = 1
            # Create a temp surface for the zoomed-in area
            temp_surface = pygame.Surface((view_size, view_size))
            temp_surface.fill((20, 40, 20))
            # Center view on colonist
            colonist = getattr(self, 'last_colonist', None)
            map_width = getattr(self, 'last_map_width', None)
            map_height = getattr(self, 'last_map_height', None)
            trees = getattr(self, 'last_trees', [])
            rocks = getattr(self, 'last_rocks', [])
            walls = getattr(self, 'last_walls', [])
            zombies = getattr(self, 'last_zombies', [])
            if colonist and map_width and map_height:
                min_x = colonist.x - view_size // 2
                min_y = colonist.y - view_size // 2
                for px in range(view_size):
                    for py in range(view_size):
                        world_x = min(max(min_x + px, 0), map_width - 1)
                        world_y = min(max(min_y + py, 0), map_height - 1)
                        color = (20, 40, 20)
                        for tree in trees:
                            if not tree.cut_down and tree.x == world_x and tree.y == world_y:
                                color = (0, 150, 0)
                        for rock in rocks:
                            if not rock.mined and rock.x == world_x and rock.y == world_y:
                                color = (100, 100, 100)
                        for wall in walls:
                            if wall.x == world_x and wall.y == world_y:
                                color = (120, 120, 120)
                        for zombie in zombies:
                            if zombie.x == world_x and zombie.y == world_y:
                                color = (200, 0, 0)
                        temp_surface.set_at((px, py), color)
                # Draw colonist last (always on top, center)
                colonist_px = view_size // 2
                colonist_py = view_size // 2
                if 0 <= colonist_px < view_size and 0 <= colonist_py < view_size:
                    temp_surface.set_at((colonist_px, colonist_py), (0, 255, 0))
            # Scale temp_surface to minimap size
            scaled_surface = pygame.transform.scale(temp_surface, (self.size, self.size))
            # Draw at correct position
            if position == "bottomright":
                x = SCREEN_WIDTH - self.size - 10
                y = SCREEN_HEIGHT - self.size - 10
            else:
                x = SCREEN_WIDTH - self.size - 10
                y = 10
            screen.blit(scaled_surface, (x, y))
            pygame.draw.rect(screen, (255, 255, 255), (x-1, y-1, self.size+2, self.size+2), 1)
            # --- End new minimap logic ---

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
