"""Date of Birth (DOB) Detector with Multi-Format Parsing and Age Plausibility Validation."""

import datetime
import re
from typing import Any, Optional
from dateutil import parser as date_parser

from .base import BaseDetector, PersonalDataClass


class DobDetector(BaseDetector):
    """Detector for human Date of Birth (DOB) fields."""

    def __init__(self):
        super().__init__(PersonalDataClass.DOB)
        self.current_year = datetime.datetime.now().year

    def evaluate_column_name(self, column_name: str, rules: dict[str, Any]) -> tuple[float, Optional[str]]:
        col_clean = column_name.lower().strip()
        dob_rules = rules.get("dob", {})
        col_patterns = dob_rules.get("column_patterns", [
            r"dob", r"birth", r"date_of_birth", r"birth_date", r"birthdate",
            r"bday", r"natal_date", r"born_on", r"d_o_b"
        ])
        negative_patterns = dob_rules.get("negative_column_patterns", [
            r"created_at", r"updated_at", r"modified", r"timestamp", r"event_date",
            r"transaction_date", r"expiry", r"valid_until", r"login_time",
            r"order_date", r"invoice_date", r"delivery_date", r"audit_date"
        ])

        for neg in negative_patterns:
            if re.search(neg, col_clean):
                return 0.0, f"Exclusion match '{neg}'"

        for pat in col_patterns:
            if re.search(pat, col_clean):
                return 1.0, pat

        # Generic date column without specific dob clue
        if re.search(r"\b(date|dt)\b", col_clean):
            return 0.35, "generic_date_token"

        return 0.0, None

    def _parse_and_validate_dob(self, val_str: str) -> tuple[bool, bool]:
        """Attempt to parse date string and check if age is plausible for human DOB.
        
        Returns:
            (is_date_format, is_plausible_dob)
        """
        s = val_str.strip()
        if len(s) < 4:
            return False, False

        # Avoid purely numeric long tokens like Aadhaar or phone numbers
        if s.isdigit() and len(s) > 8:
            return False, False

        try:
            # Parse date using dateutil
            dt = date_parser.parse(s, fuzzy=False, dayfirst=True)
            year = dt.year
            
            # Check date format validity
            is_date_format = True

            # Plausibility check for human DOB:
            # - Born between 1905 and current year
            # - Cannot be in the future
            is_plausible_dob = (1905 <= year <= self.current_year)
            return is_date_format, is_plausible_dob
        except Exception:
            return False, False

    @staticmethod
    def _mask_dob(val_str: str) -> str:
        s = val_str.strip()
        # Keep year visible, mask day and month
        digits = re.findall(r"\d+", s)
        year_candidate = next((d for d in digits if len(d) == 4), "YYYY")
        return f"**/**/{year_candidate}"

    def evaluate_values(
        self, values: list[Any], rules: dict[str, Any]
    ) -> tuple[float, float, list[str], int, int, Optional[str], Optional[str]]:
        if not values:
            return 0.0, 0.0, [], 0, 0, None, None

        total = len(values)
        match_count = 0
        valid_count = 0
        masked_samples: list[str] = []

        for v in values:
            s = str(v).strip()
            fmt_ok, dob_plausible = self._parse_and_validate_dob(s)
            if fmt_ok:
                match_count += 1
                if dob_plausible:
                    valid_count += 1
                if len(masked_samples) < 5:
                    masked_samples.append(self._mask_dob(s))

        pattern_score = match_count / total if total > 0 else 0.0
        validator_score = valid_count / match_count if match_count > 0 else 0.0

        return (
            pattern_score,
            validator_score,
            masked_samples,
            match_count,
            valid_count,
            "Multi-format calendar date (ISO/Indian/US/Textual)",
            f"Human demographic age plausibility validation (1905 - {self.current_year})",
        )
