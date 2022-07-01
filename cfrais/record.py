import wave
import cfg_parser
import os
import time
import dateparser
import random
import subprocess
import datetime

WAVE_DIR = "recording"

WAIT_TIME = 120

def write_wav(wave_data, filename):
    wf = wave.open(filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(wave_data)
    wf.close()

def say(z):
    subprocess.run(["/home/pi/chat/tts", z])


def play(zz):
        subprocess.run([
            "/usr/bin/mplayer",
            zz,
            "-af",
            "volume=-10",
            "-quiet",
            "-quiet"
        ])

class record:
    def __init__(self, stopcallback):
        self.stopcallback = stopcallback
        self.stopped = False
        self.make_recording_directory()
        self.count = 0
        self.start_time = time.time()
        say("Recording.")

    def stop(self):
        self.stopped = True
        self.stopcallback()

    def cancel(self):
        for f in os.listdir(self.recording_directory):
            fn = self.recording_directory + "/" + f
            os.unlink(fn)
        os.rmdir(self.recording_directory)
        say("Recording cancelled.")
        self.stopped = True
        self.stopcallback()

    def make_recording_directory(self):
        def trymkdir(z, j=None):
            if j is not None:
                j = "-%d" % j
            else:
                j = ""
            dirname = WAVE_DIR + "/" + z + j
            try:
                os.mkdir(dirname)
            except FileExistsError:
                return None
            return dirname
        timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
        dirname = trymkdir(timestamp)
        j = 1
        while dirname is None:
            dirname = trymkdir(timestamp, j)
            j += 1
            if j >= 10:
                raise Exception("couldn't make directory for voice record")
        self.recording_directory = dirname

    def heard(self, wave_data, text, processed_text):
        if self.stopped is True:
            raise Exception("stopped record was called")

        if cfg_parser.is_cancel_recording(processed_text):
            self.cancel()
            return

        stop = False
        quiet = False

        if self.count == 0:
            quiet = True
        if self.count > 9:
            stop = True

        if cfg_parser.is_end_recording(processed_text):
            stop = True


        if stop:
            self.stop()
            play("cfrais/data/endrecord.wav")

        if not quiet:
            write_wav(
                wave_data,
                "%s/record-%03d.wav" % (
                    self.recording_directory,
                    self.count
                )
            )
        self.count += 1

    def idle(self):
        if time.time() > self.start_time + WAIT_TIME:
            self.stop()
