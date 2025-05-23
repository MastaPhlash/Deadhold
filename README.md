# Deadhold: Zombie Survival Colony Sim (Prototype)

## Overview
Deadhold is a prototype for a zombie-themed colony simulation game inspired by RimWorld. The goal is to manage a survivor (colonist) in a post-apocalyptic world, avoiding zombies and surviving as long as possible.

## Features
- Massive scrollable map (200x150 tiles)
- Tile-based map with grid movement
- Player-controlled colonist
- Zombies that chase the colonist
- Trees that can be cut for wood (resource)
- Walls require wood to build
- Simple health and collision mechanics

## Controls
- Arrow keys: Move the colonist (up, down, left, right) and set facing direction
- Spacebar: Build a wall at colonist's position (costs 1 wood)
- **A key**: Attack in the direction you are facing (damages zombies or cuts trees for wood)
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
- Prototype code by [Your Name]
- Inspired by RimWorld (by Ludeon Studios)
- Uses [pygame](https://www.pygame.org/)

## Tips
- Your colonist attacks only in the direction they are facing (indicated by a yellow square).
- You must have wood to build walls. Attack trees to gather wood.
- The camera scrolls to keep your colonist centered as you explore the huge map.

---
*This is an early prototype. Contributions and feedback are welcome!*
