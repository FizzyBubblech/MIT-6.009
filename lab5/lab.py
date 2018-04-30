"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

class Contradiction(Exception):
    """ Raised if formula can't be satisfied """
    pass

def simplify_clause(clause, assignments):
    """Simplify the clause by removing literals that have received assignments.
       Raise Contradiction if an assignment makes the clause false"""
    s_clause = []
    for literal in clause:
        if literal[0] in assignments:
            # if literal is True, whole clause is true
            if literal[1] == assignments[literal[0]]:
                return True
            # False literal is skipped
        else:
            s_clause.append(literal)
    # if there are no terms left, the clause is false
    if len(s_clause) == 0: raise Contradiction
    return s_clause
        

def simplify_formula(formula, assignments):
    """Return simplified formula, True if assignemnts were updated with 
       singleton clauses.
       Raise Contradiction if formula is False with given assignments"""
    changed = False
    s_formula = []
    for clause in formula:
        s_clause = simplify_clause(clause, assignments)
        # if clause is satisfied, remove it
        if s_clause is True:
            continue
        # add singleton clause to assignments
        elif len(s_clause) == 1:
            assignments[s_clause[0][0]] = s_clause[0][1]
            changed = True
        else:    
            s_formula.append(s_clause)
    return s_formula, changed

def split(formula, var, val):
    """Try to satisfy a formula by setting var to val"""
    s_formula = formula
    assignments = {var: val}
    changed = True
    try:
        # simplify formula until there are no more assignments
        while changed:
            s_formula, changed = simplify_formula(formula, assignments)
        # try to satisfy it
        result = satisfying_assignment(s_formula)
        # add assignments if succeded
        if result is not None:
            result.update(assignments)
        return result
    # can't satisfy if there's contradiction
    except Contradiction:
        return None

def satisfying_assignment(formula):
    """Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    {'a': True}
    >>> satisfying_assignment([[('a', True)], [('a', False)]])"""
    # return empty, if no more variables
    if len(formula) == 0:
        return {} 
    # choose first variable 
    var = formula[0][0][0]
    val = formula[0][0][1]
    # try to split
    result = split(formula, var, val)
    # if failed, try the opposite value
    if result is None:
        result = split(formula, var, not val)
    return result

def combinations(seq, n):
    """Generate all combinations of n elements from seq"""
    if n == 0:
        yield []
    elif len(seq) == n:
        yield seq
    elif n < len(seq):
        first = seq[0]
        rest = seq[1:]
        yield from combinations(rest, n)
        for s in combinations(rest,n-1):
            yield [first] + s

def boolify_scheduling_problem(student_preferences, session_capacities):
    """Convert a quiz-room-scheduling problem into a Boolean formula.
    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session
    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores."""
    students = list(student_preferences.keys())
    sessions = list(session_capacities.keys())
    
    def var_n(student, session):
        """Construct a variable name from student and session"""
        return student + "_" + session
    
    # cover rule 1 and 2
    exactly_one = []
    preferred = []
    for student in students:
        for combo in combinations(sessions, 2):
            exactly_one.append([(var_n(student, session), False)\
                                for session in combo])
        preferred.append([(var_n(student, session), True)\
                          for session in student_preferences[student]])
    # cover rule 3
    fit = []
    for session in sessions:
        # include only sessions with capacity 
        # less than number of students
        cap = session_capacities[session]
        if cap < len(students):
            for combo in combinations(students, cap+1):
                fit.append([(var_n(student, session), False)\
                            for student in combo])
                
    return exactly_one + preferred + fit