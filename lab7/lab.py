import json
# NO ADDITIONAL IMPORTS!

class School:

    def __init__(self,data):
        self.students = {student[0]: set(student[1:]) for student in data}
        #
        self.old_state = None
        self.cur_state = str(self.students)
        self.cliques = self.get_cliques()

    def add_student(self, student):
        """
        add a student to the school, in accord with the representation that you
        choose

        student is a list containing [name, interest1, interest2, ...]
        """
        if student[0] not in self.students:
            self.students[student[0]] = set(student[1:])
            self.cur_state = str(self.students)

    def remove_student(self, student_name):
        """
        remove a student from the school
        """
        if student_name in self.students:
            del self.students[student_name]
            self.cur_state = str(self.students)

    def update_student(self, student_name, student_interests):
        """
        modify the student's interests, and update friendships and cliques
        appropriately
        """
        if student_name in self.students:
            self.students[student_name] = set(student_interests)
            self.cur_state = str(self.students)
        
    def get_common_interests(self, s1, s2):
        """ helper: return common interests of two students """
        return self.students[s1] & self.students[s2]
        
    def are_they_friends(self, student1_name, student2_name):
        """
        check if two students in the school are friends.  if so, return True.
        if they are not, or if one of the students does not go to the school,
        return False.
        """
        if student1_name != student2_name and\
           student1_name in self.students and\
           student2_name in self.students:
            return len(self.get_common_interests(student1_name, student2_name)) > 0
        else: return False

    def get_friendship_weight(self, student1_name, student2_name):
        """
        return the weight of the friendship between two students,
        as defined by the number of their mutual interests
        if they are not friends, return None
        """
        if self.are_they_friends(student1_name, student2_name):
            return len(self.get_common_interests(student1_name, student2_name))
        else: return None

    def find_friends_for_student(self, student_name):
        """
        return a list of the friends of a given student
        if the student is not in the school, return an empty list
        """
        if student_name in self.students:
            return [student for student in self.students 
                    if self.are_they_friends(student_name, student)]
        else: return []

    def get_cliques(self):
        """
        return a list of all the cliques in the school.  there should be no
        repeats.

        each clique should be a list, set, or tuple of student names (as strings)
        """
        if self.old_state != self.cur_state:
            cliques = set()
            for s1 in self.students:
                clique = {s1}
                for s2 in self.students:
                    if all(self.are_they_friends(s2, s) for s in clique):
                        clique.add(s2)
                if len(clique) > 1:
                    cliques.add(tuple(sorted(clique)))
            
            self.cliques = list(cliques)
            self.old_state = self.cur_state
            
        return self.cliques

    def get_cliques_for_student(self, student_name):
        """
        when queried with the name of a student, should return a list of all
        cliques to which they belong.  if the student is not in the school,
        return an empty list

        each clique should be a list, set, or tuple of student names (as strings)
        """
        return [clique for clique in self.get_cliques() if student_name in clique]

    def get_cliques_size_n(self, n):
        """
        when queried with a number, should return a list of all cliques of that
        size

        each clique should be a list, set, or tuple of student names (as strings)
        """
        return [clique for clique in self.get_cliques() if len(clique) == n]

    def find_independent_set(self, student_name):
        """
        find and return a maximal independent set in the graph to which the
        given student belongs

        each independent set should be a list, set, or tuple of student names
        (as strings)
        """
        ind_sets = set()
        for s1 in self.students:
            ind_set = {s1}
            for s2 in self.students:
                if all(not self.are_they_friends(s2, s) for s in ind_set):
                    ind_set.add(s2)
            if student_name in ind_set:
                ind_sets.add(tuple(sorted(ind_set)))
        
        return max(ind_sets, key=len)
    
    def __iter__(self):
        """
        a generator that yields the names of the students in the school, in
        any order.
        """
        yield from self.students

    def __contains__(self, student_name):
        """
        returns True if the given student is in the school, and False otherwise
        """
        return student_name in self.students
