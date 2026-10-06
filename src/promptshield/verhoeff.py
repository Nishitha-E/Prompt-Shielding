"""Verhoeff algorithm implementation for Aadhaar checksum validation and surrogate generation."""

VERHOEFF_D = [
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

VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

VERHOEFF_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(number: str) -> bool:
    """Validate a number string using the Verhoeff checksum algorithm."""
    clean_num = "".join(d for d in str(number) if d.isdigit())
    if not clean_num:
        return False
    c = 0
    for i, digit in enumerate(reversed([int(d) for d in clean_num])):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][digit]]
    return c == 0


def generate_verhoeff_checksum(number: str) -> int:
    """Compute the Verhoeff checksum digit for a number string."""
    clean_num = "".join(d for d in str(number) if d.isdigit())
    if not clean_num:
        raise ValueError("Number must contain at least one digit.")
    c = 0
    for i, digit in enumerate(reversed([int(d) for d in clean_num])):
        c = VERHOEFF_D[c][VERHOEFF_P[(i + 1) % 8][digit]]
    return VERHOEFF_INV[c]


def generate_verhoeff_number(number: str) -> str:
    """Append a Verhoeff checksum digit to a number string."""
    clean_num = "".join(d for d in str(number) if d.isdigit())
    checksum = generate_verhoeff_checksum(clean_num)
    return f"{clean_num}{checksum}"
