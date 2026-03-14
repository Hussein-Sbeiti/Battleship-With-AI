import unittest

from app.app_models import GameState


class GameStateResetTests(unittest.TestCase):
    def test_reset_for_new_game_restores_default_battle_state(self):
        state = GameState()
        state.num_ships = 4
        state.placing_player = 2
        state.placing_orientation = "V"
        state.current_turn = 2
        state.p2_ai_mode = "medium"
        state.p1_board[0][0] = 1
        state.p2_board[2][2] = 1
        state.p1_shots[4][4] = 2
        state.p2_shots[5][5] = 1
        state.p1_incoming[1][1] = 2
        state.p2_incoming[3][3] = 1
        state.p1_ships = [[(0, 0)]]
        state.p2_ships = [[(2, 2), (2, 3)]]
        state.p1_hits = {(0, 0)}
        state.p2_hits = {(2, 2)}
        state.p1_specials = 0
        state.p2_specials = 1

        state.reset_for_new_game()

        self.assertEqual(state.num_ships, 4)
        self.assertEqual(state.placing_player, 1)
        self.assertEqual(state.placing_orientation, "H")
        self.assertEqual(state.current_turn, 1)
        self.assertIsNone(state.p2_ai_mode)
        self.assertEqual(state.p1_specials, 3)
        self.assertEqual(state.p2_specials, 3)
        self.assertEqual(sum(sum(row) for row in state.p1_board), 0)
        self.assertEqual(sum(sum(row) for row in state.p2_board), 0)
        self.assertEqual(sum(sum(row) for row in state.p1_shots), 0)
        self.assertEqual(sum(sum(row) for row in state.p2_shots), 0)
        self.assertEqual(sum(sum(row) for row in state.p1_incoming), 0)
        self.assertEqual(sum(sum(row) for row in state.p2_incoming), 0)
        self.assertEqual(state.p1_ships, [])
        self.assertEqual(state.p2_ships, [])
        self.assertEqual(state.p1_hits, set())
        self.assertEqual(state.p2_hits, set())


if __name__ == "__main__":
    unittest.main()
