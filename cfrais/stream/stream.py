#!/home/pi/chat/env/bin/python

from .voice_detect_stream import VADAudio

DEFAULT_AGGRESSIVENESS = 3
DEFAULT_RATE = 16000
DEFAULT_DEVICE = 1
DEFAULTS = {
    'aggressiveness': DEFAULT_AGGRESSIVENESS,
    'input_rate': DEFAULT_RATE,
    'device': DEFAULT_DEVICE
}

import time
from datetime import datetime
import threading, collections, queue, os, os.path, sys
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad

class stream:
    def __init__(self,
        models,
        scorer,
        parser,
        process,
        **params,
    ):
        self.models = models
        self.scorer = scorer
        self.parser = parser
        self.process = process

        self.params = DEFAULTS.copy()
        self.params.update(params)
        self._pro = None

        self.ignore = "pay attention"
        self.ignore_until = 0

    def get_processor(self, processor_generator):
        def ignore(what):
            if what == "ongoing":
                self.ignore = "ongoing"
            elif what == "untilpause":
                self.ignore = "until"
                self.ignore_until = self.vad.stream.get_time()

        return processor_generator(ignore)

    def start(self):
        self.model = deepspeech.Model(self.models)
        self.model.enableExternalScorer(self.scorer)
        self.vad = VADAudio(**self.params)

        wav_data = bytearray()

        parser = self.parser
        neural_speech_processor = self.model.createStream()

        statement_processor = self.get_processor(self.process)

        frames = self.vad.vad_collector(1000, 0.3)

        for framewithtime in frames:
            frame, t = framewithtime

            statement_processor.idle()

            if self.ignore != "pay attention":
                if self.ignore == "until":
                    if self.ignore_until < t:
                        self.ignore = "pay attention"

            if frame is "idle":
                continue

            if self.ignore != "pay attention":
                continue

            if frame is not None:
                neural_speech_processor.feedAudioContent(
                    np.frombuffer(frame, np.int16)
                )

                wav_data.extend(frame)
            else:
                text = neural_speech_processor.finishStream()

                print(text, file=sys.stderr)

                data = None

                try:
                    data = parser.transform(text)
                except:
                    from traceback import print_exc
                    print_exc()
                    pass

                if data is not None:
                    #print("    " + str(data))
                    statement_processor.do(data)

                if statement_processor.voicerecorder:
                    statement_processor.voicerecorder.heard(
                        wav_data,
                        text,
                        data
                    )

                neural_speech_processor = self.model.createStream()
                wav_data = bytearray()
