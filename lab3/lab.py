"""6.009 Lab 3 -- Six Double-Oh Mines"""

import unittest
import importlib, importlib.util
# NO ADDITIONAL IMPORTS ALLOWED!


## CODE FOR MINES IMPLEMENTATION

def dump(game):
    """Print a human-readable representation of game.

    Arguments:
       game (dict): Game state


    >>> dump({'dimensions': [1, 2], 'mask': [[False, False]], 'board': [['.', 1]], 'state': 'ongoing'})
    dimensions: [1, 2]
    board: ['.', 1]
    mask:  [False, False]
    state: ongoing
    """
    lines = ["dimensions: {}".format(game["dimensions"]),
             "board: {}".format("\n       ".join(map(str, game["board"]))),
             "mask:  {}".format("\n       ".join(map(str, game["mask"]))),
             "state: {}".format(game["state"]),
             ]
    print("\n".join(lines))
    
def neighbor_squares(dims, row, col):
    """Helper function: returns square's neighbors"""
    return [(row+i, col+j) for i in range(-1,2) for j in range(-1,2) 
            if (0 <= row+i < dims[0]) and (0 <= col+j < dims[1])]
    
def new_game(num_rows, num_cols, bombs):
    """Start a new game.

    Return a game state dictionary, with the "dimensions", "state", "board" and
    "mask" fields adequately initialized.

    Args:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which can be
                     either tuples or lists

    Returns:
       A game state dictionary

    >>> dump(new_game(2, 4, [(0, 0), (1, 0), (1, 1)]))
    dimensions: [2, 4]
    board: ['.', 3, 1, 0]
           ['.', '.', 1, 0]
    mask:  [False, False, False, False]
           [False, False, False, False]
    state: ongoing
    """
    board = [['.' if ([r,c] in bombs) or ((r,c) in bombs) else 0 for c in range(num_cols)] 
             for r in range(num_rows)]
    mask = [[False]*num_cols for r in range(num_rows)]
    for br, bc in bombs:
        for nr, nc in neighbor_squares([num_rows, num_cols], br, bc):
            if board[nr][nc] != '.':
                board[nr][nc] += 1
    return {"dimensions": [num_rows, num_cols], "board" : board, "mask" : mask, "state": "ongoing"}

def reveal_squares(game, row, col):
    """Helper function: recursively reveal squares on the board, and return
    the number of squares that were revealed."""
    count = 1
    if game["board"][row][col] == 0:
        for r, c in neighbor_squares(game["dimensions"], row, col):
            if not game["mask"][r][c]:
                game["mask"][r][c] = True
                count += reveal_squares(game, r, c)
    return count

def is_victory(game):
    """Helper function: return True if the game is won"""
    covered_squares = 0
    for r in range(game["dimensions"][0]):
        for c in range(game["dimensions"][1]):
            if game["board"][r][c] != "." and not game["mask"][r][c]:
                covered_squares += 1
    return True if covered_squares == 0 else False

def dig(game, row, col):
    """Recursively dig up (row, col) and neighboring squares.

    Update game["mask"] to reveal (row, col); then recursively reveal (dig up)
    its neighbors, as long as (row, col) does not contain and is not adjacent
    to a bomb.  Return an integer indicating how many new squares were
    revealed.

    The state of the game should be changed to "defeat" when at least one bomb
    is visible on the board after digging (i.e. game["mask"][bomb_location] ==
    True), "victory" when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and "ongoing" otherwise.

    Args:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {"dimensions": [2, 4],
    ...         "board": [[".", 3, 1, 0],
    ...                   [".", ".", 1, 0]],
    ...         "mask": [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         "state": "ongoing"}
    >>> dig(game, 0, 3)
    4
    >>> dump(game)
    dimensions: [2, 4]
    board: ['.', 3, 1, 0]
           ['.', '.', 1, 0]
    mask:  [False, True, True, True]
           [False, False, True, True]
    state: victory

    >>> game = {"dimensions": [2, 4],
    ...         "board": [[".", 3, 1, 0],
    ...                   [".", ".", 1, 0]],
    ...         "mask": [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         "state": "ongoing"}
    >>> dig(game, 0, 0)
    1
    >>> dump(game)
    dimensions: [2, 4]
    board: ['.', 3, 1, 0]
           ['.', '.', 1, 0]
    mask:  [True, True, False, False]
           [False, False, False, False]
    state: defeat
    """
    if game["state"] != "ongoing" or game["mask"][row][col]:
        return 0
    
    game["mask"][row][col] = True
    if game["board"][row][col] == '.':
        game["state"] = "defeat"
        return 1
    else:
        revealed = reveal_squares(game, row, col)
        if is_victory(game): game["state"] = "victory"
        return revealed
    
