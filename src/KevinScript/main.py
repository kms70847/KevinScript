#ugly stuff to import modules one directory up
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

import ast
from eval_ast import evaluate
from ktypes import KTrue, KFalse, KObject, KInt, PyFunction

import sys
if len(sys.argv) < 2:
    print "please supply a file name."
    sys.exit(0);
reducible_nodes = ["StatementList", "ExpressionList", "KeyValueList"]
tree = ast.construct_ast("tokens.txt", "language.txt", sys.argv[1], reducible_nodes)
scopes = [{}]
#populate built in types and functions
scopes[0]["object"] = PyFunction(lambda scopes: KObject())
scopes[0]["True"] = KTrue
scopes[0]["False"] = KFalse
evaluate(tree, scopes)