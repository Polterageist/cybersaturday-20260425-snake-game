from __future__ import annotations

import random

import pytest

from snake_game.logic import (
    Direction,
    GameState,
    bounds_tiles,
    spawn_apple,
    spawn_apple_with_walls,
    step,
    turn,
)

def test_turn_prevents_reverse() -> None:
    assert turn(Direction.RIGHT, Direction.LEFT) == Direction.RIGHT
    assert turn(Direction.UP, Direction.DOWN) == Direction.UP


def test_turn_allows_perpendicular_change() -> None:
    assert turn(Direction.RIGHT, Direction.UP) == Direction.UP
    assert turn(Direction.RIGHT, Direction.DOWN) == Direction.DOWN


def test_step_moves_forward_without_growing() -> None:
    state = GameState(
        snake=((3, 3), (2, 3), (1, 3)),
        direction=Direction.RIGHT,
        apple=(10, 10),
        bounds=((1, 1), (20, 20)),
        walls=frozenset(),
        game_over=False,
        score=0,
    )

    nxt = step(state)
    assert nxt.snake == ((4, 3), (3, 3), (2, 3))
    assert nxt.game_over is False
    assert nxt.score == 0


def test_step_eats_apple_and_grows_and_scores() -> None:
    rng = random.Random(0)
    state = GameState(
        snake=((3, 3), (2, 3), (1, 3)),
        direction=Direction.RIGHT,
        apple=(4, 3),
        bounds=((1, 1), (6, 6)),
        walls=frozenset(),
        game_over=False,
        score=0,
    )

    nxt = step(state, rng=rng)
    assert len(nxt.snake) == 4
    assert nxt.snake[0] == (4, 3)
    assert nxt.score == 1
    assert nxt.apple not in nxt.snake


def test_step_wall_collision_sets_game_over() -> None:
    state = GameState(
        snake=((2, 1), (2, 2), (2, 3)),
        direction=Direction.UP,
        apple=(10, 10),
        bounds=((1, 1), (20, 20)),
        walls=frozenset(),
        game_over=False,
        score=0,
    )

    nxt = step(state)
    assert nxt.game_over is True


def test_step_self_collision_sets_game_over() -> None:
    # Snake shaped so that moving left puts head onto its body at (3, 2).
    state = GameState(
        snake=((4, 2), (3, 2), (2, 2), (2, 3), (3, 3), (4, 3)),
        direction=Direction.LEFT,
        apple=(10, 10),
        bounds=((1, 1), (20, 20)),
        walls=frozenset(),
        game_over=False,
        score=0,
    )

    nxt = step(state)
    assert nxt.game_over is True


def test_spawn_apple_only_in_interior_and_not_on_occupied() -> None:
    rng = random.Random(0)
    bounds = bounds_tiles(width_tiles=6, height_tiles=6)  # interior is 1..4
    occupied = {(2, 2), (3, 2), (4, 2), (2, 3), (3, 3)}
    apple = spawn_apple(rng, occupied=occupied, bounds=bounds)
    (min_xy, max_xy) = bounds
    assert min_xy[0] <= apple[0] <= max_xy[0]
    assert min_xy[1] <= apple[1] <= max_xy[1]
    assert apple not in occupied


def test_spawn_apple_not_on_walls() -> None:
    rng = random.Random(0)
    bounds = ((1, 1), (3, 3))
    walls = {(2, 2), (3, 3)}
    apple = spawn_apple_with_walls(rng, occupied=(), bounds=bounds, walls=walls)
    assert apple not in walls


def test_step_wall_collision_internal_wall_sets_game_over() -> None:
    state = GameState(
        snake=((2, 2), (1, 2), (1, 1)),
        direction=Direction.RIGHT,
        apple=(10, 10),
        bounds=((1, 1), (20, 20)),
        walls=frozenset({(3, 2)}),
        game_over=False,
        score=0,
    )

    nxt = step(state)
    assert nxt.game_over is True


def test_spawn_apple_raises_when_no_space() -> None:
    rng = random.Random(0)
    bounds = ((1, 1), (1, 1))
    with pytest.raises(ValueError):
        spawn_apple(rng, occupied={(1, 1)}, bounds=bounds)

