# game/board.py
# Battleship Project - Board data + placement validation
# Created: 2026-02-06

'''
This file defines a lightweight Board class that represents a 10×10 grid and provides helper methods for ship placement. 
It knows how to check whether a ship can be placed (can_place), how to place it (place), 
and how to compute which cells a ship would occupy based on position, length, and orientation. 
The board itself does not know about players, turns, or hits — it strictly manages grid validity. 
This separation keeps placement logic clean and reusable.
'''

from dataclasses import dataclass, field  # dataclass auto-generates init and useful methods
from typing import List, Tuple  # Used for type hints (2D grid and coordinate pairs)

GRID_SIZE = 10  # Board is 10x10


@dataclass
class Board:
    # 2D grid representing the board
    # 0 = empty cell
    # 1 = ship occupies cell
    grid: List[List[int]] = field(
        default_factory=lambda: [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    )  # Creates a fresh 10x10 grid filled with 0s

    def clear(self) -> None:
        """
        Reset the board to an empty state.
        Used when starting a new game.
        """
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]  # Rebuild empty 10x10 grid

    def can_place(self, row: int, col: int, length: int, orientation: str) -> bool:
        """
        Check whether a ship can be placed at the given position.
        Returns True if the ship fits on the board and does not overlap.
        """
        cells = self._cells_for_ship(row, col, length, orientation)  # Get all cells ship would occupy

        if not cells:  # If helper returned empty list, placement is invalid
            return False

        return all(self.grid[r][c] == 0 for r, c in cells)  # Ensure all target cells are empty

    def place(self, row: int, col: int, length: int, orientation: str) -> List[Tuple[int, int]]:
        """
        Place a ship on the board.
        Marks the grid cells and returns the ship's coordinates.
        """
        cells = self._cells_for_ship(row, col, length, orientation)  # Calculate ship cell positions

        for r, c in cells:  # Loop through each ship cell
            self.grid[r][c] = 1  # Mark grid cell as occupied by a ship

        return cells  # Return list of coordinates for that ship

    def _cells_for_ship(self, row: int, col: int, length: int, orientation: str):
        """
        Internal helper:
        Calculates the list of board cells a ship would occupy.
        Returns an empty list if placement is invalid.
        """

        if orientation not in ("H", "V"):  # Must be Horizontal or Vertical
            return []

        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):  # Start position must be inside board
            return []

        if length <= 0:  # Ship length must be positive
            return []

        if orientation == "H":  # Horizontal placement
            if col + length - 1 >= GRID_SIZE:  # Check right boundary
                return []
            return [(row, col + i) for i in range(length)]  # Build horizontal coordinates

        # Vertical placement
        if row + length - 1 >= GRID_SIZE:  # Check bottom boundary
            return []

        return [(row + i, col) for i in range(length)]  # Build vertical coordinates
