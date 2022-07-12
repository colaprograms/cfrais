This program reads an audio stream from a microphone and tries
to interpret anything it hears as a phrase in a context-free
language with English words.

To set it up:
```
    python3 -m venv --system-site-packages --symlinks env
    . env/bin/activate
    pip install -r requirements.txt
```

To run:
```
    . env/bin/activate
    python run_cfrais.py
```

For now you have to change the DEFAULT_SAMPLE_RATE and
DEFAULT_DEVICE in cfrais/stream/stream.py to match your microphone.You can figure those out with list_audio_input_devices.
Put the device number for DEFAULT_DEVICE, and your favourite
sample rate for DEFAULT_SAMPLE_RATE. The native sample rate
of the VAD and model are 16000, so if the sample rate isn't
16000 then it will resample using libsamplerate.

*Note:* I ripped it out of my larger system that works ok,
but I refactored it a lot and I'm not sure what is broken.

To change the language, you have to change the rules in
    context_free_grammar/*.gram
and then rerun generate_language_model.
