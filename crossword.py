import re
import math
import random
import time
import dictionary
import cell
import grid

class Crossword(object):
    """Class for keeping track of and interacting with a rectangular crossword grid.

    Attributes:
        width (int): Width of the rectangular crossword grid.
        height (int): Integer height of the rectangular crossword grid.
        dictionary (dict): Valid words that can be used to fill the grid.
        options (2D list of dicts): Valid letters for each cell of the grid.
        blacklist (2D list of lists): Letters that result in an unsolvable state for each cell of the grid.
        mask (2D list of bool): Indicates if certain cells should be excluded from the word validity checks.
    """

    def __init__(self, size, dictionary):
        """Initializes a new crossword instance.

        Arguments:
            size (tuple): Width and height of the grid
            dictionary (dict): Valid words that can be used to fill the grid.
        """
        self.dictionary = dictionary

        # Initially every letter is an option for every field
        self.grid = grid.Grid(size, self.dictionary.validLetters)

        # TODO - Perform an initial update based on constraints from dictionary
        #self.updateOptions()
    
    def reset(self):
        self.grid.reset()

    #@profile
    def find_frequencies(self, options):
        """Finds the frequency of letters for each position of a word based on the active dictionary. The dictionary is prefiltered by a list of allowed letters (options).
        
        Arguments:
            options (list of dicts): Valid letters for each position.

        Returns:
            frequencies (list of dicts): Letter frequencies for each position.
        """
        
        #TODO: Running this function takes ~95% of the runtime. Performance could be greatly increased by making this lookup more efficient.
        frequencies = [{} for option in options]

        # Convert elements to regular expression:
        regex = "^"
        for element in options:
            regex += "[" + ''.join([letter for letter in element if element[letter]>0]) + "]"
        regex += "$"
        r = re.compile(regex, re.UNICODE)

        # Find letter options/counts based on matching words
        for word in list(filter(r.match, self.dictionary.lookup[len(options)])):
            for position, letter in enumerate(word):
                if letter not in frequencies[position]:
                    frequencies[position][letter] = 0
                frequencies[position][letter] += 1

        return frequencies
    
    def updateWordOptions(self, letterCoords):
        """Updates the valid letter options for given cells, by performing a lookup using the current letter options, and removing those that don't appear in the results.
        
        Arguments:
            letterCoords (list of tuples): List of coordinates to set.
        """
        wordOptions = []
        for coords in letterCoords:
            wordOptions.append(self.grid[coords].options)
        
        #TODO: Running the find frequencies function takes ~95% of the runtime. Performance could be greatly increased by performing less lookups.
        for position, frequencies in enumerate(self.find_frequencies(wordOptions)):
            coords = letterCoords[position]
            for letter in self.grid[coords].options.copy():
                if letter not in frequencies or letter in self.grid[coords].blacklist:
                    # Invalidate letters that are blacklisted or don't appear in words.
                    self.grid[coords].setLetterCount(letter, 0)
                else:
                    # Take the minimum of the existing and new letter weights.
                    # This is done so that if a letter is very common for horizontal words but rare for vertical words, it will be considered rare.
                    self.grid[coords].setLetterCount(letter, min(self.grid[coords].options[letter], frequencies[letter]))

    #@profile
    def updateOptions(self):
        """Iteratively updates letter options, until a minimum subset is reached. After this update, the crossword is either solvable and all invalid letters are eliminated or a deadend is confirmed.
        """
        #TODO: reset options?
        
        old_total_options = self.grid.totalOptions()
        
        startTime = time.perf_counter()
        nUpdates = 0
        # Do this while the total number of valid letters are decreasing, hence the crossword is more defined
        while(True):
            nUpdates += 1
            # Remove blacklisted letters:
            for cell in self.grid:
                for letter in cell.blacklist:
                    cell.setLetterCount(letter, 0)
            
            # Stop updating if already deadend
            if self.grid.isDeadend():
                break
            
            # Keep track of what has been updated, to avoid updating a word for every letter
            horizontalUpdated = [[False for w in range(self.grid.width)] for h in range(self.grid.height)]
            verticalUpdated = [[False for w in range(self.grid.width)] for h in range(self.grid.height)]

            # Go through every cell
            for y in range(self.grid.height):
                for x in range(self.grid.width):
                    coords = (x, y)

                    # Skip cell if it's defined or masked
                    if self.grid[coords].isDefined() or self.grid[coords].mask:
                        continue
                    
                    # Stop updating if already deadend
                    if self.grid.isDeadend():
                        break
                    
                    # If horizontal word of the cell was not yet updated, update it
                    if horizontalUpdated[y][x] != True:
                        wordCoords = self.grid.findHorizontalWordLetters(coords)
                        if(len(wordCoords)>2):
                            self.updateWordOptions(wordCoords)
                        # Note that the word was updated
                        for x1, y1 in wordCoords:
                            horizontalUpdated[y1][x1] = True
                    
                    # Stop updating if already deadend
                    if self.grid.isDeadend():
                        break

                    # If vertical word of the cell was not yet updated, update it
                    if verticalUpdated[y][x] != True:
                        wordCoords = self.grid.findVerticalWordLetters(coords)
                        if(len(wordCoords)>2):
                            self.updateWordOptions(wordCoords)
                        # Note that the word was updated
                        for x1, y1 in wordCoords:
                            verticalUpdated[y1][x1] = True
                        
            # Calculate new weight
            new_total_options = self.grid.totalOptions()
            
            # Stop updating if no large improvement could be reached
            if new_total_options >= old_total_options * 1.0:
                break
            else:
                old_total_options = new_total_options
        
        endTime = time.perf_counter()
        print("Updating options took: %.2gs and ran %d times" % (endTime-startTime, nUpdates))
        return nUpdates
    
    def isFullyValid(self):
        """Checks if every defined word is valid.

        Returns:
            (bool): True if every full word is valid, False otherwise.
        """
        for word in self.grid.allWords():
            if word not in self.dictionary.lookup[len(word)]:
                return False
        return True