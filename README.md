This program reads an audio stream from a microphone and tries
to interpret anything it hears as a phrase in a context-free
language with English words.

It's based on Mozilla Deepspeech: https://github.com/mozilla/DeepSpeech

To set it up:
```
    python3 -m venv --system-site-packages --symlinks env
    . env/bin/activate
    pip install -r requirements.txt
```

To run:
```
    ./startup
```

To change the context-free language it detects:
```
    cd context_free_grammar
    (edit the rules in *.gram, possibly adding more files)
    cd .. 
    ./generate_language_model
```
This last thing uses binaries that were compiled for Raspberry Pi, so if you want to run the generator on anything else, you'd have to compile new binaries and put them in cfrais/generator and cfrais/generator/bins.
See https://deepspeech.readthedocs.io/en/v0.9.3/Scorer.html

Change the RATE and DEVICE at the top of cfrais/chat.py to
match your microphone. If you don't know them, you can figure
them out with list_audio_input_devices.

The native sample rate
of the VAD and model are 16000, so if the sample rate isn't
16000 then it will resample using libsamplerate.
