from parseRules import parseRules
from SLRtable import ParseTable
from LRParser import LRParser

def constructParser(rulesText, isVerbose = False):
    def log(msg=""):
        if isVerbose:
            print msg

    log("Parsing rules...")
    rules = parseRules(rulesText)
    log("\n".join(map(str, rules)))
    log()
    
    log("Constructing parse tables...")
    table = ParseTable(rules)
    log(table)

    parser = LRParser(rules, table.actionTable(), table.gotoTable())
    return parser

#returns True if the program is valid, False otherwise
def isValid(rulesText, programText):
    rules = parseRules(rulesText)
    table = ParseTable(rules)
    parser = LRParser(rules, table.actionTable(), table.gotoTable())
    try:
        derivation = parser.parse(programText)
    except:
        return False
    return True
