import history_tree
from anytree import RenderTree
from copy import deepcopy
import time

class Wavefunction(object):

    def __init__(self, matrix):
        self.root = history_tree.MoveNode(0, 0, '-',  matrix, parent=None, children=None)
        self.currentNode = self.root
        self.treelevel = 0
        self.i = 0
        self.totalUpdates = 0

    #@profile
    def run(self):
        """Runs iterations until the matrix is fully solved, or out of options.
        """

        startTime = time.perf_counter()
        while not self.currentNode.wordmatrix.isFullyDefined():
            if self.currentNode == self.root and self.currentNode.wordmatrix.isDeadend():
                print("No more options")
                print(self.currentNode.wordmatrix.blacklist)
                break
            else:
                self.iterate()
        
        endTime = time.perf_counter()
        self.print_tree()
        self.currentNode.wordmatrix.printOptions()
        self.currentNode.wordmatrix.printDefined()
        print("%d updates in total." % self.totalUpdates)
        print("Total time: %.2gs" % (endTime-startTime))
    
    def iterate(self):
        """Performs a single iteration of the Wavefunction Collapse
        Algorithm.
        """
        # Figure if we should move up or down the tree (new move or backtrack)
        if self.currentNode.wordmatrix.isDeadend() or not self.currentNode.wordmatrix.isFullyValid():
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
            self.currentNode.wordmatrix.addToBlacklist((x, y), letter)

        else:
            # New move
            self.treelevel += 1
            # Find the coordinates of minimum entropy
            x, y = self.currentNode.wordmatrix.findMinEntropy()
            # Collapse the wavefunction at these coordinates
            new_matrix = deepcopy(self.currentNode.wordmatrix) #TODO: optimize
            letter = new_matrix.define((x, y))
            # Make a note of move
            self.currentNode = history_tree.MoveNode(x, y, letter, new_matrix, parent=self.currentNode)
            print("letter added:   (", x, ",", y, "): ", letter," - ",self.treelevel)
        
        # Propagate changes, finish on a clean state
        self.totalUpdates += self.currentNode.wordmatrix.updateOptions()

        self.i += 1
        #if self.i % 100 == 0:
            #self.print_tree()
            #self.currentNode.wordmatrix.printOptions()
            #print(self.currentNode.wordmatrix.blacklist)
        
        # Debug printing
        #self.wordmatrix.print_defined()
        #self.print_tree()
        #self.currentNode.wordmatrix.print_options()

    def print_tree(self):
        for pre, _, node in RenderTree(self.root):
            treestr = u"%s%s%s%s" % (pre, node.x, node.y, node.letter)
            print(treestr.ljust(8))