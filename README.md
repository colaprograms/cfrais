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
*This only works on Raspberry Pi!* To get it to work on anything else, you'd have to replace the binaries in cfrais/generator with the appropriate ones from DeepSpeech (https://github.com/mozilla/DeepSpeech)

*Note:*
Change the RATE and DEVICE at the top of cfrais/chat.py to
match your microphone. If you don't know them, you can figure
them out with list_audio_input_devices.

The native sample rate
of the VAD and model are 16000, so if the sample rate isn't
16000 then it will resample using libsamplerate.
