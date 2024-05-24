from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import NumericProperty


class Cell(ToggleButtonBehavior, FloatLayout):
    """
    Class representing a single crossword cell.
    """
    pos_x = NumericProperty(None)
    pos_y = NumericProperty(None)

    def __init__(self, **kwargs):
        super(Cell, self).__init__(**kwargs)

    def update(self, defined, masked, options, entropy):
        if defined:
            defined_letter = next(iter(options))
            self.main_letter.text = defined_letter
            if masked:
                if defined_letter == '-':
                    #self.fill_color.rgba = 0,0,0,1
                    pass
                else:
                    #self.fill_color.rgba = 1,1,0.5,1
                    pass
                
            else:
                #self.fill_color.rgba = 1,1,1,1
                pass
        else:
            self.main_letter.text = ''
            #self.fill_color.rgba = 1, 1.0/entropy, 1.0/entropy, 1

    