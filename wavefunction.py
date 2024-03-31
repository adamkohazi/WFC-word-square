import os
import sys
class Wavefunction(object):

    def __init__(self, matrix):
        self.wordmatrix = matrix
        self.history = []

    def run(self):
        while not self.wordmatrix.is_fully_defined():
            self.iterate()
        
        self.wordmatrix.print_defined()
    
    def iterate(self):
        """Performs a single iteration of the Wavefunction Collapse
        Algorithm.
        """
        #Check if wordmatrix is possible
        if not self.wordmatrix.is_deadend():
            #Backup wordmatrix
            self.wordmatrix.backup()

            #Find the co-ordinates of minimum entropy
            x, y = self.find_min_entropy()

            #Collapse the wavefunction at these co-ordinates
            letter = self.wordmatrix.define(x, y)

            #Take a note of the move
            self.history.append([x,y,letter])
            print("letter added: x=", x, ", y=", y, ": ", letter)
            print("history length: ", len(self.wordmatrix.history))

            #Propagate the consequences of this collapse
            self.wordmatrix.update_possibilities()
        
        #If it is a deadend, backtrack
        else:
            if len(self.history) == 0:
                print("No more options")
                print(self.wordmatrix.blacklist)
                os.execl(sys.executable, sys.executable, *sys.argv)
            self.wordmatrix.restore()
            
            #Learn from the mistake
            x, y, letter = self.history.pop()
            #self.wordmatrix.add_blacklist(x, y, letter)
            print("letter removed: ", x, ", ", y, ": ", letter)
            print("history length: ", len(self.wordmatrix.history))

            #Update matrix based on new blacklist
            self.wordmatrix.update_possibilities()
        
        #Print results
        self.wordmatrix.print_defined()


    def find_min_entropy(self):
        """Returns the co-ords of the location whose wavefunction has
        the lowest entropy.
        """
        
        min_entropy_coords = (0, 0)
        min_entropy = 1000

        for y in range(self.wordmatrix.height):
            for x in range(self.wordmatrix.width):
                if self.wordmatrix.is_defined(x,y):
                    continue

                entropy = self.wordmatrix.shannon_entropy(x,y)
                # Add some noise to mix things up a little
                # entropy = entropy - (random.random() / 1000)

                if entropy < min_entropy:
                    min_entropy = entropy
                    min_entropy_coords = (x, y)

        return min_entropy_coords