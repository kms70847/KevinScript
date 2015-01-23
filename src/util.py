from parseRules import parse_rules
from SLRtable import ParseTable
from LRParser import LRParser


def construct_parser(rules_text, is_verbose=False):
    def log(msg=""):
        if is_verbose:
            print msg

    log("Parsing rules...")
    rules = parse_rules(rules_text)
    log("\n".join(map(str, rules)))
    log()

    log("Constructing parse tables...")
    table = ParseTable(rules)
    log(table)

    parser = LRParser(rules, table.action_table(), table.goto_table())
    return parser


# returns True if the program is valid, False otherwise
def is_valid(rules_text, program_text):
    rules = parse_rules(rules_text)
    table = ParseTable(rules)
    parser = LRParser(rules, table.action_table(), table.goto_table())
    try:
        derivation = parser.parse(program_text)
    except:
        return False
    return True
