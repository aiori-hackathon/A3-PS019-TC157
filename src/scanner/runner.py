"""Scanner Engine orchestrator combining detectors, rule engine, and metadata linkage."""

import os
from typing import Any, Callable, Optional
import pandas as pd

from ..detectors import (
    BaseDetector,
    ConfidenceTier,
    DobDetector,
    EmailDetector,
    FieldEvidence,
    GovtIdDetector,
    NameDetector,
    PersonalDataClass,
    PhoneDetector,
)
from ..metadata.gap_analyzer import MetadataRegistry
from ..rules.engine import RuleConfig
from .csv_scanner import CsvScanner
from .db_scanner import DbScanner


class ScannerEngine:
    """Core scanning engine for personal-data candidate discovery and privacy evidence inventory."""

    def __init__(
        self,
        rule_config: Optional[RuleConfig] = None,
        metadata_registry: Optional[MetadataRegistry] = None,
        sample_size: int = 1000,
    ):
        self.rule_config = rule_config or RuleConfig()
        self.metadata_registry = metadata_registry or MetadataRegistry()
        self.csv_scanner = CsvScanner(sample_size=sample_size)
        self.db_scanner = DbScanner(sample_size=sample_size)

        # Initialize detectors
        self.detectors: list[BaseDetector] = [
            NameDetector(),
            EmailDetector(),
            PhoneDetector(),
            GovtIdDetector(),
            DobDetector(),
        ]

    def scan_column(
        self,
        column_name: str,
        values: list[Any],
        dataset_name: str,
        table_name: str,
    ) -> dict[str, Any]:
        """Scan a single column across all 5 detectors and produce evidence and metadata link."""
        weights = self.rule_config.weights
        thresholds = self.rule_config.thresholds
        rules = self.rule_config.rules

        best_evidence: Optional[FieldEvidence] = None
        best_score = -1.0

        for detector in self.detectors:
            evidence = detector.detect(
                column_name=column_name,
                values=values,
                rules=rules,
                weights=weights,
                thresholds=thresholds,
            )
            if evidence.overall_confidence > best_score:
                best_score = evidence.overall_confidence
                best_evidence = evidence

        if not best_evidence:
            # Fallback for empty or unrecognized column
            best_evidence = FieldEvidence(
                column_name=column_name,
                data_class=PersonalDataClass.NAME,
                overall_confidence=0.0,
                confidence_tier=ConfidenceTier.NONE,
                is_candidate_pii=False,
            )

        # Link with Metadata Registry and analyze privacy compliance gap
        meta_record = self.metadata_registry.link_and_analyze(
            dataset_name=dataset_name,
            table_name=table_name,
            column_name=column_name,
            data_class=best_evidence.data_class.value if best_evidence.is_candidate_pii else "Non-PII",
            confidence_tier=best_evidence.confidence_tier.value,
            overall_confidence=best_evidence.overall_confidence,
        )

        return {
            "dataset_name": dataset_name,
            "table_name": table_name,
            "column_name": column_name,
            "detected_class": best_evidence.data_class.value if best_evidence.is_candidate_pii else "Non-PII",
            "is_pii": best_evidence.is_candidate_pii,
            "confidence_score": best_evidence.overall_confidence,
            "confidence_tier": best_evidence.confidence_tier.value,
            "column_score": best_evidence.column_name_score,
            "value_pattern_score": best_evidence.value_pattern_score,
            "validation_score": best_evidence.algorithmic_validation_score,
            "total_rows": best_evidence.total_rows,
            "non_null_rows": best_evidence.non_null_rows,
            "null_ratio": best_evidence.null_ratio,
            "matching_sample_count": best_evidence.matching_sample_count,
            "validated_sample_count": best_evidence.validated_sample_count,
            "column_rule_matched": best_evidence.column_rule_matched or "None",
            "pattern_rule_matched": best_evidence.pattern_rule_matched or "None",
            "validator_used": best_evidence.validator_used or "None",
            "masked_samples": best_evidence.masked_samples,
            "evidence_steps": best_evidence.evidence_steps,
            "declared_purpose": meta_record.declared_purpose or "MISSING / UNDECLARED",
            "retention_period": meta_record.retention_period or "MISSING / UNDECLARED",
            "is_purpose_missing": meta_record.is_purpose_missing,
            "is_retention_missing": meta_record.is_retention_missing,
            "gap_severity": meta_record.gap_severity.value if best_evidence.is_candidate_pii else "N/A (Non-PII)",
            "remediation_guidance": meta_record.remediation_guidance if best_evidence.is_candidate_pii else "No action required.",
            "legal_notes": meta_record.legal_notes,  # Deliberately blank for human legal reviewer
        }

    def scan_all(
        self,
        csv_files: list[str],
        db_files: list[str],
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> list[dict[str, Any]]:
        """Run scan across all provided CSV and SQLite files."""
        results: list[dict[str, Any]] = []
        total_targets = len(csv_files) + len(db_files)
        processed = 0

        # Scan CSV files
        for csv_path in csv_files:
            file_name = os.path.basename(csv_path)
            table_name = os.path.splitext(file_name)[0]
            if progress_callback:
                progress_callback(processed / total_targets, f"Scanning CSV: {file_name}")

            try:
                col_data = self.csv_scanner.inspect_csv(csv_path)
                for col_name, values in col_data.items():
                    res = self.scan_column(col_name, values, file_name, table_name)
                    results.append(res)
            except Exception as e:
                print(f"Error scanning {file_name}: {e}")

            processed += 1

        # Scan SQLite databases
        for db_path in db_files:
            db_name = os.path.basename(db_path)
            if progress_callback:
                progress_callback(processed / total_targets, f"Scanning Database: {db_name}")

            try:
                db_data = self.db_scanner.inspect_db(db_path)
                for tbl_name, col_data in db_data.items():
                    for col_name, values in col_data.items():
                        res = self.scan_column(col_name, values, db_name, tbl_name)
                        results.append(res)
            except Exception as e:
                print(f"Error scanning {db_name}: {e}")

            processed += 1

        if progress_callback:
            progress_callback(1.0, "Scan completed successfully.")

        return results
