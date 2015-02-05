import os
import sys

#add `src` directory to path
cur_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(cur_dir)
parser_dir = os.path.join(top_dir, "src")
sys.path.insert(0, parser_dir)

import ks

def expect_runs(code):
    try:
        ks.execute(code)
    except:
        raise Exception("Expected code {} to run successfully, got exception instead".format(repr(code)))

def expect_output(code, output):
    try:
        result = ks.check_output(code)
    except:
        raise Exception("Expected code {} to produce output {}, got exception instead".format(repr(code), repr(output)))
    assert result == output, "Expected code {} to produce output {}, got {} instead".format(repr(code), repr(output), repr(result))

expect_runs("")

#printing literals and builtins
expect_output('print "Hello, World!"', 'Hello, World!')
expect_output('print 123', '123')
expect_output('print True', 'True')
expect_output('print False', 'False')
expect_output('print None', 'None')
expect_output('print Object', "<type 'Object'>")

#assignment statements
expect_runs("foo = 23")

#while loops
expect_runs("""
    i = 0;
    while(i < 10){
        i = i + 1;
    }
""")

#for loops
expect_runs("""
    for(i in [4,8,15,16,23]){
        ;
    }
""")

#if statements
expect_runs('if (True){;}')
expect_output('if (True){print "success";}', "success")
expect_output('if (False){;} else{print "success"}', "success")
