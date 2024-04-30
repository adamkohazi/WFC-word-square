import wordmatrix
import wavefunction
import string
from copy import deepcopy

# For testing purposes
import random
#random.seed(1234)

size = [6,11]
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
    with open(filename, encoding="utf-8") as f:
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
dict = get_dictionary_word_list("HU_160k.txt")

constraints =["N   -   -    - ",
              "A  -   -    -  ",
              "G     -        ",
              "Y-        -    ",
              "O   -    -    -",
              "N  -         - ",
              "B -    -    -  ",
              "O-   -         ",
              "L         --   ",
              "D   -         -",
              "O  -    -    - ",
              "G       -   -  ",
              "G-    -        ",
              "Y -       -    ",
              "Ö   -   --    -",
              "R   -        - ",
              "G -    -    -  ",
              "YINAPOTKÍVÁNUNK",
              ]

y = len(constraints)
x = max(len(row) for row in constraints)
size = (x,y)

dict = optimize_dictionary(dict, size, lettersetHU)
table = wordmatrix.Crossword(size, dict, lettersetHU)

blocks = []
while(True):
    wfc = wavefunction.Wavefunction(deepcopy(table))
    print("Prefilling grid:")
    for y,row in enumerate(constraints):
        for x,letter in enumerate(row):
            if letter != " ":
                wfc.root.wordmatrix.setLetter((x,y), letter.lower())
                wfc.root.wordmatrix.setMask((x,y))

    for coords in blocks:
        wfc.root.wordmatrix.setLetter(coords, "-")
        wfc.root.wordmatrix.setMask(coords)

    wfc.currentNode.wordmatrix.printDefined()
    wfc.currentNode.wordmatrix.printAssessment()
    wfc.currentNode.wordmatrix.updateOptions()

    if wfc.run():
        break
    else:
        blocks.append((random.randint(1, x), random.randint(0, y-1)))

