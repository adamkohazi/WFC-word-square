import re
import string
import math
import random
from copy import deepcopy

class Wordmatrix(object):
    """Class for keeping track of all information related to a wordmatrix board.

    Attributes:
        hand: Counter class keeping track of letters available in hand.
        score: Integer value keeping track of the current score.
        isBot: Boolean indicating if the player is a bot or not.
    """

    def __init__(self, size, dictionary):
        self.width, self.height = size
        self.dictionary = dictionary

        # Initially every letter is an option for every field
        self.options = [[dict.fromkeys(string.ascii_lowercase, 9999) for w in range(self.width)] for h in range(self.height)]
        self.blacklist = [[[] for w in range(self.width)] for h in range(self.height)]
        #self.possibilities = [[[] for w in range(self.width)] for h in range(self.height)]
        self.history = []
    
        self.update_possibilities()
    
    def get_row(self, row):
        return self.options[row]

    def get_column(self, column):
        return [row[column] for row in self.options]
    
    def set_row(self, row, elements):
        self.options[row] = elements

    def set_column(self, column, elements):
        for index in len(self.options):
            self.options[index][column]=elements[index]

    def get(self, x, y):
        return self.options[y][x]

    def backup(self):
        self.history.append(deepcopy(self.options))
        return len(self.history)
    
    def restore(self):
        self.options = self.history.pop()
        return len(self.history)

    def add_blacklist(self, x, y, letter):
        self.blacklist[y][x].append(letter)

    def find_frequencies(self, elements):
        frequencies = [{} for element in elements]

        # Convert elements to regular expression:
        regex = ""
        for element in elements:
            regex += "[" + ''.join([letter for letter in element if element[letter]>0]) + "]"
        regex += "$"
        #print(regex)
        r = re.compile(regex, re.UNICODE)

        # Find letter options/counts based on matching words
        for word in list(filter(r.match, self.dictionary)):
            for position, letter in enumerate(word):
                if letter not in frequencies[position]:
                    frequencies[position][letter] = 0
                frequencies[position][letter] += 1
        
        return frequencies

    def update_possibilities(self):
        old_total_options = 0
        for y in range(self.height):
            for x in range(self.width):
                old_total_options += sum(self.options[y][x][letter] for letter in self.options[y][x])
        
        while(True):
            #Remove blacklisted letters:
            for y in range(self.height):
                for x in range(self.width):
                    for letter in self.blacklist[y][x]:
                        self.options[y][x][letter] = 0
                        #print("letter popped: ", x, ", ", y, ": ", letter)
            
            #horizontal words
            for y in range(self.height):
                for x, frequencies in enumerate(self.find_frequencies(self.get_row(y))):
                    for letter in self.options[y][x]:
                        if letter not in frequencies:
                            self.options[y][x][letter] = 0
                        else:
                            self.options[y][x][letter] = min(self.options[y][x][letter], frequencies[letter])

            #vertical words
            for x in range(self.width):
                for y, frequencies in enumerate(self.find_frequencies(self.get_column(x))):
                    for letter in self.options[y][x]:
                        if letter not in frequencies:
                            self.options[y][x][letter] = 0
                        else:
                            self.options[y][x][letter] = min(self.options[y][x][letter], frequencies[letter])

            #Calculate new weight
            new_total_options = 0
            for y in range(self.height):
                for x in range(self.width):
                    new_total_options += sum(self.options[y][x][letter] for letter in self.options[y][x])
            #check if there is a 0 weight
            if self.is_deadend():
                break
            #print(old_weight, new_weight)
            if new_total_options >= old_total_options:
                break
            else:
                old_total_options = new_total_options
        
            
    def shannon_entropy(self, x, y) -> float:
        """Calculates the Shannon Entropy of the wavefunction at given
        coordinates.
        """

        sum_of_weights = 0
        sum_of_weight_log_weights = 0
        for letter in self.options[y][x]:
            weight = self.options[y][x][letter]
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

    def is_defined(self, x, y):
        if len(self.options[y][x]) == 1:
            return True
        return False
    
    def is_deadend(self):
        for y in range(self.height):
            for x in range(self.width):
                if sum(self.options[y][x][letter] for letter in self.options[y][x]) == 0:
                    return True
        return False
    
    def define(self, x, y):
        total_weight = sum(self.options[y][x][letter] for letter in self.options[y][x])
        rnd = random.random() * total_weight

        for letter in self.options[y][x]:
            rnd -= self.options[y][x][letter]
            if rnd < 0:
                self.set(x, y, letter)
                return letter
    
    def is_fully_defined(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_defined(x,y):
                    return False
        return True
    
    def set(self, x, y, letter):
        self.options[y][x] = {letter : 1}

    def print_defined(self):
        out = "   "
        for x in range(self.width):
            out += " " + str(x) + " "
        out += "\n"
        for y in range(self.height):
            out += " " + str(y) + " "
            for x in range(self.width):
                if self.is_defined(x,y):
                    out += " " + list(self.get(x,y).keys())[0] + " "
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
                    if letter in self.options[y][x]:
                        if self.options[y][x][letter] > 0:
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
                    if letter in self.options[y][x]:
                        if self.options[y][x][letter] > 0:
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
                    if letter in self.options[y][x]:
                        if self.options[y][x][letter] > 0:
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
                    if letter in self.options[y][x]:
                        if self.options[y][x][letter] > 0:
                            out += letter
                        else:
                            out += " "
                    else:
                        out += " "
                out += "|"
            out += "\n"

            out += "   |"
            for x in range(self.width):
                for letter in "yz    ":
                    if letter in self.options[y][x]:
                        if self.options[y][x][letter] > 0:
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
    
    
