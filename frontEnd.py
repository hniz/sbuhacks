from __future__ import division

from random import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import threading
import passages
import queue
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech
from googlestreaming import MicrophoneStream
import requests
from PassageReader import match, generatePronun, passageCheck, getWord, initializeStream

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

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
    passage_label = StringProperty()
    input_label = StringProperty()
    def start_reading(self):
        target = self.passage_label
        output = []
        thr = threading.Thread(target=(lambda p, q: q.append(self.startStream())), args=(self, output), kwargs={})
        thr.start()

    def startStream(self):
        def read(responses, passage):
            missed = []
            passage_index = 0
            self.passage_label = str(".\n".join(passage[passage_index:])+".")
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                if result.is_final:
                    print(result.alternatives[0].transcript)
                    print(passageCheck(passage[passage_index], result.alternatives[0].transcript))
                    comp_result = passageCheck(passage[passage_index], result.alternatives[0].transcript)
                    missed += comp_result[0]
                    if not comp_result[1]:
                        passage_index += 1
                    else:
                        passage[passage_index] = " ".join(comp_result[1])
                        generatePronun(comp_result[1][0])
                        missed += comp_result[1][0]
                        print(getWord(comp_result[1][0]))  # call dictionary lookup
                    self.input_label = result.alternatives[0].transcript
                    if passage_index<len(passage):
                        self.passage_label = str(".\n".join(passage[passage_index:]) + ".")
                if passage_index == len(passage):
                    self.passage_label = str("")
                    return missed
        language_code = 'en-US'  # a BCP-47 language tag
        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)

            responses = client.streaming_recognize(streaming_config, requests)
            # Now, put the transcription responses to use.
            finals = read(responses, passages.english)
            return (finals)


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

