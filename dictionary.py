from string import ascii_lowercase

lettersetHU = 'aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz'
lettersetEN = ascii_lowercase

class Dictionary(object):
    """Class for keeping track of and interacting with a dictionary of words.

    Attributes:
        words (list of strings): List of every valid word.
        validLetters (set of chars): Set of valid letters. Words containing invalid letters are removed.
        lookup (dict of strings): List of every valid word organized into a dictionary by length.
    """

    def __init__(self, filename, maxLength=None, validLetters=None):
        """Initializes a new dictionary from an input file.

        Arguments:
            filename (string): Filename containing a list of words.
        """
        with open(filename, encoding="utf-8") as f:
            # Stores the split results, which is all the words in the file.
            self.words = [word.lower() for word in f.read().split()]
        
        # Perform an initial cleanup of the imported words
        self.clean(maxLength, validLetters)

        # Build letterset based on library
        self.findValidLetters()

        # Prepare for lookup
        self.prepareForLookup()

    def clean(self, maxLength=None, validLetters=None):
        """Initializes a new dictionary from an input file.

        Arguments:
            filename (string): Filename containing a list of words.
        """
        # Iterate through a copy, so items can be removed from the original
        for word in self.words[:]:
            # Check 1: Contains only alpha chars
            # This check is always active
            if not word.isalpha():
                self.words.remove(word)
                continue

            # Check 2: Contains only valid letters
            if validLetters:
                if any([letter not in validLetters for letter in word]):
                    self.words.remove(word)
                    continue

            # Check 3: No longer than max length
            if maxLength:
                if len(word) > maxLength:
                    self.words.remove(word)
                    continue

    def setValidLetters(self, validLetters):
        """Initializes a new dictionary from an input file.

        Arguments:
            filename (string): Filename containing a list of words.
        """
        self.validLetters = validLetters
        self.clean(validLetters=validLetters)

    def findValidLetters(self):
        """Initializes a new dictionary from an input file.

        Arguments:
            filename (string): Filename containing a list of words.
        """
        self.validLetters = set()
        for word in self.words:
            for letter in word:
                self.validLetters.add(letter)
    
    def prepareForLookup(self):
        """Initializes a new dictionary from an input file.
        """
        self.lookup = {}
        for word in self.words:
            length = len(word)
            if length not in self.lookup:
                self.lookup[length] = []
            self.lookup[length].append(word)

        