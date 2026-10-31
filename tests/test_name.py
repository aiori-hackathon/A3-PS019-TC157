"""Unit tests for Name Detector."""

from src.detectors.name import NameDetector


def test_name_detector():
    detector = NameDetector()
    rules = {}

    col_score, _ = detector.evaluate_column_name("customer_full_name", rules)
    assert col_score == 1.0

    valid_names = ["Rajesh Kumar", "Dr. Anita Desai", "Vikram Patel", "Sneha Rao"]
    pat_score, val_score, masked, match_c, valid_c, _, _ = detector.evaluate_values(valid_names, rules)

    assert match_c == 4
    assert valid_c == 4
    assert len(masked) == 4
    assert "*" in masked[0]


def test_name_decoys_and_negative_rules():
    detector = NameDetector()
    rules = {}

    # Negative column matches for products or table names
    col_score, _ = detector.evaluate_column_name("product_name", rules)
    assert col_score == 0.0

    col_score_table, _ = detector.evaluate_column_name("schema_table_name", rules)
    assert col_score_table == 0.0

    # Values with digits or symbols
    decoys = ["Widget3000", "4K-Monitor", "user_123@xyz", ""]
    pat_score, _, _, match_c, _, _, _ = detector.evaluate_values(decoys, rules)
    assert match_c == 0
