import history_tree
from anytree import RenderTree
from copy import deepcopy
import time
from threading import Thread
import queue

class WFCSolver(object):
    def __init__(self, crossword):
        super(WFCSolver, self).__init__()
        self.root = history_tree.MoveNode(0, 0, '-',  crossword, parent=None, children=None)
        self.currentNode = self.root
        self.treelevel = 0
        self.i = 0
        self.totalUpdates = 0

    #@profile
    def solve(self):
        """Runs iterations until the crossword is fully solved, or out of options.
        """

        startTime = time.perf_counter()
        while not self.currentNode.crossword.isFullyDefined():
            if self.currentNode == self.root and self.currentNode.crossword.isDeadend():
                print("No more options")
                #print(self.currentNode.crossword.blacklist)
                break
            else:
                self.iterate()
        
        endTime = time.perf_counter()
        #self.print_tree()
        #self.currentNode.crossword.printOptions()
        #self.currentNode.crossword.printDefined()
        print("%d updates in total." % self.totalUpdates)
        print("Total time: %.2gs" % (endTime-startTime))
    
    def iterate(self):
        """Performs a single iteration of the Wavefunction Collapse
        Algorithm.
        """
        # Figure if we should move up or down the tree (new move or backtrack)
        if self.currentNode.crossword.isDeadend() or not self.currentNode.crossword.isFullyValid():
            # Backtrack
            self.treelevel -= 1
            # Note the previous move
            x = self.currentNode.x
            y = self.currentNode.y
            letter = self.currentNode.letter
            print("letter removed: (", x, ",", y, "): ", letter," - ",self.treelevel)
            # Revert wrong move
            self.currentNode = self.currentNode.parent
            # Learn from the mistake
            self.currentNode.crossword.addToBlacklist((x, y), letter)

        else:
            # New move
            self.treelevel += 1
            # Find the coordinates of minimum entropy
            x, y = self.currentNode.crossword.findMinEntropy()
            # Collapse the wavefunction at these coordinates
            new_matrix = deepcopy(self.currentNode.crossword) #TODO: optimize
            letter = new_matrix.define((x, y))
            # Make a note of move
            self.currentNode = history_tree.MoveNode(x, y, letter, new_matrix, parent=self.currentNode)
            print("letter added:   (", x, ",", y, "): ", letter," - ",self.treelevel)
        
        # Propagate changes, finish on a clean state
        self.totalUpdates += self.currentNode.crossword.updateOptions()

        self.i += 1
        #if self.i % 100 == 0:
            #self.print_tree()
            #self.currentNode.crossword.printOptions()
            #print(self.currentNode.crossword.blacklist)
        
        # Debug printing
        self.currentNode.crossword.printDefined()
        #self.print_tree()
        #self.currentNode.crossword.print_options()

    def print_tree(self):
        for pre, _, node in RenderTree(self.root):
            treestr = u"%s%s%s%s" % (pre, node.x, node.y, node.letter)
            print(treestr.ljust(8))

class TreadedWFCSolver(WFCSolver, Thread):
    def __init__(self, crossword, statusQueue, commandQueue):
        WFCSolver.__init__(self, crossword)
        Thread.__init__(self)
        self.statusQueue = statusQueue
        self.commandQueue = commandQueue
        self.timeout = 1.0 / 10.0
    
    def onThread(self, function, *args, **kwargs):
        self.commandQueue.put((function, args, kwargs))
    
    def run(self):
        while True:
            try:
                function, args, kwargs = self.commandQueue.get(timeout=self.timeout)
                print(function, args, kwargs)
                function(*args, **kwargs)
            except queue.Empty:
                self.idle()
    
    def idle(self):
        # put the code you would have put in the `run` loop here
        pass

    def _solve(self):
        while not self.currentNode.crossword.isFullyDefined():
            if self.currentNode == self.root and self.currentNode.crossword.isDeadend():
                print("No more options")
                #print(self.currentNode.crossword.blacklist)
                break
            else:
                self.iterate()
                self.statusQueue.put(self.currentNode.crossword)
        
    def solve(self):
        self.onThread(self._solve)