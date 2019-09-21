from random import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Ellipse
from kivy.uix.boxlayout import BoxLayout

class Painter(Widget):
    def on_touch_down(self, touch):
        color = (random(), 1.,1.) #reduce number of possible colors
        with self.canvas:
            Color(*color, mode='hsv') #sets the colors to be equally bright
            d = 30.
            Ellipse(pos=(touch.x - d / 2,touch.y - d / 2), size=(d,d))
            touch.ud["line"] = Line(points=(touch.x, touch.y))


def on_touch_move(self, touch):
    touch.ud["line"].points += [touch.x, touch.y]

class MainScreen(Screen):
    pass

class EnglishScreen(Screen):
    pass

class ChineseScreen(Screen): 
    pass

class JapaneseScreen(Screen):
    pass




class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file("floating.kv") #load the kivy file

class SimpleKivy7(App):
    def build(self):
        return presentation

if __name__== "__main__":
    SimpleKivy7().run()

