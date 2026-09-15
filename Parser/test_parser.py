"""
Automated reference test runner for Laboratory Exercise 03: Parser Lab.
Run:
    python test_parser.py
"""

import sys
from scanner import scan
from LabActivity.Parser.parser import (
    parse, Program, VariableDeclaration, Assignment,
    PrintStatement, IfStatement, WhileStatement, Block,
    IntegerLiteral, Identifier, BinaryExpression
)


def run_tests():
    passed = 0
    total = 0

    def assert_test(name, fn):
        nonlocal passed, total
        total += 1
        try:
            fn()
            print(f"Test {total:02}: {name} PASS")
            passed += 1
        except Exception as e:
            print(f"Test {total:02}: {name} FAIL\n  Error: {e}")

    # 1. Empty Program
    def test_empty():
        ast = parse(scan(""))
        assert isinstance(ast, Program) and ast.statements == [] and ast.line == 1

    # 2. Variable Declaration
    def test_decl():
        ast = parse(scan("let score = 95;"))
        expected = Program([
            VariableDeclaration("score", IntegerLiteral(95, 1), 1)
        ], 1)
        assert ast == expected

    # 3. Assignment
    def test_assign():
        ast = parse(scan("x = 10;"))
        expected = Program([
            Assignment("x", IntegerLiteral(10, 1), 1)
        ], 1)
        assert ast == expected

    # 4. Print Statement
    def test_print():
        ast = parse(scan("print score;"))
        expected = Program([
            PrintStatement(Identifier("score", 1), 1)
        ], 1)
        assert ast == expected

    # 5. Operator Precedence (Multiplication before Addition)
    def test_precedence():
        ast = parse(scan("let x = 2 + 3 * 4;"))
        expected = Program([
            VariableDeclaration(
                "x",
                BinaryExpression(
                    IntegerLiteral(2, 1),
                    "PLUS",
                    BinaryExpression(IntegerLiteral(3, 1), "MULTIPLY", IntegerLiteral(4, 1), 1),
                    1
                ),
                1
            )
        ], 1)
        assert ast == expected

    # 6. Parentheses Precedence Overriding
    def test_parentheses():
        ast = parse(scan("let x = (2 + 3) * 4;"))
        expected = Program([
            VariableDeclaration(
                "x",
                BinaryExpression(
                    BinaryExpression(IntegerLiteral(2, 1), "PLUS", IntegerLiteral(3, 1), 1),
                    "MULTIPLY",
                    IntegerLiteral(4, 1),
                    1
                ),
                1
            )
        ], 1)
        assert ast == expected

    # 7. Comparison and Equality
    def test_comp_equality():
        ast = parse(scan("let res = a >= 10 == b;"))
        expected = Program([
            VariableDeclaration(
                "res",
                BinaryExpression(
                    BinaryExpression(Identifier("a", 1), "GREATER_EQUAL", IntegerLiteral(10, 1), 1),
                    "EQUAL_EQUAL",
                    Identifier("b", 1),
                    1
                ),
                1
            )
        ], 1)
        assert ast == expected

    # 8. Block Scope
    def test_block():
        ast = parse(scan("{\n let x = 5;\n print x;\n}"))
        expected = Program([
            Block([
                VariableDeclaration("x", IntegerLiteral(5, 2), 2),
                PrintStatement(Identifier("x", 3), 3)
            ], 1)
        ], 1)
        assert ast == expected

    # 9. If Statement without Else
    def test_if():
        ast = parse(scan("if (x >= 10) {\n print x;\n}"))
        expected = Program([
            IfStatement(
                BinaryExpression(Identifier("x", 1), "GREATER_EQUAL", IntegerLiteral(10, 1), 1),
                Block([PrintStatement(Identifier("x", 2), 2)], 1),
                None,
                1
            )
        ], 1)
        assert ast == expected

    # 10. If-Else Statement
    def test_if_else():
        ast = parse(scan("if (x == 0) {\n print 1;\n} else {\n print 0;\n}"))
        expected = Program([
            IfStatement(
                BinaryExpression(Identifier("x", 1), "EQUAL_EQUAL", IntegerLiteral(0, 1), 1),
                Block([PrintStatement(IntegerLiteral(1, 2), 2)], 1),
                Block([PrintStatement(IntegerLiteral(0, 4), 4)], 3),
                1
            )
        ], 1)
        assert ast == expected

    # 11. While Statement
    def test_while():
        ast = parse(scan("while (x < 10) {\n x = x + 1;\n}"))
        expected = Program([
            WhileStatement(
                BinaryExpression(Identifier("x", 1), "LESS", IntegerLiteral(10, 1), 1),
                Block([
                    Assignment("x", BinaryExpression(Identifier("x", 2), "PLUS", IntegerLiteral(1, 2), 2), 2)
                ], 1),
                1
            )
        ], 1)
        assert ast == expected

    # 12. Nested Control Structures
    def test_nested():
        source = "while (x < 10) {\n if (x == 5) {\n print x;\n }\n x = x + 1;\n}"
        ast = parse(scan(source))
        assert isinstance(ast.statements[0], WhileStatement)
        assert isinstance(ast.statements[0].body.statements[0], IfStatement)

    # 13. Rejection of Unary Minus
    def test_unary_minus():
        try:
            parse(scan("let x = -10;"))
            raise AssertionError("Should reject unary minus")
        except SyntaxError:
            pass

    # 14. Rejection of Standalone Expressions
    def test_standalone_expr():
        try:
            parse(scan("2 + 3;"))
            raise AssertionError("Should reject standalone expression")
        except SyntaxError:
            pass

    # 15. Rejection of Chained Comparisons
    def test_chained_comp():
        try:
            parse(scan("if (1 < 2 < 3) {}"))
            raise AssertionError("Should reject chained comparisons")
        except SyntaxError:
            pass

    # 16. Rejection of Chained Equality
    def test_chained_eq():
        try:
            parse(scan("let x = a == b == c;"))
            raise AssertionError("Should reject chained equality")
        except SyntaxError:
            pass

    # 17. Rejection of Scanner ERROR Token
    def test_error_token():
        try:
            parse(scan("let x = 10 @ 5;"))
            raise AssertionError("Should reject scanner error token")
        except SyntaxError:
            pass

    # 18. Missing Semicolon Detection
    def test_missing_semicolon():
        try:
            parse(scan("let x = 10"))
            raise AssertionError("Should require semicolon")
        except SyntaxError:
            pass

    # 19. Missing Matching Parenthesis
    def test_missing_paren():
        try:
            parse(scan("print (2 + 3;"))
            raise AssertionError("Should require matching paren")
        except SyntaxError:
            pass

    # 20. Rejection of Trailing Tokens After EOF
    def test_trailing_tokens():
        tokens = scan("let x = 1;")
        from scanner import Token
        tokens.append(Token("SEMICOLON", ";", 1))
        try:
            parse(tokens)
            raise AssertionError("Should reject trailing tokens after EOF")
        except SyntaxError:
            pass

    print("=" * 52)
    print("PARSER LAB REFERENCE TEST REPORT")
    print("=" * 52)

    tests = [
        ("Empty Program", test_empty),
        ("Variable Declaration", test_decl),
        ("Assignment", test_assign),
        ("Print Statement", test_print),
        ("Operator Precedence", test_precedence),
        ("Parentheses Overriding", test_parentheses),
        ("Comparison and Equality", test_comp_equality),
        ("Block Scope", test_block),
        ("If Statement", test_if),
        ("If-Else Statement", test_if_else),
        ("While Statement", test_while),
        ("Nested Structures", test_nested),
        ("Rejection of Unary Minus", test_unary_minus),
        ("Rejection of Standalone Expressions", test_standalone_expr),
        ("Rejection of Chained Comparisons", test_chained_comp),
        ("Rejection of Chained Equality", test_chained_eq),
        ("Rejection of Scanner ERROR Token", test_error_token),
        ("Missing Semicolon Detection", test_missing_semicolon),
        ("Missing Parenthesis Detection", test_missing_paren),
        ("Trailing Tokens Rejection", test_trailing_tokens),
    ]

    for name, fn in tests:
        assert_test(name, fn)

    print("=" * 52)
    print(f"SUMMARY\nPassed: {passed}\nFailed: {total - passed}\nTotal: {total}")
    print("Status: " + ("ALL TESTS PASSED" if passed == total else "TESTS FAILED"))
    print("=" * 52)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_tests())