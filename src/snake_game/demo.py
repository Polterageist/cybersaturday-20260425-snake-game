from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import pygame


@dataclass(frozen=True)
class DemoConfig:
    width: int = 720
    height: int = 720
    tile: int = 32
    fps: int = 60
    caption: str = "Snake demo (Pygame) — vibe-coding workshop"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


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


def run(config: DemoConfig | None = None) -> None:
    config = config or DemoConfig()

    pygame.init()
    try:
        screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption(config.caption)
        clock = pygame.time.Clock()

        tile_size = (config.tile, config.tile)
        assets = _assets_dir()

        sprites = {
            "head": _load_image(assets / "head.png", tile_size),
            "body": _load_image(assets / "body.png", tile_size),
            "tail": _load_image(assets / "tail.png", tile_size),
            "apple": _load_image(assets / "apple.png", tile_size),
            "wall": _load_image(assets / "wall.png", tile_size),
        }

        snake_tiles = [
            ("head", (6, 6)),
            ("body", (5, 6)),
            ("body", (4, 6)),
            ("tail", (3, 6)),
        ]
        apple_tile = ("apple", (10, 6))

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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            _draw_checkerboard(
                screen,
                tile=config.tile,
                color_a=pygame.Color(16, 18, 27),
                color_b=pygame.Color(20, 23, 35),
            )

            for kind, (tx, ty) in snake_tiles:
                x, y = tx * config.tile, ty * config.tile
                sprite = sprites.get(kind)
                if sprite is None:
                    pygame.draw.rect(
                        screen,
                        pygame.Color(92, 184, 92),
                        pygame.Rect(
                            x + 2,
                            y + 2,
                            config.tile - 4,
                            config.tile - 4,
                        ),
                        border_radius=6,
                    )
                else:
                    screen.blit(sprite, (x, y))

            kind, (tx, ty) = apple_tile
            x, y = tx * config.tile, ty * config.tile
            sprite = sprites.get(kind)
            if sprite is None:
                pygame.draw.circle(
                    screen,
                    pygame.Color(231, 76, 60),
                    (x + config.tile // 2, y + config.tile // 2),
                    config.tile // 2 - 3,
                )
            else:
                screen.blit(sprite, (x, y))

            wall = sprites.get("wall")
            if wall is not None:
                for tx in range(0, config.width // config.tile):
                    screen.blit(wall, (tx * config.tile, 0))
                    screen.blit(
                        wall,
                        (tx * config.tile, config.height - config.tile),
                    )
                for ty in range(0, config.height // config.tile):
                    screen.blit(wall, (0, ty * config.tile))
                    screen.blit(
                        wall,
                        (config.width - config.tile, ty * config.tile),
                    )

            pygame.display.flip()
            clock.tick(config.fps)

            if autoclose_seconds is not None:
                elapsed_ms = pygame.time.get_ticks() - start_ms
                if elapsed_ms >= int(autoclose_seconds * 1000):
                    running = False
    finally:
        pygame.quit()