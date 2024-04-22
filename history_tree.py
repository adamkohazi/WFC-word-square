from anytree import NodeMixin

class Move(object):  # Represents a single move
    def __init__(self, x, y, letter, matrix):
        self.x = x
        self.y = y
        self.letter = letter
        self.wordmatrix = matrix

class MoveNode(Move, NodeMixin):  # Add Node feature
    def __init__(self, x, y, letter, matrix, parent=None, children=None):
        super(MoveNode, self).__init__(x, y, letter, matrix)
        self.parent = parent
        if children:  # set children only if given
            self.children = children

