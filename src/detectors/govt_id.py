"""Government ID Detector for Indian Identifiers (Aadhaar with Verhoeff, PAN Card)."""

import re
from typing import Any, Optional

from .base import BaseDetector, PersonalDataClass
from .verhoeff import validate_verhoeff

# Regex patterns
AADHAAR_REGEX = re.compile(r"^[2-9]\d{3}\s?\d{4}\s?\d{4}$")
AADHAAR_CLEAN_REGEX = re.compile(r"^[2-9]\d{11}$")
PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
PAN_ENTITY_TYPES = {"P", "C", "H", "F", "A", "T", "B", "L", "J", "G"}


class GovtIdDetector(BaseDetector):
    """Detector for Government Identification numbers (Aadhaar & PAN)."""

    def __init__(self):
        super().__init__(PersonalDataClass.GOVT_ID)

    def evaluate_column_name(self, column_name: str, rules: dict[str, Any]) -> tuple[float, Optional[str]]:
        col_clean = column_name.lower().strip()
        govt_rules = rules.get("government_id", {})
        col_patterns = govt_rules.get("column_patterns", [
            r"aadhaar", r"aadhar", r"uidai", r"uid", r"pan", r"pan_number", r"pan_card",
            r"govt_id", r"tax_id", r"identity_num", r"national_id"
        ])
        negative_patterns = govt_rules.get("negative_column_patterns", [
            r"order_id", r"transaction_id", r"tracking_id", r"product_id", r"session_id",
            r"sku", r"uuid", r"batch_id"
        ])

        # Negative penalty
        for neg in negative_patterns:
            if re.search(neg, col_clean):
                return 0.0, f"Exclusion match '{neg}'"

        for pat in col_patterns:
            if re.search(pat, col_clean):
                # Strong match for explicit names
                if any(k in col_clean for k in ["aadhaar", "aadhar", "pan"]):
                    return 1.0, pat
                return 0.8, pat

        return 0.0, None

    @staticmethod
    def _is_aadhaar(val_str: str) -> tuple[bool, bool]:
        """Check if value matches Aadhaar format and Verhoeff checksum.
        
        Returns:
            (format_valid, checksum_valid)
        """
        clean = "".join(filter(str.isdigit, val_str))
        if len(clean) != 12:
            return False, False
        if clean[0] in ("0", "1"):
            return False, False
        
        # Check format
        format_match = bool(AADHAAR_REGEX.match(val_str.strip()) or AADHAAR_CLEAN_REGEX.match(clean))
        if not format_match:
            return False, False
            
        verhoeff_match = validate_verhoeff(clean)
        return True, verhoeff_match

    @staticmethod
    def _is_pan(val_str: str) -> tuple[bool, bool]:
        """Check if value matches PAN format and entity code.
        
        Returns:
            (format_valid, entity_valid)
        """
        clean = val_str.strip().upper()
        if len(clean) != 10:
            return False, False
            
        if not PAN_REGEX.match(clean):
            return False, False
            
        # 4th character entity type check
        entity_code = clean[3]
        return True, entity_code in PAN_ENTITY_TYPES

    @staticmethod
    def _mask_id(val_str: str, id_type: str) -> str:
        clean = val_str.strip()
        if id_type == "Aadhaar":
            digits = "".join(filter(str.isdigit, clean))
            if len(digits) >= 4:
                return f"XXXX-XXXX-{digits[-4:]}"
            return "XXXX-XXXX-XXXX"
        elif id_type == "PAN":
            if len(clean) == 10:
                return f"{clean[:2]}XXXX{clean[6:]}"
            return "XXXXXX"
        return "XXXX-CONFIDENTIAL"

    def evaluate_values(
        self, values: list[Any], rules: dict[str, Any]
    ) -> tuple[float, float, list[str], int, int, Optional[str], Optional[str]]:
        if not values:
            return 0.0, 0.0, [], 0, 0, None, None

        aadhaar_format_matches = 0
        aadhaar_checksum_valid = 0
        pan_format_matches = 0
        pan_valid_matches = 0
        
        masked_samples: list[str] = []

        for v in values:
            s = str(v).strip()
            if not s:
                continue

            is_adh_fmt, is_adh_chk = self._is_aadhaar(s)
            if is_adh_fmt:
                aadhaar_format_matches += 1
                if is_adh_chk:
                    aadhaar_checksum_valid += 1
                if len(masked_samples) < 5:
                    masked_samples.append(self._mask_id(s, "Aadhaar"))
                continue

            is_pan_fmt, is_pan_ent = self._is_pan(s)
            if is_pan_fmt:
                pan_format_matches += 1
                if is_pan_ent:
                    pan_valid_matches += 1
                if len(masked_samples) < 5:
                    masked_samples.append(self._mask_id(s, "PAN"))

        total_valid_entries = len(values)
        if total_valid_entries == 0:
            return 0.0, 0.0, [], 0, 0, None, None

        # Determine dominant Government ID type in this column
        if aadhaar_format_matches >= pan_format_matches:
            match_count = aadhaar_format_matches
            valid_count = aadhaar_checksum_valid
            pattern_rule = "12-digit Indian Aadhaar pattern (starts 2-9)"
            val_desc = "Verhoeff D5 check-digit checksum algorithm"
        else:
            match_count = pan_format_matches
            valid_count = pan_valid_matches
            pattern_rule = "10-char Indian PAN [A-Z]{5}[0-9]{4}[A-Z]"
            val_desc = "Income Tax entity letter validation (P/C/H/F/A/T/B/L/J/G)"

        pattern_score = match_count / total_valid_entries
        validator_score = (valid_count / match_count) if match_count > 0 else 0.0

        return (
            pattern_score,
            validator_score,
            masked_samples,
            match_count,
            valid_count,
            pattern_rule,
            val_desc,
        )
