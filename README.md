# Deadhold: Zombie Survival Colony Sim (Prototype)

## Overview
Deadhold is a prototype for a zombie-themed colony simulation game inspired by RimWorld. The goal is to manage a survivor (colonist) in a post-apocalyptic world, avoiding zombies and surviving as long as possible.

## Features
- **Massive scrollable map** (200x150 tiles) with buildings, trees, and rocks
- **Tile-based movement** with quick tap direction changes (tap arrow key to face direction, hold to move)
- **Player-controlled colonist** with directional sprites and facing system
- **Smart zombie AI** that chases the colonist and attacks walls
- **Resource gathering**: Cut trees for wood, mine rocks for stone
- **Construction system**: Build walls, doors, spikes, turrets using resources
- **Day/night cycle** with visual overlay and time display
- **Experience & Research system**: Gain XP, level up, unlock blueprints with skill points
- **Advanced building types**: Wood/stone walls, doors, spike traps, defensive turrets
- **Combat system**: Turrets auto-fire at zombies, spikes damage enemies
- **Minimap system** showing terrain, entities, and player position
- **Construction planning mode** (B key) to plan builds before execution
- **Comprehensive statistics** tracking kills, resources, buildings built
- **Quality of life features**: Pause, stats overlay, controls popup, auto-save
- **Robust save/load system** preserving all game state
- **Procedural world generation** with buildings, floors, and scattered resources

## Controls
- **Arrow keys**: Quick tap to change facing direction, hold to move
- **A key**: Action - attack zombies, harvest trees/rocks, open doors (in facing direction)
- **E key**: Use door when standing on it (open/close)
- **Space**: Build selected item at current position
- **TAB**: Cycle through unlocked blueprints
- **R**: Open/close research menu
- **P**: Pause/unpause game
- **B**: Toggle construction planning mode
- **C**: Clear all construction plans (when in planning mode)
- **H**: Show/hide controls popup
- **Shift+TAB**: Show/hide statistics overlay
- **F5**: Save game
- **F9**: Load game
- **Escape**: Quit game or close menus

## Game Systems

### Movement & Facing
- Quick tap arrow keys to change facing direction instantly
- Hold arrow keys for 2+ frames to move in that direction
- Facing determines attack/harvest direction and sprite display

### Resource Management
- **Wood**: Gathered from trees (2 wood per tree)
- **Stone**: Gathered from rocks (2 stone per rock)
- Trees and rocks block movement until harvested

### Building System
- **Wood Wall**: 1 wood, 100 HP
- **Stone Wall**: 2 stone, 300 HP (3x stronger)
- **Door**: 2 wood, can be opened/closed
- **Spike Trap**: 2 wood + 1 stone, damages zombies
- **Turret**: 5 stone, auto-attacks zombies in range

### Combat
- Zombies move every 4 frames toward the colonist
- Zombies attack walls if blocked (25 damage)
- Turrets auto-target zombies within 5 tiles
- Spikes damage zombies that walk on them (10 damage)
- Player attacks deal 50 damage to zombies

### Time & Waves
- Day/night cycle with visual indicators
- New zombie waves spawn periodically
- Wave size increases with each day survived

## How to Run
1. Install Python 3.x
2. Install pygame:
   ```
   pip install pygame
   ```
3. Run the game:
   ```
   python main.py
   ```

## Tips
- **Movement**: Tap arrow keys to turn, hold to move
- **Harvesting**: Face trees/rocks and press A to gather resources
- **Defense**: Build walls and doors to create safe areas
- **Combat**: Use spike traps and turrets for automated defense
- **Planning**: Use B key to plan builds, then execute when you have resources
- **Survival**: Monitor your HP - zombies deal 1 damage per contact
- **Research**: Gain XP by gathering, building, and killing zombies
- **Save often**: Use F5 to save your progress

## Quality of Life Features
- **Pause system** (P key) to plan your next moves
- **Statistics overlay** (Shift+TAB) showing detailed progress
- **Construction planning** (B key) to design before building
- **Auto-save** every 5 minutes with countdown display
- **Minimap** in bottom-right showing world overview
- **Controls popup** (H key) for quick reference
- **Visual feedback** with health bars, night overlay, and status indicators

## Assets Needed

Place these 64x64 pixel PNG files in `x:\Coding\Python\Deadhold-1\assets\`:

**Essential:**
- `colonist.png` - Main player character
- `zombie.png` - Enemy zombies
- `tree.png` - Trees (should be 64x128 pixels tall)
- `rock.png` - Mineable rocks
- `wall.png` - Wood walls
- `stone_wall.png` - Stone walls
- `door.png` - Closed doors
- `grass.png` - Ground texture
- `floor.png` - Building interior floors

**Combat & Defense:**
- `spike.png` - Spike traps
- `turret.png` - Defensive turrets
- `door_open.png` - Open doors (optional)

**Future Research Items:**
- `campfire.png` - Campfire
- `workbench.png` - Workbench  
- `trap_pit.png` - Trap pit

**Directional Sprites (Optional):**
- `colonist_up.png`, `colonist_down.png`, `colonist_left.png`, `colonist_right.png`
- `zombie_up.png`, `zombie_down.png`, `zombie_left.png`, `zombie_right.png`

The game will display colored rectangles if images are missing, but looks much better with proper sprites!

---
*This is an active prototype. The core survival mechanics are implemented and functional.*
