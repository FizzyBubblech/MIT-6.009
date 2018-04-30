#!/usr/bin/env python3
import os
import lab
import json
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)


class TestTiny(unittest.TestCase):
    def setUp(self):
        # This is called automatically and will load the tiny.json file into
        # a variable called self.data.
        filename = 'resources/tiny.json'
        with open(filename, 'r') as f:
            self.data = json.load(f)
            
    def test_01(self):
        school = lab.School(self.data)
        self.assertTrue("Regina" in school)
        self.assertTrue("Gretchen" in school)
        self.assertTrue(school.are_they_friends("Regina", "Gretchen"))
        self.assertEqual(school.get_friendship_weight("Cady", "Gretchen"), 3)
        
    def test_02(self):
        school = lab.School(self.data)
        school.update_student("Cady", ["sports", "math"])
        self.assertEqual(school.find_friends_for_student("Cady"), 
                         ["Aaron", "Shane", "Kevin"])
    
    def test_03(self):
        school = lab.School(self.data)
        self.assertEqual(len(school.get_cliques()), 4)
        self.assertEqual(len(school.get_cliques_for_student("Cady")), 3)
        self.assertEqual(len(school.get_cliques_size_n(3)), 1)
        self.assertEqual(len(school.get_cliques_size_n(2)), 3)
        
        school.remove_student("Janis")
        school.add_student(["Bob", "sports"])
        school.update_student("Kevin", ["math", "python"])
        self.assertEqual(len(school.get_cliques()), 2)
        self.assertEqual(len(school.get_cliques_size_n(4)), 1)
        self.assertEqual(len(school.get_cliques_size_n(3)), 1)
        
    def test_04(self):
        school = lab.School(self.data)
        self.assertEqual(len(school.find_independent_set("Shane")), 4)
        self.assertEqual(len(school.find_independent_set("Cady")), 2)
        
        
class TestPart1(unittest.TestCase):
    def setUp(self):
        """ Load school database """
        filename = 'resources/school.json'
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def is_removed(self,school,student_name):
        return school.get_cliques_for_student(student_name)==[] and school.find_friends_for_student(student_name)==[] and student_name not in school

    def in_school(self,school,student_name):
        return not self.is_removed(school, student_name) and student_name in school

    def test_01(self):
        school = lab.School(self.data)
        self.assertEqual(school.are_they_friends("Rowan", "Cameron"), True)
        self.assertEqual(school.are_they_friends("Taylor", "Sydney"), False)
        self.assertEqual(school.are_they_friends("Avery", "Avery"), False)
        self.assertEqual(school.are_they_friends("Logan", "Rasputin"), False)

    def test_02(self):
        school = lab.School([])
        for i in self.data:
            school.add_student(i)
        school2 = lab.School(self.data)
        school.remove_student("Rowan")
        self.assertTrue(self.is_removed(school,"Rowan"))
        self.assertTrue(self.in_school(school,"Casey"))
        school.add_student(["Sandy","outdoors","fitness","sports"])
        self.assertTrue(self.in_school(school, "Casey"))
        self.assertTrue(self.in_school(school, "Sandy"))
        school.remove_student("Sandy")
        self.assertTrue(self.in_school(school, "Casey"))
        school2.remove_student("Rowan")
        self.assertTrue(self.is_removed(school2,"Rowan"))
        self.assertTrue(self.in_school(school2,"Casey"))
        school2.add_student(["Sandy","outdoors","fitness","sports"])
        self.assertTrue(self.in_school(school2, "Casey"))
        self.assertTrue(self.in_school(school2, "Sandy"))
        school2.remove_student("Sandy")
        self.assertTrue(self.in_school(school2, "Casey"))
        self.assertEqual(sorted(list(school)), sorted(list(school2)))


