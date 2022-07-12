#!/home/pi/chat/env/bin/python

# the code below mostly comes from DeepSpeech-examples/mic_vad_streaming

import pyaudio
import wave
import sys
import os
import queue
from collections import deque
import numpy as np
import webrtcvad
import samplerate

def quietly_start_pyaudio():
    "Redirect stderr to nothing, start pyaudio, and then put old stderr back."
    devnull = os.open(os.devnull, os.O_WRONLY)

    STDERR_FILENO = sys.stderr.fileno()
    saved_stderr = os.dup(STDERR_FILENO)
    sys.stderr.flush()
    os.dup2(devnull, STDERR_FILENO)
    os.close(devnull)

    pa = pyaudio.PyAudio()

    os.dup2(saved_stderr, STDERR_FILENO)
    os.close(saved_stderr)

    return pa

class Audio(object):
    FORMAT = pyaudio.paInt16
    # Network/VAD rate-space
    RATE_PROCESS = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50

    def __init__(self, callback=None, device=None, input_rate=RATE_PROCESS, file=None):
        def proxy_callback(in_data, frame_count, time_info, status):
            self.buffer_queue.put((in_data,
                time_info['current_time']))
            return (None, pyaudio.paContinue)
        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(self.BLOCKS_PER_SECOND))
        self.block_size_input = int(self.input_rate / float(self.BLOCKS_PER_SECOND))
        self.pa = "get fed up with the errors" and quietly_start_pyaudio()

        kwargs = {
            'format': self.FORMAT,
            'channels': self.CHANNELS,
            'rate': self.input_rate,
            'input': True,
            'frames_per_buffer': self.block_size_input,
            'stream_callback': proxy_callback,
        }

        if self.device:
            kwargs['input_device_index'] = self.device
        self.resampler = None
        self.leftover = b""
        self.lefttime = None
        self.stream = self.pa.open(**kwargs)
        self.stream.start_stream()

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def resample(self, data):
        if not self.resampler:
            self.resampler = samplerate.converters.Resampler('sinc_best', 1)
        data16 = np.fromstring(data, dtype=np.int16)
        resample_size = 320 # required by vad
        ratio = resample_size/data16.shape[0]
        resample = self.resampler.process(data16, ratio, end_of_input=False)
        resample16 = np.array(resample, dtype=np.int16)
        outdata = resample16.tostring()
        return outdata

    def read_resampled_raw(self):
        that, time_i_was_reincarnated_as_a_slime = self.buffer_queue.get()
        return self.resample(that), time_i_was_reincarnated_as_a_slime

    def read_resampled(self):
        """This function has to return exactly 640 bytes of audio data
        (320 samples int16) because VAD wants exactly that amount."""
        # Get the leftover audio data from last time
        data = self.leftover
        # and the time corresponding to its start.
        starttime = self.lefttime

        while len(data) < 640:
            that, time = self.read_resampled_raw()
            if len(data) == 0:
                # If we didn't have any stored audio data, then the start
                # of our stored data is the time we just read.
                starttime = time

            leftover_time_reference = time
            time_per_character = 2/self.sample_rate
            time_reference_offset = len(data)
            data += that

        # Return exactly 640 bytes, saving all the leftovers
        self.leftover = data[640:]
        # Guess the time of the first leftover byte
        lefttime = leftover_time_reference
        lefttime += (640 - time_reference_offset) * time_per_character
        self.lefttime = lefttime
        # Here you go, exactly 640 bytes!!
        return (data[:640], starttime)

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(lambda self: 1000 * self.block_size // self.sample_rate)

    def write_wav(self, filename, data):
        logging.info("write wav %s", filename)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert self.FORMAT == pyaudio.paInt16
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()


class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness=3, device=None, input_rate=None, file=None):
        super().__init__(device=device, input_rate=input_rate, file=file)
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        if frames is None: frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = deque(maxlen=num_padding_frames)
        triggered = False

        for framewithtime in frames:
            frame, t = framewithtime
            if len(frame) < 640:
                return

            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((framewithtime, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()
                else:
                    yield "idle", t

            else:
                yield framewithtime
                ring_buffer.append((framewithtime, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None, t
                    ring_buffer.clear()
