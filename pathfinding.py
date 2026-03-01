from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

Pos = Tuple[int, int]  # (row, col)
Grid = List[List[str]]
MODE = "BFS"  # Monster chase mode: "BFS" or "DFS"


EXAMPLE_MAP_1 = """
##########
#S.......#
#..##.##.#
#...#...G#
##########
""".strip("\n")

EXAMPLE_MAP_2 = """
############
#S.........#
###.##.#.#.#
#...#..#.#G#
#.###..#...#
#......###.#
############
""".strip("\n")

CHASE_MAP = """
############
#P..#.....G#
#.#.#.###..#
#.#...#....#
#.###.#.##.#
#.....#..M.#
############
""".strip("\n")


def parse_grid(text: str) -> Tuple[Grid, Pos, Pos]:
    """
    Convert a multiline string map into a grid plus start and goal positions.

    Map legend:
    '#' wall
    '.' floor
    'S' start (exactly one)
    'G' goal (exactly one)
    """
    rows = [list(line) for line in text.splitlines() if line]
    if not rows:
        raise ValueError("grid is empty")

    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("grid must be rectangular")

    start: Optional[Pos] = None
    goal: Optional[Pos] = None
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "S":
                if start is not None:
                    raise ValueError("grid must contain exactly one S")
                start = (r, c)
            elif ch == "G":
                if goal is not None:
                    raise ValueError("grid must contain exactly one G")
                goal = (r, c)
            elif ch not in {"#", "."}:
                raise ValueError(f"invalid tile {ch!r} at {(r, c)}")

    if start is None or goal is None:
        raise ValueError("grid must contain one S and one G")

    return rows, start, goal


def neighbors(grid: Grid, node: Pos) -> List[Pos]:
    """Return valid 4-direction neighbors that are not walls."""
    r, c = node
    out: List[Pos] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out


def reconstruct_path(parent: Dict[Pos, Pos], start: Pos, goal: Pos) -> Optional[List[Pos]]:
    """Reconstruct path from start->goal using parent pointers. Return None if goal unreachable."""
    if goal == start:
        return [start]
    if goal not in parent:
        return None

    path: List[Pos] = [goal]
    cur = goal
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path


def bfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Queue-based BFS.
    Return (path, visited).
    - path is a list of positions from start to goal (inclusive), or None.
    - visited contains all explored/seen nodes.
    """
    q = deque([start])
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nxt in neighbors(grid, cur):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = cur
            q.append(nxt)

    return reconstruct_path(parent, start, goal), visited


def dfs_path(grid: Grid, start: Pos, goal: Pos) -> Tuple[Optional[List[Pos]], Set[Pos]]:
    """
    Stack-based DFS (iterative, no recursion).
    Return (path, visited).
    """
    stack: List[Pos] = [start]
    visited: Set[Pos] = {start}
    parent: Dict[Pos, Pos] = {}

    while stack:
        cur = stack.pop()
        if cur == goal:
            break
        for nxt in reversed(neighbors(grid, cur)):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = cur
            stack.append(nxt)

    return reconstruct_path(parent, start, goal), visited


def render(grid: Grid, path: Optional[List[Pos]] = None, visited: Optional[Set[Pos]] = None) -> str:
    """
    Render the grid as text.
    Overlay rules (recommended):
    - path tiles shown as '*'
    - visited tiles shown as '·' (middle dot) or '+'
    - preserve 'S' and 'G'
    """
    canvas = [row[:] for row in grid]
    path_set = set(path) if path else set()
    visited_set = visited or set()

    for r, row in enumerate(canvas):
        for c, ch in enumerate(row):
            pos = (r, c)
            if ch in {"S", "G", "#"}:
                continue
            if pos in path_set:
                canvas[r][c] = "*"
            elif pos in visited_set:
                canvas[r][c] = "+"

    return "\n".join("".join(row) for row in canvas)


def parse_chase_grid(text: str) -> Tuple[Grid, Pos, Pos, Pos]:
    rows = [list(line) for line in text.splitlines() if line]
    if not rows:
        raise ValueError("chase map is empty")

    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("chase map must be rectangular")

    player: Optional[Pos] = None
    monster: Optional[Pos] = None
    goal: Optional[Pos] = None

    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "P":
                if player is not None:
                    raise ValueError("chase map must contain exactly one P")
                player = (r, c)
                rows[r][c] = "."
            elif ch == "M":
                if monster is not None:
                    raise ValueError("chase map must contain exactly one M")
                monster = (r, c)
                rows[r][c] = "."
            elif ch == "G":
                if goal is not None:
                    raise ValueError("chase map must contain exactly one G")
                goal = (r, c)
                rows[r][c] = "."
            elif ch not in {"#", "."}:
                raise ValueError(f"invalid chase tile {ch!r} at {(r, c)}")

    if player is None or monster is None or goal is None:
        raise ValueError("chase map must contain one P, one M, and one G")

    return rows, player, monster, goal


def render_chase(grid: Grid, player: Pos, monster: Pos, goal: Pos) -> str:
    canvas = [row[:] for row in grid]
    pr, pc = player
    mr, mc = monster
    gr, gc = goal
    canvas[gr][gc] = "G"
    canvas[mr][mc] = "M"
    canvas[pr][pc] = "P"
    return "\n".join("".join(row) for row in canvas)


def try_move(grid: Grid, pos: Pos, move: str) -> Pos:
    dr_dc = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}
    if move not in dr_dc:
        return pos
    dr, dc = dr_dc[move]
    nr, nc = pos[0] + dr, pos[1] + dc
    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
        return (nr, nc)
    return pos


def chase_path(grid: Grid, start: Pos, goal: Pos) -> Optional[List[Pos]]:
    mode = MODE.upper()
    if mode == "DFS":
        path, _ = dfs_path(grid, start, goal)
    else:
        path, _ = bfs_path(grid, start, goal)
    return path


def play_monster_chase() -> None:
    grid, player, monster, goal = parse_chase_grid(CHASE_MAP)

    print("\nMonster Chase")
    print(f"Mode: {MODE.upper()} (set MODE at top of file to BFS/DFS)")
    print("Controls: w/a/s/d to move, q to quit")

    while True:
        print("\n" + render_chase(grid, player, monster, goal))

        if monster == player:
            print("You lose! The monster caught you.")
            return
        if player == goal:
            print("You win! You reached the exit.")
            return

        cmd = input("Move (WASD, q quit): ").strip().lower()
        if not cmd:
            continue
        if cmd == "q":
            print("Game quit.")
            return

        player = try_move(grid, player, cmd[0])

        if player == goal:
            print("\n" + render_chase(grid, player, monster, goal))
            print("You win! You reached the exit.")
            return

        if monster == player:
            print("\n" + render_chase(grid, player, monster, goal))
            print("You lose! The monster caught you.")
            return

        path = chase_path(grid, monster, player)
        if path and len(path) > 1:
            monster = path[1]

        if monster == player:
            print("\n" + render_chase(grid, player, monster, goal))
            print("You lose! The monster caught you.")
            return


def run_one(label: str, grid_text: str) -> None:
    grid, start, goal = parse_grid(grid_text)

    print("=" * 60)
    print(label)
    print("- Raw map")
    print(render(grid))

    path_bfs, visited_bfs = bfs_path(grid, start, goal)
    print("\n- BFS")
    print(f"found={path_bfs is not None} path_len={(len(path_bfs) if path_bfs else None)} visited={len(visited_bfs)}")
    print(render(grid, path=path_bfs, visited=visited_bfs))

    path_dfs, visited_dfs = dfs_path(grid, start, goal)
    print("\n- DFS")
    print(f"found={path_dfs is not None} path_len={(len(path_dfs) if path_dfs else None)} visited={len(visited_dfs)}")
    print(render(grid, path=path_dfs, visited=visited_dfs))


def run_maps_demo() -> None:
    run_one("Example Map 1", EXAMPLE_MAP_1)
    run_one("Example Map 2", EXAMPLE_MAP_2)


def wait_for_menu() -> None:
    try:
        input("Hit any key to return to the main menu...")
    except EOFError:
        pass


def main() -> None:
    while True:
        print("Pathfinding Practice")
        print("1) View BFS/DFS map demos")
        print("2) Play monster chase game")
        print("q) Quit")
        try:
            choice = input("Choose 1, 2, or q: ").strip().lower()
        except EOFError:
            choice = "q"

        if choice == "2":
            play_monster_chase()
            wait_for_menu()
        elif choice == "1":
            run_maps_demo()
            wait_for_menu()
        elif choice == "q":
            print("Goodbye.")
            return
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
