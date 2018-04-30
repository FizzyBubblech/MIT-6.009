#!/usr/bin/env python3
import os
import lab
import json
import unittest
import copy

import sys
sys.setrecursionlimit(10000)

TEST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'test_inputs')

class TestSat(unittest.TestCase):
    def opencase(self, casename):
        with open(os.path.join(TEST_DIRECTORY, casename + ".json")) as f:
            cnf = json.load(f)
            return [[(variable, polarity)
                     for variable, polarity in clause]
                    for clause in cnf]

    def satisfiable(self, casename):
        cnf = self.opencase(casename)
        asgn = lab.satisfying_assignment(copy.deepcopy(cnf))
        self.assertIsNotNone(asgn)

        # Check that every clause has some literal appearing in the assignment.
        self.assertTrue(all(any(variable in asgn and asgn[variable] == polarity
                                for variable, polarity in clause)
                            for clause in cnf))

    def unsatisfiable(self, casename):
        cnf = self.opencase(casename)
        asgn = lab.satisfying_assignment(copy.deepcopy(cnf))
        self.assertIsNone(asgn)

    def test_A_10_3_100(self):
        self.unsatisfiable('10_3_100')

    def test_B_20_3_1000(self):
        self.unsatisfiable('20_3_1000')

    def test_C_100_10_100(self):
        self.satisfiable('100_10_100')

    def test_D_1000_5_10000(self):
        self.unsatisfiable('1000_5_10000')

    def test_E_1000_10_1000(self):
        self.satisfiable('1000_10_1000')

    def test_F_1000_11_1000(self):
        self.satisfiable('1000_11_1000')

class TestScheduling(unittest.TestCase):
    def opencase(self, casename):
        with open(os.path.join(TEST_DIRECTORY, casename + ".json")) as f:
            v = json.load(f)
            return ({p[0] : set(p[1])
                     for p in v[0].items()}, v[1])

    def satisfiable(self, casename):
        students, sessions = self.opencase(casename)
        formula = lab.boolify_scheduling_problem(copy.deepcopy(students),
                                                      copy.deepcopy(sessions))
        sched = lab.satisfying_assignment(formula)
        self.assertIsNotNone(sched)

        unplaced_students = set(students)

        for var, val in sched.items():
            if val:
                student, session = var.split('_')

                self.assertIn(student, unplaced_students)
                unplaced_students.remove(student)

                self.assertIn(student, students)
                self.assertIn(session, students[student])

                self.assertIn(session, sessions)
                self.assertTrue(sessions[session] >= 1)
                sessions[session] -= 1

        self.assertEqual(len(unplaced_students), 0)

    def unsatisfiable(self, casename):
        students, sessions = self.opencase(casename)
        sched = lab.satisfying_assignment(
            lab.boolify_scheduling_problem(copy.deepcopy(students),
                                                copy.deepcopy(sessions)))
        self.assertIsNone(sched)

    def test_A_3_3(self):
        self.satisfiable('3_3')

    def test_B_10_10(self):
        self.satisfiable('10_10')

    def test_C_10_10_unsat(self):
        self.unsatisfiable('10_10_unsat')

    def test_D_15_5(self):
        self.satisfiable('15_5')

    def test_E_17_5_unsat(self):
        self.unsatisfiable('17_5_unsat')

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
