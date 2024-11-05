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
        _options (dict): Letter options for cell, valued based on their likelihood to appear.
        _blacklist (list): Letters that result in an unsolvable state for each cell of the grid.
        _mask (bool): Indicates if cell should be excluded from the word validity checks, e.g. fixed cells.
    """
    def __init__(self, coords, letterset) -> None:
        """Initializes a new cell instance.

        Arguments:
            coords (tuple): Coorinates of the cell.
            letterset (string): All valid letters concatenated.
        """
        self.coords = coords
        self.letterset = letterset
        self.reset()
    
    def reset(self) -> None:
        """Disable mask, empty blacklist, set every letter option.
        
        Arguments:
            coords (tuple): Coorinates of the cell to reset.
        """
        self.mask = False
        self.blacklist = []
        self.options = dict.fromkeys(self.letterset, 9999)
    
    @property
    def mask(self) -> bool:
        """Get the current mask status

        Returns:
            mask (bool): True if cell is masked.
        """
        return self._mask

    @mask.setter
    def mask(self, mask:bool = True) -> None:
        """Sets the current mask status.

        Arguments:
            mask (bool): True if cell is masked. True by default.
        """
        self._mask = mask
    
    def setLetter(self, letter:str) -> None:
        """Sets a single letter, discarding all other options.

        Arguments:
            letter (char): Letter to set.
        """
        self.options = {letter : 1}

    def setLetterCount(self, letter: str, count: int) -> None:
        """Sets the count of a single letter. If count is 0, deletes the letter from valid options.
        
        Arguments:
            letter (char): Letter to set.
            count (int): Count of given letter. If 0, letter is considered invalid for this position.
        """
        if not self.mask:
            self.options[letter] = count
    
    def sumOptions(self) -> int:
        """Sums the weights for all valid letters.

        Returns:
            (int): Sum of weights.
        """
        return sum(self.options[letter] for letter in self.options)
    
    def shannonEntropy(self) -> float:
        """Calculates the Shannon entropy ("uncertainty") for the cell. Higher number means higher uncertainty.

        Returns:
            entropy (float): Entropy of the cell (in bits).
        """
        entropy = 0
        sumOfWeights = self.sumOptions()
        for letter in self.options:
            weight = self.options[letter]
            letterProbability = weight / sumOfWeights
            if weight > 0:
                entropy -= letterProbability * log(letterProbability)
        return entropy

    def isDefined(self) -> bool:
        """Checks if there's a only single letter defined.

        Returns:
            (bool): True if single letter is defined, False otherwise.
        """
        return (sum(self.options[letter] > 0 for letter in self.options) == 1)

    def getDefined(self) -> str:
        """Returns the first (hopefully only) letter that is valid.

        Returns:
            (str): Valid letter.
        """
        for letter in self.options:
            if self.options[letter] > 0:
                return letter
    
    def define(self) -> str:
        """Defines a single letter randomly, weighted by current options.

        Returns:
            letter (char): Letter that was choosen for the cell.
        """
        sumOfWeights = self.sumOptions()
        rnd = random() * sumOfWeights

        for letter in self.options:
            rnd -= self.options[letter]
            if rnd < 0:
                self.setLetter(letter)
                return letter
    
    def isBlocked(self) -> bool:
        """Checks if cell is blocked (no letter allowed).

        Returns:
            (bool): True if single letter is blocked, False otherwise.
        """
        return self.options == {"-" : 1}
    
    