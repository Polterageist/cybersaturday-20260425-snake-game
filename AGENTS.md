# Project agent notes (Snake workshop)

This repo is used for a live **vibe-coding** master class: we start from a runnable Pygame demo and iteratively build the snake game.

## Scope / constraints

- Keep the project **always runnable** after each step.
- During initialization we keep it **dummy**:
  - no snake movement logic
  - no collisions
  - no scoring / levels

## Preferred workflow

- Make small, reviewable changes (one visible improvement per step).
- Prefer adding logic in small pure functions (easy to test) before wiring it to Pygame.
- If adding a behavior that can be tested, prefer **TDD** (unit tests first).

## Commands

Install deps:

```bash
poetry install
```

Run the demo:

```bash
poetry run snake-demo
```

