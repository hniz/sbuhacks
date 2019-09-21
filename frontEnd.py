from __future__ import division
import sys
sys.path.insert(1, "sbuhacks-2/myprosody-master")
from myprosody import mysptotal
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
import random
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech
from googlestreaming import MicrophoneStream
import requests
from PassageReader import match, generatePronun, passageCheck, getWord, initializeStream
from ForeignPassageReader import generatePronun as fgeneratePronun, passageCheck as fpassageCheck, getWord as fgetWord

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
    help_label = StringProperty()
    streamthread = threading.Thread
    def startReading(self):
        output = []
        self.streamthread = threading.Thread(target=(lambda p, q: q.append(self.startStream())), args=(self, output), kwargs={})
        self.streamthread.start()
        self.ids.return_home.disabled = True
        self.ids.return_home.background_color = (0, 1, 1, 1)
        thr = threading.Thread(target=self.streamListener)
        thr.start()


    def streamListener(self):
        self.streamthread.join()
        print("yay")
        self.ids.return_home.disabled = False
        self.ids.summary_button.disabled = False
        self.ids.return_home.background_color = (0, 1, 1, 0.5)
        self.ids.summary_button.background_color = (1, 0, 0, 0.4)


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
                        self.help_label = str("Tip: "+ " ".join(getWord(comp_result[1][0]))) # call dictionary lookup
                    self.input_label = result.alternatives[0].transcript
                    if passage_index<len(passage):
                        self.passage_label = str(".\n".join(passage[passage_index:]) + ".")
                if passage_index == len(passage):
                    self.passage_label = str("")
                    print("woo")
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
            App.get_running_app().missed_keys = finals
            print("yippee")
            return finals


class ChineseScreen(Screen):
    passage_label1 = StringProperty()
    help_label = StringProperty()
    input_label = StringProperty()
    streamthread = threading.Thread
    def startReading(self):
        output = []
        self.streamthread = threading.Thread(target=(lambda p, q: q.append(self.startStream())), args=(self, output),
                                             kwargs={})
        self.ids.return_home.disabled = True
        self.ids.return_home.background_color = (0, 1, 1, 0.5)
        self.streamthread.start()
        thr = threading.Thread(target=self.streamListener)
        thr.start()

    def streamListener(self):
        self.streamthread.join()
        self.ids.summary_button.disabled = False
        self.ids.return_home.disabled = False
        self.ids.return_home.background_color = (0, 1, 1, 1)
        self.ids.summary_button.background_color = (1, 0, 0, 0.4)

    def startStream(self):
        def read(responses, passage, lang):
            missed = []
            passage_index = 0
            transcript_index = 0
            self.passage_label1 = str(".\n".join(passage[passage_index:])+".")
            print(self.passage_label)
            for response in responses:
                # print(response.results[0])
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                if result.stability >= 0.80:
                    print(result.alternatives[0].transcript[transcript_index:])
                    transcript = result.alternatives[0].transcript
                    print(transcript_index)
                    print(passageCheck(passage[passage_index], transcript[transcript_index:]))
                    comp_result = passageCheck(passage[passage_index], transcript[transcript_index:])
                    if not comp_result[1]:
                        passage_index += 1
                    else:
                        passage[passage_index] = "".join(comp_result[1])
                        fgeneratePronun(comp_result[1][0], lang)
                        self.help_label = str("Tip: "+ " ".join(fgetWord(comp_result[1][0], lang))) # call dictionary lookup # call dictionary lookup
                    self.input_label = result.alternatives[0].transcript[transcript_index:]
                    transcript_index = len(transcript)
                    if passage_index<len(passage):
                        self.passage_label1 = str(".\n".join(passage[passage_index:]) + ".")
                if passage_index == len(passage):
                    self.passage_label1 = str("")
                    return missed
        language_code = 'zh'  # a BCP-47 language tag 'zh' 'ja-JP'
        passage = passages.chinese
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
            finals = read(responses, passage, 'zh')
            App.get_running_app().missed_keys = finals
            return finals

class JapaneseScreen(Screen):
    passage_label = StringProperty()
    help_label = StringProperty()
    input_label = StringProperty()
    streamthread = threading.Thread

    def startReading(self):
        target = self.passage_label
        output = []
        self.streamthread = threading.Thread(target=(lambda p, q: q.append(self.startStream())), args=(self, output),
                                             kwargs={})
        self.ids.return_home.disabled = True
        self.ids.return_home.background_color = (0,1,1,0.5)
        self.streamthread.start()
        thr = threading.Thread(target=self.streamListener)
        thr.start()

    def streamListener(self):
        self.streamthread.join()
        self.ids.return_home.disabled = False
        self.ids.summary_button.disabled = False
        self.ids.return_home.background_color = (0, 1, 1, 1)
        self.ids.summary_button.background_color = (1,0,0,0.4)



    def startStream(self):
        def read(responses, passage, lang):
            missed = []
            passage_index = 0
            transcript_index = 0
            self.passage_label = str(".\n".join(passage[passage_index:]) + ".")
            for response in responses:
                # print(response.results[0])
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                if result.stability >= 0.80:
                    print(result.alternatives[0].transcript[transcript_index:])
                    transcript = result.alternatives[0].transcript
                    print(transcript_index)
                    print(passageCheck(passage[passage_index], transcript[transcript_index:]))
                    comp_result = passageCheck(passage[passage_index], transcript[transcript_index:])
                    if not comp_result[1]:
                        passage_index += 1
                    else:
                        passage[passage_index] = "".join(comp_result[1])
                        fgeneratePronun(comp_result[1][0], lang)
                        self.help_label = str("Tip: " + " ".join(
                            fgetWord(comp_result[1][0], lang)))  # call dictionary lookup # call dictionary lookup
                    self.input_label = result.alternatives[0].transcript[transcript_index:]
                    transcript_index = len(transcript)
                    if passage_index < len(passage):
                        self.passage_label = str(".\n".join(passage[passage_index:]) + ".")
                if passage_index == len(passage):
                    self.passage_label = str("")
                    return missed

        language_code = 'ja-JP'  # a BCP-47 language tag 'zh' 'ja-JP'
        passage = passages.japanese
        passageIndex = 0
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
            finals = read(responses, passage, 'ja')
            App.get_running_app().missed_keys = finals
            return finals

class SummaryScreen(Screen):
    def build(self):
        s = "Missed words: " + ", ".join(App.get_running_app().missed_keys)
        self.ids.label2.text = str(s)
        values = mysptotal("user_input", "sbuhacks-2/myprosody-master/myprosody")
        labels = ["Number of syllables: ","Number of pauses: ", "Average rate of speech: ",
         "Articulation rate: ", "Speaking duration: ","Original duration: ","Average balance: ",
         "Average Frequency: "]
        s = ""
        for x in range(len(labels)):
            s += labels[x] + values[0][x] + "\n"
        self.ids.label1.text = str(s)
        averages = [13,1,0.65,2,17,30,0.55]
        num = random.randint(0,len(averages)-1)
        if float(values[0][num]) > averages[num]:
            self.ids.label3.text = str("Your "+labels[num][:-2]+ " is higher than the average of "+str(averages[num])+".")
        else:
            self.ids.label3.text = str("Your "+labels[num][:-2]+ " is lower than the average of "+str(averages[num])+".")




class ScreenManagement(ScreenManager):
    pass

with open("floating.kv", encoding="utf-8") as f:
    presentation = Builder.load_string(f.read()) #load the kivy file

class SimpleKivy7(App):
    missed_keys = []
    def build(self):
        return presentation

if __name__== "__main__":
    SimpleKivy7().run()

