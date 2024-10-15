from random import random
from math import log
from typing import NamedTuple

class Coords(NamedTuple):
    x: int
    y: int

    def __add__(self, other: 'Coords') -> 'Coords':
        return Coords(x = (self.x + other.x), y = (self.y + other.y))
    
    def __neg__ (self) -> 'Coords':
        return Coords(x = -self.x, y = -self.y)

class Cell(object):
    """Class for keeping track of and interacting with a single crossword cell.

    Attributes:
        coords (tuple): Coorinates of the cell.
        options (dict): Letter options for cell, valued based on their likelihood to appear.
        blacklist (list): Letters that result in an unsolvable state for each cell of the grid.
        mask (bool): Indicates if cell should be excluded from the word validity checks, e.g. fixed cells.
    """
    def __init__(self, coords, letterset):
        """Initializes a new cell instance.

        Arguments:
            coords (tuple): Coorinates of the cell.
            letterset (string): All valid letters concatenated.
        """
        self.coords = coords
        self.letterset = letterset
        self.reset()
    
    def reset(self):
        """Disable mask, empty blacklist, set every letter option.
        
        Arguments:
            coords (tuple): Coorinates of the cell to reset.
        """
        self.mask = False
        self.blacklist = []
        self.options = dict.fromkeys(self.letterset, 9999)
    
    def setLetterCount(self, letter, count):
        """Sets the count of a single letter. If count is 0, deletes the letter from valid options.
        
        Arguments:
            letter (char): Letter to set.
            count (int): Count of given letter. If 0, letter is considered invalid for this position.
        """
        if not self.mask:
            if count == 0:
                del self.options[letter]
            else:
                self.options[letter] = count

    def addToBlacklist(self, letter):
        """Appends an additional letter to the blacklist.
        
        Arguments:
            letter (char): Letter to blacklist.
        """
        self.blacklist.append(letter)

    def shannonEntropy(self) -> float:
        """Calculates the Shannon entropy ("uncertainty") for the cell. Higher number means higher uncertainty.

        Returns:
            entropy (float): Entropy of the cell (in bits).
        """
        entropy = 0
        sumOfWeights = sum(self.options[letter] for letter in self.options)
        for letter in self.options:
            weight = self.options[letter]
            letterProbability = weight / sumOfWeights
            if weight > 0:
                entropy -= letterProbability * log(letterProbability)
        return entropy

    def isDefined(self):
        """Checks if there's a only single letter defined.

        Returns:
            (bool): True if single letter is defined, False otherwise.
        """
        return (sum(self.options[letter] > 0 for letter in self.options) == 1)
    
    def define(self):
        """Defines a single letter based on current options.

        Returns:
            letter (char): Letter that was choosen for the cell.
        """
        total_weight = sum(self.options[letter] for letter in self.options)
        rnd = random() * total_weight

        for letter in self.options:
            rnd -= self.options[letter]
            if rnd < 0:
                self.setLetter(letter)
                return letter

    def setLetter(self, letter):
        """Sets a single letter, discarding all other options.

        Arguments:
            letter (char): Letter to set.
        """
        self.options = {letter : 1}
    