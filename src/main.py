# ugly stuff to import modules one directory up
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(cur_dir)
parser_dir = os.path.join(top_dir, "lib", "parser")
sys.path.insert(0, parser_dir)
import ast
from eval_ast import evaluate
from kobjects import builtins

import sys
if len(sys.argv) < 2:
    print("please supply a file name.")
    sys.exit(0)
reducible_nodes = ["StatementList", "ExpressionList", "KeyValueList"]
tree = ast.construct_ast(
    os.path.join(cur_dir, "tokens.txt"), 
    os.path.join(cur_dir, "language.txt"), 
    sys.argv[1], 
    reducible_nodes
)

scopes = [builtins]
evaluate(tree, scopes)