class TestPart2(unittest.TestCase):
    def setUp(self):
        """ Load school database """
        filename = 'resources/school.json'
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def is_clique(self,school,clique):
        for student1 in clique:
            for student2 in clique:
                if student1!=student2 and not school.are_they_friends(student1,student2):
                    return False
        return True

    def is_independent_set(self,school,ind_set,student_name):
        for student1 in ind_set:
            for student2 in ind_set:
                if student1!=student2 and school.are_they_friends(student1,student2):
                    return False
        return student_name in ind_set

    def test_03(self):
        school = lab.School(self.data)
        sizes = {2: 1, 11: 3, 10: 1, 13: 2}
        for i in range(2, 22):
            cliques = school.get_cliques_size_n(i)
            self.assertEqual(len(cliques), sizes.get(i, 0))
            for c in cliques:
                self.assertTrue(self.is_clique(school, c))
                self.assertEqual(len(c), i)
        self.assertEqual(set(school), {i[0] for i in self.data})
        self.assertEqual(sorted(set(school)), sorted(list(school)))
        school.remove_student("Jordan")
        school.add_student(["Pat", "scheme", "haskell", "python", "c++"])
        school.remove_student("Kelsey")
        school.remove_student("Corey")
        school.update_student("Cameron", ['c++', 'scheme', 'javascript'])
        sizes = {9: 1, 10: 2, 12: 3}
        for i in range(2, 22):
            cliques = school.get_cliques_size_n(i)
            self.assertEqual(len(cliques), sizes.get(i, 0))
            for c in cliques:
                self.assertTrue(self.is_clique(school, c))
                self.assertEqual(len(c), i)
        removed = {'Jordan', 'Kelsey', 'Corey'}
        self.assertEqual(set(school), {i[0] for i in self.data if i[0] not in removed} | {'Pat'})
        self.assertEqual(sorted(set(school)), sorted(list(school)))

    def test_04(self):
        school = lab.School(self.data)
        cliques = school.get_cliques()
        self.assertEqual(len(cliques), 7)
        for clique in cliques:
            self.assertTrue(self.is_clique(school,clique))

    def test_05(self):
        school = lab.School(self.data)
        jesse_cliques = school.get_cliques_for_student("Jesse")
        for c in jesse_cliques:
            self.assertTrue(self.is_clique(school, c))
            self.assertIn('Jesse', c)
        self.assertEqual(4, len(jesse_cliques))
        rowan_cliques = school.get_cliques_for_student("Rowan")
        for c in rowan_cliques:
            self.assertTrue(self.is_clique(school, c))
            self.assertIn('Rowan', c)
        self.assertEqual(6, len(rowan_cliques))

    def test_06(self):
        school = lab.School(self.data)
        cliques_7 = school.get_cliques_size_n(11)
        self.assertEqual(3, len(cliques_7))
        cliques_8 = school.get_cliques_size_n(13)
        self.assertEqual(2, len(cliques_8))
        for i in range(2, 14):
            for c in school.get_cliques_size_n(i):
                self.assertEqual(len(c), i)
                self.assertTrue(self.is_clique(school, c))

    def test_07(self):
        sizes = {'Taylor': 3, 'Kendall': 4, 'Jordan': 1, 'Drew': 3, 'Avery': 4,
                'Kelsey': 3, 'Dakota': 3, 'Logan': 4, 'Sydney': 4, 'Pat': 4,
                'Casey': 4, 'Jesse': 4, 'Corey': 4, 'Rowan': 2, 'Devin': 3,
                'Shawn': 4, 'Madison': 4, 'Jamie': 3, 'Addison': 2,
                'Cameron': 4, 'Peyton': 4, 'Carson': 4}
        school = lab.School(self.data)
        school.add_student(["Pat", "c++", "python"])
        for s in school:
            ind_set = school.find_independent_set(s)
            self.assertEqual(len(ind_set), sizes[s])
            self.assertTrue(self.is_independent_set(school, ind_set, s))

    def test_08(self):
        school = lab.School(self.data)
        for i in range(100):
            for s in school:
                cliques = school.get_cliques_for_student(s)
                for c in cliques:
                    self.assertTrue(self.is_clique(school, c))
                    self.assertIn(s, c)

        for i in range(100):
            for j in range(10, 15):
                for c in school.get_cliques_size_n(j):
                    self.assertEqual(len(c), j)
                    self.assertTrue(self.is_clique(school, c))

        for i in range(100):
            for s in school:
                self.assertIn(s, school)
                self.assertIn(s, set(school))
            self.assertNotIn("she doesn't even go here", school)
            self.assertNotIn("she doesn't even go here", set(school))

    def test_09(self):
        s = lab.School(self.data)
        for i in range(5):
            self.assertEqual(set(s), {i[0] for i in self.data})
            self.assertEqual(sorted(set(s)), sorted(list(s)))


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
