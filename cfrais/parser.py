import os, sys, re
import lark
from lark import Token

PATH_TO_LARKS = [
    "context_free_grammar",
    "../context_free_grammar",
]

def strip(token):
    assert isinstance(token, Token)
    ix = token.type.index("__")
    return token.type[ix+2:]

def stripall(items):
    return " ".join([strip(z) for z in items])

def isa(token, check):
    def validate(string, check):
        ix = string.find("__")
        return (string[ix+2:] if ix >= 0 else string) == check

    if isinstance(check, type):
        return isinstance(token, check)
    elif isinstance(check, str):
        if isinstance(token, Token):
            # if the token in the gram file has apostrophes,
            # they will be replaced by underscores. so if we
            # want to match the token THEY'LL in the gram file,
            # we have to compare the type to THEY_LL.
            check = check.replace("'", "_")
            return validate(token.type, check)
        if isinstance(token, lark.Tree):
            return validate(token.data, check)
        return False
    else:
        raise Exception("check should be a type or string")
    raise Exception("should have returned already")

def are(token, check):
    if len(token) != len(check):
        return False
    return all(isa(a, b) for (a, b) in zip(token, check))

def assertare(token, check):
    value = are(token, check)
    if not value:
        print("error:")
        print("    " + str(token))
        print("    doesn't match")
        print("    " + str(check))
        raise Exception()

def explanation():
    print("You have to write cfg_parser.py yourself, to parse")
    print("your generated grammar.")

def path(fnam):
    for option in PATH_TO_LARKS:
        j = os.path.join(option, fnam)
        if os.path.exists(j):
            return option
    
class parser:
    def __init__(self, transformer, fnam="main.lark"):
        pathtolarks = path(fnam)
        grammar = open(os.path.join(pathtolarks,fnam)).read()
        self.pars = lark.Lark(grammar, import_paths=[pathtolarks])
        self.form = transformer

    def parse(self, z):
        try:
            return self.pars.parse(z.strip().upper() + " ")
        except lark.UnexpectedInput:
            return None

    def transform(self, z):
        z = self.parse(z)
        z = self.form.transform(z) if z is not None else z
        return z

def run_a_simple_parser(transformer):
    print("Input sentences to parse.")

    p = parser(transformer)

    while True:
        try:
            line = input("? ").strip()
        except EOFError:
            break
        if line == "":
            break
        print("parsing:")
        pp = p.parse(line)
        if pp:
            print(pp.pretty())
        print()
        print("transforming:")
        pp = p.transform(line)
        print(pp)
        print()
