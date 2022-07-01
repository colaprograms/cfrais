#!/home/pi/chat/env/bin/python

import cfg_parser
from . import record
from . import parser
from .stream import stream

AGGRESSIVENESS = 3
RATE = 16000

# the code below mostly comes from DeepSpeech-examples/mic_vad_streaming

import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad

class that_speech_processor:
    def __init__(self, ignore_callback_function):
        self.voicerecorder = None
        self.ignore_callback_function = ignore_callback_function

    def do(self, what):
        if self.voicerecorder:
            # we are recording a reminder
            # don't do anything for now
            return

        if isinstance(what, cfg_parser.RunProgram):
            program = what.name.lower().replace(" ", "-")
            program += ".run"
            try:
                print("running exec/%s" % program)
                self.run_a_program(["exec/" + program])
            except:
                pass

        if isinstance(what, cfg_parser.RecordRequest):
            def stop():
                self.stop()

            self.ignore_indefinitely()
            self.voicerecorder = record.record(what, stop)
            self.ignore_untilpause()

    def run_a_program(self, cmd):
        subprocess.Popen(cmd, close_fds=True)


    def ignore_indefinitely(self):
        self.ignore_callback_function("ongoing")


    def ignore_untilpause(self):
        self.ignore_callback_function("untilpause")


    def idle(self):
        if self.voicerecorder:
            self.voicerecorder.idle()

    def stop(self):
        if not self.voicerecorder:
            raise Exception("tried to stop the voice recording but it was already stopped")
        self.voicerecorder = None

def run_chat(transformer):
    for i in range(4):
        try:
            stream(
                'models/deepspeech-0.9.3-models.tflite',
                'models/listen.scorer',
                parser.parser(transformer),
                that_speech_processor,
            ).start()
                
        except OSError:
            import traceback
            traceback.print_exc()
            print("attempt %d: waiting 20 seconds and trying again" % i)
            time.sleep(20.0)
