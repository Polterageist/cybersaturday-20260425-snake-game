# Snake (Pygame) — demo repo

This repository is a **workshop demo project**: a minimal Pygame window that renders a static “snake” placeholder using the sprites in `assets/`.

It is intentionally **not a full game** yet: **no snake movement, no collisions, no scoring**. We’ll build the actual snake logic during the master class via vibe-coding.

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

