#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from rpn.rpn import tokenize_string, OPERATORS, rpn_to_ast, shunting_yard, Node


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.s = '3 + 4* 2.0 / (1.-5) ^ 2 ^3'

    def test_tokenize_string(self):
        tokens = list(tokenize_string(self.s))
        expected = [
            '3', '+', '4', '*', '2.0', '/', '(', '1.', '-', '5', ')', '^', '2',
            '^', '3',
        ]
        self.assertSequenceEqual(tokens, expected)

    def test_shunting_yard(self):
        tokens = list(shunting_yard(tokenize_string(self.s)))
        expected = [
            '3', '4', '2.0', '*', '1.', '5', '-', '2', '3', '^', '^', '/', '+',
        ]
        self.assertSequenceEqual(tokens, expected)

    def test_rpn_to_ast(self):
        ast = rpn_to_ast(shunting_yard(tokenize_string(self.s)))
        # 4.0 * 2.0
        n1 = Node((4.0, 2.0), OPERATORS.get('*'))
        # 1.0 - 5.0
        n2 = Node((1.0, 5.0), OPERATORS.get('-'))
        # 2.0 ^ 3.0
        n3 = Node((2.0, 3.0), OPERATORS.get('^'))
        # (1.0 - 5.0) ^ (2.0 ^ 3.0)
        n4 = Node((n2, n3), OPERATORS.get('^'))
        # (4.0 * 2.0) / ((1.0 - 5.0) ^ (2.0 ^ 3.0))
        n5 = Node((n1, n4), OPERATORS.get('/'))
        # 3.0 + ((4.0 * 2.0) / ((1.0 - 5.0) ^ (2.0 ^ 3.0)))
        expected = Node((3.0, n5), OPERATORS.get('+'))
        self.assertEqual(ast, expected)

    def test_calculate_ast(self):
        ast = rpn_to_ast(shunting_yard(tokenize_string(self.s)))
        result = round(ast.calculate())
        expected = 3
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
