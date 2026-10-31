"""Base interfaces, data structures, and enumeration for Personal Data detectors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class PersonalDataClass(str, Enum):
    """The 5 regulated personal data classes under PS-019."""
    NAME = "Name"
    EMAIL = "Email"
    PHONE = "Phone"
    GOVT_ID = "Government ID"
    DOB = "Date of Birth"


class ConfidenceTier(str, Enum):
    """Confidence tier classification."""
    HIGH = "High"        # >= 0.75
    MEDIUM = "Medium"    # 0.45 <= score < 0.75
    LOW = "Low"          # 0.25 <= score < 0.45
    NONE = "None"        # < 0.25


@dataclass
class FieldEvidence:
    """Comprehensive technical evidence trail for a detected candidate field."""
    column_name: str
    data_class: PersonalDataClass
    sub_category: Optional[str] = None  # e.g., 'Aadhaar', 'PAN', 'Mobile', etc.
    overall_confidence: float = 0.0
    confidence_tier: ConfidenceTier = ConfidenceTier.NONE
    
    # Granular component scores [0.0 - 1.0]
    column_name_score: float = 0.0
    value_pattern_score: float = 0.0
    algorithmic_validation_score: float = 0.0
    
    # Statistical data profiling
    total_rows: int = 0
    non_null_rows: int = 0
    null_ratio: float = 0.0
    matching_sample_count: int = 0
    validated_sample_count: int = 0
    
    # Descriptive evidence trail
    column_rule_matched: Optional[str] = None
    pattern_rule_matched: Optional[str] = None
    validator_used: Optional[str] = None
    masked_samples: list[str] = field(default_factory=list)
    evidence_steps: list[str] = field(default_factory=list)
    is_candidate_pii: bool = False


class BaseDetector(ABC):
    """Abstract base detector for personal data identification."""

    def __init__(self, data_class: PersonalDataClass):
        self.data_class = data_class

    @abstractmethod
    def evaluate_column_name(self, column_name: str, rules: dict[str, Any]) -> tuple[float, Optional[str]]:
        """Compute score for the column header name based on rules."""
        pass

    @abstractmethod
    def evaluate_values(
        self, values: list[Any], rules: dict[str, Any]
    ) -> tuple[float, float, list[str], int, int, Optional[str], Optional[str]]:
        """Evaluate raw data values for regex pattern match and deep algorithmic validation.
        
        Returns:
            (pattern_score, validator_score, masked_samples, match_count, valid_count, pattern_desc, validator_desc)
        """
        pass

    def detect(
        self,
        column_name: str,
        values: list[Any],
        rules: dict[str, Any],
        weights: Optional[dict[str, float]] = None,
        thresholds: Optional[dict[str, float]] = None,
    ) -> FieldEvidence:
        """Run complete multi-signal detection and build full evidence trail."""
        if weights is None:
            weights = {"column_name": 0.35, "value_pattern": 0.40, "algorithmic_validation": 0.25}
        if thresholds is None:
            thresholds = {"high": 0.75, "medium": 0.45, "low": 0.25}

        # Profile basic stats
        total_rows = len(values)
        non_null_values = [v for v in values if v is not None and str(v).strip() != "" and str(v).lower() != "nan"]
        non_null_count = len(non_null_values)
        null_ratio = 1.0 - (non_null_count / total_rows) if total_rows > 0 else 1.0

        # Evaluate signals
        col_score, col_rule = self.evaluate_column_name(column_name, rules)
        (
            val_pattern_score,
            alg_valid_score,
            masked_samples,
            match_count,
            valid_count,
            pattern_rule,
            val_desc,
        ) = self.evaluate_values(non_null_values, rules)

        # Apply null penalty if column has very few non-null values
        density_factor = 1.0
        if null_ratio > 0.8:
            density_factor = 0.6
        elif null_ratio > 0.5:
            density_factor = 0.85

        # Apply exclusion penalty if column explicitly matches negative rule
        if col_rule and col_rule.startswith("Exclusion match"):
            density_factor *= 0.20

        # Calculate overall weighted score
        w_col = weights.get("column_name", 0.35)
        w_val = weights.get("value_pattern", 0.40)
        w_alg = weights.get("algorithmic_validation", 0.25)
        
        # If no non-null values exist, score depends solely on column name
        if non_null_count == 0:
            overall_score = round(col_score * w_col, 4)
        else:
            raw_score = (col_score * w_col) + (val_pattern_score * w_val) + (alg_valid_score * w_alg)
            overall_score = round(raw_score * density_factor, 4)

        # Classify confidence tier
        if overall_score >= thresholds.get("high", 0.75):
            tier = ConfidenceTier.HIGH
            is_pii = True
        elif overall_score >= thresholds.get("medium", 0.45):
            tier = ConfidenceTier.MEDIUM
            is_pii = True
        elif overall_score >= thresholds.get("low", 0.25):
            tier = ConfidenceTier.LOW
            is_pii = True
        else:
            tier = ConfidenceTier.NONE
            is_pii = False

        # Build evidence steps trail
        steps = []
        if col_score > 0:
            steps.append(f"Column name '{column_name}' matched pattern '{col_rule}' (+{round(col_score * w_col, 3)} pts).")
        else:
            steps.append(f"Column name '{column_name}' had no positive identifier match.")

        if non_null_count > 0:
            match_pct = round((match_count / non_null_count) * 100, 1)
            steps.append(f"{match_count}/{non_null_count} ({match_pct}%) non-null values matched regex pattern '{pattern_rule}' (+{round(val_pattern_score * w_val, 3)} pts).")
            if val_desc:
                valid_pct = round((valid_count / non_null_count) * 100, 1)
                steps.append(f"Validation algorithm [{val_desc}]: {valid_count}/{non_null_count} ({valid_pct}%) values verified (+{round(alg_valid_score * w_alg, 3)} pts).")
        else:
            steps.append("No non-null data values available in sample.")

        if null_ratio > 0.5:
            steps.append(f"High sparsity warning: {round(null_ratio * 100, 1)}% null/empty entries (density penalty applied: x{density_factor}).")

        steps.append(f"Final Technical Confidence: {round(overall_score * 100, 1)}% -> Tier {tier.value}.")

        return FieldEvidence(
            column_name=column_name,
            data_class=self.data_class,
            overall_confidence=overall_score,
            confidence_tier=tier,
            column_name_score=round(col_score, 4),
            value_pattern_score=round(val_pattern_score, 4),
            algorithmic_validation_score=round(alg_valid_score, 4),
            total_rows=total_rows,
            non_null_rows=non_null_count,
            null_ratio=round(null_ratio, 4),
            matching_sample_count=match_count,
            validated_sample_count=valid_count,
            column_rule_matched=col_rule,
            pattern_rule_matched=pattern_rule,
            validator_used=val_desc,
            masked_samples=masked_samples[:5],
            evidence_steps=steps,
            is_candidate_pii=is_pii,
        )
