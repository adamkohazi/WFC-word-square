from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock

class IntegerUpDown(StackLayout):
    current_value = BoundedNumericProperty(1, min=1, max=100)
    min = NumericProperty(1)
    max = NumericProperty(20)

    def __init__(self, **kwargs):
        super(IntegerUpDown, self).__init__(**kwargs)
        self.property('current_value').__init__(int(self.min + (self.max-self.min)/2.0),
                                                min = self.min,
                                                max = self.max,
                                                errorhandler = lambda x: self.max if x > self.max else self.min)

        #Schedule binding, as widget is not yet fully loaded
        Clock.schedule_once(self.override_insert_text)
    
    def override_insert_text(self, *args):
        # Send help: I have no idea what is happening here, but it seems to work
        self.ids["value_text"].insert_text = self.insert_text
    
    def insert_text(self, string, from_undo=False):
        try:
            self.current_value = int(self.ids["value_text"].text + string)
        except:
            pass
    
    def increment(self, amount=1):
        self.current_value += amount
    
    def decrement(self, amount=1):
        self.current_value -= amount

#https://kivy.org/doc/stable/guide/events.html