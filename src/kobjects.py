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
            self.builtins[name]["private"]["instance_methods"] = {}

        self.builtins["None"] = self.make_blank()
        connect("None", "type", "Nonetype")
        connect("Object", "parent", "None")

        self.builtins["False"] = self.make(False)
        self.builtins["True"] = self.make(True)

        obj_repr = lambda obj: self.eval_func(obj["public"]["__repr__"])["private"]["value"]

        instance_methods = {
            "Object":{
                "__repr__":  lambda obj: "<Object instance>"
            },
            "String":{
                "__repr__":  lambda obj: obj["private"]["value"]
            },
            "Integer":{
                "__repr__":  lambda obj: str(obj["private"]["value"])
            },
            "Type":{
                "__repr__":  lambda obj: "<type '{}'>".format(obj["private"]["name"])       
            },
            "Nonetype":{
                "__repr__":  lambda obj: "None"
            }
        }

        #doesn't really need to be a function, since we use it only once,
        #but the alternative is to have rather ugly binding workarounds for `host_func` in the loop
        def register_method(type, method_name, host_func):
            func = lambda scopes, *args: self.make(host_func(*args))
            #todo: support for builtin methods taking more than one argument
            native_func = self.make_Function(func, ["self"])
            self.builtins[type]["private"]["instance_methods"][method_name] = native_func

        for type, methods in instance_methods.iteritems():
            for method_name, host_func in methods.iteritems():
                register_method(type, method_name, host_func)

    #functions of the form make_*** are used by the host language to construct 
    #object instances without having to invoke their type's `__call__` method.

    #creates a nested dict which acts as the basis of all actual KS objects.
    def make_blank(self):
        return {"public": {}, "private": {}}

    def make_Object(self, type_name="Object"):
        ret = self.make_blank()
        ret["public"]["type"] = self.builtins[type_name]
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

    """
    turns a Python object into its equivalent KevinScript object.
    Works on built-in scalar types and most collections.
    Use `make_Function` for functions.
    """
    def make(self, value):
        
        d = {str: "String", int: "Integer"}
        for host_type, native_type in d.iteritems():
            if isinstance(value, host_type):
                obj = self.make_Object(native_type)
                obj["private"]["value"] = value
                return obj
        if isinstance(value, list):
            obj = self.make_Object("List")
            obj["private"]["items"] = value
            return obj

        raise Exception("No conversion found for type {}".format(type(value)))

