#table.py: see http://en.wikipedia.org/wiki/LR_parser
#converts a context-free grammar definition into an action/goto table, suitable for passing to an LR parser.




from primitives import *
from parseRules import parseRules
from prettyprint import dictPrint


def multiDict(seq, keyFunc):
    ret = {}
    for i in seq:
        key = keyFunc(i)
        if key not in ret:
            ret[key] = []
        ret[key].append(i)
    return ret

def closureRepr(items):
    return "\n".join(map(str,list(items)))




#see http://en.wikipedia.org/wiki/LR_parser
class ParseTable:
    def __init__(self, rules):
        #the rules passed in is a list, but we want a dict keyed by each rule's LHS.
        self.rules = multiDict(rules, lambda r: r.LHS)
        #we only need this for step four of constructing the action table.
        self.orderedRules = rules
        #each closure's id, keyed by the closure itself
        #technical kink: the closure must be converted from set to list.
        self.closureIds = {}
        #the transition table, keyed by the current state and symbol.
        self.transitions = {}
        
        itemsToRegister = set([Item(self.orderedRules[0])])
        self.registerClosure(itemsToRegister)
        
        
    #creates a closure of the given set of items.
    def close(self, items):
        ret = items.copy()
        for symbol in self.transitionSymbols(items):
            if symbol not in self.rules:
                continue
            for rule in self.rules[symbol]:
                ret.add(Item(rule))
        #if no new items were added, we don't need to recurse
        if len(ret) == len(items):
            return ret
        return self.close(ret)
        
    #returns a set of symbols occuring just after a dot in the given item set. 
    #This is used during the registerClosure method to recursively identify sub-itemSets to register.
    def transitionSymbols(self, items):
        return set(filter(lambda y: y != None, map(lambda x: x.markedSymbol(), items)))
        
    #returns a subset of items for which the given symbol is marked.
    def itemsOfInterest(self, items, symbol):
        return set(filter(lambda x: x.markedSymbol() != None and x.markedSymbol() == symbol, items))
        
    #moves the dots in each item forward by one. 
    def advanceDots(self, items):
        ret = set()
        for i in items:
            toAdd = i.copy()
            toAdd.advanceMarker()
            ret.add(toAdd)
        return ret
        
    def addTransition(self, sourceId, symbol, targetId):
        key = (sourceId, symbol)
        self.transitions[key] = targetId
        
    #closes the items given, then registers the closure if it is not already registered. returns the UID of the closure either way.
    #also recursively registers any sub-closures, and adds the appropriate entry to the transition dict.
    def registerClosure(self, items):
        closure = self.close(items)
        idKey = tuple(closure)
        if idKey in self.closureIds:
            return self.closureIds[idKey]
        closureId = len(self.closureIds)
        self.closureIds[idKey] = closureId
        
        for symbol in self.transitionSymbols(closure):
            nextItems = self.advanceDots(self.itemsOfInterest(closure, symbol))
            nextId = self.registerClosure(nextItems)
            self.addTransition(closureId, symbol, nextId)
        return closureId
        
    #returns true if one of the items is S ->(RHS), with the mark at the very end.
    def containsStartAcceptingRule(self, items):
        return any(map(lambda x: x.rule.LHS == NonTerminal("_") and x.terminating(), items))
        
    #we say an item terminates a rule if the item's symbols match the rule's and the mark is at the rightmost position.
    #returns a collection of rule idxs, matching the rules that are terminated by any of the given items.
    def rulesTerminated(self, items):
        ret = []
        for item in items:
            if not item.terminating():
                continue
            for idx, rule in enumerate(self.orderedRules):
                if idx != 0 and item.matchesRule(rule):
                    ret.append(idx)
        return ret
    
    #should probably seperate this stuff into some kind of rulesCollection class.
    #returns a collection of strings representing each symbol in the rule set.
    #you can supply a type, e.g. Terminal.symbolType, to get only those kinds of symbols.
    def symbols(self, type=None):
        ret = set()
        for rule in self.orderedRules:
            for symbol in rule.RHS:
                ret.add(symbol)
            ret.add(rule.LHS)
        ret.add(Terminal("$"))
        if type != None:
            ret = filter(lambda x: x.symbolType == type, ret)
        return ret
    
    #goto table and action table constructed using the rules from:
    #http://en.wikipedia.org/wiki/LR_parser
    #"Constructing the action and goto tables"
    def gotoTable(self):
        ret = {}
        #1. The columns for nonterminals are copied to the goto table.
        for state, symbol in self.transitions:
            if symbol.symbolType == NonTerminal.symbolType:
                key = (state, symbol)
                ret[key] = self.transitions[key]
        return ret
        
    def actionTable(self):
        ret = {}
        
        #2. The columns for the terminals are copied to the action table as shift actions.
        for state, symbol in self.transitions:
            if symbol.symbolType == Terminal.symbolType:
                destination = self.transitions[(state, symbol)]
                ret[(state, symbol.value)] = Action(shift, destination)
        
        #3. An extra column for '$' (end of input) is added to the action table that contains acc for every item set that contains "S -> E.".
        for closure in self.closureIds:
            if self.containsStartAcceptingRule(closure):
                idx = self.closureIds[closure]
                ret[(idx, "$")] = Action(accept)
        
        #4. If an item set i contains an item of the form "A -> w." and "A -> w" is rule m with m>0,
        #then the row for state i in the action table is completely filled with the reduce action rm.
        for closure, i in self.closureIds.iteritems():
            idxsTerminated = self.rulesTerminated(closure)
            if len(idxsTerminated) == 0:
                continue
            if len(idxsTerminated) > 1:
                raise Exception("Reduce-Reduce conflict on row {0}".format(i))
            m = idxsTerminated[0]
            for symbol in self.symbols(Terminal.symbolType):
                key = (i, symbol.value)
                if key in ret:
                    raise Exception("Shift-reduce conflict at {0}".format(key))
                ret[key] = Action(reduce, m)
        
        return ret
        
    def __repr__(self):
        return dictPrint(self.actionTable()) + "\n" + dictPrint(self.gotoTable())
