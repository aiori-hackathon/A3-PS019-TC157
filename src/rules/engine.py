"""Rules Engine for configuring Personal-Data discovery heuristics."""

import os
from typing import Any, Optional
import yaml

DEFAULT_RULES: dict[str, Any] = {
    "version": "1.0.0",
    "weights": {
        "column_name": 0.35,
        "value_pattern": 0.40,
        "algorithmic_validation": 0.25,
    },
    "thresholds": {
        "high": 0.75,
        "medium": 0.45,
        "low": 0.25,
    },
    "rules": {
        "name": {
            "description": "Individual human names (first, last, full)",
            "column_patterns": [
                r"^(first|last|full|sur|user|cust|client|emp|patient|beneficiary|lead)_?name$",
                r"^name$",
                r"name_of_",
                r"_name$",
                r"contact_person",
            ],
            "negative_column_patterns": [
                r"product", r"item", r"file", r"table", r"column", r"col",
                r"schema", r"category", r"brand", r"device", r"app",
                r"company", r"vendor_name", r"org_name",
            ],
        },
        "email": {
            "description": "Personal and enterprise email addresses",
            "column_patterns": [
                r"email", r"e_mail", r"mail_id", r"user_mail",
                r"contact_email", r"work_email", r"personal_email",
            ],
            "negative_column_patterns": [
                r"email_status", r"is_email_verified", r"bounced", r"email_template",
            ],
        },
        "phone": {
            "description": "Indian contact mobile numbers and telephone numbers",
            "column_patterns": [
                r"phone", r"mobile", r"contact_no", r"contact_num",
                r"cell", r"tel", r"telephone", r"phone_number", r"mobile_no",
            ],
            "negative_column_patterns": [
                r"fax_status", r"phone_type", r"is_phone_verified",
                r"pin_code", r"postal", r"zip",
            ],
        },
        "government_id": {
            "description": "Indian statutory identifiers (Aadhaar with Verhoeff, PAN Card)",
            "column_patterns": [
                r"aadhaar", r"aadhar", r"uidai", r"uid", r"pan",
                r"pan_number", r"pan_card", r"govt_id", r"tax_id",
            ],
            "negative_column_patterns": [
                r"order_id", r"transaction_id", r"tracking_id",
                r"product_id", r"session_id", r"sku", r"uuid",
            ],
        },
        "dob": {
            "description": "Date of Birth records (human age plausible dates)",
            "column_patterns": [
                r"dob", r"birth", r"date_of_birth", r"birth_date",
                r"birthdate", r"bday", r"natal_date", r"born_on",
            ],
            "negative_column_patterns": [
                r"created_at", r"updated_at", r"modified", r"timestamp",
                r"event_date", r"transaction_date", r"expiry", r"login_time",
                r"order_date", r"delivery_date",
            ],
        },
    },
}


class RuleConfig:
    """Manages YAML-based detection rules, weights, and thresholds."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}. Using defaults.")
        return DEFAULT_RULES.copy()

    def save(self, target_path: Optional[str] = None) -> None:
        path = target_path or self.config_path
        if not path:
            raise ValueError("No target path provided to save rules.")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    @property
    def weights(self) -> dict[str, float]:
        return self.config.get("weights", DEFAULT_RULES["weights"])

    @property
    def thresholds(self) -> dict[str, float]:
        return self.config.get("thresholds", DEFAULT_RULES["thresholds"])

    @property
    def rules(self) -> dict[str, Any]:
        return self.config.get("rules", DEFAULT_RULES["rules"])

    def to_yaml_string(self) -> str:
        return yaml.dump(self.config, default_flow_style=False, sort_keys=False)

    def update_from_yaml_string(self, yaml_content: str) -> None:
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            raise ValueError("Invalid YAML: root must be a mapping dictionary.")
        self.config = data
        if self.config_path:
            self.save()
