import re
import math
import random
from copy import deepcopy

class Wordmatrix(object):

    @staticmethod
    def list_options (dict):
        options = {}
        for word in dict:
            for letter in word:
                if letter not in options:
                    options[letter] = 1
        return options

    @staticmethod
    def optimize_dictionary (lengths, dict):
        opt_dict = []
        for word in dict:
            if len(word) in lengths:
                if word.isalpha():
                    opt_dict.append(word.lower())
        return opt_dict

    def __init__(self, size, dictionary):
        self.width, self.height = size

        #optimize directory
        self.dictionary = self.optimize_dictionary(size, dictionary)

        options = self.list_options(self.dictionary)

        self.matrix = [[options]*self.width for i in range(self.height)]
        self.blacklist = [[[] for _ in range(self.width)] for _ in range(self.height)]
        self.history = []

        for y in range(self.height):
            for x in range(self.width):
                self.matrix[y][x] = dict(options)
    
        self.update_possibilities()
    
    def get_row(self, row):
        elements = []
        for x in range(self.width):
            elements.append(self.matrix[row][x])
        return elements

    def get_column(self, col):
        elements = []
        for y in range(self.height):
            elements.append(self.matrix[y][col])
        return elements

    def get(self, x, y):
        return self.matrix[y][x]

    @staticmethod
    def elements_to_regex(elements):
        if len(elements)==0:
            print("oh no", elements)
            return
        regex = ""
        for element in elements:
            regex += "["
            for letter in element:
                regex += letter
            regex += "]"
        regex += "$"
        return regex
        

    def find_probabilities(self, regex):
        r = re.compile(regex, re.UNICODE)
        filt = list(filter(r.match, self.dictionary))
        weights = {}
        for word in filt:
            i = 0
            for letter in word:
                if i not in weights:
                    weights[i]={}
                if letter not in weights[i]:
                    weights[i][letter] = 0
                weights[i][letter] += 1
                i += 1
        return weights
    
    def backup(self):
        self.history.append(deepcopy(self.matrix))
        return len(self.history)
    
    def restore(self):
        self.matrix = self.history.pop()
        return len(self.history)

    def add_blacklist(self, x, y, letter):
        self.blacklist[y][x].append(letter)

    def update_possibilities(self):
        horizontal = [[{}]*self.width for i in range(self.height)]
        vertical = [[{}]*self.width for i in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                old_weight = sum(self.matrix[y][x][letter] for letter in self.matrix[y][x])
        while(True):
            #horizontal words
            for y in range(self.height):
                elements = self.get_row(y)
                regex = self.elements_to_regex(elements)
                weights = self.find_probabilities(regex)
                x = 0
                for w in weights:
                    horizontal[y][x] = weights[w]
                    x += 1
            #print("horizontal:\n", horizontal)
            #vertical words
            for x in range(self.width):
                elements = self.get_column(x)
                regex = self.elements_to_regex(elements)
                weights = self.find_probabilities(regex)
                y = 0
                for w in weights:
                    vertical[y][x] = weights[w]
                    y += 1
            #print("vertical:\n", vertical)
            #merge
            for y in range(self.height):
                for x in range(self.width):
                    self.matrix[y][x]={}
                    for letter in horizontal[y][x]:
                        if letter in vertical[y][x]:
                            self.matrix[y][x][letter]=min(horizontal[y][x][letter], vertical[y][x][letter])
            #print("merge:\n", self.matrix)
            #Remove blacklisted letters:
            for y in range(self.height):
                for x in range(self.width):
                    for letter in self.blacklist[y][x]:
                        self.matrix[y][x].pop(letter, None)
                        #print("letter popped: ", x, ", ", y, ": ", letter)

            #Calculate new weight
            for y in range(self.height):
                for x in range(self.width):
                    new_weight = sum(self.matrix[y][x][letter] for letter in self.matrix[y][x])
            #check if there is a 0 weight
            if self.is_deadend():
                break
            #print(old_weight, new_weight)
            if new_weight >= old_weight:
                break
            else:
                old_weight = new_weight
        
            
    def shannon_entropy(self, x, y) -> float:
        """Calculates the Shannon Entropy of the wavefunction at
        `co_ords`.
        """

        sum_of_weights = 0
        sum_of_weight_log_weights = 0
        for letter in self.matrix[y][x]:
            weight = self.matrix[y][x][letter]
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
        if len(self.matrix[y][x]) == 1:
            return True
        return False
    
    def is_deadend(self):
        for y in range(self.height):
            for x in range(self.width):
                if len(self.matrix[y][x]) == 0:
                    return True
        return False

    
    def define(self, x, y):
        total_weight = sum(self.matrix[y][x][letter] for letter in self.matrix[y][x])
        rnd = random.random() * total_weight

        for letter in self.matrix[y][x]:
            rnd -= self.matrix[y][x][letter]
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
        self.matrix[y][x] = {letter : 1}

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
    
    
