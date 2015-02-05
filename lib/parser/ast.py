from util import construct_parser
from parseRules import parse_rules
from lex import lex, gen_token_rules, LiteralTokenRule


def slurp(filename):
    file = open(filename)
    rules_text = file.read()
    file.close()
    return rules_text


def tokenize_program(data):
    lines = data.split("\n")
    # remove comments
    lines = [line.partition("#")[0] for line in lines]
    characters = []
    in_string = False
    for char in "".join(lines):
        if char == "\"":
            in_string = not in_string
        if char == " " and not in_string:
            continue
        if char == "\t" and not in_string:
            continue
        characters.append(char)
    return "".join(characters)


class Node:
    def __init__(self, klass, children=None):
        self.klass = klass
        self.children = children if children is not None else []

    def __repr__(self):
        return "Node({}, [{}])".format(self.klass, ",".join(map(repr, self.children)))
        return " ".join(map(repr, self.children))


class Leaf(Node):
    def __init__(self, token):
        Node.__init__(self, "Terminal")
        self.token = token

    def __repr__(self):
        return "Leaf({})".format(self.token)
        return repr(self.token)


def is_leaf(node):
    return isinstance(node, Leaf)


# iterates through the nodes of the tree, depth first, yielding the node and then moving down the rightmost path.
def iter_tree(tree):
    to_search = [tree]
    while to_search:
        node = to_search.pop()
        yield node
        if not is_leaf(node):
            for child in node.children:
                to_search.append(child)


def construct_parse_tree(right_derivation, rules, tokens):

    # make local copies so as not to mutate the originals
    right_derivation = right_derivation[:]
    tokens = tokens[:]

    tree = Node(rules[0].RHS[0].value)
    unfinished_nodes = [tree]
    # first pass: construct tree without assigning tokens to leaves
    while right_derivation:
        rule = rules[right_derivation.pop()]
        node = unfinished_nodes.pop()
        for symbol in rule.RHS[::-1]:
            if symbol.symbol_type == "Terminal":
                node.children.insert(0, Leaf(None))
            elif symbol.symbol_type == "NonTerminal":
                node.children.insert(0, Node(symbol.value))
            else:
                raise Exception("unexpected symbol type {}".format(symbol.symbol_type))
        unfinished_nodes.extend([child for child in node.children if not is_leaf(child)])

    # second pass: assign token values to leaves
    for node in iter_tree(tree):
        if is_leaf(node):
            node.token = tokens.pop()

    return tree


def remove_literal_tokens(tree):

    def is_literal(node):
        return isinstance(node, Leaf) and isinstance(node.token.klass, LiteralTokenRule)
    # ew, mutating an iterable while iterating over it!
    # should work anyway, though.
    for node in iter_tree(tree):
        node.children = [child for child in node.children if not is_literal(child)]


def reduce_tail_recursive_nodes(tree, klass):
    """
    if there is a nonterminal defined as X := Y | Y X,
    modifies the tree so that multiple sequential instances of that node are condensed into one.
    ex.
      X
     / \
    Y   X
       / \
      Y   X
          |
          Y
    becomes

      X
     /|\
    Y Y Y


    arguments:
        tree: the abstract syntax tree which will be modified.
        klass: the class name of the node which will be reduced.
    """
    for node in iter_tree(tree):
        if not is_leaf(node) and node.klass == klass:
            last_child = node.children[-1]
            while not is_leaf(last_child) and last_child.klass == klass:
                node.children = node.children[:-1] + last_child.children
                last_child = node.children[-1]


def get_compiler(tokens_filename, rules_filename, reducible_node_names=None):
    """Creates a callable which can be used to construct abstract syntax trees for the given program.
    arguments:
        tokens_filename - the filename of the file which contains the regexes that match literal token values.
        rules_filename  - the filename of the file which contains the language rules in Backus Naur Form.
        reducible_node_names - optional. a list of strings, indicating which tail-recursive nodes should be reduced. See `reduce_tail_recursive_nodes` for more information.
    returns:
        function construct_ast(program_text), which returns the root Node of the constructed ast.
    """
    if not reducible_node_names:
        reducible_node_names = []
    rules_text = slurp(rules_filename)
    rules = parse_rules(rules_text)

    lex_text = slurp(tokens_filename)
    token_rules = gen_token_rules(lex_text, rules)

    parser = construct_parser(rules_text)

    def construct_ast(program_text):
        tokens = lex(program_text, token_rules)

        # todo: this kind of post-lexing processing should be specified by the caller somehow.
        tokens = [token for token in tokens if token.klass.name != "whitespace"]

        right_derivation = parser.parse(tokens)

        parse_tree = construct_parse_tree(right_derivation, rules, tokens)

        remove_literal_tokens(parse_tree)
        for name in reducible_node_names:
            reduce_tail_recursive_nodes(parse_tree, name)
        return parse_tree

    return construct_ast