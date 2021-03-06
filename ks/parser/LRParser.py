# LRParser: see http://en.wikipedia.org/wiki/LR_parser
# takes a action+goto table and generates a rightmost derivation of a string within the language family.

from ks.parser.lex import LiteralTokenRule, Token
from ks.parser.parseRules import *
from ks.parser.parserExceptions import NoActionFoundError

end_of_input_token = Token(LiteralTokenRule("$"), "$")


# rules is a list of Rule objects.
# actions is a dict whose key is a tuple of state and input symbol (int and string), and whose value is an Action object.
# gotos is a dict whose key is a tuple of state(int) and non_terminal, and whose value is a state(int).
class LRParser:
    def __init__(self, rules, actions, gotos):
        self.rules = rules
        self.actions = actions
        self.gotos = gotos

    # see:
    # http://en.wikipedia.org/wiki/LR_parser
    # "Architecture of LR parsers"
    def parse(self, input):
        self.stack = [0]
        self.input = input + [end_of_input_token]
        self.output = []
        while True:
            action_key = (self.stack[-1], self.input[0].klass.name)

            # no action: syntax error is reported
            if action_key not in self.actions:
                raise NoActionFoundError(self.input[0])
            action = self.actions[action_key]

            # an accept: string is accepted
            if action.action == accept:
                return self.output

            # a shift sn:
            # the current terminal is removed from the input stream
            # the state n is pushed onto the stack and becomes the current state.
            if action.action == shift:
                self.input = self.input[1:]
                self.stack.append(action.destination)

            # a reduce rm:
            # the number m is written to the output stream
            # for every symbol in the RHS of rule m, a state is removed from the stack.
            # given the state that is then on top of the stack and the left-hand side of rule,
            # a new state is looked up in the goto table and made the new current state by pushing it onto the stack.
            if action.action == reduce:
                self.output.append(action.destination)
                rule_idx = action.destination
                amt_to_pop = len(self.rules[rule_idx].RHS)
                self.stack = self.stack[0:-amt_to_pop]
                goto_key = (self.stack[-1], self.rules[rule_idx].LHS)
                if goto_key not in self.gotos:
                    raise Exception("couldn't parse string - no goto found")
                self.stack.append(self.gotos[goto_key])
