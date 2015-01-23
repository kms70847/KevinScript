# converts a string into an array of rules.
# example input:
"""\
S -> Expression
Expression -> Expression * Binary
Expression -> Expression + Binary
Expression -> Binary
Binary -> 0
Binary -> 1"""


from primitives import *


def parse_rules(rule_text):
    ret = []
    lines = rule_text.split("\n")
    # remove comments and trailing whitespace
    lines = [line.partition("#")[0].strip() for line in lines]
    # filter out empty lines
    lines = [line for line in lines if len(line) > 1]
    # expand lines of the form "A -> B | C" into two lines, "A -> B" and "A -> C"
    expanded_lines = []
    for line in lines:
        if "|" in line:
            LHS, RHSs = line.split("->")
            for RHS in RHSs.split("|"):
                RHS = RHS.strip()
                expanded_lines.append(LHS + "->" + RHS)
        else:
            expanded_lines.append(line)
    lines = expanded_lines

    non_terminal_symbols = set(map(lambda x: x.split("->")[0].strip(), lines))
    if "_" not in non_terminal_symbols:
        print "Warning, expected starting Symbol _"
    for line in lines:
        line = line.split("->")
        LHS = NonTerminal(line[0].strip())
        RHS = []
        for token in line[1].split():
            if token == "%SPACE%":
                token = " "
            if token in non_terminal_symbols:
                RHS.append(NonTerminal(token))
            else:
                RHS.append(Terminal(token))
        ret.append(Rule(LHS, RHS))
    return ret
