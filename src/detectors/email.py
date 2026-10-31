"""Email Detector for Personal Data Discovery."""

import re
from typing import Any, Optional

from .base import BaseDetector, PersonalDataClass

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


class EmailDetector(BaseDetector):
    """Detector for personal and enterprise Email addresses."""

    def __init__(self):
        super().__init__(PersonalDataClass.EMAIL)

    def evaluate_column_name(self, column_name: str, rules: dict[str, Any]) -> tuple[float, Optional[str]]:
        col_clean = column_name.lower().strip()
        email_rules = rules.get("email", {})
        col_patterns = email_rules.get("column_patterns", [
            r"email", r"e_mail", r"mail_id", r"user_mail", r"contact_email",
            r"work_email", r"personal_email", r"email_address"
        ])
        negative_patterns = email_rules.get("negative_column_patterns", [
            r"email_status", r"is_email_verified", r"bounced", r"email_template"
        ])

        for neg in negative_patterns:
            if re.search(neg, col_clean):
                return 0.0, f"Exclusion match '{neg}'"

        for pat in col_patterns:
            if re.search(pat, col_clean):
                return 1.0, pat

        return 0.0, None

    @staticmethod
    def _validate_email_structure(val_str: str) -> tuple[bool, bool]:
        """Validate email syntax and TLD domain validity.
        
        Returns:
            (format_valid, domain_valid)
        """
        s = val_str.strip().lower()
        if not EMAIL_REGEX.match(s):
            return False, False

        try:
            user, domain = s.split("@", 1)
            if not user or not domain or ".." in domain:
                return False, False
            parts = domain.split(".")
            tld = parts[-1]
            if len(tld) < 2 or not tld.isalpha():
                return False, False
            return True, True
        except Exception:
            return False, False

    @staticmethod
    def _mask_email(val_str: str) -> str:
        try:
            user, domain = val_str.strip().split("@", 1)
            if len(user) <= 2:
                masked_user = user[0] + "***"
            else:
                masked_user = user[0] + "***" + user[-1]
            return f"{masked_user}@{domain}"
        except Exception:
            return "masked_email@domain.com"

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
            fmt_ok, dom_ok = self._validate_email_structure(s)
            if fmt_ok:
                match_count += 1
                if dom_ok:
                    valid_count += 1
                if len(masked_samples) < 5:
                    masked_samples.append(self._mask_email(s))

        pattern_score = match_count / total if total > 0 else 0.0
        validator_score = valid_count / match_count if match_count > 0 else 0.0

        return (
            pattern_score,
            validator_score,
            masked_samples,
            match_count,
            valid_count,
            "RFC-5322 Compliant Email format",
            "Domain and TLD structure validation",
        )
