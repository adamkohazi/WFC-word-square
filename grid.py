import cell
import random

class Grid(object):
    """Class for keeping track of and interacting with a rectangular grid.

    Attributes:
        width (int): Width of the grid.
        height (int): Height of the grid.
        cells (2D list of cells): Cells of the grid.
    """

    def __init__(self, size, letterset):
        """Initializes a new grid of given size.

        Arguments:
            size (tuple): Width and height of the grid
        """
        self.width, self.height = size

        # Initially every letter is an option for every field
        self.cells = [[cell.Cell(cell.Coords(x, y), letterset) for x in range(self.width)] for y in range(self.height)]
    
    def __getitem__(self, coords) -> cell:
        x,y = coords
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        else:
            raise IndexError("Grid index out of range")

    def __setitem__(self, coords, cell):
        x,y = coords
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = cell
        else:
            raise IndexError("Grid index out of range")

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield self.cells[y][x]
    
    def reset(self):
        # TODO? reset blacklist?
        # Reset options if cell is not masked
        for cell in self:
            if not cell.mask:
                cell.reset()
    
    def isFullyDefined(self) -> bool:
        """Checks if there's a single letter defined for every cell.

        Returns:
            (bool): True if single letter is defined for every cell, False otherwise.
        """
        for cell in self:
            if not cell.isDefined():
                return False
        return True

    def isDeadend(self) -> bool:
        """Checks if crossword is a deadend, meaning there's at least one cell with no valid options.

        Returns:
            (bool): True if crossword is deadend, False otherwise.
        """
        for cell in self:
            if sum(cell.options[letter] for letter in cell.options) == 0:
                return True
        return False
    
    def totalOptions(self) -> int:
        """Returns the total number of valid letters for the whole grid. If this number is smaller, the grid is more constrained.

        Returns:
            (int): Total number of valid letters.
        """
        totalOptions = 0
        for cell in self:
            totalOptions += sum(cell.options[letter] for letter in cell.options)
        return totalOptions
    
    def findHorizontalWordLetters(self, coords) -> list[tuple[int]]:
        """Finds the coordinates for each letter of a horizontal word.

        Arguments:
            coords (tuple): Coorinates of the cell from which the search should start.

        Returns:
            letterCoords (list of tuples): List of letter coordinates from left to right.
        """
        if self[coords].options=={"-" : 1}:
            return []
        
        x, y = coords

        xStart = x
        while (xStart > 0) and (self[(xStart-1, y)].options != {"-" : 1}):
            xStart -= 1
        
        xEnd = x
        while (xEnd < self.width) and (self[(xEnd, y)].options != {"-" : 1}):
            xEnd += 1

        letterCoordinates = []
        for x in range(xStart, xEnd):
            letterCoordinates.append((x, y))
        
        return letterCoordinates

    def findVerticalWordLetters(self, coords) -> list[tuple[int]]:
        """Finds the coordinates for each letter of a vertical word.
        
        Arguments:
            coords (tuple): Coorinates of the cell from which the search should start.

        Returns:
            letterCoords (list of tuples): List of letter coordinates from top to bottom.
        """
        if self[coords].options=={"-" : 1}:
            return []
        
        x, y = coords

        yStart = y
        while (yStart > 0) and (self[(x, yStart-1)].options != {"-" : 1}):
            yStart -= 1
        
        yEnd = y
        while (yEnd < self.height) and (self[(x, yEnd)].options != {"-" : 1}):
            yEnd += 1

        letterCoordinates = []
        for y in range(yStart, yEnd):
            letterCoordinates.append((x, y))
        
        return letterCoordinates
    
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
                coords = (x,y)

                # Skip the cell if it is already defined.
                if self[coords].isDefined():
                    continue

                entropy = self[coords].shannonEntropy()

                # Add some noise to mix things up a little
                if noise:
                    entropy = entropy - (noise * random.random() / 1000)

                if entropy < minEntropy:
                    minEntropy = entropy
                    minEntropyCoords = coords
        return minEntropyCoords

    def allWords(self) -> list[str]:
        words = []
        verticalChecked = [[False for x in range(self.width)] for y in range(self.height)]
        horizontalChecked = [[False for x in range(self.width)] for y in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                coords = (x,y)

                # Skip if not part of a word
                if self[coords].options == {"-" : 1} or self[coords].mask:
                    continue
                
                # Check horizontal word
                if not horizontalChecked[y][x]:
                    horizontalCoords = self.findHorizontalWordLetters(coords)
                    # Skip if 2 letters or shorter:
                    if len(horizontalCoords)>2:
                        # Skip if any letter is undefined
                        if not all(self[letterCoords].isDefined() for letterCoords in horizontalCoords):
                            continue

                        # Add word to list
                        words.append(''.join([next(iter(self[letterCoords].options)) for letterCoords in horizontalCoords]))
                        # Mark all letters are checked
                        for letterCoords in horizontalCoords:
                            u,v = letterCoords
                            horizontalChecked[v][u] = True
                
                # Same, but vertical
                if not verticalChecked[y][x]:
                    verticalCoords = self.findHorizontalWordLetters(coords)
                    # Skip if 2 letters or shorter:
                    if len(verticalCoords)>2:
                        # Skip if any letter is undefined
                        if not all(self[letterCoords].isDefined() for letterCoords in verticalCoords):
                            continue

                        # Add word to list
                        words.append(''.join([next(iter(self[letterCoords].options)) for letterCoords in verticalCoords]))
                        # Mark all letters are checked
                        for letterCoords in verticalCoords:
                            u,v = letterCoords
                            verticalChecked[v][u] = True
        return words