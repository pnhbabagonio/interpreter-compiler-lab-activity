"""
Laboratory Exercise 03: Building a Recursive-Descent Parser
Implements syntax analysis and AST generation for the programming language.
"""


# ---------------------------------------------------------------------------
# AST Node Definitions
# ---------------------------------------------------------------------------

class ASTNode:
    """Base class providing attribute inspection and equality comparison."""
    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False
        return vars(self) == vars(other)

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({attrs})"


class Program(ASTNode):
    def __init__(self, statements: list, line: int):
        self.kind = "Program"
        self.statements = statements
        self.line = line


class VariableDeclaration(ASTNode):
    def __init__(self, name: str, initializer: ASTNode, line: int):
        self.kind = "VariableDeclaration"
        self.name = name
        self.initializer = initializer
        self.line = line


class Assignment(ASTNode):
    def __init__(self, name: str, value: ASTNode, line: int):
        self.kind = "Assignment"
        self.name = name
        self.value = value
        self.line = line


class PrintStatement(ASTNode):
    def __init__(self, expression: ASTNode, line: int):
        self.kind = "PrintStatement"
        self.expression = expression
        self.line = line


class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: ASTNode, else_branch: ASTNode | None, line: int):
        self.kind = "IfStatement"
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        self.line = line


class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode, line: int):
        self.kind = "WhileStatement"
        self.condition = condition
        self.body = body
        self.line = line


class Block(ASTNode):
    def __init__(self, statements: list, line: int):
        self.kind = "Block"
        self.statements = statements
        self.line = line


class IntegerLiteral(ASTNode):
    def __init__(self, value: int, line: int):
        self.kind = "IntegerLiteral"
        self.value = value
        self.line = line


class Identifier(ASTNode):
    def __init__(self, name: str, line: int):
        self.kind = "Identifier"
        self.name = name
        self.line = line


class BinaryExpression(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int):
        self.kind = "BinaryExpression"
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line


