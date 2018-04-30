#!/usr/bin/env python3
import doctest
import traceback

try:
    import lab
except ImportError:
    import solution as lab

VERBOSE = True
FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE

def print_title(title):
    title = "** " + title + " **"
    stars = "*" * len(title)
    print("\n" + stars)
    print(title)
    print("*" * len(title))

def run(tests):
    results = []
    runner = doctest.DocTestRunner(optionflags=FLAGS, verbose=VERBOSE)

    for test in tests:
        print_title("Testing {}".format(test.name))
        results.append((test.name, runner.run(test)))

    print_title("SUMMARY")
    for name, (failed, tried) in results:
        label = ":)" if failed == 0 else ":'("
        print("[{}] {} ({}/{})".format(label, name, tried - failed, tried))

    if runner.failures == 0:
        print_title("All selected doctests passed! Yay!")
    else:
        print_title("Oh no! Some of the doctests failed. See above for details!")

def main():
    try:
        lab_tests = [t for t in doctest.DocTestFinder().find(lab) if t.examples]
        lab_tests.sort(key=lambda t: t.lineno or 0)

        """
        with open("readme.md", 'U') as readme:
            contents = readme.read() #.decode("utf-8")
            readme_tests = [doctest.DocTestParser().get_doctest(contents, {}, "readme", "readme.md", 0)]
        """

        commands = []
        commands.append(("Run all doctests in lab.py", lab_tests))

        for test in lab_tests:
            commands.append(("Run doctests of {}".format(test.name), [test]))

        print("Choose one option:")
        for idx, (label, _) in enumerate(commands):
            print("[{:2d}] {}".format(idx, label))

        option = None
        while not (isinstance(option, int) and 0 <= option < len(commands)):
            option = eval(input("Pick an option [0-{}]: ".format(len(commands) - 1)))

        run(commands[option][1])

    except: # pylint: disable=bare-except
        print("** Could not check your code **\n{}".format(traceback.format_exc()))

if __name__ == '__main__':
    main()
