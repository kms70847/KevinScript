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

        self.builtins["False"] = self.make_Object("Boolean")
        self.builtins["True"] = self.make_Object("Boolean")

        def call_type_instance(type_instance):
            ret = self.make_Object(type_instance["private"]["name"])
            init = self.get_attribute(ret, "__init__")
            assert init
            #todo: support for init functions with arguments
            self.eval_func(init)
            return ret
        def init_obj(obj, value):
            obj["private"]["value"] = value

        #append `~` to the name of your method if you don't want its return value to be run through `self.make`
        instance_methods = {
            "Object":{
                "__repr__": lambda obj: "<Object instance>",
                "__init__": lambda obj: None
            },
            "String":{
                "__init__": lambda obj: init_obj(obj, ""),
                "__repr__": lambda obj: obj["private"]["value"]
            },
            "Integer":{
                "__init__": lambda obj: init_obj(obj, 0),
                "__repr__": lambda obj: str(obj["private"]["value"]),
                "__lt__"  : lambda obj, other: obj["private"]["value"] < other["private"]["value"],
                "__gt__"  : lambda obj, other: obj["private"]["value"] > other["private"]["value"],
                "__eq__"  : lambda obj, other: obj["private"]["value"] == other["private"]["value"],
                "__add__" : lambda obj, other: obj["private"]["value"] + other["private"]["value"],
                "__sub__" : lambda obj, other: obj["private"]["value"] - other["private"]["value"],
                "__mul__" : lambda obj, other: obj["private"]["value"] * other["private"]["value"],
                "__div__" : lambda obj, other: obj["private"]["value"] / other["private"]["value"],
                "__mod__" : lambda obj, other: obj["private"]["value"] % other["private"]["value"]

            },
            "Boolean":{
                "__repr__": lambda obj: "True" if obj is self.builtins["True"] else "False"
            },
            "Type":{
                "__repr__": lambda obj: "<type '{}'>".format(obj["private"]["name"]),
                "__call__~": call_type_instance
            },
            "Nonetype":{
                "__repr__": lambda obj: "None"
            },
            "List":{
                "size": lambda obj: len(obj["private"]["items"]),
                "at~": lambda obj, idx: obj["private"]["items"][idx["private"]["value"]]
            }
        }

        #doesn't really need to be a function, since we use it only once,
        #but the alternative is to have rather ugly binding workarounds for `host_func` in the loop
        def register_method(type, method_name, host_func):
            if method_name.endswith("~"):
                method_name = method_name.rstrip("~")
                func = lambda scopes, *args: host_func(*args)
            else:
                func = lambda scopes, *args: self.make(host_func(*args))
            #accessing `func_code` doesn't necessarily work for all implementations of Python,
            #so so this section will need refactoring if we want radical compatibility in the future.
            num_args = host_func.func_code.co_argcount
            arg_names = host_func.func_code.co_varnames[:num_args]
            native_func = self.make_Function(func, arg_names)
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
        if isinstance(value, list):
            obj = self.make_Object("List")
            obj["private"]["items"] = value
            return obj

        if isinstance(value, bool):
            return self.builtins["True" if value else "False"]

        if value is None:
            return self.builtins["None"]

        #some types are just simple wrappers around host objects, with the value stored in the private dict.
        d = {str: "String", int: "Integer"}
        for host_type, native_type in d.iteritems():
            if isinstance(value, host_type):
                obj = self.make_Object(native_type)
                obj["private"]["value"] = value
                return obj

        raise Exception("No conversion found for type {}".format(type(value)))

    def get_attribute(self, obj, name):
        def iter_types(type):
            while True:
                yield type
                next = type["public"]["parent"]
                if next is self.builtins["None"]: break
                type = next

        """
        creates a version of `func` that already has `obj` bound to the first argument.
        """
        def create_bound_method(func, obj):
            arg_names = func["private"]["arguments"]
            body = lambda closure, *args: self.eval_func(func, None, (obj,) + args)
            return self.make_Function(body, arg_names[1:])
            
        #see if the attribute is directly on the object
        if name in obj["public"]:
            return obj[name]
        
        #see if the attribute is an instance method on the object's type chain
        for type in iter_types(obj["public"]["type"]):
            if "instance_methods" not in type["private"]:
                #this should only happen for poorly implemented built-in types
                raise Exception("type {} has no `instance_methods` collection".format(type["private"]["name"]))
            func = type["private"]["instance_methods"].get(name)
            if not func: continue
            return create_bound_method(func, obj)

        #Couldn't find the attribute!
        return None
            
    def has_attribute(self, obj, name):
        return self.get_attribute(obj, name) is not None