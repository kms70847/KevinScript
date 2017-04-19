# table.py: see http://en.wikipedia.org/wiki/LR_parser
# converts a context-free grammar definition into an action/goto table, suitable for passing to an LR parser.

from ks.parser.prettyprint import dict_print
from ks.parser.primitives import *


def multi_dict(seq, key_func):
    ret = {}
    for i in seq:
        key = key_func(i)
        if key not in ret:
            ret[key] = []
        ret[key].append(i)
    return ret


def closure_repr(items):
    return "\n".join(map(str, list(items)))


# see http://en.wikipedia.org/wiki/LR_parser
class ParseTable:
    def __init__(self, rules):
        # the rules passed in is a list, but we want a dict keyed by each rule's LHS.
        self.rules = multi_dict(rules, lambda r: r.LHS)
        # we only need this for step four of constructing the action table.
        self.ordered_rules = rules
        # each closure's id, keyed by the closure itself
        # technical kink: the closure must be converted from set to list.
        self.closure_ids = {}
        # the transition table, keyed by the current state and symbol.
        self.transitions = {}

        items_to_register = set([Item(self.ordered_rules[0])])
        self.register_closure(items_to_register)

    # creates a closure of the given set of items.
    def close(self, items):
        ret = items.copy()
        for symbol in self.transition_symbols(items):
            if symbol not in self.rules:
                continue
            for rule in self.rules[symbol]:
                ret.add(Item(rule))
        # if no new items were added, we don't need to recurse
        if len(ret) == len(items):
            return ret
        return self.close(ret)

    # returns a set of symbols occuring just after a dot in the given item set.
    # This is used during the register_closure method to recursively identify sub-item_sets to register.
    def transition_symbols(self, items):
        return set([y for y in [x.marked_symbol() for x in items] if y is not None])

    # returns a subset of items for which the given symbol is marked.
    def items_of_interest(self, items, symbol):
        return set([x for x in items if x.marked_symbol() is not None and x.marked_symbol() == symbol])

    # moves the dots in each item forward by one.
    def advance_dots(self, items):
        ret = set()
        for i in items:
            to_add = i.copy()
            to_add.advance_marker()
            ret.add(to_add)
        return ret

    def add_transition(self, source_id, symbol, target_id):
        key = (source_id, symbol)
        self.transitions[key] = target_id

    # closes the items given, then registers the closure if it is not already registered. returns the UID of the closure either way.
    # also recursively registers any sub-closures, and adds the appropriate entry to the transition dict.
    def register_closure(self, items):
        closure = self.close(items)
        id_key = tuple(closure)
        if id_key in self.closure_ids:
            return self.closure_ids[id_key]
        closure_id = len(self.closure_ids)
        self.closure_ids[id_key] = closure_id

        for symbol in self.transition_symbols(closure):
            next_items = self.advance_dots(self.items_of_interest(closure, symbol))
            next_id = self.register_closure(next_items)
            self.add_transition(closure_id, symbol, next_id)
        return closure_id

    # returns true if one of the items is S ->(RHS), with the mark at the very end.
    def contains_start_accepting_rule(self, items):
        return any([x.rule.LHS == NonTerminal("_") and x.terminating() for x in items])

    # we say an item terminates a rule if the item's symbols match the rule's and the mark is at the rightmost position.
    # returns a collection of rule idxs, matching the rules that are terminated by any of the given items.
    def rules_terminated(self, items):
        ret = []
        for item in items:
            if not item.terminating():
                continue
            for idx, rule in enumerate(self.ordered_rules):
                if idx != 0 and item.matches_rule(rule):
                    ret.append(idx)
        return ret

    # should probably seperate this stuff into some kind of rules_collection class.
    # returns a collection of strings representing each symbol in the rule set.
    # you can supply a type, e.g. Terminal.symbol_type, to get only those kinds of symbols.
    def symbols(self, type=None):
        ret = set()
        for rule in self.ordered_rules:
            for symbol in rule.RHS:
                ret.add(symbol)
            ret.add(rule.LHS)
        ret.add(Terminal("$"))
        if type is not None:
            ret = [x for x in ret if x.symbol_type == type]
        return ret

    # goto table and action table constructed using the rules from:
    # http://en.wikipedia.org/wiki/LR_parser
    # "Constructing the action and goto tables"
    def goto_table(self):
        ret = {}
        # 1. The columns for nonterminals are copied to the goto table.
        for state, symbol in self.transitions:
            if symbol.symbol_type == NonTerminal.symbol_type:
                key = (state, symbol)
                ret[key] = self.transitions[key]
        return ret

    def action_table(self):
        ret = {}

        # 2. The columns for the terminals are copied to the action table as shift actions.
        for state, symbol in self.transitions:
            if symbol.symbol_type == Terminal.symbol_type:
                destination = self.transitions[(state, symbol)]
                ret[(state, symbol.value)] = Action(shift, destination)

        # 3. An extra column for '$' (end of input) is added to the action table that contains acc for every item set that contains "S -> E.".
        for closure in self.closure_ids:
            if self.contains_start_accepting_rule(closure):
                idx = self.closure_ids[closure]
                ret[(idx, "$")] = Action(accept)

        # 4. If an item set i contains an item of the form "A -> w." and "A -> w" is rule m with m>0,
        # then the row for state i in the action table is completely filled with the reduce action rm.
        for closure, i in self.closure_ids.items():
            idxs_terminated = self.rules_terminated(closure)
            if len(idxs_terminated) == 0:
                continue
            if len(idxs_terminated) > 1:
                raise Exception("Reduce-Reduce conflict on row {0}".format(i))
            m = idxs_terminated[0]
            for symbol in self.symbols(Terminal.symbol_type):
                key = (i, symbol.value)
                if key in ret:
                    raise Exception("Shift-reduce conflict at {0}".format(key))
                ret[key] = Action(reduce, m)

        return ret

    def __repr__(self):
        return dict_print(self.action_table()) + "\n" + dict_print(self.goto_table())
