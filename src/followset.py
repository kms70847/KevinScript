#calculates the lookahead table for a set of rules.

#see http://en.wikipedia.org/wiki/LL_parser
#"Constructing an LL(1) parsing table"

#(looking back on this a year later, I'm confused about how the followset for a left derivation parser can be used in my right derivation parser.)

from primitives import *
from parseRules import parseRules

def setsSize(dictOfSets):
    total = 0
    for key in dictOfSets:
        total += len(dictOfSets[key])
    return total

#this needs revision if we decide to allow languages that use epsilon
def firstSets(rules):
    firstRHS = {}
    firstLHS = {}
    #initialize all the things to empty sets
    for rule in rules:
        firstLHS[rule.LHS] = set()
        firstRHS[tuple(rule.RHS)] = set()
        #terminals have only themselves as a first set
        for symbol in rule.RHS:
            if symbol.symbolType == Terminal.symbolType:
                firstLHS[symbol] = set([symbol])
    oldRetSize = setsSize(firstLHS)
    while True:
        for rule in rules:
            Ai = rule.LHS
            wi = tuple(rule.RHS)
            
            if wi[0].symbolType == Terminal.symbolType:
                firstRHS[wi].add(wi[0])
            else:
                firstRHS[wi] = firstRHS[wi].union(firstLHS[wi[0]])
            
            firstLHS[Ai] = firstLHS[Ai].union(firstRHS[wi])
        size = setsSize(firstLHS)
        if size == oldRetSize:
            return firstLHS
        oldRetSize = size


def followSets(rules):
    first = firstSets(rules)
    follow = {}
    for rule in rules:
        follow[rule.LHS] = set()
        for symbol in rule.RHS:
            follow[symbol] = set()
    follow[rules[0].LHS].add(Terminal("$"))
    oldRetSize = setsSize(follow)
    while True:
        for rule in rules:
            for idx, symbol in enumerate(rule.RHS):
                if idx == len(rule.RHS) - 1:
                    follow[symbol] = follow[symbol].union(follow[rule.LHS])
                else:
                    nextSymbol = rule.RHS[idx+1]
                    follow[symbol] = follow[symbol].union(first[nextSymbol])
        size = setsSize(follow)
        if size == oldRetSize:
            return follow
        oldRetSize = size