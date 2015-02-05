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

compile = ast.get_compiler(
    os.path.join(cur_dir, "tokens.txt"), 
    os.path.join(cur_dir, "language.txt"), 
    reducible_nodes
)

with open(sys.argv[1]) as file:
    program_text = file.read()

program_text = ''

if "--strict" not in sys.argv[2:]:
    if not program_text.endswith(";"):
        program_text = program_text + ";"

tree = compile(program_text)

scopes = [builtins]
evaluate(tree, scopes)
