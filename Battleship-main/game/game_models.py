# game/models.py
# Battleship Project - shared game state
# Created: 2026-02-06

'''
This is an earlier or alternate version of game state modeling that uses Board objects instead of raw lists. 
It tracks placement-related information such as which player is placing ships and the orientation, and it provides a reset method to clear boards between games. 
Compared to app/app_models.py, this version is more minimal and focused on setup rather than full gameplay. 
It’s likely retained for architectural clarity or future refactoring.
'''

from dataclasses import dataclass
from typing import Optional
from game.board import Board


@dataclass
class GameState:
    # Number of ships selected by the player (from welcome screen)
    # None means the game has not started yet
    num_ships: Optional[int] = None

    # Which player is currently placing ships (1 or 2)
    placing_player: int = 1

    # Length of the ship currently being placed
    placing_ship_len: int = 1

    # Ship orientation:
    # "H" = horizontal, "V" = vertical
    placing_orientation: str = "H"

    # Player 1 and Player 2 boards
    # Uses the Board class instead of raw lists
    p1_board: Board = Board()
    p2_board: Board = Board()

    def reset_for_new_game(self) -> None:
        """
        Reset placement-related state and clear both boards.
        This prepares the game for a fresh start.
        """
        # Reset placement flow
        self.placing_player = 1
        self.placing_ship_len = 1
        self.placing_orientation = "H"

        # Clear both boards
        self.p1_board.clear()
        self.p2_board.clear()
