"""Unit tests for Scanner Engine."""

import os
from src.scanner.runner import ScannerEngine
from src.rules.engine import RuleConfig
from src.metadata.gap_analyzer import MetadataRegistry


def test_scanner_engine_execution():
    engine = ScannerEngine()
    
    # Scan single synthetic phone column
    phones = ["+91 98765 43210", "9876543210", "+91-87654-32109"]
    res = engine.scan_column("contact_phone", phones, "sample.csv", "sample")

    assert res["is_pii"] is True
    assert res["detected_class"] == "Phone"
    assert res["confidence_tier"] in ("High", "Medium")
    assert len(res["masked_samples"]) > 0
    assert len(res["evidence_steps"]) > 0
    assert res["legal_notes"] == ""  # Stays blank for human reviewer
