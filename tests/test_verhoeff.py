"""Unit tests for Verhoeff check-digit checksum algorithm."""

import pytest
from src.detectors.verhoeff import generate_verhoeff, validate_verhoeff


def test_verhoeff_known_valid():
    # Test numbers where check digit is already calculated
    # 236 -> check digit is 3 -> 2363 is valid
    chk = generate_verhoeff("236")
    assert validate_verhoeff(f"236{chk}") is True


def test_verhoeff_aadhaar_examples():
    # Example 11-digit base
    base = "98765432109"
    chk = generate_verhoeff(base)
    full = base + chk
    assert validate_verhoeff(full) is True

    # Altering single digit must fail
    corrupted_single = full[:-1] + ("1" if full[-1] != "1" else "2")
    assert validate_verhoeff(corrupted_single) is False

    # Adjacent transposition error (swap two adjacent digits) must fail
    transposed = full[:-3] + full[-1] + full[-2] + full[-3]
    assert validate_verhoeff(transposed) is False


def test_verhoeff_invalid_input():
    assert validate_verhoeff("") is False
    assert validate_verhoeff("abc") is False
    with pytest.raises(ValueError):
        generate_verhoeff("")
