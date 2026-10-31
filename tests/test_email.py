"""Unit tests for Email Detector."""

from src.detectors.email import EmailDetector
from src.detectors.base import ConfidenceTier, PersonalDataClass


def test_email_detector():
    detector = EmailDetector()
    rules = {}

    score, col_rule = detector.evaluate_column_name("user_email_address", rules)
    assert score == 1.0

    valid_emails = ["priya.sharma@enterprise.in", "test.user99@gmail.com", "contact@cybercorp.org"]
    pat_score, val_score, masked, match_c, valid_c, _, _ = detector.evaluate_values(valid_emails, rules)

    assert match_c == 3
    assert valid_c == 3
    assert pat_score == 1.0
    assert val_score == 1.0
    assert len(masked) == 3
    assert "@" in masked[0]
    assert "*" in masked[0]


def test_email_invalid_and_decoys():
    detector = EmailDetector()
    rules = {}

    decoys = ["not_an_email", "user@", "@domain.com", "user@domain", ""]
    pat_score, val_score, _, match_c, _, _, _ = detector.evaluate_values(decoys, rules)
    assert match_c == 0

    # Negative column exclusion
    score_neg, _ = detector.evaluate_column_name("email_status", rules)
    assert score_neg == 0.0