# ---------------------------------------------------------------------------
# Recursive-Descent Parser Engine
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos >= len(self.tokens):
            raise SyntaxError("Unexpected end of token stream")
        token = self.tokens[self.pos]
        if token.type == "ERROR":
            raise SyntaxError(f"Line {token.line}: Lexical ERROR token encountered: {token.lexeme!r}")
        return token

    def check(self, token_type: str) -> bool:
        return self.peek().type == token_type

    def advance(self):
        token = self.peek()
        self.pos += 1
        return token

    def match(self, token_type: str):
        if self.check(token_type):
            return self.advance()
        return None

    def consume(self, token_type: str, message: str):
        token = self.peek()
        if token.type == token_type:
            return self.advance()
        raise SyntaxError(f"Line {token.line}: {message}. Found '{token.lexeme}' ({token.type})")

    # --- Grammar Rules ---

    def parse_program(self) -> Program:
        first_token = self.peek()
        program_line = first_token.line
        statements = []

        while not self.check("EOF"):
            statements.append(self.parse_statement())

        self.consume("EOF", "Expected EOF at end of input")

        if self.pos < len(self.tokens):
            raise SyntaxError(f"Line {self.tokens[self.pos].line}: Trailing tokens after EOF")

        return Program(statements=statements, line=program_line)

    def parse_statement(self) -> ASTNode:
        token = self.peek()
        if token.type == "LET":
            return self.parse_declaration()
        elif token.type == "IDENTIFIER":
            return self.parse_assignment()
        elif token.type == "PRINT":
            return self.parse_print_statement()
        elif token.type == "IF":
            return self.parse_if_statement()
        elif token.type == "WHILE":
            return self.parse_while_statement()
        elif token.type == "LEFT_BRACE":
            return self.parse_block()
        else:
            raise SyntaxError(f"Line {token.line}: Expected statement, found '{token.lexeme}' ({token.type})")

    def parse_declaration(self) -> VariableDeclaration:
        let_token = self.consume("LET", "Expected 'let'")
        name_token = self.consume("IDENTIFIER", "Expected identifier after 'let'")
        self.consume("ASSIGN", "Expected '=' after variable name")
        initializer = self.parse_expression()
        self.consume("SEMICOLON", "Expected ';' after variable declaration")
        return VariableDeclaration(name=name_token.lexeme, initializer=initializer, line=let_token.line)

    def parse_assignment(self) -> Assignment:
        id_token = self.consume("IDENTIFIER", "Expected identifier")
        self.consume("ASSIGN", "Expected '=' after identifier")
        value = self.parse_expression()
        self.consume("SEMICOLON", "Expected ';' after assignment")
        return Assignment(name=id_token.lexeme, value=value, line=id_token.line)

    def parse_print_statement(self) -> PrintStatement:
        print_token = self.consume("PRINT", "Expected 'print'")
        expr = self.parse_expression()
        self.consume("SEMICOLON", "Expected ';' after expression")
        return PrintStatement(expression=expr, line=print_token.line)

    def parse_if_statement(self) -> IfStatement:
        if_token = self.consume("IF", "Expected 'if'")
        self.consume("LEFT_PAREN", "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume("RIGHT_PAREN", "Expected ')' after condition")
        then_branch = self.parse_block()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.parse_block()
        return IfStatement(condition=condition, then_branch=then_branch, else_branch=else_branch, line=if_token.line)

    def parse_while_statement(self) -> WhileStatement:
        while_token = self.consume("WHILE", "Expected 'while'")
        self.consume("LEFT_PAREN", "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume("RIGHT_PAREN", "Expected ')' after condition")
        body = self.parse_block()
        return WhileStatement(condition=condition, body=body, line=while_token.line)

    def parse_block(self) -> Block:
        brace_token = self.consume("LEFT_BRACE", "Expected '{'")
        statements = []
        while not self.check("RIGHT_BRACE"):
            if self.check("EOF"):
                raise SyntaxError(f"Line {self.peek().line}: Expected '}}' before end of file")
            statements.append(self.parse_statement())
        self.consume("RIGHT_BRACE", "Expected '}'")
        return Block(statements=statements, line=brace_token.line)

    # --- Expressions (Enforcing Precedence & Non-Chaining Rules) ---

    def parse_expression(self) -> ASTNode:
        return self.parse_equality()

    def parse_equality(self) -> ASTNode:
        expr = self.parse_comparison()
        if self.check("EQUAL_EQUAL") or self.check("NOT_EQUAL"):
            op = self.advance()
            right = self.parse_comparison()
            expr = BinaryExpression(left=expr, operator=op.type, right=right, line=op.line)
        return expr

    def parse_comparison(self) -> ASTNode:
        expr = self.parse_term()
        if self.check("LESS") or self.check("LESS_EQUAL") or self.check("GREATER") or self.check("GREATER_EQUAL"):
            op = self.advance()
            right = self.parse_term()
            expr = BinaryExpression(left=expr, operator=op.type, right=right, line=op.line)
        return expr

    def parse_term(self) -> ASTNode:
        expr = self.parse_factor()
        while self.check("PLUS") or self.check("MINUS"):
            op = self.advance()
            right = self.parse_factor()
            expr = BinaryExpression(left=expr, operator=op.type, right=right, line=op.line)
        return expr

    def parse_factor(self) -> ASTNode:
        expr = self.parse_primary()
        while self.check("MULTIPLY") or self.check("DIVIDE"):
            op = self.advance()
            right = self.parse_primary()
            expr = BinaryExpression(left=expr, operator=op.type, right=right, line=op.line)
        return expr

    def parse_primary(self) -> ASTNode:
        token = self.peek()
        if token.type == "INTEGER":
            self.advance()
            return IntegerLiteral(value=int(token.lexeme), line=token.line)
        elif token.type == "IDENTIFIER":
            self.advance()
            return Identifier(name=token.lexeme, line=token.line)
        elif token.type == "LEFT_PAREN":
            self.advance()
            expr = self.parse_expression()
            self.consume("RIGHT_PAREN", "Expected ')' after expression")
            return expr
        else:
            raise SyntaxError(f"Line {token.line}: Expected expression, found '{token.lexeme}' ({token.type})")


def parse(tokens: list) -> Program:
    """Parses a stream of Token objects and returns a Program AST node."""
    if not tokens or tokens[-1].type != "EOF":
        raise SyntaxError("Token stream must end with an EOF token")
    parser = Parser(tokens)
    return parser.parse_program()