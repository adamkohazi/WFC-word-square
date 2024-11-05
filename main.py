import crossword
import dictionary
from solver import ThreadedWFCSolver
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import *
from kivy.clock import Clock
from queue import Queue, Empty
from kivy.core.window import Window

from components.cell.cell import Cell
from components.integer_up_down.integer_up_down import IntegerUpDown

# For testing purposes
import random
#random.seed(1234)

size = (10,10)
dict = dictionary.Dictionary("dictionary_HU.txt", validLetters=dictionary.lettersetHU)

class MainApp(App):
    def build(self):
        self.root = Builder.load_file("main.kv")

        self.statusQueue = Queue()
        self.commandQueue = Queue()

        size = (10, 10)
        rootCrossword = crossword.Crossword(size, dict)
        self.threadedSolver = ThreadedWFCSolver(rootCrossword, self.statusQueue, self.commandQueue)
        self.threadedSolver.start()
    
        self._keyboard = Window.request_keyboard(self._keyboard_closed, None)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Display crossword when UI is loaded
        Clock.schedule_once(self.start_display)

        return self.root

    def start_display(self, *args):
        self.setCrosswordSize()
        Clock.schedule_interval(self.update, 1.0/10.0)

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
            if coords is not None:
                self.threadedSolver.onThread(self.threadedSolver.root.crossword.grid[coords].reset)
                self.threadedSolver.onThread(self.threadedSolver.updateStatus)
        
        elif True:
            # Find active cell:
            coords = None
            for cell in self.root.ids.grid.children:
                if cell.state == "down":
                    coords = (int(cell.pos_x), int(cell.pos_y))
                    break

            # Set letter and mask, than update
            if coords is not None:
                self.threadedSolver.onThread(self.threadedSolver.root.crossword.grid[coords].setLetter, text)
                self.threadedSolver.onThread(setattr, self.threadedSolver.root.crossword.grid[coords], 'mask', True)
                self.threadedSolver.onThread(self.threadedSolver.root.crossword.updateOptions)
                self.threadedSolver.onThread(self.threadedSolver.updateStatus)

        return True

    def moveActiveCell(self, direction):
        # Find active cell:
        coords = None
        for cell in self.root.ids.grid.children:
            if cell.state == "down":
                coords = (int(cell.pos_x), int(cell.pos_y))
                cell.state = "normal"
        
        newCoords = (max(0, min(coords[0] + direction[0], self.root.ids.width_input.current_value-1)),
                     max(0, min(coords[1] + direction[1], self.root.ids.height_input.current_value-1)))
        
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
                    crosswordCell = currentCrossword.grid[coords]
                    defined = crosswordCell.isDefined()
                    masked = crosswordCell.mask
                    options = crosswordCell.options
                    entropy = crosswordCell.shannonEntropy()
                    cell.update(defined, masked, options, entropy)
                except:
                    pass
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
        size = (self.root.ids.width_input.current_value, self.root.ids.height_input.current_value)
        self.removeCells()
        self.root.ids.grid.cols = self.root.ids.width_input.current_value
        self.root.ids.grid.rows = self.root.ids.height_input.current_value
        self.addCells()
        rootCrossword = crossword.Crossword(size, dict)
        self.threadedSolver.onThread(self.threadedSolver.reset, rootCrossword)
    
    def removeCells(self):
        self.root.ids.grid.clear_widgets()
    
    def addCells(self):
        for y in range(self.root.ids.height_input.current_value):
            for x in range(self.root.ids.width_input.current_value):
                self.root.ids.grid.add_widget(Cell(x, y))

if __name__ == "__main__":
    MainApp().run()