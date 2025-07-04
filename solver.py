import history_tree
from anytree import RenderTree
from copy import deepcopy
import time
from threading import Thread
import queue
from dictionary import Dictionary

class WFCSolver(object):
    def __init__(self, crossword):
        self.reset(crossword)
    
    def reset(self, crossword=None):
        if crossword is None:
            crossword = self.root.crossword
        crossword.reset()
        self.root = history_tree.MoveNode(0, 0, '-',  crossword, parent=None, children=None)
        self.currentNode = self.root
        self.treelevel = 0
        self.i = 0
        self.totalUpdates = 0

    def solve(self):
        """Runs iterations until the crossword is fully solved, or out of options.
        """

        startTime = time.perf_counter()
        while not (self.currentNode.crossword.grid.isFullyDefined() and self.currentNode.crossword.isFullyValid()):
            if self.currentNode == self.root and self.currentNode.crossword.grid.isDeadend():
                print("No more options")
                break
            else:
                self.iterate()
        
        endTime = time.perf_counter()
        print("%d updates in total." % self.totalUpdates)
        print("Total time: %.2gs" % (endTime-startTime))
    
    def iterate(self):
        """Performs a single iteration of the Wavefunction Collapse
        Algorithm.
        """
        # Figure if we should move up or down the tree (new move or backtrack)
        if self.currentNode.crossword.grid.isDeadend() or not self.currentNode.crossword.isFullyValid():
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
            self.currentNode.crossword.grid[(x,y)].blacklist.append(letter)

        else:
            # New move
            self.treelevel += 1
            # Find the coordinates of minimum entropy
            x, y = self.currentNode.crossword.grid.findMinEntropy()
            # Collapse the wavefunction at these coordinates
            new_matrix = deepcopy(self.currentNode.crossword) #TODO: optimize
            letter = new_matrix.grid[(x,y)].define()
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

    def print_tree(self):
        for pre, _, node in RenderTree(self.root):
            treestr = u"%s%s%s%s" % (pre, node.x, node.y, node.letter)
            print(treestr.ljust(8))

class ThreadedWFCSolver(WFCSolver, Thread):
    def __init__(self, crossword, statusQueue, commandQueue):
        self.statusQueue = statusQueue
        self.commandQueue = commandQueue
        self.timeout = 1.0 / 10.0
        WFCSolver.__init__(self, crossword)
        Thread.__init__(self)
        self.daemon = True
        
        self.updateStatus()
    
    def updateStatus(self):
        # Remove all previous statuses
        while not self.statusQueue.empty():
            self.statusQueue.get_nowait()
        # Place current status
        self.statusQueue.put(self.currentNode.crossword)
    
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
        # Small sleep, so thread can be interrupted if needed
        time.sleep(0.001)
    
    def solve(self):
        """Runs iterations until the crossword is fully solved, or out of options.
        """

        while not self.currentNode.crossword.grid.isFullyDefined():
            try:
                function, args, kwargs = self.commandQueue.get_nowait()
                if function == self.stop:
                    print("stop detected")
                    break
                else:
                    print("can't stop, won't stop")
            except queue.Empty:
                if self.currentNode == self.root and self.currentNode.crossword.grid.isDeadend():
                    print("No more options")
                    break
                else:
                    self.iterate()

    def stop(self):
        pass

    def reset(self, crossword=None):
        WFCSolver.reset(self, crossword)
        self.updateStatus()
    
    def iterate(self):
        WFCSolver.iterate(self)
        self.updateStatus()