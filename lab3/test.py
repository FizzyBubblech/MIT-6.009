#!/usr/bin/env python3
import os
import lab
import json
import unittest
import doctest
from copy import deepcopy

TEST_DIRECTORY = os.path.dirname(__file__)

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
TESTDOC_SKIP = ["lab"]

class TestDocTests(unittest.TestCase):
    def test_doctests_run(self):
        """ Checking to see if all lab doctests run successfully """
        results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
        self.assertEqual(results[0], 0)

    def test_all_doc_strings_exist(self):
        """ Checking if docstrings have been written for everything in lab.py """
        tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
        for test in tests:
            if test.name in TESTDOC_SKIP:
                continue
            if not test.docstring:
                missing = "Oh no, '{}' has no docstring!".format(test.name)
                self.fail(missing)


class TestNewGame(unittest.TestCase):
    def test_newsmallgame(self):
        """ Testing new_game on a small board """
        result = lab.new_game(10, 8, [(7, 3), (2, 6), (8, 7), (4, 4), (3, 5),
                                      (4, 6), (6, 2), (9, 4), (4, 2), (4, 0),
                                      (8, 6), (9, 7), (8, 5), (5, 0), (7, 2),
                                      (5, 3)])
        expected = {"board": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 1, 1, 1],
                              [0, 0, 0, 0, 1, 2, ".", 1],
                              [1, 2, 1, 2, 2, ".", 3, 2],
                              [".", 3, ".", 3, ".", 3, ".", 1],
                              [".", 4, 3, ".", 2, 2, 1, 1],
                              [1, 3, ".", 4, 2, 0, 0, 0],
                              [0, 2, ".", ".", 2, 2, 3, 2],
                              [0, 1, 2, 3, 3, ".", ".", "."],
                              [0, 0, 0, 1, ".", 3, 4, "."]],
                    "dimensions": [10, 8],
                    "mask": [[False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False]],
                    "state": "ongoing"}
        self.assertEqual(result, expected)

    def test_newmediumgame(self):
        """ Testing new_game on a medium board """
        result = lab.new_game(30, 16, [(16, 6), (17, 7), (14, 4), (13, 4),
                                       (0, 7), (21, 6), (2, 5), (5, 5), (6, 10),
                                       (12, 6), (24, 14), (14, 1), (24, 1),
                                       (26, 12), (8, 15), (9, 3), (16, 0),
                                       (19, 13), (15, 14), (13, 10), (18, 10),
                                       (21, 15), (28, 15), (29, 14), (11, 15),
                                       (14, 8), (17, 8), (24, 8), (25, 5),
                                       (2, 1), (10, 3), (27, 2), (17, 6),
                                       (7, 15), (15, 0), (21, 8), (20, 0),
                                       (1, 10), (10, 4), (14, 6), (1, 0),
                                       (4, 11), (27, 0), (9, 13), (23, 5),
                                       (14, 12), (20, 15), (3, 15), (26, 14),
                                       (4, 8), (10, 15), (7, 11), (18, 1),
                                       (25, 4), (26, 3), (22, 14), (28, 2),
                                       (13, 2), (19, 6), (1, 4), (21, 4),
                                       (1, 9), (8, 7), (23, 1), (22, 11),
                                       (19, 5), (18, 7), (0, 6), (26, 4),
                                       (3, 4), (5, 9), (24, 13), (20, 8),
                                       (19, 0), (0, 3), (21, 13), (3, 3),
                                       (28, 9), (11, 1), (12, 10), (24, 10),
                                       (18, 13), (0, 0), (21, 0), (3, 13),
                                       (27, 13), (5, 15), (26, 9), (17, 4),
                                       (7, 9), (19, 9), (24, 7), (22, 5),
                                       (3, 8), (27, 8), (9, 5), (23, 13),
                                       (5, 2), (10, 2)])
        with open("test_outputs/test_newmediumgame.json") as f:
            expected = json.load(f)
        self.assertEqual(result, expected)


    def test_newlargegame(self):
        """ Testing new_game on a medium board """
        with open("test_outputs/test_newlargegame.json") as f:
            expected = json.load(f)
        with open("test_inputs/test_newlargegame.json") as f:
            inputs = json.load(f)
        result = lab.new_game(inputs["num_rows"], inputs["num_cols"], inputs["bombs"])
        self.assertEqual(result, expected)


class TestDig(unittest.TestCase):
    def test_dig(self):
        for t in ('complete', 'mine', 'small'):
            with self.subTest(test=t):
                with open("test_outputs/test_dig%s.json" % t) as f:
                    expected = json.load(f)
                with open("test_inputs/test_dig%s.json" % t) as f:
                    inputs = json.load(f)
                game = inputs["game"]
                result = {"revealed": lab.dig(game, inputs["row"], inputs["col"]), "game": game}
                self.assertEqual(result, expected)


