import sys
import gram

USAGE_EXPLANATION = \
    "regenerate_grammar.py <source dir> <target dir>"

if len(sys.argv) != 3:
    print(USAGE_EXPLANATION, file=sys.stderr)
    sys.exit(1)

source_direct = sys.argv[1]
target_direct = sys.argv[2]
print("source:", source_direct)
print("target:", target_direct)

gram.regenerate_grammar(
    source_direct,
    target_direct,
)
