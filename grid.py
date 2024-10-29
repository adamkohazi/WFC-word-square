import cell

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