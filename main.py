import crossword
from solver import ThreadedWFCSolver
import string
from copy import deepcopy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.properties import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from math import atan, pi
from time import sleep
from threading import Thread
from queue import Queue, Empty
from kivy.core.window import Window


from components.cell.cell import Cell

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
        #if len(word) > max(lengths):
        #    valid = False

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
size = (5,5)
dict = optimize_dictionary(dict, size, lettersetHU)

class NumericInput(TextInput):
    min_value = NumericProperty()
    max_value = NumericProperty()
    def __init__(self, *args, **kwargs):
        TextInput.__init__(self, *args, **kwargs)
        self.input_filter = 'int'
        self.multiline = False

    def insert_text(self, string, from_undo=False):
        new_text = self.text + string
        try:
            self.text = str(max(min(self.max_value, int(new_text)), self.min_value))
        except:
            pass
    
    def increment(self, amount=1):
        try:
            self.text = str(min(int(self.text) + amount, self.max_value))
        except:
            pass
    
    def decrement(self, amount=1):
        try:
            self.text = str(max(int(self.text) - amount, self.min_value))
        except:
            pass

class CrosswordCell(TextInput):
    pos_x = NumericProperty()
    pos_y = NumericProperty()

    def __init__(self, *args, **kwargs):
        TextInput.__init__(self, *args, **kwargs)
    
    def insert_text(self, substring, from_undo=False):
        try:
            coords = (int(self.pos_x), int(self.pos_y))
            print("modifying cell content:")
            print(coords)
            app = App.get_running_app()
            app.threadedSolver.onThread(app.threadedSolver.root.crossword.setLetter, coords, substring.lower())
            app.threadedSolver.onThread(app.threadedSolver.root.crossword.setMask, coords)
            app.threadedSolver.onThread(app.threadedSolver.updateStatus)
        except:
            pass

    def update(self, defined, masked, options, entropy):
        if defined:
            self.text = next(iter(options))
        else:
            self.text = ''
        if self.text == '-':
            self.background_color = 0,0,0,1
        else:
            if masked:
                self.background_color = 1,1,0.5,1
            else:
                self.background_color = 1, 1.0/entropy, 1.0/entropy, 1
    
        return self

class MainApp(App):
    crosswordWidth = NumericProperty(5)
    crosswordHeight = NumericProperty(5)

    def build(self):
        self.statusQueue = Queue()
        self.commandQueue = Queue()

        size = (int(self.crosswordWidth), int(self.crosswordHeight))
        rootCrossword = crossword.Crossword(size, dict, lettersetHU)
        
        self.threadedSolver = ThreadedWFCSolver(rootCrossword, self.statusQueue, self.commandQueue)
        self.threadedSolver.start()

        self.root = Builder.load_file("main.kv")
        self.addCells()

        Clock.schedule_interval(self.update, 1.0/60.0)
    
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        return self.root

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'up':
            pass
        elif keycode[1] == 'down':
            pass
        elif keycode[1] == 'left':
            pass
        elif keycode[1] == 'right':
            pass
        elif keycode[1] == 'backspace':
            pass
        elif keycode[1] == 'del':
            pass
        elif keycode[1] == 'space':
            pass
        
        print(keycode[1])

        return True

    def update(self, dt):
        try:
            currentCrossword = self.statusQueue.get_nowait()
            # Show current status
            for cell in self.root.ids.grid.children:
                try:
                    coords = (int(cell.pos_x), int(cell.pos_y))
                    defined = currentCrossword.isDefined(coords)
                    masked = currentCrossword.getMask(coords)
                    options = currentCrossword.getOptions(coords)
                    entropy = currentCrossword.shannonEntropy(coords)
                    cell.update(defined, masked, options, entropy)
                    print("updating: ", coords)
                except:
                    pass
            currentCrossword.printDefined()
        except Empty:
            pass

    def startSolver(self):
        print("starting")
        self.threadedSolver.onThread(self.threadedSolver.solve)

    def resetSolver(self):
        print("reseting")
        self.threadedSolver.onThread(self.threadedSolver.reset)

    def setCrosswordSize(self):
        global solver
        try:
            self.crosswordWidth = int(self.root.ids.width_text.text)
            self.crosswordHeight = int(self.root.ids.height_text.text)
            size = (self.crosswordWidth, self.crosswordHeight)
            print(size)
            self.removeCells()
            self.root.ids.grid.cols = self.crosswordWidth
            self.root.ids.grid.rows = self.crosswordHeight
            self.addCells()
            rootCrossword = crossword.Crossword(size, dict, lettersetHU)
            self.threadedSolver.onThread(self.threadedSolver.reset, rootCrossword)
        except:
            pass
    
    def removeCells(self):
        self.root.ids.grid.clear_widgets()
    
    def addCells(self):
        for y in range(self.crosswordHeight):
            for x in range(self.crosswordWidth):
                self.root.ids.grid.add_widget(Cell(pos_x=x, pos_y=y))

if __name__ == "__main__":
    MainApp().run()