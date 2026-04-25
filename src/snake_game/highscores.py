from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    name: str
    score: int


def load_scores(path: Path) -> list[ScoreEntry]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except OSError:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    out: list[ScoreEntry] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        score = item.get("score")
        if not isinstance(name, str):
            continue
        if not isinstance(score, int):
            continue
        name = name.strip()
        if not name:
            continue
        if score < 0:
            continue
        out.append(ScoreEntry(name=name, score=score))
    return out


def record_score(
    entries: list[ScoreEntry],
    *,
    name: str,
    score: int,
    limit: int = 10,
) -> list[ScoreEntry]:
    cleaned = name.strip()
    if not cleaned:
        cleaned = "Player"
    if score < 0:
        score = 0

    next_entries = [*entries, ScoreEntry(name=cleaned, score=score)]
    next_entries.sort(key=lambda e: e.score, reverse=True)
    if limit <= 0:
        return []
    return next_entries[:limit]


def save_scores(path: Path, entries: list[ScoreEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload: list[dict[str, Any]] = [{"name": e.name, "score": e.score} for e in entries]
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    data = data + "\n"

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(data, encoding="utf-8")
    os.replace(tmp_path, path)

