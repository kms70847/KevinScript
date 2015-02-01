#kobjects.py - a replacement for the to-be-deprecated ktypes.py

import operator

#probably shouldn't have a singleton `builtins`, but we're not currently concerned with running multiple interpreter instances.
builtins = {}

make_blank = lambda: {"public": {}, "private": {}}

def connect(target, name, dest):
    builtins[target]["public"][name] = builtins[dest]

type_names = "Object Type Nonetype Function Boolean Integer String List Dict".split()

for name in type_names:
    builtins[name] = make_blank()
for name in type_names:
    connect(name, "type", "Type")
    connect(name, "parent", "Object")
    builtins[name]["private"]["name"] = name

builtins["None"] = make_blank()
connect("None", "type", "Nonetype")
connect("Object", "parent", "None")


#functions of the form make_*** are used by the host language to construct 
#object instances without having to invoke their type's `__call__` method.

def make_Object(type_name="Object"):
    ret = make_blank()
    ret["public"]["type"] = builtins[type_name]

    #we want to define a generic __repr__, but
    #we can't call `make_Function` without an infinite loop.
    #So we'll need to define the method manually.
    repr = {
        "private": {
            "closure":[], 
            "arguments":[], 
            "body": lambda closure: make_String("<{} instance>".format(type_name))
        },
        "public": {
            "type": builtins["Function"]
        }
    }
    repr["public"]["__repr__"] = repr

    ret["public"]["__repr__"] = repr
    return ret

#probably don't need this just yet
def make_Type(name, instance_methods):
    ret = make_Object("Type")
    ret["public"]["parent"] = builtins["Object"]
    ret["public"]["name"] = name
    ret["public"]["instance_methods"] = instance_methods
    return ret

def make_String(s=""):
    ret = make_Object("String")
    ret["private"]["value"] = s
    ret["public"]["__repr__"] = make_Function(lambda scopes: ret)
    return ret

def make_Integer(value=0):
    ret = make_Object("Integer")
    ret["private"]["value"] = value
    #uggggghhhh this syntax is so wordy
    #we only support ops between objects of the same type right now, but it might be nice to do more later
    ret["public"]["__lt__"]  = make_Function(lambda scopes, other: make_Boolean(ret["private"]["value"] <  other["private"]["value"]))
    ret["public"]["__gt__"]  = make_Function(lambda scopes, other: make_Boolean(ret["private"]["value"] >  other["private"]["value"]))
    ret["public"]["__eq__"]  = make_Function(lambda scopes, other: make_Boolean(ret["private"]["value"] == other["private"]["value"]))
    ret["public"]["__neq__"] = make_Function(lambda scopes, other: make_Boolean(ret["private"]["value"] != other["private"]["value"]))
    ret["public"]["__add__"] = make_Function(lambda scopes, other: make_Integer(ret["private"]["value"] + other["private"]["value"]))
    ret["public"]["__sub__"] = make_Function(lambda scopes, other: make_Integer(ret["private"]["value"] - other["private"]["value"]))
    ret["public"]["__mul__"] = make_Function(lambda scopes, other: make_Integer(ret["private"]["value"] * other["private"]["value"]))
    ret["public"]["__div__"] = make_Function(lambda scopes, other: make_Integer(ret["private"]["value"] / other["private"]["value"]))
    ret["public"]["__mod__"] = make_Function(lambda scopes, other: make_Integer(ret["private"]["value"] % other["private"]["value"]))
    ret["public"]["__repr__"] = make_Function(lambda scopes: make_String(str(ret["private"]["value"])))
    return ret

"""
Creates a function object.
`body` may be a host-language callable, or a StatementList ast.Node.
  if it is a host-language callable, its argument should be `closure`, and the remaining arguments should match the ones found in `arguments`.
`closure` should be a sequence of string:object dicts.
`arguments` should be a sequence of strings.
"""
def make_Function(body, arguments=None, closure=None):
    ret = make_Object("Function")
    if arguments is None:
        arguments = []
    if closure is None:
        closure = []
    assert all(isinstance(arg, str) for arg in arguments), "expected str, got {} instead".format(set(type(arg) for arg in arguments))
    ret["private"]["closure"] = closure
    ret["private"]["arguments"] = arguments
    ret["private"]["body"] = body
    return ret

def make_Boolean(value=False):
    ret = make_Object("Boolean")
    ret["private"]["value"] = value
    return ret

def make_List(items):
    ret = make_Object("Boolean")
    ret["private"]["items"] = items
    ret["public"]["size"] = make_Function(lambda scope: make_Integer(len(ret["private"]["items"])))
    ret["public"]["at"] = make_Function(lambda scope, idx: ret["private"]["items"][idx["private"]["value"]])
    ret["public"]["append"] = make_Function(lambda scope, value: [builtins["None"], items.append(value)][0])
    ret["public"]["pop"] = make_Function(lambda scope: [builtins["None"], items.pop()][0])
    return ret

for name in type_names:
    builtins[name]["public"]["__repr__"] = (lambda n=name: make_Function(lambda scopes: make_String("<type '{}'>".format(n))))()
builtins["None"]["public"]["__repr__"] = make_Function(lambda scopes: make_String("None"))

builtins["False"] = make_Boolean(False)
builtins["True"] = make_Boolean(True)
builtins["Object"]["public"]["__call__"] = make_Function(lambda scope: make_Object())