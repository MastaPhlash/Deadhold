# Deadhold: Zombie Survival Colony Sim (Prototype)

## Overview
Deadhold is a prototype for a zombie-themed colony simulation game inspired by RimWorld. The goal is to manage a survivor (colonist) in a post-apocalyptic world, avoiding zombies and surviving as long as possible.

## Features
- Massive scrollable map (200x150 tiles)
- Tile-based map with grid movement
- Player-controlled colonist
- Zombies that chase the colonist
- Trees that can be cut for wood (resource) **and block movement until cut**
- Rocks that can be mined for stone (resource) **and block movement until mined**
- Walls require wood or stone to build (stone walls are 3x stronger)
- **Day and night cycle**
- Simple health and collision mechanics
- Experience system: gain XP for gathering and killing zombies, level up for skill points
- Research menu to unlock new blueprints (press R)
- Scroll through buildable items (TAB) and see a preview before building
- Modular and extensible codebase for future features
- Robust save/load system that captures all game state
- Many researchable items: walls, doors, traps, turrets, campfire, workbench, trap pit, and more
- Research can be done in any order
- Doors can be built and opened/closed with the **E** key
- **Camera always centers on colonist for responsive movement**
- **Harvesting resources is always possible when facing a tree or rock**

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
- **E**: Open/close a door when standing on it
- **You cannot walk through trees or rocks until they are harvested.**
- **Camera instantly follows colonist (no lag).**

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
- **You cannot walk through trees or rocks until you harvest them.**
- The camera scrolls to keep your colonist centered as you explore the huge map, with no lag.
- Press **F5** to save and **F9** to load your game at any time.
- The game alternates between day and night. At night, the world is darker.
- Gain XP by chopping trees, mining rocks, and killing zombies. Level up to earn skill points.
- Spend skill points in the research menu (R) to unlock new blueprints.
- Use TAB to scroll through unlocked build options and see a preview before building.

## Assets Needed

For the new blueprints and researchable items, add these PNG files to your `assets` folder:

- `wall.png` (Wood Wall)
- `stone_wall.png` (Stone Wall)
- `spike.png` (Spike Trap)
- `turret.png` (Turret)
- `door.png` (Door, closed)
- `door_open.png` (Door, open)
- `campfire.png` (Campfire)
- `workbench.png` (Workbench)
- `trap_pit.png` (Trap Pit)

**All images should be 64x64 pixels.**

Place these files in:
```
x:\Coding\Python\Deadhold-1\assets\
```

If you don't have custom images, you can use placeholder PNGs with the correct names and sizes.

---
*This is an early prototype. Contributions and feedback are welcome!*
