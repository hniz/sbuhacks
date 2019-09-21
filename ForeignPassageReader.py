from __future__ import division

import re
import sys
import passages
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech
import pyaudio
from six.moves import queue
from googlestreaming import MicrophoneStream
import requests
import json

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
dictapi = {
    'zh':"http://api.mandarincantonese.com/pinyin/"
}
dictapikey={
    'zh':""
}
dictresponse = {
    'zh': ['pinyin']
}


def getWord(word: str, lang: str):
    response = requests.get(dictapi[lang] + word + dictapikey['zh'])
    entry = response.json()
    result = []
    for value in dictresponse[lang]:
        result += [entry[value]]
    return result

def generatePronun(word, lang):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=word)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=lang,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')


def read(responses, passage, lang):
    passage_index = 0
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
            if not comp_result[1]:
                passage_index += 1
            else:
                passage[passage_index] = "".join(comp_result[1])
                generatePronun(comp_result[1][0], lang)
                print(getWord(comp_result[1][0], lang)) #call dictionary lookup
        if passage_index == len(passage):
            break


def match(passagewords, responsewords):
    index = 0
    missed_words = []
    for word in responsewords:
        if index<len(passagewords) and word == passagewords[index]:
            index += 1
        else:
            if word in passagewords[index:]:
                prev_index = index
                index = index+passagewords[index:].index(word)+1
                missed_words += passagewords[prev_index:(index-1)]
    if index != len(passagewords):
        return [missed_words, passagewords[index:]]
    return [missed_words, []]


def passageCheck(passage: str, response: str):
    try:
        passage = passage.lower()
        response = response.lower()
    except:
        pass
    if " " in passage:
        passagewords = passage.split(" ")
        responsewords = response.split(" ")
    else:
        passagewords = passage
        responsewords = response
    return match(passagewords, responsewords)


def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'zh'  # a BCP-47 language tag
    passage = passages.chinese
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
        finals = read(responses, passage)
        #print(passageCheck(passage[passageIndex], finals))


if __name__ == '__main__':
    print(getWord("如", 'zh'))


#print(getWord("english"))