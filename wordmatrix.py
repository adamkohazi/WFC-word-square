import re
import math
import random
import time

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

    def __init__(self, size, dictionary, letterset):
        """Initializes a new crossword instance.

        Arguments:
            size (tuple): Width and height of the grid
            dictionary (dict): Valid words that can be used to fill the grid.
            letterset (string): All valid letters concatenated.
        """
        self.width, self.height = size
        self.dictionary = {}
        for length in range(max(size)):
            self.dictionary[length+1] = []
        for word in dictionary:
            self.dictionary[len(word)].append(word)

        # Initially every letter is an option for every field
        self.options = [[dict.fromkeys(letterset, 9999) for w in range(self.width)] for h in range(self.height)]
        # Start with a clean blacklist
        self.blacklist = [[[] for w in range(self.width)] for h in range(self.height)]
        # Clean mask
        self.mask = [[False for w in range(self.width)] for h in range(self.height)]

        # Perform an initial update based on constraints from dictionary TODO
        #self.updateOptions()
    
    def findHorizontalWordLetters(self, coords):
        """Finds the coordinates for each letter of a horizontal word.

        Arguments:
            coords (tuple): Coorinates of the cell from which the search should start.

        Returns:
            letterCoords (list of tuples): List of letter coordinates from left to right.
        """
        if self.getOptions(coords)=={"-" : 1}:
            return []
        
        x, y = coords

        xStart = x
        while (xStart > 0) and (self.getOptions((xStart-1, y)) != {"-" : 1}):
            xStart -= 1
        
        xEnd = x
        while (xEnd < self.width) and (self.getOptions((xEnd, y)) != {"-" : 1}):
            xEnd += 1

        letterCoordinates = []
        for x in range(xStart, xEnd):
            letterCoordinates.append((x, y))
        
        return letterCoordinates

    def findVerticalWordLetters(self, coords):
        """Finds the coordinates for each letter of a vertical word.
        
        Arguments:
            coords (tuple): Coorinates of the cell from which the search should start.

        Returns:
            letterCoords (list of tuples): List of letter coordinates from top to bottom.
        """
        if self.getOptions(coords)=={"-" : 1}:
            return []
        
        x, y = coords

        yStart = y
        while (yStart > 0) and (self.getOptions((x, yStart-1)) != {"-" : 1}):
            yStart -= 1
        
        yEnd = y
        while (yEnd < self.height) and (self.getOptions((x, yEnd)) != {"-" : 1}):
            yEnd += 1

        letterCoordinates = []
        for y in range(yStart, yEnd):
            letterCoordinates.append((x, y))
        
        return letterCoordinates
    
    def getRow(self, y):
        """Lists valid letters for each cell of a row.
        
        Arguments:
            y (int): Coordinate of the row to check.

        Returns:
            (list of dicts) Valid letters for each cell of the row.
        """
        return self.options[y]

    def getColumn(self, x):
        """Lists valid letters for each cell of a column.
        
        Arguments:
            x (int): Coordinate of the column to check.

        Returns:
            (list of dicts): Valid letters for each cell of the column.
        """
        return [row[x] for row in self.options]
    
    def setRow(self, y, options):
        """Sets valid letters for each cell of a row.
        
        Arguments:
            y (int): Coordinate of the row to set.
            options (list of dicts): Valid letters for each cell.
        """
        self.options[y] = options

    def setColumn(self, x, options):
        """Sets valid letters for each cell of a column.
        
        Arguments:
            x (int): Coordinate of the column to set.
            options (list of dicts): Valid letters for each cell of the column.
        """
        for y in len(self.options):
            self.options[y][x]=options[y]

    def getOptions(self, coords):
        """Lists valid letters for a single cell.
        
        Arguments:
            coords (tuple): Coorinates of the cell to check.

        Returns:
            (dict): Valid letters for the cell.
        """
        x, y = coords
        return self.options[y][x]
    
    def setOptions(self, letterCoords, options):
        """Sets valid letters for multiple cells with given coordinates.
        
        Arguments:
            letterCoords (list of tuples): List of letter coordinates to set.
            options (list of dicts): Valid letters for each cell.
        """
        for position, coords in enumerate(letterCoords):
            x, y = coords
            self.options[y][x] = options[position]
    
    def setLetterCount(self, coords, letter, count):
        """Sets the count of a single letter of cell for given coordinates. If count is 0, deletes the letter option.
        
        Arguments:
            coords (tuple): Coorinates of the cell to set.
            letter (char): Letter to set.
            count (int): Count of given letter. If 0, letter is considered invalid for this position.
        """
        x, y = coords
        if count == 0:
            del self.options[y][x][letter]
        else:
            self.options[y][x][letter] = count
    
    def getBlacklist(self, coords):
        """Lists blacklisted letters for a single cell.
        
        Arguments:
            coords (tuple): Coorinates of the cell to check.

        Returns:
            (list): Blacklisted letters for the cell.
        """
        x, y = coords
        return self.blacklist[y][x]

    def addToBlacklist(self, coords, letter):
        """Adds letter to blacklist for a single cell.
        
        Arguments:
            coords (tuple): Coorinates of the cell to set.
            letter (char): Letter to blacklist.

        """
        x, y = coords
        self.blacklist[y][x].append(letter)
    
    def getMask(self, coords):
        """Returns if given cell is excluded from word validity checks.
        
        Arguments:
            coords (tuple): Coorinates of the cell to check.

        Returns:
            (bool): True if cell is excluded from validity checks.
        """
        x, y = coords
        return self.mask[y][x]

    def setMask(self, coords, value=True):
        """Sets mask for a single cell.
        
        Arguments:
            coords (tuple): Coorinates of the cell to set.
            value (bool): (True by default) Mask status for set.

        """
        x, y = coords
        self.mask[y][x] = value

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
        for word in list(filter(r.match, self.dictionary[len(options)])):
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
            wordOptions.append(self.getOptions(coords))
        
        #TODO: Running the find frequencies function takes ~95% of the runtime. Performance could be greatly increased by performing less lookups.
        for position, frequencies in enumerate(self.find_frequencies(wordOptions)):
            coords = letterCoords[position]
            for letter in self.getOptions(coords).copy():
                if letter not in frequencies or letter in self.getBlacklist(coords):
                    # Invalidate letters that are blacklisted or don't appear in words.
                    self.setLetterCount(coords, letter, 0)
                else:
                    # Take the minimum of the existing and new letter weights.
                    # This is done so that if a letter is very common for horizontal words but rare for vertical words, it will be considered rare.
                    self.setLetterCount(coords, letter, min(self.getOptions(coords)[letter], frequencies[letter]))

    #@profile
    def updateOptions(self):
        """Iteratively updates letter options, until a minimum subset is reached. After this update, the crossword is either solvable and all invalid letters are eliminated or a deadend is confirmed.
        """
        old_total_options = 0
        for y in range(self.height):
            for x in range(self.width):
                old_total_options += sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y)))
        
        startTime = time.perf_counter()
        nUpdates = 0
        # Do this while the total number of valid letters are decreasing, hence the crossword is more defined
        while(True):
            nUpdates += 1
            # Remove blacklisted letters:
            for y in range(self.height):
                for x in range(self.width):
                    for letter in self.blacklist[y][x]:
                        self.options[y][x][letter] = 0
            
            # Stop updating if already deadend
            if self.isDeadend():
                break
            
            # Keep track of what has been updated, to avoid updating a word for every letter
            horizontalUpdated = [[False for w in range(self.width)] for h in range(self.height)]
            verticalUpdated = [[False for w in range(self.width)] for h in range(self.height)]

            # Go through every cell
            for y in range(self.height):
                for x in range(self.width):
                    coords = (x, y)

                    # Skip cell if it's defined or masked
                    if self.isDefined(coords) or self.getMask(coords):
                        continue
                    
                    # Stop updating if already deadend
                    if self.isDeadend():
                        break
                    
                    # If horizontal word of the cell was not yet updated, update it
                    if horizontalUpdated[y][x] != True:
                        wordCoords = self.findHorizontalWordLetters(coords)
                        if(len(wordCoords)>2):
                            self.updateWordOptions(wordCoords)
                        # Note that the word was updated
                        for x1, y1 in wordCoords:
                            horizontalUpdated[y1][x1] = True
                    
                    # Stop updating if already deadend
                    if self.isDeadend():
                        break

                    # If vertical word of the cell was not yet updated, update it
                    if verticalUpdated[y][x] != True:
                        wordCoords = self.findVerticalWordLetters(coords)
                        if(len(wordCoords)>2):
                            self.updateWordOptions(wordCoords)
                        # Note that the word was updated
                        for x1, y1 in wordCoords:
                            verticalUpdated[y1][x1] = True
                        
            # Calculate new weight
            new_total_options = 0
            for y in range(self.height):
                for x in range(self.width):
                    new_total_options += sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y)))
            
            # Stop updating if no large improvement could be reached
            if new_total_options >= old_total_options * 1.0:
                break
            else:
                old_total_options = new_total_options
        
        endTime = time.perf_counter()
        print("Updating options took: %.2gs and ran %d times" % (endTime-startTime, nUpdates))
        return nUpdates
            
    def shannonEntropy(self, coords) -> float:
        """Calculates the Shannon entropy ("uncertainty") for a cell with given coordinates. Higher number means higher uncertainty.

        Arguments:
            coords (tuple): Coorinates of the cell to check.

        Returns:
            entropy (float): Entropy of the cell (in bits).
        """
        entropy = 0
        sumOfWeights = sum(self.getOptions(coords)[letter] for letter in self.getOptions(coords))
        for letter in self.getOptions(coords):
            weight = self.getOptions(coords)[letter]
            letterProbability = weight / sumOfWeights
            if weight > 0:
                entropy -= letterProbability * math.log(letterProbability)
        return entropy

    def findMinEntropy(self, noise=None):
        """Finds the coordinates with the lowest entropy (e.g. the "most likely" letter)

        Arguments:
            noise (float) - optional: Level of noise mix into the entropies. (Default: No noise is present)

        Returns:
            minEntropyCoords (tuple): Coorinates of the cell with the minimum entropy.
        """
        
        minEntropyCoords = (0, 0)
        minEntropy = 1000

        for y in range(self.height):
            for x in range(self.width):
                # Skip the cell if it is already defined.
                if self.isDefined((x,y)):
                    continue

                entropy = self.shannonEntropy((x,y))

                # Add some noise to mix things up a little
                if noise:
                    entropy = entropy - (noise * random.random() / 1000)

                if entropy < minEntropy:
                    minEntropy = entropy
                    minEntropyCoords = (x, y)

        return minEntropyCoords

    def isDefined(self, coords):
        """Checks if there's a single letter defined for a cell.

        Arguments:
            coords (tuple): Coorinates of the cell to check.

        Returns:
            (bool): True if single letter is defined, False otherwise.
        """
        if sum(self.getOptions(coords)[letter] > 0 for letter in self.getOptions(coords)) == 1:
            return True
        return False
    
    def isFullyDefined(self):
        """Checks if there's a single letter defined for every cell.

        Returns:
            (bool): True if single letter is defined for every cell, False otherwise.
        """
        for y in range(self.height):
            for x in range(self.width):
                if not self.isDefined((x,y)):
                    return False
        return True
    
    def isFullyValid(self):
        """Checks if every defined word is valid.

        Returns:
            (bool): True if every full word is valid, False otherwise.
        """
        for y in range(self.height):
            for x in range(self.width):
                # Skip cell if it's a blank or masked
                coords = (x,y)
                if self.getOptions(coords) == {"-" : 1} or self.getMask(coords):
                    continue
                
                # Check horizontal word
                horizontalCoords = self.findHorizontalWordLetters(coords)
                if len(horizontalCoords)>2 and all(self.isDefined(xy) for xy in horizontalCoords):
                    if ''.join([next(iter(self.getOptions(xy))) for xy in horizontalCoords]) not in self.dictionary[len(horizontalCoords)]:
                        return False
                
                # Check vertical word
                verticalCoords = self.findVerticalWordLetters(coords)
                if len(verticalCoords)>2 and all(self.isDefined(xy) for xy in verticalCoords):
                    if ''.join([next(iter(self.getOptions(xy))) for xy in verticalCoords]) not in self.dictionary[len(verticalCoords)]:
                        return False
        return True

    def printAssessment(self):
        """Checks if every defined word is valid.

        Returns:
            (bool): True if every full word is valid, False otherwise.
        """
        wordOptions = [[" " for w in range(self.width)] for h in range(self.height)]
        
        # Assess number of word options considering only fixed letters
        for y in range(self.height):
            for x in range(self.width):
                # Skip cell if it's defined or masked
                if self.isDefined((x,y)) or self.getMask((x,y)):
                    wordOptions[y][x] = next(iter(self.getOptions((x,y))))
                    continue
                
                # Check horizontal word
                wordCoords = self.findHorizontalWordLetters((x,y))
                horizontalCount = 9999
                if len(wordCoords) > 2:
                    # Convert elements to regular expression:
                    regex = "^"
                    for coords in wordCoords:
                        if self.isDefined(coords):
                            regex += next(iter(self.getOptions(coords)))
                        else:
                            regex += '.'
                    regex += "$"
                    r = re.compile(regex, re.UNICODE)

                    horizontalCount = len(list(filter(r.match, self.dictionary[len(wordCoords)])))
                
                # Check vertical word
                wordCoords = self.findVerticalWordLetters((x,y))
                verticalCount = 9999
                if len(wordCoords) > 2:
                    # Convert elements to regular expression:
                    regex = "^"
                    for coords in wordCoords:
                        if self.isDefined(coords):
                            regex += next(iter(self.getOptions(coords)))
                        else:
                            regex += '.'
                    regex += "$"
                    r = re.compile(regex, re.UNICODE)

                    verticalCount = len(list(filter(r.match, self.dictionary[len(wordCoords)])))

                wordOptions[y][x] = math.log10(min(horizontalCount, verticalCount))

        self.printMatrix(wordOptions, 5)

        horizontalUpdated = [[False for w in range(self.width)] for h in range(self.height)]
        verticalUpdated = [[False for w in range(self.width)] for h in range(self.height)]

        horizontalLength = [[' ' for w in range(self.width)] for h in range(self.height)]
        verticalLength = [[' ' for w in range(self.width)] for h in range(self.height)]

        lengthDistribution = [0 for n in range(max(self.width, self.height) + 1)]


        # Assess word lengths
        for y in range(self.height):
            for x in range(self.width):
                # Skip cell if it's a blank
                if self.getOptions((x,y)) == {"-" : 1}:
                    continue
                
                # Check horizontal word
                horizontalCoords = self.findHorizontalWordLetters((x,y))
                horizontalLength[y][x] = len(horizontalCoords)
                # If horizontal word yet counted, increment counter
                if horizontalUpdated[y][x] != True:
                    lengthDistribution[horizontalLength[y][x]] += 1
                    for x1, y1 in horizontalCoords:
                        horizontalUpdated[y1][x1] = True
                        
                # Check vertical word
                verticalCoords = self.findVerticalWordLetters((x,y))
                verticalLength[y][x] = len(verticalCoords)
                # If vertical word yet counted, increment counter
                if verticalUpdated[y][x] != True:
                    lengthDistribution[verticalLength[y][x]] += 1
                    for x1, y1 in verticalCoords:
                        verticalUpdated[y1][x1] = True

        self.printMatrix(horizontalLength)
        self.printMatrix(verticalLength)
        print(lengthDistribution)
                
    def isDeadend(self):
        """Checks if crossword is a deadend, meaning there's at least one cell with no valid options.

        Returns:
            (bool): True if crossword is deadend, False otherwise.
        """
        for y in range(self.height):
            for x in range(self.width):
                if sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y))) == 0:
                    return True
        return False
    
    def define(self, coords):
        """Defines a single letter for a cell with multiple options, weighted by letter frequencies for valid words.

        Arguments:
            coords (tuple): Coorinates of the cell to set.

        Returns:
            letter (char): Letter that was choosen for the cell.
        """
        total_weight = sum(self.getOptions(coords)[letter] for letter in self.getOptions(coords))
        rnd = random.random() * total_weight

        for letter in self.getOptions(coords):
            rnd -= self.getOptions(coords)[letter]
            if rnd < 0:
                self.setLetter(coords, letter)
                return letter
    
    def setLetter(self, coords, letter):
        """Defines a single letter for a cell, discarding all other options.

        Arguments:
            coords (tuple): Coorinates of the cell to set.
            letter (char): Letter to set.
        """
        x, y = coords
        self.options[y][x] = {letter : 1}

    def printDefined(self):
        """Prints the crossword, by only filling cells with single defined letters.
        """
        defined = [[" " for w in range(self.width)] for h in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.isDefined((x,y)):
                    defined[y][x] = next(iter(self.getOptions((x,y))))
        self.printMatrix(defined)
    
    def printMatrix(self, matrix, width=3):
        """Prints any value into the console, in a nice matrix-like way

        Arguments:
            matrix (2D list): Matrix of values that should be printed. Any type is acceptable as long as it can be cast to string using str().
            width (int): Width of one column in characters.
        """
        out = "   "
        for x in range(self.width):
            out += str(x).center(width)
        out += "\n"
        for y in range(self.height):
            out += str(y).center(width)
            for x in range(self.width):
                out += str(matrix[y][x])[:width].center(width)
            out += "\n"
        print(out)
    
    def printOptions(self):
        """Prints the crossword, by filling cells with every letter that is still a valid option.
        """
        #Column headers
        out = "   |"
        for x in range(self.width):
            out += "   " + str(x) + "  |"
        out += "\n"

        #Column header separator
        out += "---|"
        for x in range(self.width):
            out += "------|"
        out += "\n"

        #Row headers
        for y in range(self.height):
            out += "   |"
            for x in range(self.width):
                for letter in "abcdef":
                    if letter in self.getOptions((x, y)):
                        if self.getOptions((x, y))[letter] > 0:
                            out += letter
                        else:
                            out += " "
                    else:
                        out += " "
                out += "|"
            out += "\n"

            out += "   |"
            for x in range(self.width):
                for letter in "ghijkl":
                    if letter in self.getOptions((x, y)):
                        if self.getOptions((x, y))[letter] > 0:
                            out += letter
                        else:
                            out += " "
                    else:
                        out += " "
                out += "|"
            out += "\n"

            out += " "+ str(y) +" |"
            for x in range(self.width):
                for letter in "mnopqr":
                    if letter in self.getOptions((x, y)):
                        if self.getOptions((x, y))[letter] > 0:
                            out += letter
                        else:
                            out += " "
                    else:
                        out += " "
                out += "|"
            out += "\n"

            out += "   |"
            for x in range(self.width):
                for letter in "stuvwx":
                    if letter in self.getOptions((x, y)):
                        if self.getOptions((x, y))[letter] > 0:
                            out += letter
                        else:
                            out += " "
                    else:
                        out += " "
                out += "|"
            out += "\n"

            out += "   |"
            for x in range(self.width):
                for letter in "yz-áéó":
                    if letter in self.getOptions((x, y)):
                        if self.getOptions((x, y))[letter] > 0:
                            out += letter
                        else:
                            out += " "
                    else:
                        out += " "
                out += "|"
            out += "\n"

            out += "---|"
            for x in range(self.width):
                out += "------|"
            out += "\n"

        print(out)
    
    
