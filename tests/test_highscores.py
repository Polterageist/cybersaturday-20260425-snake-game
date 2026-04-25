from __future__ import annotations

from pathlib import Path

from snake_game.highscores import ScoreEntry, load_scores, record_score, save_scores


def test_record_score_sorts_desc_and_limits() -> None:
    entries = [
        ScoreEntry(name="A", score=2),
        ScoreEntry(name="B", score=10),
        ScoreEntry(name="C", score=5),
    ]
    out = record_score(entries, name="D", score=7, limit=3)
    assert [e.score for e in out] == [10, 7, 5]


def test_load_scores_missing_file_is_empty(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    assert load_scores(path) == []


def test_load_scores_bad_json_is_empty(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    path.write_text("{not valid json", encoding="utf-8")
    assert load_scores(path) == []


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "scores.json"
    entries = [ScoreEntry(name="Player", score=3)]
    save_scores(path, entries)
    assert load_scores(path) == entries

