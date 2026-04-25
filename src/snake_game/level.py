from __future__ import annotations

import random
from typing import Iterable

from snake_game.logic import Bounds, Vec2


def generate_walls(
    rng: random.Random,
    *,
    bounds: Bounds,
    occupied: Iterable[Vec2],
    segment_count: int = 10,
    segment_min_len: int = 3,
    segment_max_len: int = 8,
    max_attempts_per_segment: int = 50,
) -> frozenset[Vec2]:
    """
    Generate simple internal walls as random axis-aligned segments.

    Constraints:
    - walls are strictly inside `bounds` (playable interior)
    - walls never overlap `occupied`
    """
    occ = set(occupied)
    (min_x, min_y), (max_x, max_y) = bounds

    if min_x > max_x or min_y > max_y:
        return frozenset()

    walls: set[Vec2] = set()

    for _ in range(segment_count):
        placed = False
        for _attempt in range(max_attempts_per_segment):
            horizontal = rng.random() < 0.5
            length = rng.randint(segment_min_len, segment_max_len)

            if horizontal:
                if (max_x - min_x + 1) < length:
                    continue
                x0 = rng.randint(min_x, max_x - length + 1)
                y0 = rng.randint(min_y, max_y)
                seg = [(x0 + i, y0) for i in range(length)]
            else:
                if (max_y - min_y + 1) < length:
                    continue
                x0 = rng.randint(min_x, max_x)
                y0 = rng.randint(min_y, max_y - length + 1)
                seg = [(x0, y0 + i) for i in range(length)]

            if any(p in occ for p in seg):
                continue
            if any(p in walls for p in seg):
                continue

            walls.update(seg)
            placed = True
            break

        if not placed:
            continue

    return frozenset(walls)

