from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import NumericProperty


class Cell(ToggleButtonBehavior, FloatLayout):
    """
    Class representing a single crossword cell.
    """

    def __init__(self, x, y, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.pos_x = x
        self.pos_y = y

        self.defined = False
        self.masked = False
        self.options = ''
        self.entropy = 1.0

    def fillBackground(self, color):
        with self.canvas.before:
            Color(*color)
            Rectangle(size=[self.size[0]-2, self.size[1]-2], pos=self.pos)
    
    def setBackground(self):
        if self.defined:
            if self.masked:
                if self.main_letter.text == '-':
                    self.fillBackground((0,0,0,1))
                else:
                    self.fillBackground((1, 1, 0.5, 1))
            else:
                self.fillBackground((1, 1, 1, 1))
        else:
            if self.entropy > 0:
                saturation = 1.0 - 0.5*max(0.0, min(1.0 / self.entropy, 1.0))
                self.fillBackground((1, saturation, saturation, 1))
            else:
                self.fillBackground((1, 0, 0, 1))

    def update(self, defined, masked, options, entropy):
        self.defined = defined
        self.masked = masked
        self.options = options
        self.entropy = entropy

        if defined:
            defined_letter = next(iter(options))
            self.main_letter.text = defined_letter.upper()
            self.letter_options.text = ''
        else:
            self.main_letter.text = ''
            self.letter_options.text = ''.join(options.keys())
        
        self.setBackground()

    def change_state(self):
        print("asd")
        if self.state == "down":
            # Red frame white fill to indicate active cell
            with self.canvas.before:
                Color(1, 0, 0, 1)
                Rectangle(size=[self.size[0]-2, self.size[1]-2], pos=self.pos)
                Color(1, 1, 1, 1)
                Rectangle(size=[self.size[0]-10, self.size[1]-10], pos=[self.pos[0]+4, self.pos[1]+4])
        else:
            self.setBackground()