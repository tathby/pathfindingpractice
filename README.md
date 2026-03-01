# pathfindingpractice
# BFS + DFS Pathfinding (Python Console)

## Run
```bash
python pathfinding.py
```

At startup, choose:
- `1` to view the BFS/DFS pathfinding demos on built-in maps
- `2` to play the monster chase game

## Monster Chase
- Tiles: `#` wall, `.` floor, `P` player, `M` monster, `G` exit
- Move with `WASD`
- Monster recomputes a path to the player each turn and moves one step
- Monster solver mode is controlled by `MODE = "BFS"` or `MODE = "DFS"` in `pathfinding.py`

After each game/demo, the app prompts:
- `Hit any key to return to the main menu...`

## BFS vs DFS (example comparison)
Use **Example Map 2** from `pathfinding.py` as a direct comparison map.

- BFS result on this map: `path_len=12`, `visited=33`
- DFS result on this map: `path_len=26`, `visited=32`

So on this map, the **DFS path is longer than the BFS path**.

### Why BFS tends to guarantee shortest path (and DFS does not)
- BFS explores in **layers by distance** from the start.
- With equal step cost and 4-direction moves, the first time BFS reaches `G`, it has found the minimum-number-of-steps path.
- DFS goes deep along one branch first; it may reach `G` through a long route before trying other branches.
- Because of that search order, DFS can return a valid path that is not shortest.

### Why visited counts can differ
- `visited` depends on search order and when the goal is discovered.
- BFS may visit more tiles overall before reaching goal if many same-depth alternatives exist.
- DFS may visit fewer or more depending on branch ordering, but its path quality is not guaranteed.
