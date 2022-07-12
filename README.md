This program reads an audio stream from a microphone and tries
to interpret anything it hears as a phrase in a context-free
language with English words.

To set it up:```
    python3 -m venv --system-site-packages --symlinks env
    . env/bin/activate
    pip install -r requirements.txt
```

To run:```
    . env/bin/activate
    python run_cfrais.py
```

*Note:* I ripped it out of my larger system that works ok,
but I refactored it a lot and I'm not sure what is broken.

To change the language, you have to change the rules in
    context_free_grammar/*.gram
and then rerun generate_language_model.
