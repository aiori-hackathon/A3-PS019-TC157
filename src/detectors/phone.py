"""Indian Phone and Mobile Number Detector."""

import re
from typing import Any, Optional

from .base import BaseDetector, PersonalDataClass

# Broad phone regex allowing common Indian formats (+91, 0, spaces, dashes)
INDIAN_PHONE_REGEX = re.compile(
    r"^(?:(?:\+|00)91[\s.-]?|[0]?)?([6-9]\d{4}[\s.-]?\d{5})$"
)


class PhoneDetector(BaseDetector):
    """Detector for Indian mobile and telephone contact numbers."""

    def __init__(self):
        super().__init__(PersonalDataClass.PHONE)

    def evaluate_column_name(self, column_name: str, rules: dict[str, Any]) -> tuple[float, Optional[str]]:
        col_clean = column_name.lower().strip()
        phone_rules = rules.get("phone", {})
        col_patterns = phone_rules.get("column_patterns", [
            r"phone", r"mobile", r"contact_no", r"contact_num", r"cell",
            r"tel", r"telephone", r"phone_number", r"mobile_no", r"whatsapp"
        ])
        negative_patterns = phone_rules.get("negative_column_patterns", [
            r"fax_status", r"phone_type", r"is_phone_verified", r"pin_code",
            r"postal", r"zip", r"dial_code"
        ])

        for neg in negative_patterns:
            if re.search(neg, col_clean):
                return 0.0, f"Exclusion match '{neg}'"

        for pat in col_patterns:
            if re.search(pat, col_clean):
                return 1.0, pat

        return 0.0, None

    @staticmethod
    def _validate_indian_phone(val_str: str) -> tuple[bool, bool]:
        """Validate phone format and check Indian telecommunication prefix.
        
        Returns:
            (format_valid, telecom_prefix_valid)
        """
        s = val_str.strip()
        # Clean out non-digit characters except leading plus
        digits_only = re.sub(r"[^\d]", "", s)
        
        # Check overall length of digits
        if len(digits_only) not in (10, 11, 12):
            return False, False
            
        # Extract 10-digit national number
        if len(digits_only) == 10:
            national_num = digits_only
        elif len(digits_only) == 11 and digits_only.startswith("0"):
            national_num = digits_only[1:]
        elif len(digits_only) == 12 and digits_only.startswith("91"):
            national_num = digits_only[2:]
        else:
            return False, False

        # First digit must be 6, 7, 8, or 9 for Indian cellular networks
        is_telecom_valid = national_num[0] in ("6", "7", "8", "9")
        
        # Match pattern
        format_valid = bool(INDIAN_PHONE_REGEX.match(s)) or is_telecom_valid
        return format_valid, is_telecom_valid

    @staticmethod
    def _mask_phone(val_str: str) -> str:
        digits = re.sub(r"[^\d]", "", val_str)
        if len(digits) >= 10:
            last4 = digits[-4:]
            first2 = digits[-10:-8]
            return f"+91 {first2}XXX-XX{last4}"
        return "+91 XXXXX-XXXXX"

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
            fmt_ok, prefix_ok = self._validate_indian_phone(s)
            if fmt_ok:
                match_count += 1
                if prefix_ok:
                    valid_count += 1
                if len(masked_samples) < 5:
                    masked_samples.append(self._mask_phone(s))

        pattern_score = match_count / total if total > 0 else 0.0
        validator_score = valid_count / match_count if match_count > 0 else 0.0

        return (
            pattern_score,
            validator_score,
            masked_samples,
            match_count,
            valid_count,
            "10-digit Indian Mobile format with optional +91/0 prefix",
            "Indian DoT cellular allocation series check (6/7/8/9 prefix)",
        )
