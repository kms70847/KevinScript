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
    except Exception as e:
        print "Expected code {} to run successfully, got exception {} instead".format(repr(code), repr(str(e)))
        raise

def expect_output(code, output):
    try:
        result = ks.check_output(code)
    except Exception as e:
        print "Expected code {} to produce output {}, got exception {} instead".format(repr(code), repr(output), repr(str(e)))
        raise
    assert result == output, "Expected code {} to produce output {}, got {} instead".format(repr(code), repr(output), repr(result))

expect_runs("")

#printing literals and builtins
expect_output('print "Hello, World!"', 'Hello, World!')
expect_output('print 123', '123')
expect_output('print True', 'True')
expect_output('print False', 'False')
expect_output('print [1, 2, 3]', '[1, 2, 3]')
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
expect_output('if (False){;} else{print "success";}', "success")

#functions - declaration, `return`, evaluation
expect_runs('function frob(){;}')
expect_output("""
    function frob(x){
        return x;
    }
    print frob(23)
    """,
    "23"
)

#expression statements
expect_runs('True')

#empty statements
expect_runs(';;;')

#enclosure expressions
expect_runs('(True)')
expect_runs('(((((True)))))')

#arithmetic
expect_output("print 1+1", "2")
expect_output("print 42-23", "19")
expect_output("print 23*2", "46")
expect_output("print 42/2", "21")
expect_output("print 23%2", "1")
expect_output("print 0==0", "True")
expect_output("print 23 < 42", "True")
expect_output("print 42 > 23", "True")
expect_runs("1 * 1 + 1 / 1 - 1 < 1")

#attribute getting/setting
expect_output("foo = Object(); foo.bar=23; print foo.bar", "23")
expect_output("foo = Object(); foo.bar=function(){return 23;}; print foo.bar()", "23")


#tests we'd like to pass for future versions
#none right now :-)