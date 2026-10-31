"""Unit tests for Date of Birth (DOB) Detector."""

from src.detectors.dob import DobDetector


def test_dob_multi_format():
    detector = DobDetector()
    rules = {}

    col_score, _ = detector.evaluate_column_name("date_of_birth", rules)
    assert col_score == 1.0

    valid_dobs = [
        "1990-05-24",
        "15/08/1985",
        "22-11-1972",
        "14-Jul-1995",
        "12/30/2000",
    ]
    pat_score, val_score, masked, match_c, valid_c, _, _ = detector.evaluate_values(valid_dobs, rules)

    assert match_c == 5
    assert valid_c == 5
    assert pat_score == 1.0
    assert len(masked) == 5
    assert "**/**/" in masked[0]


def test_dob_future_dates_and_decoys():
    detector = DobDetector()
    rules = {}

    # Future date (year 2099) cannot be DOB
    future_dates = ["2099-01-01", "2050-12-31"]
    _, val_score, _, match_c, valid_c, _, _ = detector.evaluate_values(future_dates, rules)
    assert valid_c == 0

    # Negative column exclusion
    col_score, _ = detector.evaluate_column_name("created_at_timestamp", rules)
    assert col_score == 0.0
