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
    
    def get(self, coords) -> cell:
        x,y = coords
        return self.cells[y][x]

    def set(self, coords, cell):
        x,y = coords
        self.cells[y][x] = cell

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield self.cells[y][x]
    
    def findHorizontalWordLetters(self, coords) -> list[tuple[int]]:
        """Finds the coordinates for each letter of a horizontal word.

        Arguments:
            coords (tuple): Coorinates of the cell from which the search should start.

        Returns:
            letterCoords (list of tuples): List of letter coordinates from left to right.
        """
        if self.get(coords).options=={"-" : 1}:
            return []
        
        x, y = coords

        xStart = x
        while (xStart > 0) and (self.get((xStart-1, y)).options != {"-" : 1}):
            xStart -= 1
        
        xEnd = x
        while (xEnd < self.width) and (self.get((xEnd, y)).options != {"-" : 1}):
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
        if self.get(coords).options=={"-" : 1}:
            return []
        
        x, y = coords

        yStart = y
        while (yStart > 0) and (self.get((x, yStart-1)).options != {"-" : 1}):
            yStart -= 1
        
        yEnd = y
        while (yEnd < self.height) and (self.get((x, yEnd)).options != {"-" : 1}):
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
                if self.get(coords).isDefined():
                    continue

                entropy = self.get(coords).shannonEntropy()

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
                if self.get(coords).options == {"-" : 1} or self.get(coords).mask:
                    continue
                
                # Check horizontal word
                if not horizontalChecked[y][x]:
                    horizontalCoords = self.findHorizontalWordLetters(coords)
                    # Skip if 2 letters or shorter:
                    if len(horizontalCoords)>2:
                        # Skip if any letter is undefined
                        if not all(self.get(letterCoords).isDefined() for letterCoords in horizontalCoords):
                            continue

                        # Add word to list
                        words.append(''.join([next(iter(self.get(letterCoords).options)) for letterCoords in horizontalCoords]))
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
                        if not all(self.get(letterCoords).isDefined() for letterCoords in verticalCoords):
                            continue

                        # Add word to list
                        words.append(''.join([next(iter(self.get(letterCoords).options)) for letterCoords in verticalCoords]))
                        # Mark all letters are checked
                        for letterCoords in verticalCoords:
                            u,v = letterCoords
                            verticalChecked[v][u] = True
        return words