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
from kivy.uix.checkbox import CheckBox
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

class MainApp(App):
    def build(self):
        self.root = Builder.load_file("main.kv")

        self.statusQueue = Queue()
        self.commandQueue = Queue()

        size = (int(self.root.ids.width_text.text), int(self.root.ids.height_text.text))
        rootCrossword = crossword.Crossword(size, dict, lettersetHU)
        self.threadedSolver = ThreadedWFCSolver(rootCrossword, self.statusQueue, self.commandQueue)
        self.threadedSolver.start()
    
        self._keyboard = Window.request_keyboard(self._keyboard_closed, None)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        Clock.schedule_interval(self.update, 1.0/60.0)

        return self.root

    def on_start(self):
        self.setCrosswordSize()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        
        if keycode[1] == 'up':
            self.moveActiveCell((0, -1))
        elif keycode[1] == 'down':
            self.moveActiveCell((0, 1))
        elif keycode[1] == 'left':
            self.moveActiveCell((-1, 0))
        elif keycode[1] == 'right':
            self.moveActiveCell((1, 0))

        elif keycode[1] == 'backspace' or keycode[1] == 'delete' or keycode[1] == 'space':
            # Find active cell:
            coords = None
            for cell in self.root.ids.grid.children:
                if cell.state == "down":
                    coords = (int(cell.pos_x), int(cell.pos_y))
                    break

            self.threadedSolver.onThread(self.threadedSolver.root.crossword.resetCell, coords)
            self.threadedSolver.onThread(self.threadedSolver.updateStatus)
        
        elif True:
            # Find active cell:
            coords = None
            for cell in self.root.ids.grid.children:
                if cell.state == "down":
                    coords = (int(cell.pos_x), int(cell.pos_y))
                    break

            # Set letter and mask
            if coords is not None:
                self.threadedSolver.onThread(self.threadedSolver.root.crossword.setLetter, coords, keycode[1])
                self.threadedSolver.onThread(self.threadedSolver.root.crossword.setMask, coords)
                self.threadedSolver.onThread(self.threadedSolver.updateStatus)

        return True

    def moveActiveCell(self, direction):
        # Find active cell:
        coords = None
        for cell in self.root.ids.grid.children:
            if cell.state == "down":
                coords = (int(cell.pos_x), int(cell.pos_y))
                cell.state = "normal"
        
        newCoords = (max(0, min(coords[0] + direction[0], int(self.root.ids.width_text.text)-1)),
                     max(0, min(coords[1] + direction[1], int(self.root.ids.height_text.text)-1)))
        
        print(newCoords)

        for cell in self.root.ids.grid.children:
            if (int(cell.pos_x), int(cell.pos_y)) == newCoords:
                print("changing active cell")
                cell.state = "down"

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

    def updateOptions(self):
        print("Updating")
        self.threadedSolver.onThread(self.threadedSolver.root.crossword.updateOptions)
        self.threadedSolver.onThread(self.threadedSolver.updateStatus)

    def startSolver(self):
        print("starting")
        self.threadedSolver.onThread(self.threadedSolver.solve)
    
    def stopSolver(self):
        print("Stopping")
        self.threadedSolver.onThread(self.threadedSolver.stop)

    def resetSolver(self):
        print("reseting")
        self.threadedSolver.onThread(self.threadedSolver.reset)

    def setCrosswordSize(self):
        try:
            size = (int(self.root.ids.width_text.text), int(self.root.ids.height_text.text))
            print(size)
            self.removeCells()
            self.addCells()
            rootCrossword = crossword.Crossword(size, dict, lettersetHU)
            self.threadedSolver.onThread(self.threadedSolver.reset, rootCrossword)
        except:
            pass
    
    def removeCells(self):
        self.root.ids.grid.clear_widgets()
    
    def addCells(self):
        for y in range(int(self.root.ids.height_text.text)):
            for x in range(int(self.root.ids.width_text.text)):
                self.root.ids.grid.add_widget(Cell(x, y))

if __name__ == "__main__":
    MainApp().run()