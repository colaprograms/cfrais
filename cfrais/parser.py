import os, sys, re
import lark
from lark import Token

def strip(token):
    assert isinstance(token, Token)
    ix = token.type.index("__")
    return token.type[ix+2:]

def stripall(items):
    return " ".join([strip(z) for z in items])

def assertare(token, check):
    value = are(token, check)
    if not value:
        print("error:")
        print("    " + str(token))
        print("    doesn't match")
        print("    " + str(check))
        raise Exception()

class parser:
    def __init__(self, target_direct, fnam="__main.lark"):
        self.pars = lark.Lark(
            open(os.path.join(target_direct, fnam)).read(),
            import_paths = [target_direct],
        )
        self.form = tupler()

    def parse(self, z):
        try:
            return self.pars.parse(z.strip().upper() + " ")
        except lark.UnexpectedInput:
            return None

    def transform(self, z):
        z = self.parse(z)
        z = self.form.transform(z) if z is not None else z
        return z

from lark.visitors import Transformer
class tupler(Transformer):
    def start(self, args):
        return args
    def __default__(self, data, children, meta):
        return (data, children)
    def __default_token__(self, token):
        # in gram.py we replace all the apostrophes
        # with underscores, so here we put them back
        token = strip(token)
        token = token.replace("_", "'")
        return token

if __name__ == "__main__":
    print("Input sentences to parse.")

    it = parser("../context_free_grammar.generated")

    while True:
        try:
            line = input("? ").strip()
        except EOFError:
            break
        if line == "":
            break

        print("parsing:")
        utterance = it.parse(line)
        if utterance:
            print(utterance.pretty())
        else:
            print("Couldn't parse!")

        print("transforming:")
        import json
        print(json.dumps(tupler().transform(utterance)))
        print()
