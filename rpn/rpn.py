#!/usr/bin/env python
# -*- coding: utf-8 -*-


import operator


class ParenthesesMismatchError(Exception):
    pass


LEFT = 0
RIGHT = 1


class Operator(object):
    def __init__(self,
                 symbol,
                 precedence=1,
                 associativity=LEFT,
                 args_count=2,
                 callback=lambda a, b: None):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity
        self.args_count = args_count
        self.callback = callback

    def weaker_than(self, op2):
        if self.associativity is LEFT and self.precedence == op2.precedence:
            return True
        return self.associativity is RIGHT and self.precedence < op2.precedence


LEFT_PARENTHESES = '('
RIGHT_PARENTHESES = ')'
PARENTHESES = LEFT_PARENTHESES + RIGHT_PARENTHESES


OPERATORS = {
    '^': Operator('^', 4, RIGHT, 2, lambda a, b: a ** b),
    '*': Operator('*', 3, LEFT, 2, operator.mul),
    '/': Operator('/', 3, LEFT, 2, operator.truediv),
    '+': Operator('+', 2, LEFT, 2, operator.add),
    '-': Operator('-', 2, LEFT, 2, operator.sub),
    'derp': Operator('derp', 4, LEFT, 2),
}


def tokenize_string(s):
    compound_data = []
    token_data = None
    for char in s:
        appending_to_compound_data = True
        if char == ' ':
            continue
        if any(char in group for group in (PARENTHESES, OPERATORS)):
            appending_to_compound_data = False
            token_data = char
        if appending_to_compound_data:
            compound_data.append(char)
            continue
        if compound_data:
            for chunk in ''.join(compound_data).split(','):
                yield chunk
            compound_data = []
        if token_data:
            yield token_data
    if compound_data:
        yield ''.join(compound_data)


class Node(object):
    def __init__(self, children=None, operator=None):
        self.children = children
        self.operator = operator

    def __repr__(self):
        return "<Node '%s' (%s)>" % \
            (self.operator.symbol, ', '.join(str(v) for v in self.children))

    def __str__(self):
        values = [str(v) for v in self.children]
        symbol = self.operator.symbol
        return '({0})'.format((' {0} '.format(symbol)).join(values))

    def calculate(self):
        args = []
        for child in self.children:
            if isinstance(child, Node):
                args.append(child.calculate())
            else:
                args.append(child)
        return self.operator.callback(*args)

    def __eq__(self, other):
        return self.children == other.children \
            and self.operator == other.operator


def shunting_yard(tokens):
    op_stack = []
    for token in tokens:
        if token in OPERATORS:
            op1 = OPERATORS.get(token)
            for _op in reversed(op_stack):
                op2 = OPERATORS.get(_op)
                if op2 is None:
                    break
                if op1.weaker_than(op2):
                    yield op_stack.pop()
            op_stack.append(token)
        elif token in LEFT_PARENTHESES:
            op_stack.append(token)
        elif token in RIGHT_PARENTHESES:
            matched = False
            for _ in reversed(op_stack):
                op = op_stack.pop()
                if op in LEFT_PARENTHESES:
                    matched = True
                    break
                yield op
            if not matched:
                raise ParenthesesMismatchError
        else:
            yield token
    if LEFT_PARENTHESES in op_stack:
        raise ParenthesesMismatchError
    while op_stack:
        yield op_stack.pop()


def rpn_to_ast(rpn_tokens):
    stack = []
    for token in rpn_tokens:
        op = OPERATORS.get(token)
        if op is not None:
            args = []
            for _ in range(op.args_count):
                args.append(stack.pop())
            node = Node(tuple(reversed(args)), op)
            stack.append(node)
        else:
            stack.append(float(token))
    return stack[0]


