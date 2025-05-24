# Deadhold: Zombie Survival Colony Sim (Prototype)

## Overview
Deadhold is a prototype for a zombie-themed colony simulation game inspired by RimWorld. The goal is to manage a survivor (colonist) in a post-apocalyptic world, avoiding zombies and surviving as long as possible.

## Features
- Massive scrollable map (200x150 tiles)
- Tile-based map with grid movement
- Player-controlled colonist
- Zombies that chase the colonist
- Trees that can be cut for wood (resource)
- Rocks that can be mined for stone (resource)
- Walls require wood or stone to build (stone walls are 3x stronger)
- **Day and night cycle**
- Simple health and collision mechanics
- Experience system: gain XP for gathering and killing zombies, level up for skill points
- Research menu to unlock new blueprints (press R)
- Scroll through buildable items (TAB) and see a preview before building
- Modular and extensible codebase for future features
- Robust save/load system that captures all game state

## Controls
- Arrow keys: Move the colonist (up, down, left, right) and set facing direction
- Spacebar: Build at colonist's position (costs resources)
- **A key**: Attack in the direction you are facing (damages zombies, cuts trees for wood, or mines rocks for stone)
- **TAB**: Scroll through unlocked build blueprints
- **R**: Open/close research menu (spend skill points to unlock new blueprints)
- **F5**: Save game (all progress, research, and resources)
- **F9**: Load game
- **Escape**: Quit the game or close research menu
- Close window: Quit the game

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

## Planned Features
- Base building and resource management
- Multiple colonists with unique traits
- Advanced zombie AI and infection mechanics
- Procedural map generation
- Dynamic events and research system

## Credits
- Prototype code by MastaPhlash
- Uses [pygame](https://www.pygame.org/)

## Tips
- Your colonist attacks only in the direction they are facing (indicated by a yellow square).
- You must have wood to build walls. Attack trees to gather wood.
- Attack rocks to gather stone. Stone will be used for advanced building in the future.
- The camera scrolls to keep your colonist centered as you explore the huge map.
- Press **F5** to save and **F9** to load your game at any time.
- The game alternates between day and night. At night, the world is darker.
- Gain XP by chopping trees, mining rocks, and killing zombies. Level up to earn skill points.
- Spend skill points in the research menu (R) to unlock new blueprints.
- Use TAB to scroll through unlocked build options and see a preview before building.

## Assets Needed

For the new blueprints in the research/build system, add these PNG files to your `assets` folder:

- `wall.png` (for "Wood Wall")
- `stone_wall.png` (for "Stone Wall")
- `spike.png` (for the "Spike Trap" blueprint)
- `turret.png` (for the "Turret" blueprint)

Place these files in:
```
x:\Coding\Python\Deadhold-1\assets\
```

If you don't have custom images, you can use placeholder PNGs with the correct names and sizes (64x64 pixels).

---
*This is an early prototype. Contributions and feedback are welcome!*
