"""Verhoeff Checksum Algorithm Implementation.

The Verhoeff algorithm is a decimal check digit algorithm developed by Dutch mathematician
Jacobus Verhoeff in 1969. It detects all single-digit errors and 100% of adjacent
transposition errors. It is utilized by UIDAI for 12-digit Indian Aadhaar validation.
"""

from typing import Union

# Multiplication table d (dihedral group D5 multiplication)
D_TABLE: list[list[int]] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

# Permutation table p
P_TABLE: list[list[int]] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

# Inverse table inv
INV_TABLE: list[int] = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(number: Union[str, int]) -> bool:
    """Validate a numeric string with a Verhoeff check digit.

    Args:
        number: The digit string or integer to validate (e.g. 12-digit Aadhaar).

    Returns:
        True if the check digit is valid according to Verhoeff algorithm, False otherwise.
    """
    clean_str = "".join(filter(str.isdigit, str(number)))
    if not clean_str:
        return False

    c = 0
    # Process digits right to left (index 0 is check digit at rightmost position)
    for i, digit_char in enumerate(reversed(clean_str)):
        digit = int(digit_char)
        c = D_TABLE[c][P_TABLE[i % 8][digit]]

    return c == 0


def generate_verhoeff(number: Union[str, int]) -> str:
    """Generate the Verhoeff check digit for a given number.

    Args:
        number: The digit string without the check digit.

    Returns:
        The single check digit character '0'-'9'.
    """
    clean_str = "".join(filter(str.isdigit, str(number)))
    if not clean_str:
        raise ValueError("Number must contain at least one digit.")

    c = 0
    # Process right to left starting at position index 1
    for i, digit_char in enumerate(reversed(clean_str)):
        digit = int(digit_char)
        c = D_TABLE[c][P_TABLE[(i + 1) % 8][digit]]

    return str(INV_TABLE[c])
