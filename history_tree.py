from anytree import NodeMixin

class Move(object):  # Represents a single move
    def __init__(self, x, y, letter, crossword):
        self.x = x
        self.y = y
        self.letter = letter
        self.crossword = crossword

class MoveNode(Move, NodeMixin):  # Add Node feature
    def __init__(self, x, y, letter, crossword, parent=None, children=None):
        super(MoveNode, self).__init__(x, y, letter, crossword)
        self.parent = parent
        if children:  # set children only if given
            self.children = children

