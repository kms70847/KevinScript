# Introduction
KevinScript (abbreviated "KS") is a programming language inspired by Python and Javascript. 

# Quick Start
## Installation
KS requires Python to run.
Download this repository to a directory of your choosing. For example, `C:\programming\Github projects\KevinScript`.

## Starting the REPL
You can experiment with KS right away by using the REPL. Execute `python -m ks` with no arguments.

    C:\programming\Github projects\KevinScript>python -m ks
    >>> print("Hello, world!")
    ...
    Hello, world!
Exit the REPL with ctrl-C or ctrl-Z.
## Running source files
You can execute KS source files by supplying a file name to `python -m ks`.

    C:\programming\Github projects\KevinScript>python -m ks samples\prime_detector.k
    Prime numbers below 100:
    2
    3
    5
    7
    11
    13
    17
    19
    23
    29
    31
    37
    41
    43
    47
    53
    59
    61
    67
    71
    73
    79
    83
    89
    97

## Installing as a package

Optionally, you may install KevinScript as a package. This will make it accessible from any directory. 
From the KevinScript directory, execute:

    python setup.py install

Now you can access KevinScript by using `KevinScript` instead of `python -m ks`.

# Built-in Types
## Boolean
There are only two Boolean values. They are named `True` and `False`.

    >>> True;
    True
    >>> False;
    False
    >>> True and False;
    False
    >>> True or False;
    True
## Integer
An Integer is represented by a sequence of digits. Like in most other languages, they can be manipulated using typical arithmetic operators.

    >>> 12345;
    12345
    >>> 2+2;
    4
    >>> 23-42;
    -19
    >>> 6*7;
    42
    >>> 100/4;
    25
    >>> 16/3;
    5
    >>> 15 % 2;
    1
Note that division rounds down to the nearest Integer.
## List
The List is the primary compound data type. It can be used to collect objects together.

    >>> seq = [4, 8, 15, 16, 23, 42];
    >>> seq[0];
    4
    >>> seq[5];
    42
    >>> seq.size();
    6
    >>> seq.append(100);
    >>> seq[0] = 999;
    >>> seq;
    [999, 8, 15, 16, 23, 42, 100]
    >>> seq.size();
    7
    >>> for(item in seq){print(item);}
    999
    8
    15
    16
    23
    42
    100
A list can contain any type of object. Elements do not need to share the same type.
## String
Strings are collections of characters.

    >>> print("Hello, World!");
    Hello, World!
## Nonetype
`None` is an object used to indicate the absence of a value. it is the return value of any function that does not explicitly return anything.

    >>> function f(){
    ...     "this function does nothing";
    ... }
    >>> print(f());
    None
## Object
All types in KevinScript inherit basic behavior from `Object`. This is true for both built-in types, and user defined types.
## Type
The Type object is the type of all types. It can be used to create new types, although it is usually preferable to use the class declaration statement instead.

    >>> Object.type;
    <type 'Type'>
    >>> Integer.type;
    <type 'Type'>
    >>> String.type;
    <type 'Type'>

Parameters needed to call type:

- name: a string describing the type.
- parent: the type that this type should inherit from. Use `Object` if you don't want anything in particular.
- methods: a list of even length. Each even-indexed item is the string name of a method, and each odd-indexed item is the callable describing that method's behavior.

For example,

    >>> Fred = Type("Fred", Object, ["durf", function(self) {return 23;}]);
    >>> x = Fred();
    >>> x.durf();
    23

## Function
The type of all functions. Can't be called by the user. Only used for type checking.
## Dict
(coming soon?)

# Statements
## Assignment Statement
Used to bind values to variables.

    >>> x = 23;
    >>> y = x;
    >>> x = 42;
    >>> x;
    42
    >>> y;
    23
Assignment is by reference. If two variables refer to the same value, then calling a mutating method on one will mutate the other.

    >>> a = [1,2,3];
    >>> a.size();
    3
    >>> b = a;
    >>> b.append(42);
    >>> b.size();
    4
    >>> a.size();
    4
Here, `a` and `b` refer to the same list, so `a.size()` changes from 3 to 4 when we append to `b`.

## If Statement
Causes a block of code to only execute if the condition is True.

    >>> if (1 < 100){
    ...     print("the if condition passed");
    ... }
    the if condition passed
    >>> if (999 < 100){
    ...     print("the if condition passed");
    ... }
    >>>
Following the if block, you may have an `else` block. The contents of this block only executes if the condition is not True.

    >>> if (999 < 100){
    ...     print("the if condition passed");
    ... } else {
    ...     print("the if condition failed");
    ... }
    the if condition failed

## While Statement
Causes a block of code to repeat as long as the predicate is True.

    >>> x = 1;
    >>> while (x < 100){
    ...     print(x);
    ...     x = x * 2;
    ... }
    1
    2
    4
    8
    16
    32
    64

## For Statement
Repeats a block of code once for each element of the supplied list.

    >>> items = [4, 8, 15, 16, 23, 42];
    >>> for(x in items){
    ...     print(x);
    ... }
    4
    8
    15
    16
    23
    42

## Function Declaration Statement
Creates a Function object, which can later be called in order to execute the code block.

    >>> function sum(x,y,z){
    ...     return x+y+z;
    ... }
    >>>
    >>> print(sum(16, 23, 42));
    81

## Class Declaration Statement
Creates a new type, which can be called to make new objects of that type.

    >>> class Dog{
    ...     function __init__(self, breed){
    ...             self.breed = breed;
    ...     }
    ...     function bark(self){
    ...             print("woof");
    ...     }
    ...     function speak(self){
    ...             print("Hello, I am a dog. My breed is:");
    ...             print(self.breed);
    ...     }
    ... }
    >>> fido = Dog("terrier");
    >>> fido.bark();
    woof
    >>> fido.speak();
    Hello, I am a dog. My breed is:
    terrier
