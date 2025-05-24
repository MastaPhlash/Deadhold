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
- Walls require wood to build
- **Day and night cycle**
- Simple health and collision mechanics

## Controls
- Arrow keys: Move the colonist (up, down, left, right) and set facing direction
- Spacebar: Build a wall at colonist's position (costs 1 wood)
- **A key**: Attack in the direction you are facing (damages zombies, cuts trees for wood, or mines rocks for stone)
- **F5**: Save game
- **F9**: Load game
- **Escape**: Quit the game
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

---
*This is an early prototype. Contributions and feedback are welcome!*
