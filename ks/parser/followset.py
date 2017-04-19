# calculates the lookahead table for a set of rules.

# see http://en.wikipedia.org/wiki/LL_parser
# "Constructing an LL(1) parsing table"

# (looking back on this a year later, I'm confused about how the followset for a left derivation parser can be used in my right derivation parser.)

from ks.parser.primitives import *


def sets_size(dict_of_sets):
    total = 0
    for key in dict_of_sets:
        total += len(dict_of_sets[key])
    return total


# this needs revision if we decide to allow languages that use epsilon
def first_sets(rules):
    first_r_h_s = {}
    first_l_h_s = {}
    # initialize all the things to empty sets
    for rule in rules:
        first_l_h_s[rule.LHS] = set()
        first_r_h_s[tuple(rule.RHS)] = set()
        # terminals have only themselves as a first set
        for symbol in rule.RHS:
            if symbol.symbol_type == Terminal.symbol_type:
                first_l_h_s[symbol] = set([symbol])
    old_ret_size = sets_size(first_l_h_s)
    while True:
        for rule in rules:
            Ai = rule.LHS
            wi = tuple(rule.RHS)

            if wi[0].symbol_type == Terminal.symbol_type:
                first_r_h_s[wi].add(wi[0])
            else:
                first_r_h_s[wi] = first_r_h_s[wi].union(first_l_h_s[wi[0]])

            first_l_h_s[Ai] = first_l_h_s[Ai].union(first_r_h_s[wi])
        size = sets_size(first_l_h_s)
        if size == old_ret_size:
            return first_l_h_s
        old_ret_size = size


def follow_sets(rules):
    first = first_sets(rules)
    follow = {}
    for rule in rules:
        follow[rule.LHS] = set()
        for symbol in rule.RHS:
            follow[symbol] = set()
    follow[rules[0].LHS].add(Terminal("$"))
    old_ret_size = sets_size(follow)
    while True:
        for rule in rules:
            for idx, symbol in enumerate(rule.RHS):
                if idx == len(rule.RHS) - 1:
                    follow[symbol] = follow[symbol].union(follow[rule.LHS])
                else:
                    next_symbol = rule.RHS[idx+1]
                    follow[symbol] = follow[symbol].union(first[next_symbol])
        size = sets_size(follow)
        if size == old_ret_size:
            return follow
        old_ret_size = size
