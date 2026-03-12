# utils/coords.py
# Coordinate helpers for Battleship

LETTERS = "ABCDEFGHIJ"  # String used to convert column index (0–9) into board letters A–J


def col_to_letter(col: int) -> str:
    return LETTERS[col]  # Convert numeric column (0–9) into corresponding letter


def row_to_number(row: int) -> str:
    return str(row + 1)  # Convert 0-based row index into human-readable 1–10 string


def to_label(row: int, col: int) -> str:
    return f"{LETTERS[col]}{row + 1}"  # Combine column letter and row number (ex: 0,0 → "A1")
