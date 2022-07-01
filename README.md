This program reads an audio stream from a microphone and tries
to interpret anything it hears as a phrase in a context-free
language with English words.

*Note:* I ripped it out of my larger system that works ok,
but I refactored it a lot and I'm not sure what is broken.

To change the language, you have to change the rules in
    context_free_grammar/*.gram
and change the lark.Transformer in
    cfg_parser.py
and you also have to add another statement to main.lark.

Then you have to add stuff to interpret your new objects
in chat.py. This is pretty annoying but that's how it is for now.
