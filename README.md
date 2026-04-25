# Snake (Pygame) — demo repo

This repository is a **workshop demo project**: a minimal Snake game in Pygame using the sprites in `assets/`.

It includes:
- Snake movement (arrow keys)
- Collisions (walls + self)
- Apples, score, and speed-up as you eat
- Internal randomly-generated walls
- Persistent Top-10 high scores saved locally to `scores.json` (enter your name on Game Over)

## Requirements

- Python **3.13**
- [Poetry](https://python-poetry.org/)

## Run

```bash
poetry install
poetry run snake-demo
```

Close the window or press **ESC** to exit.

## Assets

Sprites live in `assets/` (e.g. `head.png`, `body.png`, `tail.png`, `apple.png`, `wall.png`). The demo falls back to simple shapes if an asset is missing.

