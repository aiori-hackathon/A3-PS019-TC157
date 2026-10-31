"""Unit tests for Government ID Detector (Aadhaar and PAN Card)."""

from src.detectors.govt_id import GovtIdDetector
from src.detectors.verhoeff import generate_verhoeff
from src.detectors.base import ConfidenceTier, PersonalDataClass


def test_aadhaar_validation():
    detector = GovtIdDetector()
    rules = {}

    # Valid Aadhaar
    base = "45678901234"
    chk = generate_verhoeff(base)
    valid_aadhaar = f"{base[:4]} {base[4:8]} {base[8:]}{chk}"

    score, col_rule = detector.evaluate_column_name("emp_aadhaar_no", rules)
    assert score == 1.0

    pattern_score, val_score, masked, match_c, valid_c, _, _ = detector.evaluate_values(
        [valid_aadhaar, "XXXX", ""], rules
    )
    assert match_c >= 1
    assert valid_c >= 1
    assert len(masked) > 0
    assert masked[0].startswith("XXXX-XXXX-")


def test_aadhaar_invalid_leading_digits():
    detector = GovtIdDetector()
    # Cannot start with 0 or 1
    fmt, chk = detector._is_aadhaar("012345678901")
    assert fmt is False
    fmt2, chk2 = detector._is_aadhaar("112345678901")
    assert fmt2 is False


def test_pan_card_validation():
    detector = GovtIdDetector()
    rules = {}

    valid_pan = "ABCDE1234F"  # Individual entity code 'P' or 'E'
    valid_pan_ind = "ABCPE1234F"

    fmt_ok, ent_ok = detector._is_pan(valid_pan_ind)
    assert fmt_ok is True
    assert ent_ok is True

    # Invalid PAN format
    fmt_bad, _ = detector._is_pan("12345ABCDE")
    assert fmt_bad is False

    # Negative column pattern
    score_neg, reason = detector.evaluate_column_name("order_id", rules)
    assert score_neg == 0.0