def render(game, xray=False):
    """Prepare a game for display.

    Returns a two-dimensional array (list of lists) of "_" (hidden squares), "."
    (bombs), " " (empty squares), or "1", "2", etc. (squares neighboring bombs).
    game["mask"] indicates which squares should be visible.  If xray is True (the
    default is False), game["mask"] is ignored and all cells are shown.

    Args:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game["mask"]

    Returns:
       A 2D array (list of lists)

    >>> render({"dimensions": [2, 4],
    ...         "state": "ongoing",
    ...         "board": [[".", 3, 1, 0],
    ...                   [".", ".", 1, 0]],
    ...         "mask":  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render({"dimensions": [2, 4],
    ...         "state": "ongoing",
    ...         "board": [[".", 3, 1, 0],
    ...                   [".", ".", 1, 0]],
    ...         "mask":  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    rows, cols = game["dimensions"]
    return [["_" if (not xray) and (not game["mask"][r][c]) else " " if game["board"][r][c] == 0 
            else str(game["board"][r][c]) for c in range(cols)] for r in range(rows)]

def render_ascii(game, xray=False):
    """Render a game as ASCII art.

    Returns a string-based representation of argument "game".  Each tile of the
    game board should be rendered as in the function "render(game)".

    Args:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game["mask"]

    Returns:
       A string-based representation of game

    >>> print(render_ascii({"dimensions": [2, 4],
    ...                     "state": "ongoing",
    ...                     "board": [[".", 3, 1, 0],
    ...                               [".", ".", 1, 0]],
    ...                     "mask":  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    return "\n".join("".join(r) for r in render(game, xray))


## CODE FOR BUG HUNT / TESTING


class TestMinesImplementation(unittest.TestCase):
    """
    This class defines testing methods for each of the behaviors described in
    the lab handout.  In the methods below, mines_imp will be the module you
    are testing.  For example, to call the "dig" function from the
    implementation being tested, you can use:

        mines_imp.dig(game, r, c)

    You are welcome to use your methods from above as a "gold standard" to
    compare against, or to manually construct test cases, or a mix of both.
    """
    
    def init_game(self):
        """Helper method: return dictionary representing a game""" 
        return {"board": [[0, 1, ".", 1, 0],
                          [1, 2, 1, 1, 0],
                          [".", 1, 0, 0, 0],
                          [2, 2, 0, 1, 1],
                          [".", 1, 0, 1, "."]],
                "dimensions": [5, 5],
                "mask": [[False, False, False, False, False],
                         [False, False, False, False, False],
                         [False, False, False, False, False],
                         [False, False, False, False, False],
                         [False, False, False, False, False]],
                "state": "ongoing"}
    
    def test_newgame_dimensions(self):
        """
        Tests that the dimensions of the game are initialized correctly.
        """
        result = new_game(5, 5, [(0,2), (2,0), (4,0), (4,4)])
        self.assertEqual(result["dimensions"], [5, 5])

    def test_newgame_board(self):
        """
        Tests that the board is initialized correctly.
        """
        result = new_game(5, 5, [(0,2), (2,0), (4,0), (4,4)])
        expected = self.init_game()
        self.assertEqual(result["board"], expected["board"])

    def test_newgame_mask(self):
        """
        Tests that the mask is initialized correctly (so that, if used with a
        working implementation of the dig function, it would behave as expected
        in all cases.
        """
        result = new_game(5, 5, [(0,2), (2,0), (4,0), (4,4)])
        expected = self.init_game()
        self.assertEqual(result["mask"], expected["mask"])

    def test_newgame_state(self):
        """
        Tests that the state of a new game is always "ongoing".
        """
        result = new_game(5, 5, [(0,2), (2,0), (4,0), (4,4)])
        self.assertEqual(result["state"], "ongoing")

    def test_dig_mask(self):
        """
        Tests that, in situations that should modify the game, dig affects the
        mask, and not the board.  (NOTE that this should not test for the
        correctness of dig overall, just that it modifies mask and does not
        modify board.)
        """
        result = self.init_game()
        expected = self.init_game()
        dig(result, 0, 3)
        self.assertEqual(result["board"], expected["board"])
        self.assertNotEqual(result["mask"], expected["mask"])

    def test_dig_reveal(self):
        """
        Tests that dig reveals the square that was dug.
        """
        result = self.init_game()
        dig(result, 0, 3)
        self.assertTrue(result["mask"][0][3])

    def test_dig_neighbors(self):
        """
        Tests that dig properly reveals other squares when appropriate (if a 0
        is revealed during digging, all of its neighbors should automatically
        be revealed as well).
        """
        result = self.init_game()
        dig(result, 0, 0)
        self.assertTrue(all([result["mask"][0][0], result["mask"][0][1], 
                             result["mask"][1][0], result["mask"][1][1]]))

    def test_completed_dig_nop(self):
        """
        Tests that dig does nothing when performed on a game that is not
        ongoing.
        """
        result = self.init_game()
        expected = self.init_game()
        result["state"] = "victory"
        dig(result, 0, 0)
        self.assertEqual(expected["board"], result["board"])
        self.assertEqual(expected["mask"], result["mask"])

    def test_multiple_dig_nop(self):
        """
        Tests that dig does nothing when performed on a square that has already
        been dug.
        """
        result = self.init_game()
        expected = self.init_game()
        result["mask"][0][1] = True
        expected["mask"][0][1] = True
        dig(result, 0, 1)
        self.assertEqual(expected["board"], result["board"])
        self.assertEqual(expected["mask"], result["mask"])
        
    def test_dig_count(self):
        """
        Tests that dig returns the number of squares that were revealed (NOTE
        this that should always report the number that were revealed, even if
        that is different from the number that should have been revealed).
        """
        game = self.init_game()
        result1 = dig(game, 0, 0)
        result2 = dig(game, 0, 3)
        self.assertEqual(result1, 4)
        self.assertEqual(result2, 1)

    def test_defeat_state(self):
        """
        Tests that the game state switches to "defeat" when a mine is dug, and
        not in other situations.
        """
        result = self.init_game()
        dig(result, 0, 0)
        self.assertNotEqual(result["state"], "defeat")
        dig(result, 0, 2)
        self.assertEqual(result["state"], "defeat")

    def test_victory_state(self):
        """
        Tests that the game state switches to "victory" when there are no more
        safe squares to dig, and not in other situations.
        """
        result = self.init_game()
        dig(result, 0, 0)
        self.assertNotEqual(result["state"], "victory")
        dig(result, 0, 4)
        dig(result, 3, 0)
        self.assertEqual(result["state"], "victory")


class TestResult6009(unittest.TestResult):
    """ Extend unittest framework for this 6.009 lab """
    def __init__(self, *args, **kwargs):
        """ Keep track of test successes, in addition to failures and errors """
        self.successes = []
        super().__init__(*args, **kwargs)

    def addSuccess(self, test):
        """ If a test succeeds, add it to successes """
        self.successes.append((test,))

    def results_dict(self):
        """ Report out names of tests that succeeded as 'correct', and those that
        either failed (e.g., a self.assert failure) or had an error (e.g., an uncaught
        exception during the test) as 'incorrect'.
        """
        return {'correct': [test[0]._testMethodName for test in self.successes],
                'incorrect': [test[0]._testMethodName for test in self.errors + self.failures]}


def run_implementation_tests(imp):
    """Test whether an implementation of the mines game correctly implements
    all the desired behaviors.

    Returns a dictionary with two keys: 'correct' and 'incorrect'.  'correct'
    maps to a list containing the string names of the behaviors that were
    implemented correctly (as given in the readme); and 'incorrect' maps to a
    list containing the string descriptions of the behaviors that were
    implemented incorrectly.

    Args:
        imp: a string containing the name of the module to be tested.

    Returns:
       A dictionary mapping strings to sequences.
    """
    global mines_imp
    spec = importlib.util.spec_from_file_location(imp, "resources/%s.py" % imp)
    mines_imp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mines_imp)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMinesImplementation)
    res = unittest.TextTestRunner(resultclass=TestResult6009,verbosity=1).run(suite).results_dict()
    return {'correct': [tag[5:] for tag in res['correct']],
            'incorrect': [tag[5:] for tag in res['incorrect']]}


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    doctest.testmod()

    # Test of my unit tests (on my own lab.py). Helpful to debug the
    # unit tests themselves.
    ## import lab as mines_imp
    ## unittest.main(verbosity=3, exit=False)

    # Test of resources/mines* with my implementation tests. Helpful
    # to detect bugs in those mines* implementations.
    ## for fname in ["mines0", "mines1", "mines2", "mines3", "mines4"]:
    ##    res = run_implementation_tests(fname)
    ##    print("\nTESTED", fname)
    ##    print(" correct:", res['correct'])
    ##    print(" incorrect:", res['incorrect'])
