import os
import importlib, importlib.util
import json

try:
    import lab
    importlib.reload(lab)
except ImportError:
    import solution
    lab = solution

data = {}
for i in os.listdir('resources'):
    if not i.endswith('.json'):
        continue

    x = i.rsplit('.', 1)[0]
    
    with open('./resources/%s.json' % x, 'r') as f:
        js = json.load(f)
        data[x] = js

def load_data(d):
    return data

import traceback
def trim(val, lim=400):
    val_str = str(val)
    return val_str if len(val_str)<lim else val_str[0:lim]+' ...'

school = None
all_students = set()

def get_friendships():
    try:
        # for each student, make a friendship graph
        friendship = {}
        for student1 in all_students:
            friendship[student1] = []
            for student2 in all_students:
                # Adding this asymmetrically so that issues in the 
                # student code show up
                if school.are_they_friends(student1, student2):
                    friendship[student1].append(student2)
        print (friendship)
        return friendship
    except:
        print(traceback.format_exc(), flush=True)
        return {}

def ui_setup_school(test_case_name):
    global school
    global all_students
    students_data = data[test_case_name]
    # student names are unique
    all_students = set()
    try:        
        # Create a new school
        school = lab.School(students_data)
        # Add all students
        for student_data in students_data:
            all_students.add(student_data[0])
        
        return get_friendships()
    except:
        print(traceback.format_exc(), flush=True)
        return {}


    
def ui_add_student(student_data):
    print(student_data)
    try:
        school.add_student(student_data)
        print(list(school))
        all_students.add(student_data[0])
        print(all_students)
        return get_friendships()
    except:
        print(traceback.format_exc(), flush=True)
        return {}

def ui_remove_student(student_name):
    try:
        school.remove_student(student_name)
        all_students.remove(student_name)
        return get_friendships()
    except:
        print(traceback.format_exc(), flush=True)
        return {}

def ui_update_student(student_data):
    try:
        school.update_student(student_data[0], student_data[1:])
        return get_friendships()
    except:
        print(traceback.format_exc(), flush=True)
        return {}

def process_cliques(cliques):
    return [list(clique) for clique in cliques]

def ui_get_cliques_for_student(student_name):
    try:
        # Just a list of lists of students
        cliques = school.get_cliques_for_student(student_name)
        print("lab.get_cliques_for_student returned: " + trim(cliques), flush=True)
        return process_cliques(cliques)
    except:
        print(traceback.format_exc(), flush=True)
        return []

def ui_get_cliques(d):
    try:
        # Just a list of lists of students
        cliques = school.get_cliques()
        print("lab.get_cliques returned: " + trim(cliques), flush=True)
        return process_cliques(cliques)
    except:
        print(traceback.format_exc(), flush=True)
        return []

def ui_get_cliques_size_n(n):
    try:
        # Just a list of lists of students
        cliques = school.get_cliques_size_n(int(n))
        print("lab.get_cliques_size_n returned: " + trim(cliques), flush=True)
        return process_cliques(cliques)
    except:
        print(traceback.format_exc(), flush=True)
        return []


def ui_find_independent_set(student_name):
    try:
        # Just a list of lists of students
        ind_set = school.find_independent_set(student_name)
        print("lab.find_independent_set returned: " + trim(ind_set), flush=True)
        return list(ind_set)
    except:
        print(traceback.format_exc(), flush=True)
        return []