#!/usr/bin/env python3
import os.path
import lab
import json
import unittest
import types

import sys
sys.setrecursionlimit(10000)

TEST_DIRECTORY = os.path.dirname(__file__)

def setup_trie(words = None):
    # build an empty tree
    trie = lab.Trie()

    # insert words from corpus or from supplied list
    if words == 'jules_verne':
        with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'words.json')) as f:
            words = json.load(f)
            # pre-compute frequency to avoid a zillion
            # separate inserts for each word in corpus
            for w in set(words):
                trie.insert(w, words.count(w))
    else:
        for w in words:
            trie.insert(w)

    # okay, our work here is done...
    return trie

# convert trie into a dictionary
def dictify(trie,prefix=''):
    if trie is None: return None
    result = {"frequency": trie.frequency, "children": {}}
    for ch,child in trie.children.items():
        result["children"][ch] = dictify(child,prefix + ch)
    return result

# read in expected result
def read_expected(fname):
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', fname)) as f:
        return json.load(f)

class Test_1_Trie(unittest.TestCase):
    def test_01_insert(self):
        # generate simple trie for three words
        trie = setup_trie(("cat", "car", "carpet"))
        expect = read_expected('1.json')
        self.assertTrue(dictify(trie) == expect,msg="Your trie is incorrect.")

    def test_02_insert(self):
        # generate trie with only one child on each level
        trie = setup_trie(("a","an","ant","anteater","a","an","ant","a"))
        expect = read_expected('2.json')
        self.assertTrue(dictify(trie) == expect,msg="Your trie is incorrect.")

    def test_03_insert(self):
        # generate trie with multiple children on every level
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        expect = read_expected('3.json')
        self.assertTrue(dictify(trie) == expect,msg="Your trie is incorrect.")

    def test_04_insert(self):
        # generate large trie with corpus
        trie = setup_trie('jules_verne')
        expect = read_expected('4.json')
        self.assertTrue(dictify(trie) == expect,msg="Your trie is incorrect.")

    def test_05_find(self):
        # find root node
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.find('')
        expect = read_expected('5.json')
        self.assertTrue(dictify(result) == expect,msg="Find returned incorrect trie node.")

    def test_06_find(self):
        # trie with 1 entry
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.find('a')
        expect = read_expected('6.json')
        self.assertTrue(dictify(result) == expect,msg="Find returned incorrect trie node.")

    def test_07_find(self):
        # trie with 2 entries
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.find('mat')
        expect = read_expected('7.json')
        self.assertTrue(dictify(result) == expect,msg="Find returned incorrect trie node.")

    def test_08_find(self):
        # find on missing node
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.find('matter')
        self.assertIsNone(result,msg="Find returned incorrect trie node.")

    def test_09_contains(self):
        # look for valid word in trie
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = "man" in trie
        self.assertTrue(result,msg="'man' not found in trie.")

    def test_10_contains(self):
        # look for prefix (but not valid word) in trie
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = "ma" in trie
        self.assertFalse(result,msg="'ma' incorrectly found in trie.")

    def test_11_contains(self):
        # look for missing word in tree 
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = "mate" in trie
        self.assertFalse(result,msg="'mate' incorrectly found in trie.")
        
    def test_12_contains(self):
        # look for valid word in trie
        trie = setup_trie('jules_verne')
        result = "annulment" in trie
        self.assertTrue(result,msg="'annulment' not found in trie (large corpus).")

    def test_13_contains(self):
        # look for missing word in trie
        trie = setup_trie('jules_verne')
        result = "annexations" in trie
        self.assertFalse(result,msg="'annexations' mistakenly found in trie (large corpus).")
        
    def test_14_iter(self):
        # iterate over small trie"
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = iter(trie)
        self.assertIsInstance(result, types.GeneratorType,"iteration didn't produce a generator.")
        result = sorted(list(result))
        expected = [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]
        self.assertEqual(result,expected,msg="incorrect result from iterating over small trie")

    def test_15_iter(self):
        # iterate over large tree
        trie = setup_trie('jules_verne')
        result = iter(trie.find('am'))
        self.assertIsInstance(result, types.GeneratorType,"iteration didn't produce a generator.")
        result = sorted(list(result))
        expected = [("", 6), ("bassador", 3), ("bassadors", 1), ("erica", 1), ("erican", 2),
                    ("ericans", 4), ("ong", 2), ("ount", 1), ("ounting", 1)]
        self.assertEqual(result,expected,msg="incorrect result from iterating over trie.find('am')")
        
class Test_2_Autocomplete(unittest.TestCase):
    def test_01_autocomplete(self):
        # Autocomplete on simple trie with less than N valid words
        trie = setup_trie(("cat", "car", "carpet"))
        result = trie.autocomplete('car',3)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["car", "carpet"]
        self.assertEqual(result,expect,msg="incorrect result from autocomplete.")

    def test_02_autocomplete(self):
        # Autocomplete on one-child-per-level trie with tie
        trie = setup_trie(("a","an","ant","anteater","a","an","ant","a"))
        result = trie.autocomplete('a',2)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect_one_of = [["a","an"],["a","ant"]]
        self.assertIn(result,expect_one_of,msg="incorrect result from autocomplete.")
        
    def test_03_autocomplete(self):
        # Autocomplete on trie with multiple children per level
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.autocomplete('m',3)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["man","map","met"]
        self.assertEqual(result,expect,msg="incorrect result from autocomplete.")
        
    def test_04_autocomplete(self):
        # Autocomplete with no word possibilities
        trie = setup_trie(("hello","hell","history"))
        result = trie.autocomplete('help',3)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        expect = []
        self.assertEqual(result,expect,msg="incorrect result from autocomplete.")

    def test_05_autocomplete(self):
        # Autocomplete on large corpus
        trie = setup_trie('jules_verne')
        result = trie.autocomplete('th',5)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect_one_of = [["that", "the", "these", "they", "this"],
                         ["that", "the", "their", "they", "this"]]
        self.assertIn(result,expect_one_of,msg="incorrect result from autocomplete.")
        
