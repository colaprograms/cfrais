import sys, re, random

DIRECTORY_WITH_GRAMMAR_INSIDE = "../../context_free_grammar"

class probabilistic_grammar:
    def __init__(self):
        self.rule = {}

    def preprocess(self, zz):
        zz = zz.strip()
        commentix = zz.find("#")
        if commentix != -1:
            zz = zz[:commentix]
        zz = zz.strip()
        return re.split(r'\s+', zz)

    def read(self, fn):
        f = open(fn, "r")
        while True:
            line = f.readline()
            if line == "":
                # end of file
                return
            words = self.preprocess(line)
            if len(words) == 1 and words[0] == "":
                continue

            name = words.pop(0)
            if ":" in name:
                raise Exception("don't put colons in the names for .gram")
            out = words
            the = re.match(r'([^*]+)(\*\d+)?', name)
            if the is None:
                print("parse error: didn't know what to do with", name)
                raise Exception("parse error")
            name, add = the.groups()
            weight = 1
            if add is not None:
                assert add[0] == "*"
                add = add[1:]
                weight = int(add)
            if len(out) == 1 and out[0] == "{":
                # scigen-style brackets
                out = []
                while True:
                    line = f.readline()
                    if line == "":
                        # end of file, but we're in brackets
                        print("parse error: hit end of file while reading %s" % name)
                        raise Exception("parse error")
                    curwords = self.preprocess(line)
                    if len(curwords) == 1 and curwords[0] == "}":
                        # brackets done
                        break
                    out.extend(curwords)
            self.add_rule(name, weight, out)

    def add_rule(self, name, weight, out):
        self.rule.setdefault(name, [])
        self.rule[name].append({
            'weight': weight,
            'out': out
        })

    def _print(self):
        for name in self.rule.keys():
            print(name)
            for what in self.rule[name]:
                print("    %4d: %s" % (what['weight'], " ".join(what['out'])))
    
    def writelark(self, fo):
        literals = {}
        def addliteral(tex):
            literals[tex] = tex.replace("'", "_")
            return literals[tex]

        for name in self.rule.keys():
            first = True
            for what in self.rule[name]:
                def format(zz):
                    if zz == zz.lower():
                        return zz
                    elif zz == zz.upper():
                        return addliteral(zz)
                    else:
                        raise Exception("error: the symbol %s is neither lowercase nor uppercase" % zz)
                rule = " ".join(format(j) for j in what['out'])
                if first:
                    fo.write("%s: %s\n" % (name, rule))
                    first = False
                    # rar
                else:
                    fo.write("    | %s\n" % rule)

        # rar
        for z in literals:
            the = literals[z]
            fo.write("%s: \"%s \"\n" % (the, z))

    def generate(self, z):
        if z == z.upper():
            return [z]
        if z not in self.rule:
            raise Exception("No rule for %s" % z)
        totalweight = sum(what['weight'] for what in self.rule[z])
        if totalweight == 0:
            raise Exception("error: the symbol %s has total weight 0" % z)
        gene = None
        choice = random.randint(1, totalweight)
        for what in self.rule[z]:
            choice -= what['weight']
            if choice <= 0:
                gene = what['out']
                break
        if gene is None:
            raise Exception("error: random choice failed")
        result = []
        for what in gene:
            result.extend(self.generate(what))
        return result

def remove_suffix(a, b):
    assert a.endswith(b)
    return a[:-len(b)]

def grammars():
    import glob
    return [remove_suffix(fnam, ".gram") for fnam in
            glob.glob(DIRECTORY_WITH_GRAMMAR_INSIDE + "/*.gram")]

def test():
    p = probabilistic_grammar()
    p.read("test.gram")
    p.writelark(sys.stdout)

def regenerate_grammar():
    for fnam in grammars():
        print("making %s.lark from %s.gram" % (fnam, fnam))
        p = probabilistic_grammar()
        p.read(fnam + ".gram")
        fo = open(fnam + ".lark", "w")
        fo.truncate(0)
        p.writelark(fo)
        fo.close()
