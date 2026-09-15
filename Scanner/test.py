import sys
from scanner import scan


def expected(spec, line=1):
    return [(kind, lexeme, line) for kind, lexeme in spec] + [('EOF', '', line)]


CASES = [
    ('Basic Declaration', 'let score = 95;', expected([
        ('LET', 'let'), ('IDENTIFIER', 'score'), ('ASSIGN', '='),
        ('INTEGER', '95'), ('SEMICOLON', ';')])),
    ('Arithmetic', 'a+b-2*3/4', expected([
        ('IDENTIFIER', 'a'), ('PLUS', '+'), ('IDENTIFIER', 'b'),
        ('MINUS', '-'), ('INTEGER', '2'), ('MULTIPLY', '*'),
        ('INTEGER', '3'), ('DIVIDE', '/'), ('INTEGER', '4')])),
    ('Identifiers', 'x score2 abc123 Player2 Let LET iffy', expected([
        ('IDENTIFIER', word) for word in ['x', 'score2', 'abc123', 'Player2', 'Let', 'LET', 'iffy']])),
    ('Comparison Operators', '= == != < > <= >=', expected([
        ('ASSIGN', '='), ('EQUAL_EQUAL', '=='), ('NOT_EQUAL', '!='),
        ('LESS', '<'), ('GREATER', '>'), ('LESS_EQUAL', '<='), ('GREATER_EQUAL', '>=')])),
    ('Whitespace', ' \tlet\n\nx\t= 0;\n', [
        ('LET', 'let', 1), ('IDENTIFIER', 'x', 3), ('ASSIGN', '=', 3),
        ('INTEGER', '0', 3), ('SEMICOLON', ';', 3), ('EOF', '', 4)]),
    ('No-Whitespace Input', 'let x=5+10*2;', expected([
        ('LET', 'let'), ('IDENTIFIER', 'x'), ('ASSIGN', '='), ('INTEGER', '5'),
        ('PLUS', '+'), ('INTEGER', '10'), ('MULTIPLY', '*'), ('INTEGER', '2'), ('SEMICOLON', ';')])),
    ('Invalid Character', 'let x = 10 @ 5;', expected([
        ('LET', 'let'), ('IDENTIFIER', 'x'), ('ASSIGN', '='), ('INTEGER', '10'),
        ('ERROR', '@'), ('INTEGER', '5'), ('SEMICOLON', ';')])),
    ('Complete Program (PDF page 5)', 'let score = 80;\n\nif score >= 75 {\n    print score;\n}', [
        ('LET', 'let', 1), ('IDENTIFIER', 'score', 1), ('ASSIGN', '=', 1),
        ('INTEGER', '80', 1), ('SEMICOLON', ';', 1), ('IF', 'if', 3),
        ('IDENTIFIER', 'score', 3), ('GREATER_EQUAL', '>=', 3), ('INTEGER', '75', 3),
        ('LEFT_BRACE', '{', 3), ('PRINT', 'print', 4), ('IDENTIFIER', 'score', 4),
        ('SEMICOLON', ';', 4), ('RIGHT_BRACE', '}', 5), ('EOF', '', 5)]),
    ('All Keywords', 'let if else while print', expected([
        ('LET', 'let'), ('IF', 'if'), ('ELSE', 'else'), ('WHILE', 'while'), ('PRINT', 'print')])),
    ('All Delimiters', '(){},;', expected([
        ('LEFT_PAREN', '('), ('RIGHT_PAREN', ')'), ('LEFT_BRACE', '{'),
        ('RIGHT_BRACE', '}'), ('COMMA', ','), ('SEMICOLON', ';')])),
    ('Empty Input', '', [('EOF', '', 1)]),
    ('Only Whitespace', '\t \n\n', [('EOF', '', 3)]),
    ('Longest Match', '===!=>=<=!', expected([
        ('EQUAL_EQUAL', '=='), ('ASSIGN', '='), ('NOT_EQUAL', '!='),
        ('GREATER_EQUAL', '>='), ('LESS_EQUAL', '<='), ('ERROR', '!')])),
    ('Unsupported Decimal', '3.14', expected([
        ('INTEGER', '3'), ('ERROR', '.'), ('INTEGER', '14')])),
    ('ASCII Rules and Recovery', 'é_９@x', expected([
        ('ERROR', 'é'), ('ERROR', '_'), ('ERROR', '９'), ('ERROR', '@'), ('IDENTIFIER', 'x')])),
    ('Number-Word Boundary', '123abc -10 007', expected([
        ('INTEGER', '123'), ('IDENTIFIER', 'abc'), ('MINUS', '-'), ('INTEGER', '10'), ('INTEGER', '007')])),
    ('No Comment or String Syntax', '//"x"', expected([
        ('DIVIDE', '/'), ('DIVIDE', '/'), ('ERROR', '"'), ('IDENTIFIER', 'x'), ('ERROR', '"')])),
    ('Lexical Only, No Syntax Validation', 'print 6 + ;', expected([
        ('PRINT', 'print'), ('INTEGER', '6'), ('PLUS', '+'), ('SEMICOLON', ';')])),
    ('Errors Across Lines', '@\n!\nx', [
        ('ERROR', '@', 1), ('ERROR', '!', 2), ('IDENTIFIER', 'x', 3), ('EOF', '', 3)]),
    ('Strict Whitespace Contract', '\r\v\f', expected([
        ('ERROR', '\r'), ('ERROR', '\v'), ('ERROR', '\f')])),
]


def main():
    print('=' * 52)
    print('SCANNER LAB REFERENCE TEST REPORT')
    print('=' * 52)
    passed = 0
    for index, (name, source, wanted) in enumerate(CASES, 1):
        try:
            result = scan(source)
            assert isinstance(result, list), 'scan must return a list'
            actual = [(token.type, token.lexeme, token.line) for token in result]
            assert actual == wanted, f'Expected: {wanted!r}\nActual:   {actual!r}'
        except Exception as error:
            print(f'Test {index:02}: {name} FAIL\n  {error}')
        else:
            passed += 1
            print(f'Test {index:02}: {name} PASS')
    print('=' * 52)
    print(f'SUMMARY\nPassed: {passed}\nFailed: {len(CASES) - passed}\nTotal: {len(CASES)}')
    print('Status: ' + ('ALL TESTS PASSED' if passed == len(CASES) else 'TESTS FAILED'))
    print('=' * 52)
    return 0 if passed == len(CASES) else 1


if __name__ == '__main__':
    sys.exit(main())