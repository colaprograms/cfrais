import os
import sys
import re
import gram
import random
import select

def make_grammar_list():
    grammar_list = []
    grammar_files = gram.grammars()
    for what in grammar_files:
        grammar = gram.probabilistic_grammar()
        grammar.read(what + ".gram")
        grammar_start_token = os.path.basename(what)
        grammar_list.append((grammar, grammar_start_token))
    return grammar_list

def generate_random_tokens():
    that = make_grammar_list()
    while True:
        grammar, grammar_start_token = random.choice(that)
        out = grammar.generate(grammar_start_token)
        yield " ".join(out)

if __name__ == "__main__":
    z = generate_random_tokens()

    count = 0
    while True:
        out = next(z)
        try:
            print(out)
        except BrokenPipeError:
            sys.stderr.write("\n")
            sys.stderr.flush()
            break
        count += 1
        if count % 100000 == 0:
            sys.stderr.write("%d" % ((count//100000)%10))
            sys.stderr.flush()
