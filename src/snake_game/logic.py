from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import random
from typing import Iterable, TypeAlias

Vec2: TypeAlias = tuple[int, int]
Bounds: TypeAlias = tuple[Vec2, Vec2]  # inclusive min/max tile coordinates (interior only)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self) -> Vec2:
        return self.value


@dataclass(frozen=True, slots=True)
class GameState:
    snake: tuple[Vec2, ...]  # head first
    direction: Direction
    apple: Vec2
    bounds: Bounds
    game_over: bool
    score: int


def bounds_tiles(*, width_tiles: int, height_tiles: int) -> Bounds:
    # Border is walls; playable interior is 1..(n-2) on each axis.
    return (1, 1), (width_tiles - 2, height_tiles - 2)


def next_head(pos: Vec2, direction: Direction) -> Vec2:
    dx, dy = direction.delta
    return (pos[0] + dx, pos[1] + dy)


def _is_in_bounds(pos: Vec2, bounds: Bounds) -> bool:
    (min_x, min_y), (max_x, max_y) = bounds
    return min_x <= pos[0] <= max_x and min_y <= pos[1] <= max_y


def turn(current: Direction, desired: Direction) -> Direction:
    # Disallow instant 180° reversals.
    dx0, dy0 = current.delta
    dx1, dy1 = desired.delta
    if (dx0 + dx1, dy0 + dy1) == (0, 0):
        return current
    return desired


def spawn_apple(rng: random.Random, *, occupied: Iterable[Vec2], bounds: Bounds) -> Vec2:
    occ = set(occupied)
    (min_x, min_y), (max_x, max_y) = bounds
    free: list[Vec2] = [
        (x, y)
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        if (x, y) not in occ
    ]
    if not free:
        raise ValueError("No free tiles left to spawn apple.")
    return free[rng.randrange(len(free))]


def step(
    state: GameState,
    *,
    pending_turn: Direction | None = None,
    rng: random.Random | None = None,
) -> GameState:
    if state.game_over:
        return state

    direction = state.direction
    if pending_turn is not None:
        direction = turn(direction, pending_turn)

    head = state.snake[0]
    new_head = next_head(head, direction)

    if not _is_in_bounds(new_head, state.bounds):
        return replace(state, direction=direction, game_over=True)

    ate = new_head == state.apple
    if ate:
        new_snake = (new_head,) + state.snake
        rng = rng or random.Random()
        new_apple = spawn_apple(rng, occupied=new_snake, bounds=state.bounds)
        return replace(
            state,
            snake=new_snake,
            direction=direction,
            apple=new_apple,
            score=state.score + 1,
        )

    # Normal move: add head, drop tail.
    new_snake = (new_head,) + state.snake[:-1]
    if new_head in new_snake[1:]:
        return replace(state, snake=new_snake, direction=direction, game_over=True)

    return replace(state, snake=new_snake, direction=direction)

