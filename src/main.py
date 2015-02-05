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

reducible_nodes = ["StatementList", "ExpressionList", "KeyValueList"]

compile = ast.get_compiler(
    os.path.join(cur_dir, "tokens.txt"), 
    os.path.join(cur_dir, "language.txt"), 
    reducible_nodes
)

def execute(program_text, strict=False):
    if not strict:
        program_text += ";"
    tree = compile(program_text)
    scopes = [builtins]
    evaluate(tree, scopes)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("please supply a file name.")
        sys.exit(0)


    with open(sys.argv[1]) as file:
        program_text = file.read()

    execute(program_text, "--strict" in sys.argv[2:])