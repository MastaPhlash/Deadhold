# Deadhold: Zombie Survival Colony Sim (Prototype)

## Overview
Deadhold is a prototype for a zombie-themed colony simulation game. The goal is to manage a survivor (colonist) in a post-apocalyptic world, avoiding zombies and surviving as long as possible.

## Features
- **Massive scrollable map** (200x150 tiles) with buildings, trees, and rocks
- **Tile-based movement** with quick tap direction changes (tap arrow key to face direction, hold to move)
- **Player-controlled colonist** with directional sprites and facing system
- **Smart zombie AI** that chases the colonist and attacks walls
- **Resource gathering**: Cut trees for wood, mine rocks for stone
- **Advanced construction system**: Build walls, doors, traps, workstations using resources
- **Day/night cycle** with visual overlay and time display
- **Experience & Research system**: Gain XP, level up, unlock blueprints with skill points
- **Comprehensive building types**: Defensive structures, workstations, and utility buildings
- **Dynamic combat system**: Turrets, spike traps, and trap pits with degradation mechanics
- **Workstation functionality**: Crafting benches and healing campfires
- **Minimap system** showing terrain, entities, and player position
- **Construction planning mode** (B key) to plan builds before execution
- **Comprehensive statistics** tracking kills, resources, buildings built
- **Quality of life features**: Pause, stats overlay, controls popup, auto-save
- **Robust save/load system** preserving all game state
- **Procedural world generation** with smart building placement (no corner doors)

## Controls
- **Arrow keys**: Quick tap to change facing direction, hold to move
- **A key**: Action - attack zombies, harvest trees/rocks, open doors (in facing direction)
- **E key**: Use/interact - doors, workbenches, campfires when standing on them
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

### Advanced Building System

#### Defensive Structures
- **Wood Wall**: 1 wood, 100 HP - Basic defense
- **Stone Wall**: 2 stone, 300 HP - Strong defense (3x wood wall durability)
- **Door**: 2 wood, 100 HP - Toggle open/closed with E key
- **Spike Trap**: 2 wood + 1 stone, 50 HP - Damages zombies walking through (10 DPS), degrades with use
- **Trap Pit**: 3 stone, 75 HP - Heavy damage + slows zombies (20 DPS), more durable than spikes
- **Turret**: 5 stone, 100 HP - Auto-attacks zombies within 5 tiles (50 damage, 10 frame cooldown)

#### Workstations & Utility
- **Workbench**: 3 wood, 150 HP - Stand on it and press E to craft bonus resources
  - Takes 6 seconds to complete
  - Rewards: +1 wood, +1 stone, +2 XP
  - Glows yellow when in use
- **Campfire**: 1 wood + 1 stone, 75 HP - Healing and utility station
  - Press E to light/extinguish
  - Heals nearby colonist (+5 HP every 2 seconds within 2 tiles)
  - Consumes fuel over time (visual fuel bar)
  - Shows `campfire.png` when lit, `campfire_off.png` when extinguished

### Combat & Defense Mechanics

#### Zombie Behavior
- Zombies move every 4 frames toward the colonist
- **NEW**: Zombies walk through spike traps and trap pits (taking damage)
- Zombies still attack solid walls and structures (25 damage)
- Player attacks deal 50 damage to zombies

#### Trap Mechanics
- **Spike Traps**: Zombies walk through and take 10 damage per frame
  - Spikes degrade: 1 HP lost per frame of zombie contact
  - 50 HP = 50 frames of continuous use before destruction
- **Trap Pits**: Zombies walk through taking heavy damage + movement penalty
  - Deal 20 damage per frame + reset zombie movement counter (slows them)
  - Degrade slower: 0.5 HP lost per frame of zombie contact
  - 75 HP = 150 frames of continuous use before destruction

#### Automated Defense
- **Turrets**: Auto-target nearest zombie within 5-tile range
- Shoot bullets that deal 50 damage on impact
- 10-frame cooldown between shots

### Time & Wave System
- Day/night cycle with visual indicators
- New zombie waves spawn every 2 minutes + at dawn
- Wave size increases with each day survived (base 5 + day number)

### Workstation Systems

#### Workbench Crafting
1. Build workbench (3 wood)
2. Stand on workbench and press E
3. Wait 6 seconds (workbench glows yellow)
4. Receive +1 wood, +1 stone, +2 XP

#### Campfire Healing
1. Build campfire (1 wood + 1 stone)
2. Press E while standing on it to light/extinguish
3. Stay within 2 tiles of lit campfire
4. Automatically heal +5 HP every 2 seconds
5. Campfire consumes fuel over time (orange fuel bar)

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

## Strategy Tips

### Early Game
- **Movement**: Tap arrow keys to turn, hold to move
- **Harvesting**: Face trees/rocks and press A to gather resources
- **First builds**: Wood walls and doors for basic shelter
- **Resource priority**: Gather wood first, then stone for stronger defenses

### Mid Game  
- **Defense layers**: Create spike trap fields leading to your base
- **Workstation setup**: Build workbench for resource generation
- **Healing station**: Place campfire in secure area for health recovery
- **Turret placement**: Position turrets to cover trap fields

### Late Game
- **Stone walls**: Upgrade to stone walls for maximum durability
- **Trap combinations**: Use both spikes and trap pits for layered defense
- **Multiple workstations**: Build several workbenches for faster resource generation
- **Strategic campfires**: Place campfires at key defensive positions

### Advanced Tactics
- **Trap maintenance**: Monitor trap HP and replace before they break
- **Fuel management**: Keep campfires fueled by standing near them
- **Planning mode**: Use B key to design complex defensive layouts
- **Save management**: Use F5 frequently to preserve progress

## Quality of Life Features
- **Pause system** (P key) to plan your next moves
- **Statistics overlay** (Shift+TAB) showing detailed progress
- **Construction planning** (B key) to design before building
- **Auto-save** every 5 minutes with countdown display
- **Minimap** in bottom-right showing world overview
- **Controls popup** (H key) for quick reference
- **Visual feedback** with health bars, night overlay, fuel bars, and status indicators
- **Smart building generation** (doors never appear in building corners)

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
- `grass.png` - Ground texture (base layer)
- `floor.png` - Building interior floors (over grass)

**Combat & Defense:**
- `spike.png` - Spike traps (show degradation with HP bar)
- `turret.png` - Defensive turrets
- `trap_pit.png` - Trap pits (heavy damage + slow)
- `door_open.png` - Open doors (optional)

**Workstations & Utility:**
- `workbench.png` - Crafting workbench (glows when in use)
- `campfire.png` - Lit campfire (shows fuel bar)
- `campfire_off.png` - Extinguished campfire

**Directional Sprites (Optional):**
- `colonist_up.png`, `colonist_down.png`, `colonist_left.png`, `colonist_right.png`
- `zombie_up.png`, `zombie_down.png`, `zombie_left.png`, `zombie_right.png`

The game displays colored rectangles as placeholders if images are missing, but looks much better with proper sprites!

## Recent Updates
- **Workbench system**: Interactive crafting station with visual feedback
- **Campfire mechanics**: Healing station with fuel system and on/off states
- **Improved trap behavior**: Zombies walk through traps instead of attacking them
- **Trap degradation**: Spikes and pits slowly break down from use
- **Visual improvements**: Grass as base layer, better layering system
- **Smart building generation**: Doors no longer generate in building corners
- **Enhanced save/load**: Support for all new building types and states

---
*This is an active prototype with fully functional survival, crafting, and defensive mechanics.*
