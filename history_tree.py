from anytree import NodeMixin, RenderTree

class Move(object):  # Represents a single move
    deadEnd = False
    def __init__(self, x, y, letter):
        self.x = x
        self.y = y
        self.letter = letter

class MoveNode(Move, NodeMixin):  # Add Node feature
    def __init__(self, x, y, letter, parent=None, children=None):
        super(MoveNode, self).__init__(x, y, letter)
        #super(Move, self).__init__(x, y, letter)
        self.parent = parent
        if children:  # set children only if given
            self.children = children

