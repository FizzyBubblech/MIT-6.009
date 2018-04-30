"""6.009 Lab 4 -- HyperMines"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


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
             "state: {}".format(game["state"])]
    print("\n".join(lines))
    
def make_board(dims, value):
    """
    Recursively construct an N-dimensional board filled with a given value.
    
    Args:
        dims (list): Dimensions of the board
        value (any): Value to put in the board
        
    Returns:
        A list representing board
        
    >>> make_board([2, 2, 2], 0)
    [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
    """
    if len(dims) == 1:
        return [value] * dims[0]
    else:
        return [make_board(dims[1:], value) for i in range(dims[0])]
    
def get_value(array, coords):
    """
    Return the value at the given location in the given array.
    
    Args:
        array (list): Array represented as a list of lists
        coords (list): Location in the array to get value from
        
    Returns:
        Value of the given location
        
    >>> get_value([[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [0, 0, 0])
    0
    """
    if len(coords) == 1:
        return array[coords[0]]
    else:
        return get_value(array[coords[0]], coords[1:])
    
def set_value(array, coords, value):
    """
    Change the value at the given location in the given array.
    
    Args:
        array (list): Array represented as a list of lists
        coords (list): Location whose value to change
    
    >>> array = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
    >>> set_value(array, [0, 0, 0], ".")
    >>> array
    [[['.', 0], [0, 0]], [[0, 0], [0, 0]]]
    """
    if len(coords) == 1:
        array[coords[0]] = value
    else:
        set_value(array[coords[0]], coords[1:], value)

def neighbors(dims, coords):
    """
    Generate neighbors' coordinates of the given location.
    
    Args:
        dims (list) : Dimensions
        coords (list) : Location whose neighbors to find
    
    Returns:
        A generator of neigbors' coordinates
        
    >>> list(neighbors([2, 2, 2], [0, 0, 0]))
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
    """
    if len(coords) == 0:
        yield tuple()
    else:
        for j in neighbors(dims[1:], coords[1:]):
            yield from ((x,)+j for x in (coords[0]-1, coords[0], coords[0]+1) if 0<=x<dims[0])
            
def all_coords(dims):
    """
    Generate all coordinates given dimensions of a board.
    
    Args:
        dims (list): Dimensions of a board
        
    Returns:
        A generator of all boards' coordinates
        
    >>> list(all_coords([2, 2, 2]))
    [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    """
    if len(dims) == 0:
        yield tuple()
    else:
        yield from ((i, )+j for i in range(dims[0]) for j in all_coords(dims[1:]))

def nd_new_game(dims, bombs):
    """Start a new game.

    Return a game state dictionary, with the "board" and "mask" fields
    adequately initialized.  This is an N-dimensional version of new_game().

    Args:
       dims (list): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> dump(nd_new_game([2, 4, 2], [[0, 0, 1], [1, 0, 0], [1, 1, 1]]))
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, False], [False, False], [False, False], [False, False]]
           [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    board = make_board(dims, 0)
    mask = make_board(dims, False)
    for b_coords in bombs:
        set_value(board, b_coords, '.')
        for n_coords in neighbors(dims, b_coords):
            value = get_value(board, n_coords)
            if value != ".":
                set_value(board, n_coords, value+1)
    return {"dimensions": dims, "board" : board, "mask" : mask, "state": "ongoing"}

def reveal_squares(game, coords):
    """
    Recursively reveal squares on the board, and return the number of squares that were revealed.
    
    Args:
        game (dict): Game state
        coords (list): Where to start revealing
        
    Returns:
        A number of squares revealed
        
    >>> game = {"dimensions": [2, 4, 2],
    ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                  [[False, False], [False, False], [False, False], [False, False]]],
    ...         "state": "ongoing"}
    >>> set_value(game["mask"], [0, 3, 0], True)
    >>> reveal_squares(game, [0, 3, 0])
    8
    >>> dump(game)
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, False], [False, True], [True, True], [True, True]]
           [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    """
    count = 1
    if get_value(game["board"], coords) == 0:
        for n_coords in neighbors(game["dimensions"], coords):
            if not get_value(game["mask"], n_coords):
                set_value(game["mask"], n_coords, True)
                count += reveal_squares(game, n_coords)
    return count 

def is_victory(game):
    """
    Determine whether the game is won or not.
    
    Args:
        game (dict): Game state
        
    Returns:
        True if the game is won, False otherwise
        
    >>> game = {"dimensions": [2, 4, 2],
    ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                  [[False, False], [False, False], [False, False], [False, False]]],
    ...         "state": "ongoing"}
    >>> is_victory(game)
    False
    >>> game = {"dimensions": [2, 2],
    ...         "board": [['.', 1],
    ...                   [1, 1]],
    ...         "mask": [[False, True],
    ...                  [True, True]],
    ...         "state": "ongoing"}
    >>> is_victory(game)
    True
    """
    covered_squares = 0
    for coords in all_coords(game["dimensions"]):
            if get_value(game["board"], coords) != "." and not get_value(game["mask"], coords):
                covered_squares += 1
    return True if covered_squares == 0 else False

def nd_dig(game, coords):
    """Recursively dig up square at coords and neighboring squares.

    Update game["mask"] to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No action
    should be taken and 0 returned if the incoming state of the game is not "ongoing".

    The updated state is "defeat" when at least one bomb is visible on the board
    after digging (i.e. game["mask"][bomb_location] == True), "victory" when all
    safe squares (squares that do not contain a bomb) and no bombs are visible,
    and "ongoing" otherwise.

    This is an N-dimensional version of dig().

    Args:
       game (dict): Game state
       coords (list): Where to start digging

    Returns:
       int: number of squares revealed

    >>> game = {"dimensions": [2, 4, 2],
    ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                  [[False, False], [False, False], [False, False], [False, False]]],
    ...         "state": "ongoing"}
    >>> nd_dig(game, [0, 3, 0])
    8
    >>> dump(game)
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, False], [False, True], [True, True], [True, True]]
           [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> game = {"dimensions": [2, 4, 2],
    ...         "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                   [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...         "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                  [[False, False], [False, False], [False, False], [False, False]]],
    ...         "state": "ongoing"}
    >>> nd_dig(game, [0, 0, 1])
    1
    >>> dump(game)
    dimensions: [2, 4, 2]
    board: [[3, '.'], [3, 3], [1, 1], [0, 0]]
           [['.', 3], [3, '.'], [1, 1], [0, 0]]
    mask:  [[False, True], [False, True], [False, False], [False, False]]
           [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    if game["state"] != "ongoing" or get_value(game["mask"], coords):
        return 0
    
    set_value(game["mask"], coords, True)
    if get_value(game["board"], coords) == '.':
        game["state"] = "defeat"
        return 1
    else:
        revealed = reveal_squares(game, coords)
        if is_victory(game): game["state"] = "victory"
        return revealed


def nd_render(game, xray=False):
    """Prepare a game for display.

    Returns an N-dimensional array (nested lists) of "_" (hidden squares), "."
    (bombs), " " (empty squares), or "1", "2", etc. (squares neighboring bombs).
    game["mask"] indicates which squares should be visible.  If xray is True (the
    default is False), game["mask"] is ignored and all cells are shown.

    This is an N-dimensional version of render().

    Args:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game["mask"]

    Returns:
       An n-dimensional array (nested lists)

    >>> nd_render({"dimensions": [2, 4, 2],
    ...            "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                      [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...            "mask": [[[False, False], [False, True], [True, True], [True, True]],
    ...                     [[False, False], [False, False], [True, True], [True, True]]],
    ...            "state": "ongoing"},
    ...           False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> nd_render({"dimensions": [2, 4, 2],
    ...            "board": [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                      [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...            "mask": [[[False, False], [False, True], [False, False], [False, False]],
    ...                     [[False, False], [False, False], [False, False], [False, False]]],
    ...            "state": "ongoing"},
    ...           True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    result = make_board(game["dimensions"], None)
    for coords in all_coords(game["dimensions"]):
        b_v = get_value(game["board"], coords)
        m_v = get_value(game["mask"], coords)
        set_value(result, coords, "_" if (not xray) and (not m_v) else " " if b_v == 0 else str(b_v))
    return result

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
