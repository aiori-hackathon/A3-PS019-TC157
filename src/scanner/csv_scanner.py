"""CSV Scanner for personal-data candidate discovery."""

import os
from typing import Any
import pandas as pd


class CsvScanner:
    """Reads CSV files safely handling messy encodings, null values, and sample data."""

    def __init__(self, sample_size: int = 1000):
        self.sample_size = sample_size

    def inspect_csv(self, file_path: str) -> dict[str, list[Any]]:
        """Read CSV file and extract column values up to sample_size rows.
        
        Returns:
            Dictionary mapping column_name -> list of values.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        # Attempt reading with various encodings
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
        df: pd.DataFrame = pd.DataFrame()

        for enc in encodings:
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=enc,
                    nrows=self.sample_size,
                    dtype=str,
                    keep_default_na=False,
                )
                break
            except Exception:
                continue

        if df.empty:
            # Fallback
            df = pd.read_csv(file_path, nrows=self.sample_size, dtype=str)

        columns_data: dict[str, list[Any]] = {}
        for col in df.columns:
            columns_data[str(col)] = df[col].tolist()

        return columns_data
