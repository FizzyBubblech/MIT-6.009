import os
import doctest
import time
import traceback

import importlib, importlib.util
from copy import deepcopy
from collections import OrderedDict

# programmatically import buggy implementations

buggy_impls = OrderedDict()
for i in sorted(os.listdir('resources')):
    if not i.endswith('.py'):
        continue
    x = i.rsplit('.', 1)[0]
    spec = importlib.util.spec_from_file_location(x, "resources/%s.py" % x)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    buggy_impls[i] = mod


try:
    import lab
    importlib.reload(lab)
except ImportError:
    import solution
    lab = solution

# list different implementations
# called by ui
def list_impls(d):
    return ["lab"] + list(buggy_impls.keys())

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

def dig(game, *args): # Dig mutates game in place
    result = lab.dig(game, *args)
    return [result, game]

def nd_dig(game, *args):
    result = lab.nd_dig(game, *args)
    return [result, game]

def new_game(num_rows, num_cols, bombs):
    return lab.new_game(num_rows, num_cols, list(map(tuple, bombs)))

def get_impl(d):
    if d["impl"] in buggy_impls:
        return buggy_impls[d["impl"]]
    return lab

def ui_new_game(d):
    r = get_impl(d).new_game(d["num_rows"], d["num_cols"], d["bombs"])
    return r

def ui_dig(d):
    game, row, col = d["game"], d["row"], d["col"]
    nb_dug = get_impl(d).dig(game, row, col)
    status = game['state']
    return [game, status, nb_dug]

def ui_render(d):
    g = d['game']
    x = d['xray']
    b = g['board']
    m = g['mask']
    r = d['our_renderer']
    if r:
        return [[ '_' if (not x) and (not m[r][c]) else ' ' if b[r][c] == 0 else str(b[r][c]) for c in range(d['num_cols'])] for r in range(d['num_rows'])]
    else:
        try:
            r = get_impl(d).render(d["game"], d["xray"])
        except:
            r = [['ERROR' for i in range(d['num_cols'])] for j in range(d['num_rows'])]
        return r

def check_module(x):
    spec = importlib.util.spec_from_file_location(x, "resources/%s.py" % x)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return lab.test_mines_implementation(mod)

FUNCTIONS = {
    "checkdoc": checkdoc,
    "testdoc": testdoc,
    "new_game": new_game,
    "dig": dig,
    "render": lab.render,
    "render_ascii": lab.render_ascii,
    "check_module": check_module,
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
