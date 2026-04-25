from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import random

import pygame

from snake_game.logic import (
    Direction,
    GameState,
    bounds_tiles,
    spawn_apple,
    spawn_apple_with_walls,
    step,
)
from snake_game.level import generate_walls
from snake_game.highscores import ScoreEntry, load_scores, record_score, save_scores


@dataclass(frozen=True)
class DemoConfig:
    width: int = 720
    height: int = 720
    tile: int = 32
    fps: int = 60
    caption: str = "Snake demo (Pygame) — vibe-coding workshop"


def _repo_root() -> Path:
    # demo.py -> snake_game/ (0), src/ (1), snake/ (2)
    return Path(__file__).resolve().parents[2]


def _assets_dir() -> Path:
    return _repo_root() / "assets"


def _load_image(path: Path, size: tuple[int, int]) -> pygame.Surface | None:
    try:
        surface = pygame.image.load(str(path)).convert_alpha()
    except Exception:
        return None

    return pygame.transform.smoothscale(surface, size)


def _draw_checkerboard(
    screen: pygame.Surface,
    *,
    tile: int,
    color_a: pygame.Color,
    color_b: pygame.Color,
) -> None:
    w, h = screen.get_size()
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            is_even = ((x // tile) + (y // tile)) % 2 == 0
            pygame.draw.rect(
                screen,
                color_a if is_even else color_b,
                pygame.Rect(x, y, tile, tile),
            )


def _new_game_state(config: DemoConfig, *, rng: random.Random) -> GameState:
    width_tiles = config.width // config.tile
    height_tiles = config.height // config.tile
    bounds = bounds_tiles(width_tiles=width_tiles, height_tiles=height_tiles)

    # Start in the middle, heading right.
    cx = width_tiles // 2
    cy = height_tiles // 2
    snake = ((cx, cy), (cx - 1, cy), (cx - 2, cy), (cx - 3, cy))
    walls = generate_walls(rng, bounds=bounds, occupied=snake)
    apple = spawn_apple_with_walls(rng, occupied=snake, bounds=bounds, walls=walls)

    return GameState(
        snake=snake,
        direction=Direction.RIGHT,
        apple=apple,
        bounds=bounds,
        walls=walls,
        game_over=False,
        score=0,
    )


def _dir_from_key(key: int) -> Direction | None:
    if key == pygame.K_UP:
        return Direction.UP
    if key == pygame.K_DOWN:
        return Direction.DOWN
    if key == pygame.K_LEFT:
        return Direction.LEFT
    if key == pygame.K_RIGHT:
        return Direction.RIGHT
    return None


def _draw_tile(
    screen: pygame.Surface,
    *,
    sprites: dict[str, pygame.Surface | None],
    kind: str,
    tx: int,
    ty: int,
    tile: int,
) -> None:
    x, y = tx * tile, ty * tile
    sprite = sprites.get(kind)
    if sprite is None:
        if kind == "apple":
            pygame.draw.circle(
                screen,
                pygame.Color(231, 76, 60),
                (x + tile // 2, y + tile // 2),
                tile // 2 - 3,
            )
            return

        pygame.draw.rect(
            screen,
            pygame.Color(92, 184, 92),
            pygame.Rect(x + 2, y + 2, tile - 4, tile - 4),
            border_radius=6,
        )
        return

    screen.blit(sprite, (x, y))


def _draw_walls(
    screen: pygame.Surface,
    *,
    wall: pygame.Surface | None,
    config: DemoConfig,
) -> None:
    if wall is None:
        return

    w_tiles = config.width // config.tile
    h_tiles = config.height // config.tile

    for tx in range(0, w_tiles):
        screen.blit(wall, (tx * config.tile, 0))
        screen.blit(wall, (tx * config.tile, (h_tiles - 1) * config.tile))
    for ty in range(0, h_tiles):
        screen.blit(wall, (0, ty * config.tile))
        screen.blit(wall, ((w_tiles - 1) * config.tile, ty * config.tile))


def _draw_internal_walls(
    screen: pygame.Surface,
    *,
    wall: pygame.Surface | None,
    walls: frozenset[tuple[int, int]],
    tile: int,
) -> None:
    if wall is None:
        return
    for tx, ty in walls:
        screen.blit(wall, (tx * tile, ty * tile))


def _draw_overlay(
    screen: pygame.Surface,
    *,
    config: DemoConfig,
    text: str,
    font: pygame.font.Font,
) -> None:
    overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    lines = text.splitlines() or [""]
    rendered_lines = [
        font.render(line, True, pygame.Color(240, 240, 240)) for line in lines
    ]

    line_height = font.get_linesize()
    total_h = line_height * len(rendered_lines)
    y = (config.height - total_h) // 2
    for rendered in rendered_lines:
        rect = rendered.get_rect(centerx=(config.width // 2), y=y + line_height // 2)
        screen.blit(rendered, rect)
        y += line_height


def run(config: DemoConfig | None = None) -> None:
    config = config or DemoConfig()

    pygame.init()
    try:
        screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption(config.caption)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)

        tile_size = (config.tile, config.tile)
        assets = _assets_dir()

        sprites = {
            "head": _load_image(assets / "head.png", tile_size),
            "body": _load_image(assets / "body.png", tile_size),
            "tail": _load_image(assets / "tail.png", tile_size),
            "apple": _load_image(assets / "apple.png", tile_size),
            "wall": _load_image(assets / "wall.png", tile_size),
            "box": _load_image(assets / "box.png", tile_size),
        }

        rng = random.Random()
        scores_path = _repo_root() / "scores.json"
        highscores = load_scores(scores_path)

        state = _new_game_state(config, rng=rng)
        pending_turn: Direction | None = None
        name_input = ""
        score_saved_for_round = False

        base_move_hz = 10.0
        move_hz_per_score = 0.75
        max_move_hz = 25.0

        move_hz = base_move_hz
        move_interval_ms = int(1000 / move_hz)
        acc_ms = 0

        autoclose_seconds: float | None = None
        raw_autoclose = os.getenv("SNAKE_DEMO_AUTOCLOSE_SECONDS")
        if raw_autoclose:
            try:
                autoclose_seconds = float(raw_autoclose)
            except ValueError:
                autoclose_seconds = None

        start_ms = pygame.time.get_ticks()

        running = True
        while running:
            dt_ms = clock.tick(config.fps)
            acc_ms += dt_ms

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        continue

                    if state.game_over:
                        if not score_saved_for_round:
                            if event.key == pygame.K_BACKSPACE:
                                name_input = name_input[:-1]
                                continue
                            if event.key == pygame.K_RETURN:
                                highscores = record_score(
                                    highscores,
                                    name=name_input,
                                    score=state.score,
                                    limit=10,
                                )
                                save_scores(scores_path, highscores)
                                score_saved_for_round = True
                                continue

                            ch = getattr(event, "unicode", "")
                            if isinstance(ch, str) and ch and ch.isprintable():
                                if ch not in "\r\n\t":
                                    if len(name_input) < 16:
                                        name_input += ch
                            continue

                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            state = _new_game_state(config, rng=rng)
                            pending_turn = None
                            acc_ms = 0
                            move_hz = base_move_hz
                            move_interval_ms = int(1000 / move_hz)
                            name_input = ""
                            score_saved_for_round = False
                        continue

                    desired = _dir_from_key(event.key)
                    if desired is not None and not state.game_over:
                        pending_turn = desired

            while not state.game_over and acc_ms >= move_interval_ms:
                prev_score = state.score
                state = step(state, pending_turn=pending_turn, rng=rng)
                pending_turn = None
                acc_ms -= move_interval_ms
                if state.score != prev_score:
                    move_hz = min(max_move_hz, base_move_hz + state.score * move_hz_per_score)
                    move_interval_ms = max(1, int(1000 / move_hz))

            _draw_checkerboard(
                screen,
                tile=config.tile,
                color_a=pygame.Color(16, 18, 27),
                color_b=pygame.Color(20, 23, 35),
            )

            # Apple.
            ax, ay = state.apple
            _draw_tile(
                screen,
                sprites=sprites,
                kind="apple",
                tx=ax,
                ty=ay,
                tile=config.tile,
            )

            # Snake.
            for idx, (tx, ty) in enumerate(state.snake):
                kind = "body"
                if idx == 0:
                    kind = "head"
                elif idx == len(state.snake) - 1:
                    kind = "tail"

                _draw_tile(
                    screen,
                    sprites=sprites,
                    kind=kind,
                    tx=tx,
                    ty=ty,
                    tile=config.tile,
                )

            _draw_walls(screen, wall=sprites.get("wall"), config=config)
            _draw_internal_walls(
                screen,
                wall=(sprites.get("box") or sprites.get("wall")),
                walls=state.walls,
                tile=config.tile,
            )

            score_text = font.render(
                f"Score: {state.score}",
                True,
                pygame.Color(220, 220, 220),
            )
            screen.blit(score_text, (12, 12))

            if state.game_over:
                top_lines = ["High scores:"]
                for idx, entry in enumerate(highscores[:10], start=1):
                    top_lines.append(f"{idx:>2}. {entry.name} — {entry.score}")

                if not score_saved_for_round:
                    prompt = f"Name: {name_input or ''}_ (Enter to save)"
                else:
                    prompt = "Saved. Press Enter/Space to restart"

                _draw_overlay(
                    screen,
                    config=config,
                    text="Game Over\n"
                    + "\n".join(top_lines)
                    + "\n\n"
                    + prompt,
                    font=font,
                )

            pygame.display.flip()

            if autoclose_seconds is not None:
                elapsed_ms = pygame.time.get_ticks() - start_ms
                if elapsed_ms >= int(autoclose_seconds * 1000):
                    running = False
    finally:
        pygame.quit()
