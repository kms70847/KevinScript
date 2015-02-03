"testing of basic language grammar. We won't make assertions about expected output. It's satisfactory just for it to not crash or loop forever.";


"print statements";
print "testing print statements...";
print 1;
print True;
print False;
print None;
print None.type;
print "passed.";

"assignment statements";
foo = 23;

"while statements";
i = 0;
while(i < 10){
    i = i + 1;
}

"for statements";
for(i in [4,8,15,16,23]){
    ;
}

"if statements";
if (True){;}
if (True){;}else{;}

"function declaration and return statement";
function frob(){return 23;}
function troz(x, y){return x + y;}

"expression statements";
True;

"empty statements";
;




"numbers";
1; 23; 42; 999999999999999999;

"string literals";
"the quick brown fox jumps over the lazy dog";
"the human torch was denied a bank loan";
"escaped quote marks are not implemented yet, sorry";

"enclosures";
(4);
(2+2);
("foo");

"function calls";
frob();
troz(23, 42);

"list displays";
[];
[4, 8, 15, 16, 23, 42];
"list methods";
l = [];
l.append(23);
l.at(0);
l.pop();

"dict displays";
print "dict displays are not implemented yet";
"(but if they were, they'd look like this:";
"{};";
"{4:8, 15:16, 23:42};";

"operators";
"these might fail even if the grammar and ast are correct. In particular, the Int object might not support all of these operators";
1 * 1;
1 / 1;
1 % 1;
1 + 1;
1 - 1;
1 == 1;
1 > 1;
1 < 1;
1 * 1 + 1 / 1 - 1 < 1 ;

"function expressions, AKA anonymous functions";
zort = function(){return 23;};
narf = function(x,y){return x - y;};

"built-in nonliterals";
True;
False;
Object();

"attribute access";
foo = Object();
foo.bar = 23;
foo.troz = function(){return 23;};
foo.troz();

print "all tests passed!";