import wordmatrix
import wavefunction
import string

size = [7,5]

def optimize_dictionary (lengths, dict):
    opt_dict = []
    for word in dict:
        if len(word) in lengths:
            if word.isalpha():
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
dict = get_dictionary_word_list("HU_100k.txt")
#dict = optimize_dictionary(size, dict)

lettersetHU = 'aábcdeéfghiíjklmnoóöőpqrstuúüűvwxyz'
lettersetEN = string.ascii_lowercase

table = wordmatrix.Crossword(size, dict, lettersetHU)
wfc = wavefunction.Wavefunction(table)


print("inserting black squares")
blankLocations=[(3,2 )]

for coords in blankLocations:
    wfc.root.wordmatrix.setOptions([coords], [{'-':1}])
wfc.currentNode.wordmatrix.update_possibilities()

wfc.run()

