import os
import sys
import re
import gram
import random
import select

def make_grammar_list(source_direct):
    grammar_list = []
    namelist=gram.grammar_files(source_direct)
    for name,source in namelist:
        grammar = gram.probabilistic_grammar()
        grammar.read(source)
        grammar_start_token = name
        grammar_list.append((grammar, grammar_start_token))
    return grammar_list

def generate_random_tokens(source_direct):
    that=make_grammar_list(source_direct)
    while True:
        grammar, grammar_start_token = random.choice(that)
        out = grammar.generate(grammar_start_token)
        yield " ".join(out)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("generate_sentences.py <directory to read the gram files from>", file=sys.stderr)
        sys.exit(1)

    source_direct = sys.argv[1]
    z = generate_random_tokens(source_direct)

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
