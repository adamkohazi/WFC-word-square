import wordmatrix
import wavefunction
import string

# For testing purposes
from random import seed
seed(1234)

size = [7,5]
lettersetHU = 'aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz'
lettersetEN = string.ascii_lowercase

def optimize_dictionary (dict, lengths, letterset):
    opt_dict = []
    for word in dict:
        valid = True
        # Check 1: Contains only alpha chars
        if not word.isalpha():
            valid = False

        # Check 2: Contains only defined letters
        for letter in word:
            if letter not in letterset:
                valid = False
                break

        # Check 3: No longer than max length
        if len(word) > max(lengths):
            valid = False

        if valid:
            opt_dict.append(word.lower())
    return opt_dict

def get_dictionary_word_list(filename):
    with open(filename, encoding="iso-8859-2") as f:
        # Return the split results, which is all the words in the file.
        return f.read().split()

def findLetterset(dictionary):
    letters = set()
    for word in dictionary:
        for letter in word:
            letters.add(letter)
    print(''.join(letters))
    return ''.join(letters)

# Loading words to a dictionary for generation
dict = get_dictionary_word_list("dictionary_EN.txt")
#dict = optimize_dictionary(dict, size, lettersetHU)

table = wordmatrix.Crossword(size, dict, lettersetHU)
wfc = wavefunction.Wavefunction(table)


print("inserting black squares")
blankLocations=[(3,2 )]

for coords in blankLocations:
    wfc.root.wordmatrix.setOptions([coords], [{'-':1}])
wfc.currentNode.wordmatrix.update_possibilities()

wfc.run()

