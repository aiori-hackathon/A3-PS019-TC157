"""Persistent SQLite Database for Human Privacy Reviewer Notes and Lawful Basis Assessments."""

import datetime
import sqlite3
from typing import Any, Optional


class ReviewerDatabase:
    """Manages persistence of human reviewer notes, verification statuses, and legal audit notes."""

    def __init__(self, db_path: str = "data/reviewer_notes.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reviewer_notes (
                    dataset_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    data_class TEXT,
                    verification_status TEXT DEFAULT 'Unreviewed',
                    lawful_basis_note TEXT DEFAULT '',
                    risk_assessment TEXT DEFAULT 'Unassessed',
                    retention_approval TEXT DEFAULT 'Pending Review',
                    reviewer_identity TEXT DEFAULT 'DPO / Privacy Reviewer',
                    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (dataset_name, table_name, column_name)
                )
                """
            )
            conn.commit()

    def save_note(
        self,
        dataset_name: str,
        table_name: str,
        column_name: str,
        data_class: str,
        verification_status: str,
        lawful_basis_note: str,
        risk_assessment: str,
        retention_approval: str,
        reviewer_identity: str,
    ) -> None:
        """Insert or replace human reviewer notes for a specific discovered field."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO reviewer_notes (
                    dataset_name, table_name, column_name, data_class,
                    verification_status, lawful_basis_note, risk_assessment,
                    retention_approval, reviewer_identity, reviewed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_name,
                    table_name,
                    column_name,
                    data_class,
                    verification_status,
                    lawful_basis_note,
                    risk_assessment,
                    retention_approval,
                    reviewer_identity,
                    now,
                ),
            )
            conn.commit()

    def get_note(self, dataset_name: str, table_name: str, column_name: str) -> Optional[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM reviewer_notes
                WHERE dataset_name = ? AND table_name = ? AND column_name = ?
                """,
                (dataset_name, table_name, column_name),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_notes(self) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviewer_notes ORDER BY reviewed_at DESC")
            return [dict(row) for row in cursor.fetchall()]
