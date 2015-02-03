import re


# subclasses should implement:
# attribute `self.name`
# method `self.match(s:str)`, which returns either `None` if the string does not match, or the length of the slice of the string that matches.
class TokenRule:
    pass


class RegexTokenRule(TokenRule):
    def __init__(self, name, regex):
        self.name = name
        self.regex_text = regex
        self.regex = re.compile(regex)

    def match(self, s):
        result = self.regex.match(s)
        if not result:
            return None
        return len(result.group(0))

    def __repr__(self):
        return "RegexTokenRule({}, {})".format(repr(self.name), repr(self.regex_text))


class LiteralTokenRule(TokenRule):
    def __init__(self, name):
        self.name = name

    def match(self, s):
        if s.startswith(self.name):
            return len(self.name)
        else:
            return None

    def __repr__(self):
        return "LiteralTokenRule({})".format(repr(self.name))


def gen_token_rules(text, rules):
    from primitives import Terminal
    # identify terminal symbols in our language
    terminals = list(set(symbol.value for rule in rules for symbol in rule.RHS if isinstance(symbol, Terminal)))

    lines = text.split("\n")
    lines = [line.strip() for line in lines if len(line.strip()) > 0 and not line.startswith("#")]

    # pass 1: determine which terminals are defined in the tokens file
    nonliteral_tokens = set()
    for line in lines:
        nonliteral_tokens.add(line.partition("->")[0].strip())
    literal_tokens = list(set(terminals) - nonliteral_tokens)
    nonliteral_tokens = list(nonliteral_tokens)

    rules = []
    # literals should have higher priority than nonliterals.
    # this is generally a good idea since nonliterals tend to match much more than literals,
    # and they would overshadow literals if they had higher priority.
    for literal in literal_tokens:
        rules.append(LiteralTokenRule(literal))

    # pass 2: compiling nonliterals
    for line in lines:
        name, _, regex = line.partition("->")
        name = name.strip()
        regex = regex.strip()
        rules.append(RegexTokenRule(name, regex))

    return rules


class Token:
    def __init__(self, klass, value, position=None):
        self.klass = klass
        self.value = value
        self.position = position

    def __repr__(self):
        return "Token({}, {}, {})".format(repr(self.klass.name), repr(self.value), self.position)


def lex(text, token_rules):
    idx = 0
    line_number = 0
    tokens = []
    while len(text) > 0:
        matches = [{"rule": rule, "size": rule.match(text)} for rule in token_rules]
        matches = [match for match in matches if match["size"] and match["size"] > 0]
        assert len(matches) > 0, "Couldn't parse text at line {}, position {}: {}".format(line_number, idx, repr(text[:20]))
        match = max(matches, key=lambda m: m["size"])
        size = match["size"]
        literal = text[:size]
        tokens.append(Token(match["rule"], literal, (line_number+1, idx)))
        text = text[size:]
        idx += size
        line_number += literal.count("\n")
    return tokens
