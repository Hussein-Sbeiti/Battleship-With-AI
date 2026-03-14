# game/rules.py
# Battleship Project
# This file contains the core battle rules:
# shooting, hit/miss logic, sinking ships, and win checks.
# No UI code lives here.

'''
This file contains the core Battleship rules, completely independent of the UI. 
The fire_shot() function determines whether a shot is a hit, miss, sink, or already-fired location, 
and updates both the attacker’s shot board and the defender’s incoming board. 
It also tracks hits using a set so ship destruction can be detected efficiently. 
The ships_remaining() function counts how many ships are still afloat and is used to determine when the game is over.
'''

from typing import List, Tuple, Set

# Shot state constants
UNKNOWN = 0   # cell has not been shot yet
MISS = 1      # shot missed
HIT = 2       # shot hit a ship

# Coordinate type (row, column)
Coord = Tuple[int, int]


def fire_shot(
    shots_board: List[List[int]],         # attacker's shot tracking board
    incoming_board: List[List[int]],      # defender's incoming shot board
    defender_ships: List[List[Coord]],    # defender ships as coordinate lists
    defender_hits: Set[Coord],            # set of hit coordinates
    row: int,
    col: int,
) -> str:
    """
    Handle a single shot fired at (row, col).

    Returns one of:
    - "already" → this cell was already shot
    - "miss"    → no ship at this location
    - "hit"     → ship hit but not sunk
    - "sink"    → ship fully destroyed
    """

    # Prevent firing at the same cell twice
    if shots_board[row][col] != UNKNOWN:
        return "already"

    target = (row, col)

    # Check if the shot hits any ship
    ship_index = None
    for i, ship in enumerate(defender_ships):
        if target in ship:
            ship_index = i
            break

    # No ship found → MISS
    if ship_index is None:
        shots_board[row][col] = MISS
        incoming_board[row][col] = MISS
        return "miss"

    # Ship was hit
    shots_board[row][col] = HIT
    incoming_board[row][col] = HIT
    defender_hits.add(target)

    # Check if the entire ship is now hit
    ship_coords = defender_ships[ship_index]
    if all(coord in defender_hits for coord in ship_coords):
        return "sink"

    # Otherwise, it's just a hit
    return "hit"


def ships_remaining(defender_ships: List[List[Coord]], defender_hits: Set[Coord]) -> int:
    """
    Count how many ships are still afloat.
    A ship is considered sunk only if all its coordinates are hit.
    """
    remaining = 0

    for ship in defender_ships:
        # If any part of the ship is not hit, it is still alive
        if not all(coord in defender_hits for coord in ship):
            remaining += 1

    return remaining

def ship_hit_counters(ships_list, hits_set):
    """
    Returns a list like ["2/3", "0/4", ...] in the same order as ships_list.
    Each entry is: hits_on_that_ship / ship_length
    """
    counters = []
    for ship in ships_list:
        hit_count = sum(1 for cell in ship if cell in hits_set)
        counters.append(f"{hit_count}/{len(ship)}")
    return counters

def ship_hit_counters_sorted(ships_list, hits_set):
    ships_sorted = sorted(ships_list, key=len)
    return ship_hit_counters(ships_sorted, hits_set)