class TestRender(unittest.TestCase):
    def test_render(self):
        """ Testing render on a small board """
        with open("test_inputs/test_render.json") as f:
            inp = json.load(f)
        result = lab.render(inp)
        expected = [[" ", " ", " ", " ", " ", " ", " ", " "],
                    [" ", " ", " ", " ", " ", "1", "1", "1"],
                    [" ", " ", " ", " ", "1", "2", "_", "_"],
                    ["1", "2", "1", "2", "2", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"]]
        self.assertEqual(result, expected)

class TestRenderAscii(unittest.TestCase):
    def test_asciismall(self):
        """ Testing render_ascii on a small 2d board """
        with open("test_inputs/test_asciismall.json") as f:
            input = json.load(f)
        result = lab.render_ascii(input)
        expected = ("        \n"
                    "     111\n"
                    "    12__\n"
                    "12122___\n"
                    "________\n"
                    "________\n"
                    "________\n"
                    "________\n"
                    "________\n"
                    "________")
        self.assertEqual(result, expected)

    def test_asciixray(self):
        """ Testing render_ascii on a small 2d board with xray """
        with open("test_inputs/test_asciixray.json") as f:
            inputs = json.load(f)
        result = lab.render_ascii(inputs["game"], inputs["xray"])
        expected = ("        \n"
                    "     111\n"
                    "    12.1\n"
                    "12122.32\n"
                    ".3.3.3.1\n"
                    ".43.2211\n"
                    "13.42   \n"
                    " 2..2232\n"
                    " 1233...\n"
                    "   1.34.")
        self.assertEqual(result, expected)


class TestIntegration(unittest.TestCase):
    def test_integration(self):
        """ dig, render, and render_ascii on boards """
        for t in range(1, 4):
            with self.subTest(test=t):
                with open("test_outputs/test_integration%d.json" % t) as f:
                    expected = json.load(f)
                with open("test_inputs/test_integration%s.json" % t) as f:
                    inputs = json.load(f)
                results = []
                game = inputs['game']
                for coord in inputs['coords']:
                    results.append([["dig", lab.dig(game, *coord)],
                                    ["board", deepcopy(game)],
                                    ["render", lab.render(game)],
                                    ["render/xray", lab.render(game, True)],
                                    ["render_ascii", lab.render_ascii(game)],
                                    ["render_ascii/xray", lab.render_ascii(game, True)]])
                self.assertEqual(results, expected)


class TestBugHunt(unittest.TestCase):
    def test_bugs_mines0(self):
        """ Check the mines0 implementation """
        expected = {"correct": ["newgame_board", "newgame_state",
                                "newgame_mask", "newgame_dimensions",
                                "victory_state", "defeat_state", "dig_reveal",
                                "dig_neighbors", "multiple_dig_nop",
                                "completed_dig_nop", "dig_mask", "dig_count",
                                "newgame_state"],
                    "incorrect": []}
        result = lab.run_implementation_tests("mines0")
        self.assertEqual(set(result["correct"]), set(expected["correct"]))
        self.assertEqual(set(result["incorrect"]), set(expected["incorrect"]))

    def test_bugs_mines1(self):
        """ Check the mines1 implementation """
        expected = {"incorrect": ["newgame_board", "newgame_mask",
                                   "newgame_dimensions", "victory_state",
                                   "dig_reveal", "dig_neighbors",
                                   "multiple_dig_nop", "completed_dig_nop",
                                   "dig_mask", "newgame_state"],
                    "correct": ["defeat_state", "dig_count"]}
        result = lab.run_implementation_tests("mines1")
        self.assertEqual(set(result["correct"]), set(expected["correct"]))
        self.assertEqual(set(result["incorrect"]), set(expected["incorrect"]))

    def test_bugs_mines2(self):
        """ Check the mines2 implementation """
        expected = {"incorrect": ["newgame_mask", "victory_state", "dig_reveal",
                                  "dig_neighbors", "dig_mask", "dig_count"],
                    "correct": ["newgame_board", "newgame_state",
                                "newgame_dimensions", "defeat_state",
                                "multiple_dig_nop", "completed_dig_nop",
                                "newgame_state"]}
        result = lab.run_implementation_tests("mines2")
        self.assertEqual(set(result["correct"]), set(expected["correct"]))
        self.assertEqual(set(result["incorrect"]), set(expected["incorrect"]))

    def test_bugs_mines3(self):
        """ Check the mines3 implementation """
        expected = {"incorrect": ["victory_state", "defeat_state",
                                  "dig_neighbors", "dig_count"],
                    "correct": ["newgame_board", "newgame_state",
                                "newgame_mask", "newgame_dimensions",
                                "dig_reveal", "multiple_dig_nop",
                                "completed_dig_nop", "dig_mask",
                                "newgame_state"]}
        result = lab.run_implementation_tests("mines3")
        self.assertEqual(set(result["correct"]), set(expected["correct"]))
        self.assertEqual(set(result["incorrect"]), set(expected["incorrect"]))

    def test_bugs_mines4(self):
        """ Check the mines4 implementation """
        expected = {"correct": ["newgame_board", "newgame_state",
                                "newgame_mask", "newgame_dimensions",
                                "victory_state", "defeat_state", "dig_reveal",
                                "dig_neighbors", "multiple_dig_nop",
                                "completed_dig_nop", "dig_mask",
                                "newgame_state"],
                    "incorrect": ['dig_count']}
        result = lab.run_implementation_tests("mines4")
        self.assertEqual(set(result["correct"]), set(expected["correct"]))
        self.assertEqual(set(result["incorrect"]), set(expected["incorrect"]))

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
