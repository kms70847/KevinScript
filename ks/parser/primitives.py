# primitives.py - classes used by one or more of the other files.


# a nonterminal is a symbol in a grammar that does expand into additional symbols.
class NonTerminal:
    symbol_type = "NonTerminal"

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if other is None:
            return False
        return self.symbol_type == other.symbol_type and self.value == other.value

    def __hash__(self):
        return hash((self.value, self.symbol_type))

    def __repr__(self):
        return str(self.value)


# a terminal is a symbol used in a grammar that doesn't expand into additional symbols. Typically character literals.
class Terminal:
    symbol_type = "Terminal"

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if other is None:
            return False
        return self.symbol_type == other.symbol_type and self.value == other.value

    def __hash__(self):
        return hash((self.value, self.symbol_type))

    def __repr__(self):
        return str(self.value)


# a rule is a NonTerminal left hand side and a right hand side with one or more symbols (can be either terminals or nonterminals or both)
class Rule:
    def __init__(self, LHS, RHS):
        if LHS.symbol_type != NonTerminal.symbol_type:
            raise Exception("Expected terminal symbol")
        self.LHS = LHS
        self.RHS = RHS

    def __eq__(self, other):
        return self.LHS == other.LHS and self.RHS == other.RHS

    def __hash__(self):
        return hash((self.LHS, tuple(self.RHS)))

    def __repr__(self):
        return "{0} -> {1}".format(self.LHS, " ".join(map(str, self.RHS)))


# an Item is a grammar rule with a "special dot" added somewhere on the right hand side.
# See http://en.wikipedia.org/wiki/LR_parser#Constructing_LR.280.29_parsing_tables
# primarily used in SLRtable.py and table.py
class Item:
    def __init__(self, rule, mark_pos=0):
        self.rule = rule
        self.mark_pos = mark_pos

    def marked_symbol(self):
        if self.mark_pos >= len(self.rule.RHS):
            return None
        return self.rule.RHS[self.mark_pos]

    def advance_marker(self):
        self.mark_pos += 1

    def copy(self):
        return Item(self.rule, self.mark_pos)

    def terminating(self):
        return self.marked_symbol() is None

    def matches_rule(self, rule):
        return self.rule == rule

    def __eq__(self, other):
        return self.rule == other.rule and self.mark_pos == other.mark_pos

    def __hash__(self):
        return hash((self.rule, self.mark_pos))

    def __repr__(self):
        ret = str(self.rule.LHS) + " -> "
        RHS = []
        for idx, symbol in enumerate(self.rule.RHS):
            if idx == self.mark_pos:
                RHS.append(".")
            RHS.append(str(symbol))
        if self.mark_pos == len(self.rule.RHS):
            RHS.append(".")
        ret = ret + " ".join(RHS)
        return ret


shift = 0
reduce = 1
accept = 2


class Action:
    def __init__(self, action, dest=None):
        self.action = action
        self.destination = dest

    def __repr__(self):
        if self.action == accept:
            return "acc"
        return "s r a".split()[self.action] + str(self.destination)
