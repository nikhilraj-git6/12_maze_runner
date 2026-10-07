import random
from collections import deque

CELL = 40  # cell size in pixels


def generate_maze(cols, rows):
    """Recursive backtracker maze generation. Returns 2D grid of walls."""
    visited = [[False] * cols for _ in range(rows)]

    # Walls: each cell has [N, S, E, W]
    walls = [
        [[True, True, True, True] for _ in range(cols)]
        for _ in range(rows)
    ]

    def neighbors(r, c):
        dirs = [
            (-1, 0, 0, 1),
            (1, 0, 1, 0),
            (0, 1, 2, 3),
            (0, -1, 3, 2)
        ]

        result = []

        for dr, dc, wd, od in dirs:
            nr, nc = r + dr, c + dc

            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and not visited[nr][nc]
            ):
                result.append((nr, nc, wd, od))

        return result

    stack = [(0, 0)]
    visited[0][0] = True

    while stack:
        r, c = stack[-1]
        nbrs = neighbors(r, c)

        if nbrs:
            nr, nc, wd, od = random.choice(nbrs)

            walls[r][c][wd] = False
            walls[nr][nc][od] = False

            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

    return walls


def shortest_path(walls, start, goal):
    """
    Return the shortest route between cells
    as a list of (row, col) pairs.

    Uses Breadth-First Search (BFS).
    """
    rows = len(walls)
    cols = len(walls[0]) if rows else 0

    if not (
        0 <= start[0] < rows
        and 0 <= start[1] < cols
    ):
        return []

    if not (
        0 <= goal[0] < rows
        and 0 <= goal[1] < cols
    ):
        return []

    # Directions:
    # N, S, E, W
    directions = [
        (-1, 0, 0),
        (1, 0, 1),
        (0, 1, 2),
        (0, -1, 3)
    ]

    # BFS queue
    queue = deque([start])

    # Store the previous cell for each visited cell
    previous = {
        start: None
    }

    while queue:
        row, col = queue.popleft()

        # Goal reached
        if (row, col) == goal:
            path = []
            cell = goal

            while cell is not None:
                path.append(cell)
                cell = previous[cell]

            return list(reversed(path))

        # Explore neighbouring cells
        for row_offset, col_offset, wall_index in directions:
            neighbor = (
                row + row_offset,
                col + col_offset
            )

            next_row, next_col = neighbor

            if (
                0 <= next_row < rows
                and 0 <= next_col < cols
                and not walls[row][col][wall_index]
                and neighbor not in previous
            ):
                previous[neighbor] = (row, col)
                queue.append(neighbor)

    # No path found
    return []


def cell_rect(r, c, import_pygame=None):
    import pygame

    return pygame.Rect(
        c * CELL,
        r * CELL,
        CELL,
        CELL
    )