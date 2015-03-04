# ugly stuff to import modules one directory up
import os
import sys
import StringIO
cur_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(cur_dir)
parser_dir = os.path.join(top_dir, "lib", "parser")
sys.path.insert(0, parser_dir)
import ast
import parserExceptions
from eval_ast import evaluate

reducible_nodes = ["StatementList", "ExpressionList", "IdentifierList", "KeyValueList", "FunctionDeclarationStatementList"]

compile = ast.get_compiler(
    os.path.join(cur_dir, "tokens.txt"), 
    os.path.join(cur_dir, "language.txt"), 
    reducible_nodes
)

def execute(program_text, strict=False):
    try:
        tree = compile(program_text)
    except parserExceptions.NoActionFoundError as ex:
        if ex.token.klass.name == "$" and not strict:
            #got end of file unexpectedly.
            #the user may have forgotten the terminating semicolon.
            tree = compile(program_text + ";")
        else:
            raise
    evaluate(tree)

def check_output(*args, **kargs):
    """
    #behaves identically to `execute`, 
    except it suppresses all print statements, 
    and returns a string containing what would have been printed.
    """
    class SplitIO:
        def __init__(self, *channels):
            self.channels = channels
        def write(self, data):
            for channel in self.channels:
                channel.write(data)

    verbose = kargs.pop("verbose", True)
    string_io = StringIO.StringIO()
    old_stdout = sys.stdout

    if verbose:
        sys.stdout = SplitIO(string_io, sys.stdout)
    else:
        sys.stdout = string_io

    try:
        execute(*args, **kargs)
    finally:
        sys.stdout = old_stdout

    return string_io.getvalue().rstrip()
    

def repl():
    def isEofException(ex):
        return isinstance(ex, parserExceptions.NoActionFoundError) and ex.token.klass.name == "$"
    data = ""
    print ">>>",
    while True:
        try:
            line = raw_input("")
        except (EOFError, KeyboardInterrupt):
            return
        data += line
        try:
            #if user entered an empty line, he's done with his statement even if he didn't end with a semicolon.
            execute(data, strict=bool(line))
        except Exception as ex:
            if isEofException(ex):
                print "...",
                continue
            else:
                print ex
        data = ""
        print ">>>",

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        repl()
        sys.exit(0)

    with open(sys.argv[1]) as file:
        program_text = file.read()

    execute(program_text, "--strict" in sys.argv[2:])