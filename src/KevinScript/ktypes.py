# built-in KevinScript types.

import eval_ast


# base class for all objects in KevinScript.
class KObject:
    def __init__(self, name="object"):
        self.attributes = {}
        self.name = name

    def set_attribute(self, name, obj):
        self.attributes[name] = obj

    def get_attribute(self, name):
        if name in self.attributes:
            return self.attributes[name]

        # for convenience, we'll let KBasic access some methods defined on this class.
        if name == "__repr__":
            return PyFunction(lambda scopes: self.repr())
        if name == "__hash__":
            return PyFunction(lambda scopes: self.hash())

        if name.startswith("__") and name.endswith("__") and len(name) > 4:
            names = "add sub mul div mod gt lt eq neq bool"
            stripped_name = name[2:-2]
            if stripped_name in names and hasattr(self, stripped_name):
                return PyFunction(lambda scopes, other: getattr(self, stripped_name)(other))

        # most objects report their type, but some don't (namely, base Objects don't).
        # This is because the type attribute is usually set in the __init__ method, but the ObjectType object doesn't exist when we initialize Objects for the first time.
        # This is a rather tricky dependency problem. Maybe implenting properties would help?
        type_name = self.attributes["type"].name if "type" in self.attributes else "unknown"
        raise Exception("no attribute {} found for {} object".format(name, type_name))

    def bool(self):
        return KTrue

    def repr(self):
        return KString("<{} instance at {}>".format(self.name, hex(id(self))))

    def hash(self):
        return KInt(hash(id(self)))

    def add(self, other):
        return self


# other primitive types
# there's some twisty dependencies here with regards to who is who's parent, etc, so we'll declare everything up front and modify their attributes later.
class KType(KObject):
    def __init__(self, name):
        KObject.__init__(self, name)

    def eq(self, other):
        if not isinstance(other, KType):
            return KFalse
        return to_KBool(self.name == other.name)

    def repr(self):
        return KString("<type '{}'>".format(self.name))

    def hash(self):
        return KInt(hash(self.name))

NoneType = KType("None")
ObjectType = KType("object")
TypeType = KType("type")
FunctionType = KType("function")
BoolType = KType("bool")
IntType = KType("int")
StringType = KType("string")
ListType = KType("list")
DictType = KType("dict")

# singleton None object. Required for defining the attributes of ObjectType.
KNone = KObject()
KNone.repr = lambda: KString("None")
KNone.attributes["type"] = NoneType

# type attributes
# NoneType is a bit odd since you can't actually instantiate a None.
# it's just there so that type(None) has a coherent result.
NoneType.attributes["type"] = TypeType
NoneType.attributes["parent"] = ObjectType
# todo: comparison operators

ObjectType.attributes["type"] = TypeType
ObjectType.attributes["parent"] = KNone
# todo: __call__ is a Function that returns an object instance.
# remember to set the "type" attribute to ObjectType.

TypeType.attributes["type"] = TypeType
TypeType.attributes["parent"] = ObjectType

# Like NoneType, functions can't be instantiated from FunctionType.
# It's just here so type(my_function) has a coherent result.
FunctionType.attributes["type"] = TypeType
FunctionType.attributes["parent"] = ObjectType

"""
functions have special behavior in regards to __call__.
`a.__call__ == a` for all functions `a`.
Ordinarily, when you call an object, the interpreter accesses the `__call__` attribute of that object and invokes it. For functions, however, the interpreter should ignore the __call__ attribute, and execute the Python-land method `eval` instead.
"""


# class used to instantiate KevinScript-land functions.
class Function(KObject):
    # closure is the list of scopes at time of declaration
    # arguments is a list of strings corresponding to identifiers
    # statements is a StatementList node representing the body of the function
    def __init__(self, closure, arguments, statements):
        KObject.__init__(self)
        self.attributes["type"] = FunctionType
        self.attributes["__call__"] = self
        self.closure = closure
        self.arguments = arguments
        self.statements = statements

    def eval(self, scopes, argument_values):
        locals = {}
        for i in range(len(self.arguments)):
            name = self.arguments[i]
            value = argument_values[i]
            locals[name] = value
        return eval_ast.evaluate(self.statements, self.closure + [locals])["value"]


# a function that can be bound to an identifier in KBasic.
# when the function is executed in the KBasic program, then the python code will execute.
# used primarily to implement built-in functions.
class PyFunction(Function):
    def __init__(self, func):
        KObject.__init__(self)
        self.attributes["type"] = FunctionType
        self.attributes["__call__"] = self
        self.func = func

    def eval(self, scopes, argument_values):
        return self.func(scopes, *argument_values)


class KBool(KObject):
    def __init__(self, value):
        KObject.__init__(self)
        self.attributes["type"] = BoolType
        self.value = bool(value)

    def bool(self):
        return to_KBool(self.value)

    def repr(self):
        return KString(self.value)


KTrue = KBool(True)
KFalse = KBool(False)
to_KBool = lambda value: KTrue if value else KFalse

IntType.attributes["type"] = TypeType
IntType.attributes["parent"] = ObjectType


class KInt(KObject):
    def __init__(self, value):
        KObject.__init__(self)
        self.attributes["type"] = IntType
        self.value = value

    def add(self, other):
        return KInt(self.value + other.value)

    def sub(self, other):
        return KInt(self.value - other.value)

    def mul(self, other):
        return KInt(self.value * other.value)

    def div(self, other):
        return KInt(self.value / other.value)

    def mod(self, other):
        return KInt(self.value % other.value)

    def eq(self, other):
        return to_KBool(self.value == other.value)

    def neq(self, other):
        return to_KBool(self.value != other.value)

    def gt(self, other):
        return to_KBool(self.value > other.value)

    def lt(self, other):
        return to_KBool(self.value < other.value)

    def bool(self):
        return to_KBool(bool(self.value))

    def repr(self):
        return KString(repr(self.value))

    def hash(self):
        return KInt(hash(self.value))


StringType.attributes["type"] = TypeType
StringType.attributes["parent"] = ObjectType


class KString(KObject):
    def __init__(self, value):
        KObject.__init__(self)
        self.attributes["type"] = StringType
        self.value = value

    def repr(self):
        return self

    def hash(self):
        return KInt(hash(self.value))


ListType.attributes["type"] = TypeType
ListType.attributes["parent"] = ObjectType


class KList(KObject):
    def __init__(self, items=None):
        KObject.__init__(self)
        self.attributes["type"] = ListType
        self.items = items if items is not None else []
        self.attributes["size"] = PyFunction(lambda scopes: KInt(len(self.items)))
        self.attributes["at"] = PyFunction(lambda scopes, idx: self.items[idx.value])
        self.attributes["set"] = PyFunction(lambda scopes, idx, value: self.set(idx, value))
        self.attributes["append"] = PyFunction(lambda scopes, item: self.append(item))
        self.attributes["pop"] = PyFunction(lambda scopes: self.pop())

    def set(self, idx, value):
        idx = idx.value
        self.items[idx] = value

    def append(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def repr(self):
        return KString("[" + ", ".join(item.repr().value for item in self.items) + "]")

    def bool(self):
        return to_KBool(bool(self.items))


DictType.attributes["type"] = TypeType
DictType.attributes["parent"] = ObjectType


class KDict(KObject):
    def __init__(self, data=None):
        KObject.__init__(self)
        self.attributes["type"] = DictType
        self.data = data if data is not None else {}
        self.attributes["at"] = PyFunction(lambda scopes, key: self.at(key))

    def at(self, obj):
        # not implemented yet
        pass
