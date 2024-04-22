import re
import math
import random

#random.seed(1234) # Used for testing

class Crossword(object):
    """Class for keeping track of and interacting with a rectangular crossword grid.

    Attributes:
        width (int): Width of the rectangular crossword grid.
        height (int): Integer height of the rectangular crossword grid.
        dictionary (dict): Valid words that can be used to fill the grid.
        options (2D list of dicts): Valid letters for each cell of the grid.
        blacklist (2D list of lists): Letters that result in an unsolvable state for each cell of the grid.
    """

    def __init__(self, size, dictionary, letterset):
        """Initializes a new crossword instance.

        Arguments:
            size (tuple): Width and height of the grid
            dictionary (dict): Valid words that can be used to fill the grid.
            letterset (string): All valid letters concatenated.
        """
        self.width, self.height = size
        self.dictionary = dictionary

        # Initially every letter is an option for every field
        self.options = [[dict.fromkeys(letterset, 9999) for w in range(self.width)] for h in range(self.height)]
        # Start with a clean blacklist
        self.blacklist = [[[] for w in range(self.width)] for h in range(self.height)]

        # Perform an initial update based on constraints from dictionary
        self.update_possibilities()
    
    def find_horizontal_word_letters(self, coords):
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

    def find_vertical_word_letters(self, coords):
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
        """Sets valid letters cells with given coordinates.
        
        Arguments:
            letterCoords (list of tuples): List of letter coordinates to set.
            options (list of dicts): Valid letters for each cell.

        Returns:
            (dict): Valid letters for the cell.
        """
        for position, coords in enumerate(letterCoords):
            x, y = coords
            self.options[y][x] = options[position]
    
    def setLetterOption(self, coords, letter, count):
        x, y = coords
        self.options[y][x][letter] = count
    
    def getBlacklist(self, coords):
        x, y = coords
        return self.blacklist[y][x]

    def add_blacklist(self, coords, letter):
        x, y = coords
        self.blacklist[y][x].append(letter)

    #@profile
    def find_frequencies(self, elements):
        frequencies = [{} for element in elements]

        # Convert elements to regular expression:
        regex = ""
        for element in elements:
            regex += "[" + ''.join([letter for letter in element if element[letter]>0]) + "]"
        regex += "$"
        r = re.compile(regex, re.UNICODE)

        # Find letter options/counts based on matching words
        for word in list(filter(r.match, self.dictionary)):
            for position, letter in enumerate(word):
                if letter not in frequencies[position]:
                    frequencies[position][letter] = 0
                frequencies[position][letter] += 1

        return frequencies
    
    def updateWord(self, letterCoords):
        wordOptions = []
        for coords in letterCoords:
            wordOptions.append(self.getOptions(coords))
            
        for position, frequencies in enumerate(self.find_frequencies(wordOptions)):
            coords = letterCoords[position]
            for letter in self.getOptions(coords):
                if letter not in frequencies or letter in self.getBlacklist(coords):
                    self.setLetterOption(coords, letter, 0)
                else:
                    self.setLetterOption(coords, letter, min(self.getOptions(coords)[letter], frequencies[letter]))
    

    #@profile
    def update_possibilities(self):
        old_total_options = 0
        for y in range(self.height):
            for x in range(self.width):
                old_total_options += sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y)))
        
        while(True):
            #Remove blacklisted letters:
            for y in range(self.height):
                for x in range(self.width):
                    for letter in self.blacklist[y][x]:
                        self.options[y][x][letter] = 0
                        #print("letter popped: ", x, ", ", y, ": ", letter)
            
            #Stop updating if already deadend
            if self.is_deadend():
                break
            
            if(False):#old
                #horizontal words
                for y in range(self.height):
                    for x, frequencies in enumerate(self.find_frequencies(self.getRow(y))):
                        for letter in self.getOptions((x, y)):
                            if letter not in frequencies or letter in self.blacklist[y][x]:
                                self.options[y][x][letter] = 0
                            else:
                                self.options[y][x][letter] = min(self.getOptions((x, y))[letter], frequencies[letter])
                
                #Stop updating if already deadend
                if self.is_deadend():
                    break
                
                #vertical words
                for x in range(self.width):
                    for y, frequencies in enumerate(self.find_frequencies(self.getColumn(x))):
                        for letter in self.getOptions((x, y)):
                            if letter not in frequencies or letter in self.blacklist[y][x]:
                                self.options[y][x][letter] = 0
                            else:
                                self.options[y][x][letter] = min(self.getOptions((x, y))[letter], frequencies[letter])
            else:#new
                horizontalUpdated = [[False for w in range(self.width)] for h in range(self.height)]
                verticalUpdated = [[False for w in range(self.width)] for h in range(self.height)]
                for y in range(self.height):
                    for x in range(self.width):
                        if self.is_deadend():
                            break
                        coords = (x, y)
                        #print(coords)
                        if self.getOptions(coords) == {"-" : 1}:
                            next
                        else:
                            if horizontalUpdated[y][x] != True:
                                wordCoords = self.find_horizontal_word_letters(coords)
                                #print("horizontal: ", wordCoords)
                                self.updateWord(wordCoords)
                                for x1, y1 in wordCoords:
                                    horizontalUpdated[y1][x1] = True
                            if self.is_deadend():
                                break
                            if verticalUpdated[y][x] != True:
                                wordCoords = self.find_vertical_word_letters(coords)
                                #print("vertical: ", wordCoords)
                                self.updateWord(wordCoords)
                                for x1, y1 in wordCoords:
                                    verticalUpdated[y1][x1] = True
                        

            #Calculate new weight
            new_total_options = 0
            for y in range(self.height):
                for x in range(self.width):
                    new_total_options += sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y)))
            
            #Stop updating if no improvement could be reached
            if new_total_options >= old_total_options:
                break
            else:
                old_total_options = new_total_options
        
            
    def shannon_entropy(self, coords) -> float:
        """Calculates the Shannon Entropy of the wavefunction at given
        coordinates.
        """
        x, y = coords
        sum_of_weights = 0
        sum_of_weight_log_weights = 0
        for letter in self.getOptions((x, y)):
            weight = self.getOptions((x, y))[letter]
            if weight > 0:
                sum_of_weights += weight
                sum_of_weight_log_weights += weight * math.log(weight)

        return math.log(sum_of_weights) - (sum_of_weight_log_weights / sum_of_weights)

    def entropies(self):
        entropies = [[float]*self.width for i in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                entropies[y][x] = self.shannon_entropy(x, y)
        return entropies

    def find_min_entropy(self, noise=None):
        """Returns the co-ords of the location whose wavefunction has
        the lowest entropy.
        """
        
        min_entropy_coords = (0, 0)
        min_entropy = 1000

        for y in range(self.height):
            for x in range(self.width):
                if self.is_defined((x,y)):
                    continue

                entropy = self.shannon_entropy((x,y))

                # Add some noise to mix things up a little
                if noise:
                    entropy = entropy - (noise * random.random() / 1000)

                if entropy < min_entropy:
                    min_entropy = entropy
                    min_entropy_coords = (x, y)

        return min_entropy_coords

    def is_defined(self, coords):
        x, y = coords
        if sum(self.getOptions((x, y))[letter] > 0 for letter in self.getOptions((x, y))) == 1:
            return True
        return False
    
    def is_deadend(self):
        for y in range(self.height):
            for x in range(self.width):
                if sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y))) == 0:
                    #print("Deadend at (",x,",",y,")")
                    return True
        return False
    
    def define(self, coords):
        x, y = coords
        total_weight = sum(self.getOptions((x, y))[letter] for letter in self.getOptions((x, y)))
        rnd = random.random() * total_weight

        for letter in self.getOptions((x, y)):
            rnd -= self.getOptions((x, y))[letter]
            if rnd < 0:
                self.set((x, y), letter)
                return letter
    
    def is_fully_defined(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_defined((x,y)):
                    return False
        return True
    
    def set(self, coords, letter):
        x, y = coords
        self.options[y][x] = {letter : 1}

    def print_defined(self):
        out = "   "
        for x in range(self.width):
            out += " " + str(x) + " "
        out += "\n"
        for y in range(self.height):
            out += " " + str(y) + " "
            for x in range(self.width):
                if self.is_defined((x,y)):
                    out += " " + ''.join([letter for letter in  self.getOptions((x, y)) if  self.getOptions((x, y))[letter]>0]) + " "
                else:
                    out += "   "
            out += "\n"
        print(out)
    
    def print_options(self):
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
                for letter in "yz-   ":
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
    
    
