class Token:
    def __init__(self, token_type, lexeme, line):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        return f'Token("{self.type}", "{self.lexeme}", {self.line})'


def scan(source: str):
    tokens = []
    current = 0
    line = 1

    keywords = {
        "let": "LET",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "print": "PRINT"
    }

    single_char_tokens = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE",
        "=": "ASSIGN",
        "<": "LESS",
        ">": "GREATER",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
        "{": "LEFT_BRACE",
        "}": "RIGHT_BRACE",
        ",": "COMMA",
        ";": "SEMICOLON"
    }

    while current < len(source):
        char = source[current]

        # Skip spaces and tabs
        if char == " " or char == "\t":
            current += 1
            continue

        # New line
        if char == "\n":
            line += 1
            current += 1
            continue

        # Identifier or keyword
        if ("a" <= char <= "z") or ("A" <= char <= "Z"):
            start = current

            current += 1

            while current < len(source):
                next_char = source[current]

                if (("a" <= next_char <= "z") or
                    ("A" <= next_char <= "Z") or
                    ("0" <= next_char <= "9")):
                    current += 1
                else:
                    break

            lexeme = source[start:current]

            if lexeme in keywords:
                token_type = keywords[lexeme]
            else:
                token_type = "IDENTIFIER"

            tokens.append(Token(token_type, lexeme, line))
            continue

        # Integer
        if "0" <= char <= "9":
            start = current

            current += 1

            while current < len(source):
                next_char = source[current]

                if "0" <= next_char <= "9":
                    current += 1
                else:
                    break

            lexeme = source[start:current]

            tokens.append(Token("INTEGER", lexeme, line))
            continue

        # Two-character comparison operators
        if char == "=":
            if current + 1 < len(source) and source[current + 1] == "=":
                tokens.append(Token("EQUAL_EQUAL", "==", line))
                current += 2
            else:
                tokens.append(Token("ASSIGN", "=", line))
                current += 1

            continue

        if char == "!":
            if current + 1 < len(source) and source[current + 1] == "=":
                tokens.append(Token("NOT_EQUAL", "!=", line))
                current += 2
            else:
                tokens.append(Token("ERROR", "!", line))
                current += 1

            continue

        if char == "<":
            if current + 1 < len(source) and source[current + 1] == "=":
                tokens.append(Token("LESS_EQUAL", "<=", line))
                current += 2
            else:
                tokens.append(Token("LESS", "<", line))
                current += 1

            continue

        if char == ">":
            if current + 1 < len(source) and source[current + 1] == "=":
                tokens.append(Token("GREATER_EQUAL", ">=", line))
                current += 2
            else:
                tokens.append(Token("GREATER", ">", line))
                current += 1

            continue

        # Single-character operators and delimiters
        if char in single_char_tokens:
            tokens.append(
                Token(single_char_tokens[char], char, line)
            )
            current += 1
            continue

        # Invalid character
        tokens.append(Token("ERROR", char, line))
        current += 1

    # End of file
    tokens.append(Token("EOF", "", line))

    return tokens