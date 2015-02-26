import ast
from kobjects import ObjectFactory

def extract_identifiers(node):
    if isinstance(node, ast.Leaf):
        if node.token.klass.name == "identifier":
            return [node.token.value]
        else:
            return []
    else:
        ret = []
        for child in node.children:
            ret = ret + extract_identifiers(child)
        return ret

def evaluate_function(func, scopes=None, argument_values=None):
    if scopes == None:
        scopes = []
    if argument_values == None:
        argument_values = []
    assert all(isinstance(value, dict) for value in argument_values), "expected native objects as arguments, got {} instead".format([type(x) for x in argument_values])

    if isinstance(func["private"]["body"], ast.Node):
        #pure KS func
        assert len(argument_values) == len(func["private"]["arguments"]), "expected {} argument(s) for function call, got {}".format(len(func["private"]["arguments"]), len(argument_values))
        locals = {}
        for i in range(len(argument_values)):
            name = func["private"]["arguments"][i]
            value = argument_values[i]
            locals[name] = value
        result = evaluate(
            func["private"]["body"], 
            func["private"]["closure"] + [locals]
        )
        return result["value"]
    else:
        #external code func
        return func["private"]["body"](scopes, *argument_values)

def get_type_name(obj):
    return obj["public"]["type"]["private"]["name"]