You can specify a parent class, which your type will inherit methods from.

    >>> class Fred{
    ...     function speak(self){
    ...             print("Yabba dabba doo!");
    ...     }
    ... }
    >>> class Barney(Fred){
    ... }
    >>> b = Barney();
    >>> b.speak();
    Yabba dabba doo!

## Return Statement
Terminates a function and presents a value to the calling context. Should not be used if you aren't inside a function.

    >>> function frob(){
    ...     return 23;
    ...     print("This line will never execute no matter what");
    ... }
    >>>
    >>> print(frob() + 42);
    65
## Expression Statement
An expression statement may contain any one expression. When used inside the REPL, the result of the expression will be printed, unless it is None.

    >>> 42;
    42
    >>> 2+2;
    4
    >>> "Hello, I am an expression containing a string literal";
    Hello, I am an expression containing a string literal
    >>> None;
    >>>
## Empty Statement

a statement that doesn't do anything. Represented by a lone semicolon.

    >>> ;
    >>>

# Expressions
## Arithmetic Operators
See [Integers] for example usage. You can override the behavior of your own types by defining the appropriate double-underscore methods:

 - multiplication - `__mul__`  
 - division - `__div__`  
 - modulus - `__mod__`  
 - addition - `__add__`  
 - subtraction - `__sub__`  

## Comparison Operators
Used to compare the values of two objects.

    >>> 100 > 3;
    True
    >>> 1 > 3;
    False
    >>> 4 < 100;
    True
    >>> 4 == 4;
    True
Define the behavior of your own types by defining:  

 - greater than - `__gt__`  
 - less than - `__lt__`  
 - equals - `__eq__`  
 - does not equal - `__ne__`  

## Boolean Operators
Used to chain together boolean expressions.

    >>> 25 > 0 and 25 < 100;
    True
    >>> 999 < 0 or 999 > 100;
    True
Define the behavior of your own types by defining:

 - and - `__and__`
 - or - `__or__`

## Function Expression
Similar to the function declaration statement, except it can be used anywhere an expression could go - as an argument to a call, inside a list, etc.

    >>> function apply_each(value, functions){
    ...     for(func in functions){
    ...             value = func(value);
    ...     }
    ...     return value;
    ... }
    >>>
    >>> funcs = [function(x){return x+1;}, function(y){return y*2;}, function(z){return z-100;}];
    >>> print(apply_each(23, funcs));
    -52

Function expressions are anonymous. There is no identifier between "function" and the parameter list.

## List Comprehension
Used to create new lists by applying some expression to each element of an existing list.

    >>> x = [1,2,3];
    >>> y = [a*2 for a in x];
    >>> y;
    [2, 4, 6]

## Calling Objects
An expression can be called by adding a pair of parentheses, which may contain zero to infinity arguments. For example, `print` is a function that can be called with one argument.

    >>> print(23);
    23
## Attribute and Method Access
The attributes and methods of an object can be accessed using the period operator.

    >>> x = Object();
    >>> x.foo = 23;
    >>> x.foo;
    23
## Item Access
Some objects, such as List, support indexed item access.
    >>> x = [4, 8, 15, 16, 23, 42];
    >>> x[1] = 99;
    >>> print(x);
    [4, 99, 15, 16, 23, 42]
    >>> print(x[1]);
    99

Define this behavior in your own types by defining:

 - item getting - `__getitem__(self, key)`  
 - item setting - `__setitem__(self, key, value)`

## Atom Expression
An atom expression is one of three things:

- a variable name, ex. `foo`, `Object`, `print`.
- a literal value, ex. `23`, `[1,2,3]`, `"Hello"`.
- any expression inside a pair of parentheses, ex. `(1+2-3*4/5)`.
    

# FAQs
## Is this a joke?
No, this is a real programming language that has real code. You can download it and it really runs.
## What good is this language for?
Currently nothing. For any programming project you can think of, there is probably a language that would execute it faster and more concisely than this one.
## Have you considered using [insert grammar-reading / token-lexing / code-generating / compiler-writing library here]?
KevinScript subscribes to a policy of radical compatibility. It ought to be able to run on any machine that has any Python distribution of 2.7 or higher. We don't want the user to have to download anything else. And anyway, implementing it the hard way builds character.
## Why are you doing this?
Working on this project primarily serves as a learning experience about the decisions and pitfalls of language design. Why does Python have two kinds of classes? Why does `this` in Javascript sometimes point to the Window object, and sometimes to the object the current method is called on? Trying to do these kinds of things your own way can give valuable insight into the thought process of the original devs, and convey a level of understanding greater than just from reading source code or blog posts.
## What's next?
In addition to perpetually improving the original interpreter, a number of possible spin-off projects are in the planning stage.  
JKevinScript - A KS interpreter written in Javascript. Will run in the browser.  
KSKevinScript - A KS interpreter written in KevinScript.  
Compiled KevinScript - compiles KS to C, which can then be compiled into an executable.  
## How can I contribute?
Please submit bug reports and feature requests on the Github Issues page. QA and Design eagerly await your feedback!  
We are not actively seeking code contributions at this time.

# Credits
Concept - Kevin  
Design - Kevin  
Development - Kevin  
Quality Assurance - Kevin  
Documentation - Kevin  
Branding - Kevin  
Public Relations - Kevin  
Help Desk - Kevin  
Catering - Kevin  
Technical advisors and emotional support - the fine members of SOPython  
