import random
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
        """Handle turret AI and shooting"""
        for turret in turrets:
            if turret.hp <= 0 or turret.cooldown > 0:
                if turret.cooldown > 0:
                    turret.cooldown -= 1
                continue
            
            # Find nearest zombie in range
            min_dist = 999
            target_z = None
            for z in zombies:
                dist = abs(z.x - turret.x) + abs(z.y - turret.y)
                if dist <= 5 and dist < min_dist and z.hp > 0:
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
        """Update bullet movement and collision"""
        for bullet in bullets[:]:
            bullet.update()
            # Remove if out of bounds or expired
            if (bullet.x < 0 or bullet.y < 0 or 
                bullet.x >= MAP_WIDTH or bullet.y >= MAP_HEIGHT or 
                bullet.timer > 20):
                bullets.remove(bullet)
                continue
            
            # Check zombie hits
            for z in zombies:
                if z.x == bullet.x and z.y == bullet.y and z.hp > 0:
                    z.hp -= 50
                    bullets.remove(bullet)
                    break

    @staticmethod
    def update_spikes(spikes, zombies):
        """Handle spike trap damage"""
        for spike in spikes:
            for z in zombies:
                if z.x == spike.x and z.y == spike.y and z.hp > 0:
                    z.hp -= 10
