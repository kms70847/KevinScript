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


#helper function to transform AssignmentDeclarationStatements during `evaluate`
"""
creates an AssignmentStatement node of the form `className = Type('classname', parent, ['firstname', function(){...}, 'secondname', function(){...}]
arguments:
    class_name - the name of the class. Must be a Token.
    parent_name - the name of the class' parent. Must be a Token.
    function_names - a list of the class' methods' names. Must be Tokens.
    function_nodes - a list of the class' methods. Must be Nodes of the FunctionDeclaration klass.
"""
def make_type_call_node(class_name, parent_name, function_names, function_nodes):
    Node = ast.Node
    Leaf = ast.Leaf
    def make_string_literal_node(token):
        import lex
        token = token.copy()
        token.klass = lex.LiteralTokenRule("string_literal")
        return Node("Expression", [Node("CompExpression", [Node("AddExpression", [Node("MultExpression", [Node("Primary", [Node("Atom", [Node("Literal", [Leaf(token)])])])])])])])

    def make_identifier_node(token):
        return Node("Primary", [Node("Atom", [Leaf(token)])])

    def make_identifier_expression_node(token):
        primary = make_identifier_node(token)
        return Node("Expression", [Node("CompExpression", [Node("AddExpression", [Node("MultExpression", [primary])])])])

    def make_list_literal_node(value_nodes):
        return Node("Expression", [Node("CompExpression", [Node("AddExpression", [Node("MultExpression", [Node("Primary", [Node("Atom", [Node("Enclosure", [Node("ListDisplay", [Node("ExpressionList", value_nodes)])])])])])])])])

    def make_call_expression_node(obj, argument_nodes):
        expression_list = Node("ExpressionList", argument_nodes)
        return Node("Expression", [Node("CompExpression", [Node("AddExpression", [Node("MultExpression", [Node("Primary", [Node("Call", [obj, expression_list])])])])])])


    #I don't want to import `lex` just to create one token,
    #so we'll just copy an existing token and modify it for `Type`.
    type_class_identifier = class_name.copy()
    type_class_identifier.value = "Type"
    list_literal_contents = []
    for function_name, function_node in zip(function_names, function_nodes):
        list_literal_contents.append(make_string_literal_node(function_name))
        list_literal_contents.append(Node("Expression", [function_node]))
    return Node("Statement", [Node("AssignmentStatement", [
        Leaf(class_name),
        make_call_expression_node(
            make_identifier_node(type_class_identifier),
            [
                make_string_literal_node(class_name),
                make_identifier_expression_node(parent_name),
                make_list_literal_node(list_literal_contents)
            ]
        )
    ])])

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
            class_name = node.children[0].token
            if len(node.children) == 2: raise Exception("parent-less class declaration not implemented yet")
            parent_name = node.children[1].token
            function_names, function_nodes = [], []
            declaration_list = node.children[-1]
            for declaration_statement in declaration_list.children:
                name = declaration_statement.children[0].token
                func = ast.Node("FunctionDeclaration", declaration_statement.children[1:])
                function_names.append(name)
                function_nodes.append(func)
            type_call_node = make_type_call_node(class_name, parent_name, function_names, function_nodes)
            return evaluate(type_call_node, scopes)
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
            attr = get_attribute(obj, attribute_name)
            assert attr, "{} object has no attribute '{}'".format(get_type_name(obj), attribute_name)
            return attr
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