import unittest

from game.rules import HIT, MISS, UNKNOWN, fire_area_shot, fire_shot, ships_remaining


class FireShotTests(unittest.TestCase):
    def test_fire_shot_marks_miss(self):
        shots = [[UNKNOWN] * 10 for _ in range(10)]
        incoming = [[UNKNOWN] * 10 for _ in range(10)]
        ships = [[(2, 2)]]
        hits = set()

        result = fire_shot(shots, incoming, ships, hits, 0, 0)

        self.assertEqual(result, "miss")
        self.assertEqual(shots[0][0], MISS)
        self.assertEqual(incoming[0][0], MISS)
        self.assertEqual(hits, set())

    def test_fire_shot_marks_hit_then_sink(self):
        shots = [[UNKNOWN] * 10 for _ in range(10)]
        incoming = [[UNKNOWN] * 10 for _ in range(10)]
        ships = [[(1, 1), (1, 2)]]
        hits = set()

        first = fire_shot(shots, incoming, ships, hits, 1, 1)
        second = fire_shot(shots, incoming, ships, hits, 1, 2)

        self.assertEqual(first, "hit")
        self.assertEqual(second, "sink")
        self.assertEqual(shots[1][1], HIT)
        self.assertEqual(shots[1][2], HIT)
        self.assertEqual(incoming[1][1], HIT)
        self.assertEqual(incoming[1][2], HIT)
        self.assertEqual(hits, {(1, 1), (1, 2)})

    def test_fire_shot_rejects_repeated_target(self):
        shots = [[UNKNOWN] * 10 for _ in range(10)]
        incoming = [[UNKNOWN] * 10 for _ in range(10)]
        ships = [[(4, 4)]]
        hits = set()

        fire_shot(shots, incoming, ships, hits, 4, 4)
        result = fire_shot(shots, incoming, ships, hits, 4, 4)

        self.assertEqual(result, "already")
        self.assertEqual(hits, {(4, 4)})


class FireAreaShotTests(unittest.TestCase):
    def test_fire_area_shot_hits_and_misses_from_center(self):
        shots = [[UNKNOWN] * 10 for _ in range(10)]
        incoming = [[UNKNOWN] * 10 for _ in range(10)]
        ships = [[(4, 4), (4, 5)], [(6, 6)]]
        hits = set()

        summary = fire_area_shot(shots, incoming, ships, hits, 4, 4)

        self.assertEqual(summary, {"hits": 2, "misses": 7, "sinks": 1, "already": 0})
        self.assertEqual(hits, {(4, 4), (4, 5)})
        self.assertEqual(shots[4][4], HIT)
        self.assertEqual(shots[4][5], HIT)
        self.assertEqual(shots[3][3], MISS)

    def test_fire_area_shot_clips_at_board_edge(self):
        shots = [[UNKNOWN] * 10 for _ in range(10)]
        incoming = [[UNKNOWN] * 10 for _ in range(10)]
        ships = [[(0, 0), (1, 1)]]
        hits = set()

        summary = fire_area_shot(shots, incoming, ships, hits, 0, 0)

        self.assertEqual(summary, {"hits": 2, "misses": 2, "sinks": 1, "already": 0})
        self.assertEqual(hits, {(0, 0), (1, 1)})
        self.assertEqual(shots[0][1], MISS)
        self.assertEqual(shots[1][0], MISS)

    def test_fire_area_shot_counts_already_fired_cells(self):
        shots = [[UNKNOWN] * 10 for _ in range(10)]
        incoming = [[UNKNOWN] * 10 for _ in range(10)]
        ships = [[(3, 3)]]
        hits = set()

        shots[3][3] = HIT
        incoming[3][3] = HIT
        hits.add((3, 3))

        summary = fire_area_shot(shots, incoming, ships, hits, 3, 3)

        self.assertEqual(summary["already"], 1)
        self.assertEqual(summary["hits"], 0)
        self.assertEqual(summary["sinks"], 0)


class ShipsRemainingTests(unittest.TestCase):
    def test_ships_remaining_counts_only_unsunk_ships(self):
        ships = [[(0, 0)], [(1, 1), (1, 2)], [(5, 5)]]
        hits = {(0, 0), (1, 1)}

        remaining = ships_remaining(ships, hits)

        self.assertEqual(remaining, 2)


if __name__ == "__main__":
    unittest.main()
