'''
This file defines a simple Ship dataclass and a helper function for building a ship set based on the chosen difficulty. 
Given a number like 3, it produces ships of length 1, 2, and 3, which directly matches your game design. 
The ships here are configuration objects only They don’t track position or hits themselves. 
This keeps ship sizing logic separate from board placement and combat logic.
'''

# game/ships.py
# Battleship Project - ship configuration helpers
# Created: 2026-02-06

from dataclasses import dataclass
from typing import List


@dataclass
class Ship:
    """
    A ship is defined mainly by its length.
    We'll track its cells/hits later during gameplay.
    """
    length: int


def build_ship_set(num_ships: int) -> List[Ship]:
    """
    Convert the welcome-screen selection into a ship set.
    1 -> [1]
    2 -> [1,2]
    3 -> [1,2,3]
    ...
    """
    return [Ship(length=i) for i in range(1, num_ships + 1)]