import lab, json, traceback, sys
from importlib import reload
reload(lab) # this forces the student code to be reloaded when page is refreshed

##################################################
## for server.py
##################################################

# global trie that holds resources/words.json
trie = None
def load_words():
    global trie
    if trie is not None: return

    # load json word list, insert into trie
    print("LOADING CORPUS")
    trie = lab.Trie()
    with open("testing_data/words.json", "r") as f:
        words = json.load(f)
        for w in set(words):
            trie.insert(w,words.count(w))

def autocomplete( input_data ):
    global trie
    load_words()
    print(input_data,file=sys.stderr)
    return trie.autocomplete(input_data["prefix"], input_data["N"])

def autocorrect( input_data ):
    global trie
    load_words()
    print(input_data,file=sys.stderr)
    return trie.autocorrect(input_data["prefix"], input_data["N"])

def init():
    # Nothing to initialize
    return None

init()
