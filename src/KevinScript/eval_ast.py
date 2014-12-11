import ast
from ktypes import Function, KObject, KInt, KBool, KString, KList, KNone

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

def evaluate(node, scopes):
    def getVar(name):
        for scope in scopes[::-1]:
            if name in scope:
                return scope[name]
        raise Exception("Unrecognized name \"{}\"".format(name))

    def line(node):
        if isinstance(node, ast.Leaf):
            return node.token.position
        else:
            return line(node.children[0])

    statement_default_return_value = {"returning": False, "value": KNone}

    if isinstance(node, ast.Leaf):
        if node.token.klass.name == "number":
            return KInt(int(node.token.value))
        elif node.token.klass.name == "identifier":
            return getVar(node.token.value)
        elif node.token.klass.name == "string_literal":
            return KString(node.token.value[1:-1])
        else:
            raise Exception("evaluate not implemented yet for leaf {}".format(node.token))
    else:
        #classes that just pass its single child forward
        if node.klass in "Expression Value Enclosure Literal Atom Primary".split():
            return evaluate(node.children[0], scopes)

        #statements.
        #when evaluated, all statements should return one of two values:
        #{"returning": True, "value": returnValue} - when a `Return` statement was executed, and we need to move back up to the most recent function call
        #`statement_default_return_value` - when no return statement has been executed.
        if node.klass == "Statement":
            result = evaluate(node.children[0], scopes)
            if result["returning"]: return result
            return statement_default_return_value
        if node.klass == "StatementList":
            for child in node.children:
                ret = evaluate(child, scopes)
                if ret["returning"]:
                    return ret
            return statement_default_return_value
        elif node.klass == "AssignmentStatement":
            lhs, expression_node = node.children
            #identifier assignment
            if isinstance(lhs, ast.Leaf):
                scopes[-1][lhs.token.value] = evaluate(expression_node, scopes)
            #attribute assignment
            else:
                node = evaluate(lhs.children[0], scopes)
                attribute_name = lhs.children[1].token.value
                node.set_attribute(attribute_name, evaluate(expression_node, scopes))
            return statement_default_return_value
        elif node.klass == "PrintStatement":
            obj = evaluate(node.children[0], scopes)
            method = obj.get_attribute("__repr__")
            assert method, "object {} has no method __repr__".format(obj)
            result = method.eval(scopes, [])
            assert isinstance(result, KString), "expected repr to return KString, got {}".format(type(result))
            print result.value
            return statement_default_return_value
        elif node.klass == "ReturnStatement":
            value = evaluate(node.children[0], scopes)
            return {"returning": True, "value": value}
        elif node.klass == "WhileStatement":
            while True:
                cond = evaluate(node.children[0], scopes)
                if not isinstance(cond, KBool):
                    cond = cond.bool()
                if not cond.value: break
                result = evaluate(node.children[1], scopes)
                if result["returning"]: return result
            return statement_default_return_value
        #expression must evaluate to an object that has a `size` and `at` method
        elif node.klass == "ForStatement":
            identifier = node.children[0].token.value
            seq = evaluate(node.children[1], scopes)
            size = seq.get_attribute("size").eval(scopes, []).value
            for idx in range(size):
                item = seq.get_attribute("at").eval(scopes, [KInt(idx)])
                scopes[-1][identifier] = item
                result = evaluate(node.children[2], scopes)
                if result["returning"]: return result
            return statement_default_return_value
        elif node.klass == "IfStatement":
            cond = evaluate(node.children[0], scopes)
            if not isinstance(cond, KBool):
                cond = cond.bool()
            assert isinstance(cond, KBool), "expected KBool, got {}".format(type(cond))
            if cond.value:
                result = evaluate(node.children[1], scopes)
                if result["returning"]: return result
            elif len(node.children) > 2:
                result = evaluate(node.children[2], scopes)
                if result["returning"]: return result
            return statement_default_return_value
        if node.klass == "FunctionDeclarationStatement":
            #function statements, ex. `function frob(x){return x;}`, 
            #are just syntactic sugar for ex. `frob = function(x){return x;};`
            func = ast.Node("FunctionDeclaration", node.children[1:])
            id = node.children[0]
            assignment = ast.Node("AssignmentStatement", [id, func])
            return evaluate(assignment, scopes)
        if node.klass == "ExpressionStatement":
            evaluate(node.children[0], scopes)
            return statement_default_return_value
        elif node.klass == "EmptyStatement":
            return statement_default_return_value

        elif node.klass == "FunctionDeclaration":
            if len(node.children) > 1: #no arguments
                arguments = evaluate(node.children[0], scopes)
                body = node.children[1]
            else:
                arguments = []
                body = node.children[0]
            return Function(scopes, arguments, body)
        elif node.klass == "FunctionDeclarationArgumentList":
            first = node.children[0].token.value
            if len(node.children) == 1:
                return [first]
            else:
                return [first] + evaluate(node.children[1], scopes)
        
        #note: this only gets evaluated for AttributeRefs not belonging to an AssignmentStatement. 
        #Those nodes are handled specially in the AssignmentStatement block.
        elif node.klass == "AttributeRef":
            obj = evaluate(node.children[0], scopes)
            attribute_name = node.children[1].token.value
            return obj.get_attribute(attribute_name)
        elif node.klass == "Call":
            callable = evaluate(node.children[0], scopes)
            if len(node.children) == 1:
                arguments = []
            else:
                arguments = evaluate(node.children[1], scopes)
            if isinstance(callable, KObject):
                callable = callable.get_attribute("__call__")

            assert isinstance(callable, Function), "expected function, got {} at {}".format(callable, line(node))
            return callable.eval(scopes, arguments)
        elif node.klass == "ExpressionList":
            return [evaluate(child, scopes) for child in node.children]
        elif node.klass in "AddExpression CompExpression MultExpression".split():
            if len(node.children) == 1:
                return evaluate(node.children[0], scopes)
            else:
                left = evaluate(node.children[0], scopes)
                operator = node.children[1].token.value
                right = evaluate(node.children[2], scopes)
                func_name = {
                    "+": "__add__", 
                    "-": "__sub__",
                    "*": "__mul__",
                    "/": "__div__",
                    "%": "__mod__",
                    ">": "__gt__",
                    "<": "__lt__",
                    "==": "__eq__",
                    "!=": "__neq__"
                }[operator]
                method = left.get_attribute(func_name)
                assert method, "object {} has no method {}".format(left, func_name)
                
                return method.eval(scopes, [right])
        elif node.klass == "ListDisplay":
            items = []
            if node.children:
                items = evaluate(node.children[0], scopes)
            return KList(items)
        else:
            raise Exception("evaluate not implemented yet for node {}".format(node.klass))