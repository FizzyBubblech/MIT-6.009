import doctest
import time
import traceback
from copy import deepcopy
from importlib import reload

try:
    import lab
    reload(lab)
except ImportError:
    import solution
    lab = solution

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
def testdoc(target):
    if target == "lab":
        results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
    elif target == "readme":
        results = doctest.testfile("readme.md", optionflags=TESTDOC_FLAGS, report=False)
    return results[0] == 0

def checkdoc(kind):
    tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
    for test in tests:
        if test.name == "lab":
            continue
        if kind == "docstrings" and not test.docstring:
            return "Oh no, '{}' has no docstring!".format(test.name)
        if kind == "doctests" and not test.examples:
            return "Oh no, '{}' has no doctests!".format(test.name)
    return {"docstrings": "All functions are documented; great!",
            "doctests": "All functions have tests; great!"}[kind]

def nd_dig(game, args):
    result = lab.nd_dig(game, args)
    # capture both the number of tiles revealed and the updated game state
    return [result, game]

def nd_new_game(dims, bombs):
    return lab.nd_new_game(dims, bombs)

def integration_test_nd(game, coords):
    results = []
    for coord in coords:
        results.append([("dig", lab.nd_dig(game, coord)),
                        ("board", deepcopy(game)),
                        ("render", lab.nd_render(game)),
                        ("render/xray", lab.nd_render(game, True))])
    return results

def ui_new_game(d):
    r = lab.nd_new_game([d["num_rows"], d["num_cols"]], d["bombs"])
    return r

def ui_dig(d):
    game, row, col = d["game"], d["row"], d["col"]
    nb_dug = lab.nd_dig(game, [row, col])
    status = game['state']
    return [game, status, nb_dug]

def ui_render(d):
    r = lab.nd_render(d["game"], d["xray"])
    return r

FUNCTIONS = {
    "checkdoc": checkdoc,
    "testdoc": testdoc,
    "nd_new_game": nd_new_game,
    "nd_dig": nd_dig,
    "nd_render": lab.nd_render,
    "integration_nd": integration_test_nd
}

def run_test(input_data):
    start_time = time.time()

    try:
        result = FUNCTIONS[input_data["function"]](*input_data["args"])
        return (time.time() - start_time), result
    except ValueError as e:
        return None, e.message
    except:
        return None, traceback.format_exc()
