import history_tree
from anytree import RenderTree
from copy import deepcopy

class Wavefunction(object):

    def __init__(self, matrix):
        self.root = history_tree.MoveNode(0, 0, '-',  matrix, parent=None, children=None)
        self.currentNode = self.root

    def run(self):
        """Runs iterations until the matrix is fully solved, or out of options.
        """
        while not self.currentNode.wordmatrix.is_fully_defined():
            if self.currentNode == self.root and self.currentNode.wordmatrix.is_deadend():
                print("No more options")
                print(self.currentNode.wordmatrix.blacklist)
                break
            else:
                self.iterate()

        self.print_tree()
        self.currentNode.wordmatrix.print_options()
        self.currentNode.wordmatrix.print_defined()
    
    def iterate(self):
        """Performs a single iteration of the Wavefunction Collapse
        Algorithm.
        """
        # Figure if we should move up or down the tree (new move or backtrack)
        if self.currentNode.wordmatrix.is_deadend():
            # Backtrack
            # Note the previous move
            x = self.currentNode.x
            y = self.currentNode.y
            letter = self.currentNode.letter
            print("letter removed: (", x, ",", y, "): ", letter)
            # Revert wrong move
            self.currentNode = self.currentNode.parent
            # Learn from the mistake
            self.currentNode.wordmatrix.add_blacklist(x, y, letter)

        else:
            # New move
            # Find the coordinates of minimum entropy
            x, y = self.currentNode.wordmatrix.find_min_entropy()
            # Collapse the wavefunction at these coordinates
            new_matrix = deepcopy(self.currentNode.wordmatrix)
            letter = new_matrix.define(x, y)
            # Make a note of move
            self.currentNode = history_tree.MoveNode(x, y, letter, new_matrix, parent=self.currentNode)
            print("letter added:   (", x, ",", y, "): ", letter)
        
        # Propagate changes, finish on a clean state
        self.currentNode.wordmatrix.update_possibilities()
        
        # Debug printing
        #self.wordmatrix.print_defined()
        #self.print_tree()
        #self.currentNode.wordmatrix.print_options()

    def print_tree(self):
        for pre, _, node in RenderTree(self.root):
            treestr = u"%s%s%s%s" % (pre, node.x, node.y, node.letter)
            print(treestr.ljust(8))