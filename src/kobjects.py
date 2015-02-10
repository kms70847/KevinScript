#kobjects.py - a replacement for the to-be-deprecated ktypes.py

import operator

class ObjectFactory:
    """arguments:
    eval_func - a function that takes a KS Function and executes it. Should have arguments (func, scopes, argument_values). (eval_ast.evaluate_function is a good candidate)
    """
    def __init__(self, eval_func):
        self.eval_func = eval_func
        self.builtins = {}

        def connect(target, name, dest):
            self.builtins[target]["public"][name] = self.builtins[dest]

        type_names = "Object Type Nonetype Function Boolean Integer String List Dict".split()

        for name in type_names:
            self.builtins[name] = self.make_blank()
        for name in type_names:
            connect(name, "type", "Type")
            connect(name, "parent", "Object")
            self.builtins[name]["private"]["name"] = name

        self.builtins["None"] = self.make_blank()
        connect("None", "type", "Nonetype")
        connect("Object", "parent", "None")

        for name in type_names:
            self.builtins[name]["public"]["__repr__"] = (lambda n=name: self.make_Function(lambda scopes: self.make_String("<type '{}'>".format(n))))()
        self.builtins["None"]["public"]["__repr__"] = self.make_Function(lambda scopes: self.make_String("None"))

        self.builtins["False"] = self.make_Boolean(False)
        self.builtins["True"] = self.make_Boolean(True)
        self.builtins["Object"]["public"]["__call__"] = self.make_Function(lambda scope: self.make_Object())

    #functions of the form make_*** are used by the host language to construct 
    #object instances without having to invoke their type's `__call__` method.

    #creates a nested dict which acts as the basis of all actual KS objects.
    def make_blank(self):
        return {"public": {}, "private": {}}

    def make_Object(self, type_name="Object"):
        ret = self.make_blank()
        ret["public"]["type"] = self.builtins[type_name]

        #we want to define a generic __repr__, but
        #we can't call `make_Function` without an infinite loop.
        #So we'll need to define the method manually.
        repr = {
            "private": {
                "closure":[], 
                "arguments":[], 
                "body": lambda closure: self.make_String("<{} instance>".format(type_name))
            },
            "public": {
                "type": self.builtins["Function"]
            }
        }
        repr["public"]["__repr__"] = repr

        ret["public"]["__repr__"] = repr
        return ret

    #probably don't need this just yet
    def make_Type(self, name, instance_methods):
        ret = self.make_Object("Type")
        ret["public"]["parent"] = self.builtins["Object"]
        ret["public"]["name"] = name
        ret["public"]["instance_methods"] = instance_methods
        return ret

    def make_String(self, s=""):
        ret = self.make_Object("String")
        ret["private"]["value"] = s
        ret["public"]["__repr__"] = self.make_Function(lambda scopes: ret)
        return ret

    def make_Integer(self, value=0):
        ret = self.make_Object("Integer")
        ret["private"]["value"] = value
        #we only support ops between objects of the same type right now, but it might be nice to do more later

        def assign_operator(name, op_func, return_type_make_func):
            value = lambda obj: obj["private"]["value"]
            ret["public"][name] = self.make_Function(lambda scopes, other: return_type_make_func(op_func(value(ret), value(other))))
        assign_operator("__lt__",  operator.lt, self.make_Boolean)
        assign_operator("__gt__",  operator.gt, self.make_Boolean)
        assign_operator("__eq__",  operator.eq, self.make_Boolean)
        assign_operator("__neq__", operator.ne, self.make_Boolean)
            
        assign_operator("__add__", operator.add, self.make_Integer)
        assign_operator("__sub__", operator.sub, self.make_Integer)
        assign_operator("__mul__", operator.mul, self.make_Integer)
        assign_operator("__div__", operator.div, self.make_Integer)
        assign_operator("__mod__", operator.mod, self.make_Integer)
        ret["public"]["__repr__"] = self.make_Function(lambda scopes: self.make_String(str(ret["private"]["value"])))
        return ret

    """
    Creates a function object.
    `body` may be a host-language callable, or a StatementList ast.Node.
      if it is a host-language callable, its argument should be `closure`, and the remaining arguments should match the ones found in `arguments`.
    `closure` should be a sequence of string:object dicts.
    `arguments` should be a sequence of strings.
    """
    def make_Function(self, body, arguments=None, closure=None):
        ret = self.make_Object("Function")
        if arguments is None:
            arguments = []
        if closure is None:
            closure = []
        assert all(isinstance(arg, str) for arg in arguments), "expected str, got {} instead".format(set(type(arg) for arg in arguments))
        ret["private"]["closure"] = closure
        ret["private"]["arguments"] = arguments
        ret["private"]["body"] = body
        return ret

    def make_Boolean(self, value=False):
        ret = self.make_Object("Boolean")
        ret["private"]["value"] = value
        ret["public"]["__repr__"] = self.make_Function(lambda scopes: self.make_String("True" if ret["private"]["value"] else "False"))
        return ret

    def make_List(self, items):
        ret = self.make_Object("List")
        ret["private"]["items"] = items
        ret["public"]["size"] = self.make_Function(lambda scope: self.make_Integer(len(ret["private"]["items"])))
        ret["public"]["at"] = self.make_Function(lambda scope, idx: ret["private"]["items"][idx["private"]["value"]])
        ret["public"]["append"] = self.make_Function(lambda scope, value: [self.builtins["None"], items.append(value)][0])
        ret["public"]["pop"] = self.make_Function(lambda scope: [self.builtins["None"], items.pop()][0])

        obj_repr = lambda obj: self.eval_func(obj["public"]["__repr__"])["private"]["value"]
        ret["public"]["__repr__"] = self.make_Function(lambda scope: self.make_String("[" + ", ".join(obj_repr(item) for item in items) + "]"))
        return ret