class Test_3_Autocorrect(unittest.TestCase):
    def test_01_autocorrect(self):
        # Autocorrect on cat in small corpus
        trie = setup_trie(("cats", "cattle", "hat", "car", "act", "at", "chat", "crate", "act", "car", "act"))
        result = trie.autocorrect('cat',4)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["act", "car", "cats", "cattle"]
        self.assertEqual(result,expect,msg="incorrect result from autocorrect.")

    def test_02_autocorrect(self):
        # Autocorrect on large corpus
        trie = setup_trie('jules_verne')
        result = trie.autocorrect('tat',10)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["at","tap","that"]
        self.assertEqual(result,expect,msg="incorrect result from autocorrect.")

    def test_03_autocorrect(self):
        # Autocorrect on large corpus
        trie = setup_trie('jules_verne')
        result = trie.autocorrect('sto',10)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["so", "stomach", "stood", "stored", "stories", "story", "to"]
        self.assertEqual(result,expect,msg="incorrect result from autocorrect.")

    def test_04_autocorrect(self):
        # Autocorrect on large corpus
        trie = setup_trie('jules_verne')
        result = trie.autocorrect('mad',10)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["bad", "had", "made", "madrid", "maid", "man",  "map", "may"]
        self.assertEqual(result,expect,msg="incorrect result from autocorrect.")
        
class Test_4_Filter(unittest.TestCase):
    def test_01_filter(self):
        # Filter to select all words in trie
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.filter('*')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_02_filter(self):
        # All three-letter words in trie
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.filter('???')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("man", 3), ("map", 2), ("mat", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_03_filter(self):
        # Words beginning with 'mat'
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.filter('mat*')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("mat", 1), ("mattress", 1)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_04_filter(self):
        # Words beginning with 'm', third letter is t
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.filter('m?t*')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("mat", 1), ("mattress", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_05_filter(self):
        # Words with at least 4 letters
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.filter('*????')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("mattress", 1)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_06_filter(self):
        # All words
        trie = setup_trie(("man","mat","mattress","map","me","met","a","man","a","a","a","map","man","met"))
        result = trie.filter('**')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")
        
    def test_07_filter(self):
        # large corpus, words ending in 'ing'
        trie = setup_trie('jules_verne')
        result = trie.filter('*ing')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("abating", 1), ("accepting", 1), ("according", 2), ("addressing", 4),
                  ("advertising", 1), ("amounting", 1), ("annexing", 1), ("anything", 2),
                  ("applying", 2), ("approaching", 1), ("astounding", 1), ("awaiting", 1),
                  ("awakening", 2), ("begging", 1), ("being", 10), ("bowing", 1),
                  ("building", 3), ("calling", 1), ("coming", 4), ("communicating", 1),
                  ("completing", 1), ("complimenting", 1), ("crossing", 1), ("crowding", 1),
                  ("displaying", 1), ("dissecting", 1), ("dreaming", 2), ("during", 3),
                  ("entreating", 1), ("evening", 3), ("everything", 1), ("examining", 2),
                  ("explaining", 1), ("facing", 1), ("failing", 1), ("falling", 1),
                  ("feeling", 3), ("finishing", 1), ("fleeting", 1), ("gathering", 1),
                  ("getting", 1), ("giving", 1), ("going", 2), ("growing", 2),
                  ("having", 7), ("imploring", 1), ("increasing", 1), ("interesting", 2),
                  ("interrupting", 1), ("inventionsasphyxiating", 1), ("king", 4), ("laughing", 1),
                  ("lighting", 1), ("living", 3), ("looking", 1), ("manifesting", 1),
                  ("mitigating", 1), ("morning", 7), ("needing", 1), ("nothing", 6),
                  ("notwithstanding", 3), ("opening", 2), ("overpowering", 1), ("owing", 1),
                  ("painting", 1), ("passing", 1), ("pestering", 1), ("preceding", 1),
                  ("pronouncing", 1), ("rejecting", 1), ("removing", 1), ("reproducing", 2),
                  ("rising", 1), ("rumbling", 2), ("saying", 1), ("setting", 1),
                  ("sitting", 1), ("skyadvertising", 1), ("sleeping", 1), ("solving", 1),
                  ("something", 2), ("starting", 1), ("stretching", 1), ("striking", 1),
                  ("supplying", 1), ("suspending", 1), ("taking", 1), ("talking", 1),
                  ("thing", 4), ("touching", 2), ("trifling", 1), ("turning", 3),
                  ("undertaking", 1), ("unfailing", 1), ("waiting", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_08_filter(self):
        # large corpus, words ending in 'ing' + one letter
        trie = setup_trie('jules_verne')
        result = trie.filter('*ing?')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("blessings", 1), ("feelings", 1), ("meanderings", 1), ("springs", 1), ("things", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")
        
if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
