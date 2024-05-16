import wordmatrix
import wavefunction
import string
from copy import deepcopy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.properties import *
from kivy.uix.screenmanager import ScreenManager, Screen


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
dict = get_dictionary_word_list("dictionary_HU.txt")

constraints =["-N     -       ", # 0
              "-A      -   -  ", # 1
              " G  -     -    ", # 2
              "-Y -     -    -", # 3
              " O     -       ", # 4
              "-N    -   -    ", # 5
              "-B-  -   -    -", # 6
              "-O -    -    - ", # 7
              " L     -    -  ", # 8
              "-D -       -   ", # 9
              " O  -         -", # 10
              " G   -   -     ", # 11
              "-N -    -   -  ", # 12
              " É   -    -    ", # 13
              "-VNAPOTKÍVÁNUNK", # 14
              ]

y = len(constraints)
x = max(len(row) for row in constraints)
size = (x,y)

dict = optimize_dictionary(dict, size, lettersetHU)
rootCrossword = wordmatrix.Crossword(size, dict, lettersetHU)
solver = wavefunction.Wavefunction(rootCrossword)


class MainApp(App):
    def build(self):
        self.root = Builder.load_file("main.kv")
        return self.root
    
    def setCrosswordSize(self):
        try:
            size = int(self.root.ids.width_text.text), int(self.root.ids.height_text.text)
            print(size)
        except:
            print("wrong format")
    
    pass

if __name__ == "__main__":
    MainApp().run()

"""
print("Prefilling grid:")
for y,row in enumerate(constraints):
    for x,letter in enumerate(row):
        if letter != " ":
            wfc.root.wordmatrix.setLetter((x,y), letter.lower())
            wfc.root.wordmatrix.setMask((x,y))

wfc.currentNode.wordmatrix.printDefined()
wfc.currentNode.wordmatrix.printAssessment()
wfc.currentNode.wordmatrix.updateOptions()
if wfc.currentNode.wordmatrix.isDeadend():
    print("oh no")
else:
    wfc.run()
    
"""


