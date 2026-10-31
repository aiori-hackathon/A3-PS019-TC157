"""Metadata Registry and Compliance Gap Analyzer."""

from dataclasses import dataclass
from enum import Enum
import os
from typing import Any, Optional
import pandas as pd


class GapSeverity(str, Enum):
    """Compliance gap severity level."""
    CRITICAL = "Critical Gap"
    HIGH = "High Gap"
    MEDIUM = "Medium Gap"
    COMPLIANT = "Declared"


@dataclass
class FieldMetadataRecord:
    """Metadata linkage and privacy compliance gap profile for a single column."""
    dataset_name: str
    table_name: str
    column_name: str
    data_class: str
    confidence_tier: str
    overall_confidence: float
    declared_purpose: Optional[str]
    retention_period: Optional[str]
    legal_notes: str
    is_purpose_missing: bool
    is_retention_missing: bool
    gap_severity: GapSeverity
    remediation_guidance: str


class MetadataRegistry:
    """Manages metadata registry mapping from metadata.csv and computes compliance gaps."""

    def __init__(self, metadata_path: Optional[str] = None):
        self.metadata_path = metadata_path
        self.registry: dict[tuple[str, str], dict[str, Any]] = {}
        if metadata_path and os.path.exists(metadata_path):
            self.load_metadata(metadata_path)

    def load_metadata(self, path: str) -> None:
        self.metadata_path = path
        df = pd.read_csv(path)
        self.registry.clear()
        for _, row in df.iterrows():
            table = str(row.get("table_name", "")).strip().lower()
            col = str(row.get("column_name", "")).strip().lower()
            purpose = str(row.get("declared_purpose", "")).strip()
            retention = str(row.get("retention_period", "")).strip()
            legal = str(row.get("legal_notes", "")).strip()
            
            # Treat nan, null, or empty string as missing
            purpose_val = None if purpose.lower() in ("nan", "none", "") else purpose
            retention_val = None if retention.lower() in ("nan", "none", "") else retention
            legal_val = "" if legal.lower() in ("nan", "none") else legal

            self.registry[(table, col)] = {
                "dataset_name": str(row.get("dataset_name", "")),
                "table_name": table,
                "column_name": col,
                "declared_purpose": purpose_val,
                "retention_period": retention_val,
                "legal_notes": legal_val,
            }

    def link_and_analyze(
        self,
        dataset_name: str,
        table_name: str,
        column_name: str,
        data_class: str,
        confidence_tier: str,
        overall_confidence: float,
    ) -> FieldMetadataRecord:
        """Link a discovered field to declared metadata and determine compliance status."""
        table_key = table_name.lower().strip()
        col_key = column_name.lower().strip()

        meta = self.registry.get((table_key, col_key))
        if meta:
            purpose = meta.get("declared_purpose")
            retention = meta.get("retention_period")
            legal_notes = meta.get("legal_notes", "")
        else:
            purpose = None
            retention = None
            legal_notes = ""

        is_purpose_missing = (purpose is None or purpose.strip() == "")
        is_retention_missing = (retention is None or retention.strip() == "")

        # Compute Gap Severity based on missing attributes and data confidence
        if is_purpose_missing and is_retention_missing:
            if confidence_tier in ("High", "Medium"):
                severity = GapSeverity.CRITICAL
                remediation = "Urgent: Unregistered Personal Data. Add to RoPA (Record of Processing Activities), specify lawful purpose, and define binding retention schedule."
            else:
                severity = GapSeverity.HIGH
                remediation = "Verify whether field contains true personal data; document declared purpose and retention limits."
        elif is_purpose_missing:
            severity = GapSeverity.HIGH
            remediation = "Missing declared lawful processing purpose. Define operational requirement under privacy policy."
        elif is_retention_missing:
            severity = GapSeverity.MEDIUM
            remediation = "Purpose is declared, but retention schedule is missing. Establish maximum storage limitation and automated purging window."
        else:
            severity = GapSeverity.COMPLIANT
            remediation = "Processing purpose and retention schedule are documented in compliance registry."

        return FieldMetadataRecord(
            dataset_name=dataset_name,
            table_name=table_name,
            column_name=column_name,
            data_class=data_class,
            confidence_tier=confidence_tier,
            overall_confidence=overall_confidence,
            declared_purpose=purpose,
            retention_period=retention,
            legal_notes=legal_notes,
            is_purpose_missing=is_purpose_missing,
            is_retention_missing=is_retention_missing,
            gap_severity=severity,
            remediation_guidance=remediation,
        )
