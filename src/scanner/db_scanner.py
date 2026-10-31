"""SQLite Database Scanner for multi-table Personal-Data candidate discovery."""

import os
import sqlite3
from typing import Any


class DbScanner:
    """Discovers tables and samples column data from SQLite databases."""

    def __init__(self, sample_size: int = 1000):
        self.sample_size = sample_size

    def inspect_db(self, db_path: str) -> dict[str, dict[str, list[Any]]]:
        """Inspect all user tables in a SQLite database.
        
        Returns:
            Dictionary mapping table_name -> {column_name -> list of values}.
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")

        result: dict[str, dict[str, list[Any]]] = {}

        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            # Fetch user tables excluding internal sqlite tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                # Get column names
                cursor.execute(f"PRAGMA table_info({table})")
                col_info = cursor.fetchall()
                col_names = [col[1] for col in col_info]

                # Fetch rows
                cursor.execute(f"SELECT * FROM {table} LIMIT {self.sample_size}")
                rows = cursor.fetchall()

                table_data: dict[str, list[Any]] = {col: [] for col in col_names}
                for row in rows:
                    for idx, col in enumerate(col_names):
                        table_data[col].append(row[idx])

                result[table] = table_data
        finally:
            conn.close()

        return result
