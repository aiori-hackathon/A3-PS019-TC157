"""Human Name Detector for Personal Data Discovery."""

import re
from typing import Any, Optional

from .base import BaseDetector, PersonalDataClass

# Regex for human names: allows letters, spaces, hyphens, periods, apostrophes
HUMAN_NAME_REGEX = re.compile(r"^[A-Za-z\s\.\'-]{2,50}$")
HONORIFICS = {"mr", "mrs", "ms", "miss", "dr", "prof", "shri", "smt", "kumar", "kumari"}


class NameDetector(BaseDetector):
    """Detector for human personal names (first, last, full names)."""

    def __init__(self):
        super().__init__(PersonalDataClass.NAME)

    def evaluate_column_name(self, column_name: str, rules: dict[str, Any]) -> tuple[float, Optional[str]]:
        col_clean = column_name.lower().strip()
        name_rules = rules.get("name", {})
        col_patterns = name_rules.get("column_patterns", [
            r"^(first|last|full|sur|user|cust|client|emp|patient|beneficiary|lead)_?name$",
            r"^name$", r"name_of_", r"_name$", r"contact_person"
        ])
        negative_patterns = name_rules.get("negative_column_patterns", [
            r"product", r"item", r"file", r"table", r"column", r"col", r"schema",
            r"category", r"brand", r"device", r"app", r"package", r"service_name",
            r"role_name", r"event_name", r"city_name", r"country_name"
        ])

        for neg in negative_patterns:
            if re.search(neg, col_clean):
                return 0.0, f"Exclusion match '{neg}'"

        for pat in col_patterns:
            if re.search(pat, col_clean):
                return 1.0, pat

        return 0.0, None

    @staticmethod
    def _validate_name_structure(val_str: str) -> tuple[bool, bool]:
        """Validate human name format and morphological structure.
        
        Returns:
            (format_valid, linguistic_structure_valid)
        """
        s = val_str.strip()
        if len(s) < 2 or len(s) > 60:
            return False, False

        # Must not contain digits or email/url tokens
        if any(char.isdigit() for char in s) or "@" in s or "http" in s or "/" in s:
            return False, False

        if not HUMAN_NAME_REGEX.match(s):
            return False, False

        words = [w.strip(" .") for w in s.split() if w.strip(" .")]
        if not words:
            return False, False

        # Plausible word count for person's name (1 to 4 words)
        if len(words) > 5:
            return False, False

        has_honorific = any(w.lower() in HONORIFICS for w in words)
        has_multiple_tokens = len(words) >= 2
        is_title_case = all(w[0].isupper() for w in words if len(w) > 0)

        # Full human names typically have 2+ capitalized name tokens (first + last)
        # or a distinct honorific title (e.g. Dr., Mr., Smt.).
        # Single isolated words (e.g. "Finance", "Resolved", "Active") are generic categories.
        if not (has_honorific or (has_multiple_tokens and is_title_case)):
            return False, False

        return True, True

    @staticmethod
    def _mask_name(val_str: str) -> str:
        words = val_str.strip().split()
        masked_words = []
        for w in words:
            if len(w) <= 1:
                masked_words.append(w)
            else:
                masked_words.append(w[0] + "*" * (len(w) - 1))
        return " ".join(masked_words)

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
            fmt_ok, struct_ok = self._validate_name_structure(s)
            if fmt_ok:
                match_count += 1
                if struct_ok:
                    valid_count += 1
                if len(masked_samples) < 5:
                    masked_samples.append(self._mask_name(s))

        pattern_score = match_count / total if total > 0 else 0.0
        validator_score = valid_count / match_count if match_count > 0 else 0.0

        return (
            pattern_score,
            validator_score,
            masked_samples,
            match_count,
            valid_count,
            "Alphabetic human name pattern (excluding digits/symbols)",
            "Linguistic title-casing and honorific/multi-token name structure",
        )
