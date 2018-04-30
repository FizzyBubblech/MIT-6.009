# NO IMPORTS!

def match(word, pattern):
    """Match a word to a pattern.
       pattern is a string, interpreted as explained below:
             * matches any sequence of zero or more characters,
             ? matches any single character,
             otherwise char in pattern char must equal char in word. 
    """
    # if the pattern is empty, only match empty word
    if len(pattern) == 0: return len(word) == 0
    # if the word is empty, only match "*"
    if len(word) == 0: return pattern == "*"
    
    # otherwise try to match first char in pattern
    if pattern[0] == "?" or pattern[0] == word[0]:
        # try to match pattern and word without first chars
        return match(word[1:], pattern[1:])
    elif pattern[0] == "*":
        # skip chars and try to match with rest of pattern
        for i in range(len(word)+1):
           if match(word[i:], pattern[1:]):
               return True
        return False
    else:
        return False
            
        
class Trie:
    ##################################################
    ## basic methods
    ##################################################

    def __init__(self):
        # is word if > 0
        self.frequency = 0
        # char : Trie
        self.children = {}

    def insert(self, word, frequency=1):
        """ add word with given frequency to the trie. """
        # end of the word, update freq for the node
        if len(word) == 1:
            # create children node if needed
            if word not in self.children:
                self.children[word] = Trie()
            self.children[word].frequency += frequency
    
        # descend through trie one char at a time
        else:
            # create children node if needed
            if word[0] not in self.children:
                self.children[word[0]] = Trie()
            self.children[word[0]].insert(word[1:], frequency)

    def find(self, prefix):
        """ return trie node for specified prefix, None if not in trie. """
        # return root if empty prefix
        if len(prefix) == 0:
            return self
        
        # end of prefix, return the node
        elif len(prefix) == 1:
            if prefix in self.children:
                return self.children[prefix]
            # None if not in trie
            
        # descend through trie one character at a time
        else:
            if prefix[0] in self.children:
               return self.children[prefix[0]].find(prefix[1:])
            # None if not in trie

    def __contains__(self, word):
        """ is word in trie? return True or False. """
        trie = self.find(word)
        return trie is not None and trie.frequency > 0

    def __iter__(self):
        """ generate list of (word,freq) pairs for all words in
            this trie and its children.  Must be a generator! """
        def helper(trie, prefix):
            # if word, then yield
            if trie.frequency > 0:
                    yield (prefix, trie.frequency)
            # visit all children
            for ch,child in trie.children.items():
                yield from helper(child, prefix + ch)
            
        return helper(self, "")
    
    ##################################################
    ## additional methods
    ##################################################

    def autocomplete(self, prefix, N):
        """ return the list of N most-frequently occurring words
            that start with prefix. """
        # find the node with prefix
        node = self.find(prefix)
        # return empty list if no such node
        if node is None: return []
        
        # generate list of all words with prefix
        # and sort in descending order
        words = list((freq, prefix+suffix) for suffix,freq in node)
        words.sort(reverse=True)

        # return N most-frequent words
        return [words[i][1] for i in range(min(N,len(words)))]
        
    def autocorrect(self, prefix, N):
        """ return the list of N most-frequent words that start with
            prefix or that are valid words that differ from prefix
            by a small edit. """
       
        def add_word(string):
            """ add string to the set if in the trie and is word """
            if string in self:
                freq = self.find(string).frequency
                if freq > 0: words.add((freq, string))

        # find autocomplete words
        result = self.autocomplete(prefix, N)

        # if list is smaller than N, add eddited words
        C = len(result)
        if C < N:
            words = set()
            for i in range(len(prefix)):
                # single-char deletion
                delete = prefix[:i] + prefix[i+1:]
                add_word(delete)
                for ch in "abcdefghijklmnopqrstuvwxyz":
                    # single-char replacement
                    replace = prefix[:i] + ch + prefix[i+1:]
                    add_word(replace)
                    # single-char insertion
                    insert = prefix[:i] + ch + prefix[i:]
                    add_word(insert)
                if i < len(prefix)-1:
                    # char transposition
                    transpose = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
                    add_word(transpose)

            # sort in descending order and
            # add as many as needed to the list
            words = list(words)
            words.sort(reverse=True)
            for i in range(min(N-C,len(words))):
                result.append(words[i][1])
            
        return result

    def filter(self,pattern):
        """ return list of (word, freq) for all words in trie that match
            pattern.  pattern is a string, interpreted as explained below:
             * matches any sequence of zero or more characters,
             ? matches any single character,
             otherwise char in pattern char must equal char in word. """
        # iterate through all words and leave only which match
        return [(word, freq) for word,freq in self if match(word, pattern)]

# handy stand-alone testing setup
if __name__ == '__main__':
    # read in words
    import json   # this import allowed as part of testing...
    with open('testing_data/words.json') as f:
        words = json.load(f)

    """
    # small corpus: insert words one-by-one
    trie = Trie()
    for w in words[:50]: trie.insert(w)
    """

    # large corpus: precompute count for each word
    trie = Trie()
    for w in set(words):
        trie.insert(w,words.count(w))
    
    t = Trie()
    t.insert("bat")
    t.insert("bark")
    t.insert("bat")
    t.insert("bar")
    # your test here!
    # Example: 5- or more letter words beginning in "a" and  ending in "ing"
    #print(trie.filter('a?*ing'))