def evaluate(node, scopes=None):
    if scopes == None:
        scopes = [builtins]

    def get_var(name):
        for scope in scopes[::-1]:
            if name in scope:
                return scope[name]
        raise Exception("Unrecognized name \"{}\"".format(name))

    def line(node):
        if isinstance(node, ast.Leaf):
            return node.token.position
        else:
            return line(node.children[0])

    statement_default_return_value = {"returning": False, "value": builtins["None"]}

    if isinstance(node, ast.Leaf):
        if node.token.klass.name == "number":
            return objectFactory.make(int(node.token.value))
        elif node.token.klass.name == "identifier":
            return get_var(node.token.value)
        elif node.token.klass.name == "string_literal":
            return objectFactory.make(node.token.value[1:-1])
        else:
            raise Exception("evaluate not implemented yet for leaf {}".format(node.token))
    else:
        # classes that just pass its single child forward
        if node.klass in "Expression Value Enclosure Literal Atom Primary".split():
            return evaluate(node.children[0], scopes)

        # statements.
        # when evaluated, all statements should return one of two values:
        # {"returning": True, "value": return_value} - when a `Return` statement was executed, and we need to move back up to the most recent function call
        # `statement_default_return_value` - when no return statement has been executed.
        if node.klass == "Statement":
            result = evaluate(node.children[0], scopes)
            if result["returning"]:
                return result
            return statement_default_return_value
        elif node.klass == "StatementList":
            for child in node.children:
                ret = evaluate(child, scopes)
                if ret["returning"]:
                    return ret
            return statement_default_return_value
        elif node.klass == "AssignmentStatement":
            lhs, expression_node = node.children
            # identifier assignment
            if isinstance(lhs, ast.Leaf):
                scopes[-1][lhs.token.value] = evaluate(expression_node, scopes)
            # attribute assignment
            else:
                node = evaluate(lhs.children[0], scopes)
                attribute_name = lhs.children[1].token.value
                node["public"][attribute_name] = evaluate(expression_node, scopes)
            return statement_default_return_value
        elif node.klass == "PrintStatement":
            obj = evaluate(node.children[0], scopes)
            method = get_attribute(obj, "__repr__")
            assert method, "{} object has no method __repr__".format(get_type_name(obj))
            result = evaluate_function(method, scopes, [])
            assert get_type_name(result) == "String", "expected repr to return String, got {}".format(get_type_name(result))
            print(result["private"]["value"])
            return statement_default_return_value
        elif node.klass == "ReturnStatement":
            value = evaluate(node.children[0], scopes)
            return {"returning": True, "value": value}
        elif node.klass == "WhileStatement":
            while True:
                cond = evaluate(node.children[0], scopes)
                if not get_type_name(cond) == "Boolean":
                    cond = cond.bool()
                if cond is not builtins["True"]:
                    break
                result = evaluate(node.children[1], scopes)
                if result["returning"]:
                    return result
            return statement_default_return_value
        # expression must evaluate to an object that has a `size` and `at` method
        elif node.klass == "ForStatement":
            identifier = node.children[0].token.value
            seq = evaluate(node.children[1], scopes)
            size_func = get_attribute(seq, "size")
            at_func = get_attribute(seq, "at")
            assert size_func, "Can't iterate over type {} with no `size` function".format(get_type_name(seq))
            assert at_func, "Can't iterate over type {} with no `at` function".format(get_type_name(seq))
            size = evaluate_function(size_func, scopes, [])["private"]["value"]
            for idx in range(size):
                item = evaluate_function(at_func, scopes, [objectFactory.make(idx)])
                scopes[-1][identifier] = item
                result = evaluate(node.children[2], scopes)
                if result["returning"]:
                    return result
            return statement_default_return_value
        elif node.klass == "IfStatement":
            cond = evaluate(node.children[0], scopes)
            if not get_type_name(cond) == "Boolean":
                cond = cond.bool()
            assert get_type_name(cond) == "Boolean", "expected Boolean, got {}".format(get_type_name(cond))
            if cond is builtins["True"]:
                result = evaluate(node.children[1], scopes)
                if result["returning"]:
                    return result
            elif len(node.children) > 2:
                result = evaluate(node.children[2], scopes)
                if result["returning"]:
                    return result
            return statement_default_return_value
        elif node.klass == "FunctionDeclarationStatement":
            # function statements, ex. `function frob(x){return x;}`,
            # are just syntactic sugar for ex. `frob = function(x){return x;};`
            func = ast.Node("FunctionDeclaration", node.children[1:])
            id = node.children[0]
            assignment = ast.Node("AssignmentStatement", [id, func])
            return evaluate(assignment, scopes)
        elif node.klass == "ClassDeclarationStatement":
            #this is a pretty ugly implementation.
            #we tear apart the node structure so we can manually execute Type.__call__ with the proper arguments.
            #it would be preferable to just transform the node structure into the node structure for `name = Type(name, parent, [a,b,...])`
            #effectively making this whole statement into just syntactic sugar 
            #but it's a bit tricky to transform a node into a call expression, due to the twisty definition of the `Primary` node.
            name = objectFactory.make(node.children[0].token.value)
            if len(node.children) == 2:
                parent_name = "Object"
            else:
                parent_name = node.children[1].token.value
            parent_name = objectFactory.make(parent_name)
            declaration_list = node.children[-1]
            pairs = []
            for declaration_statement in declaration_list.children:
                func = ast.Node("FunctionDeclaration", node.children[1:])
                func = evaluate(func, scopes)
                id = objectFactory.make(node.children[0].token.value)
                pairs.append(id)
                pairs.append(func)
            pairs = objectFactory.make(list(pairs))
            evaluate_function(builtins["Type"]["private"]["instance_methods"]["__call__"], scopes, [builtins["Type"], name, parent_name, pairs])
            return statement_default_return_value
        elif node.klass == "ExpressionStatement":
            evaluate(node.children[0], scopes)
            return statement_default_return_value
        elif node.klass == "EmptyStatement":
            return statement_default_return_value

        elif node.klass == "FunctionDeclaration":
            if len(node.children) > 1:
                arguments = evaluate(node.children[0], scopes)
                body = node.children[1]
            else:  # no arguments
                arguments = []
                body = node.children[0]
            return objectFactory.make_Function(body, arguments, scopes)
        elif node.klass == "FunctionDeclarationArgumentList":
            return evaluate(node.children[0], scopes)

        # note: this only gets evaluated for AttributeRefs not belonging to an AssignmentStatement.
        # Those nodes are handled specially in the AssignmentStatement block.
        elif node.klass == "AttributeRef":
            obj = evaluate(node.children[0], scopes)
            attribute_name = node.children[1].token.value
            return get_attribute(obj, attribute_name)
        elif node.klass == "Call":
            callable = evaluate(node.children[0], scopes)
            if len(node.children) == 1:
                arguments = []
            else:
                arguments = evaluate(node.children[1], scopes)
            is_func = lambda obj: all(attr in obj["private"] for attr in ("body", "arguments", "closure"))
            while has_attribute(callable, "__call__") and not is_func(callable):
                callable = get_attribute(callable, "__call__")
            assert is_func(callable), "expected callable, got {} at {}".format(get_type_name(callable), line(node))
            try:
                return evaluate_function(callable, scopes, arguments)
            except:
                print "Couldn't call function on line {}".format(line(node))
                raise
        elif node.klass == "ExpressionList":
            return [evaluate(child, scopes) for child in node.children]
        elif node.klass == "IdentifierList":
            return [child.token.value for child in node.children]
        elif node.klass in "AddExpression CompExpression MultExpression".split():
            if len(node.children) == 1:
                return evaluate(node.children[0], scopes)
            else:
                left = evaluate(node.children[0], scopes)
                operator = node.children[1].children[0].klass
                right = evaluate(node.children[2], scopes)
                func_name = "__" + operator + "__"
                method = get_attribute(left, func_name)
                assert method, "object {} has no method {}".format(get_type_name(left), func_name)

                return evaluate_function(method, scopes, [right])
        elif node.klass == "ListDisplay":
            items = []
            if node.children:
                items = evaluate(node.children[0], scopes)
            return objectFactory.make(items)
        else:
            raise Exception("evaluate not implemented yet for node {}".format(node.klass))

objectFactory = ObjectFactory(evaluate_function)
builtins = objectFactory.builtins
get_attribute = objectFactory.get_attribute
has_attribute = objectFactory.has_attribute