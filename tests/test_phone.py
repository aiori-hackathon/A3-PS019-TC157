"""Unit tests for Indian Phone Detector."""

from src.detectors.phone import PhoneDetector
from src.detectors.base import ConfidenceTier, PersonalDataClass


def test_indian_phone_formats():
    detector = PhoneDetector()
    rules = {}

    col_score, _ = detector.evaluate_column_name("mobile_no", rules)
    assert col_score == 1.0

    valid_phones = [
        "9876543210",
        "+91 98765 43210",
        "+91-87654-32109",
        "07654321098",
        "6123456789",
    ]
    pat_score, val_score, masked, match_c, valid_c, _, _ = detector.evaluate_values(valid_phones, rules)

    assert match_c == 5
    assert valid_c == 5
    assert pat_score == 1.0
    assert len(masked) == 5
    assert "+91" in masked[0]
    assert "XXX" in masked[0]


def test_phone_decoys_rejection():
    detector = PhoneDetector()
    rules = {}

    # 10-digit numbers starting with 0-5 are not Indian cellular lines
    decoys = ["1004928172", "2918273645", "5544332211", "999"]
    pat_score, val_score, _, match_c, valid_c, _, _ = detector.evaluate_values(decoys, rules)
    assert valid_c == 0

    # Negative column pattern
    score_neg, _ = detector.evaluate_column_name("postal_pin_code", rules)
    assert score_neg == 0.0
