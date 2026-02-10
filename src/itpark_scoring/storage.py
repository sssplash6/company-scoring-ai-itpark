from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import CriterionScore, Feature, Scorecard


class CacheStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS pages (
                    url TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    website TEXT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    overall_score REAL,
                    coverage REAL,
                    confidence REAL,
                    flags_json TEXT
                );

                CREATE TABLE IF NOT EXISTS features (
                    run_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    evidence_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS criteria (
                    run_id TEXT NOT NULL,
                    criterion_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    weight REAL NOT NULL,
                    rationale TEXT NOT NULL
                );
                """
            )

    def get_page(self, url: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute("SELECT content FROM pages WHERE url = ?", (url,)).fetchone()
            return row["content"] if row else None

    def save_page(self, url: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO pages (url, content, fetched_at) VALUES (?, ?, ?)",
                (url, content, datetime.utcnow().isoformat()),
            )

    def start_run(self, run_id: str, company_name: str, website: Optional[str]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO runs (id, company_name, website, started_at) VALUES (?, ?, ?, ?)",
                (run_id, company_name, website, datetime.utcnow().isoformat()),
            )

    def finish_run(self, run_id: str, scorecard: Scorecard) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE runs
                SET finished_at = ?, overall_score = ?, coverage = ?, confidence = ?, flags_json = ?
                WHERE id = ?
                """,
                (
                    datetime.utcnow().isoformat(),
                    scorecard.overall_score,
                    scorecard.coverage,
                    scorecard.confidence,
                    json.dumps(scorecard.flags),
                    run_id,
                ),
            )

    def save_features(self, run_id: str, features: Dict[str, Feature]) -> None:
        with self._connect() as conn:
            for feature in features.values():
                conn.execute(
                    """
                    INSERT INTO features (run_id, name, value_json, confidence, evidence_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        feature.name,
                        json.dumps(feature.value, default=str),
                        feature.confidence,
                        json.dumps([e.__dict__ for e in feature.evidence], default=str),
                    ),
                )

    def save_criteria(self, run_id: str, criteria: List[CriterionScore]) -> None:
        with self._connect() as conn:
            for criterion in criteria:
                conn.execute(
                    """
                    INSERT INTO criteria (
                        run_id, criterion_id, name, category, score, max_score, weight, rationale
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        criterion.criterion_id,
                        criterion.name,
                        criterion.category,
                        criterion.score,
                        criterion.max_score,
                        criterion.weight,
                        criterion.rationale,
                    ),
                )
