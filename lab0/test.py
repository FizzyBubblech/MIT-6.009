#!/usr/bin/env python3

import sys, os, json, copy
import wrapper, verifier

# Enumerate files in ./cases
cases = sorted([f[:-3] for f in os.listdir('cases/') if os.path.isfile("cases/"+f) and f.endswith(".in")])
cases.sort(key=int)

errors = 0

# If any args are given, keep only those cases
def print_usage():
    print("%s 4 5 7 # RUNS TESTS 4, 5 and 7" % sys.argv[0])

if len(sys.argv)>1:
    selected_cases = []
    for c in sys.argv[1:]:
        if c in cases:
            selected_cases.append(c)
        else:
            print_usage()
            sys.exit(1)
    cases = selected_cases

passed = []
for case in cases:
    d = None
    g = None

    print("-----------------")
    print("Test %s.in" % case)

    # Read inputs
    with open("cases/"+case+'.in', 'r') as f:
        d = json.loads(f.read())

    print("Description: %s" % d["test"])

    # Run test
    r = wrapper.run_test(copy.deepcopy(d))

    # JSON-encode and decode the result to mimic sandboxed autograder
    try:
        r = json.loads(json.dumps(r))
    except:
        print("WARNING: your return value in this test uses an unsupported type!")
        print("Stick to dictionaries, objects, arrays, strings, numbers, booleans, and null.")

    # Read golden output
    with open("cases/"+case+'.out', 'r') as f:
        g = json.loads(f.read().replace("\'", '"').replace("(", '[').replace(")", ']'))

    # Verify test output
    ok, message = verifier.verify(r, d, g)

    # Accounting and grading
    if ok:
        passed.append(case)
    errors += 0 if ok else 1
    print (("OK" if ok else "FAILED") + ": Test \"" + case + ".in\" " + (message if message else (" yields \n" + str(r) + "\n, expecting \n" + str(g))))

print("--------------")

if errors == 0:
    print("Yay! Everything looks correct! Good work.")
else:
    print("Oh no! " + str(errors) + " tests failed, so you aren't done yet.")
