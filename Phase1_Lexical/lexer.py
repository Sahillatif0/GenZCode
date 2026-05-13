"""Lexer for GenZ/Brainrot language.

Converts source code string into a stream of tokens.
"""

import sys
import os
from pathlib import Path

root = str(Path(__file__).resolve().parents[1])
if root not in sys.path:
    sys.path.insert(0, root)

from Phase1_Lexical import tokens
from Phase1_Lexical.tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Raised when the lexer encounters invalid input."""

    def __init__(self, message: str, line: int, column: int):
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class Lexer:
    """Tokenizes GenZ source code."""

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_column = 1

    def tokenize(self) -> list[Token]:
        """Convert source code into a list of tokens."""
        while not self._is_at_end():
            self.start = self.current
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, '', None, self.line, self.column))
        return self.tokens

    def _scan_token(self) -> None:
        """Scan a single token from the current position."""
        c = self._advance()

        match c:
            # Single character tokens
            case '+':
                self._add_token(TokenType.PLUS)
            case '-':
                self._add_token(TokenType.MINUS)
            case '*':
                self._add_token(TokenType.STAR)
            case '/':
                if self._peek() == '/':
                    # Comment: consume until end of line
                    while self._peek() != '\n' and not self._is_at_end():
                        self._advance()
                    # Comments are ignored
                else:
                    self._add_token(TokenType.SLASH)
            case '%':
                self._add_token(TokenType.PERCENT)
            case '(':
                self._add_token(TokenType.LPAREN)
            case ')':
                self._add_token(TokenType.RPAREN)
            case '{':
                self._add_token(TokenType.LBRACE)
            case '}':
                self._add_token(TokenType.RBRACE)
            case '[':
                self._add_token(TokenType.LBRACKET)
            case ']':
                self._add_token(TokenType.RBRACKET)
            case ';':
                self._add_token(TokenType.SEMI)
            case ',':
                self._add_token(TokenType.COMMA)
            case ':':
                self._add_token(TokenType.COLON)
            case '!':
                if self._match('='):
                    self._add_token(TokenType.NEQ)
                else:
                    self._add_token(TokenType.NOT)
            case '=':
                if self._match('='):
                    self._add_token(TokenType.EQ)
                else:
                    self._add_token(TokenType.ASSIGN)
            case '<':
                if self._match('='):
                    self._add_token(TokenType.LTE)
                else:
                    self._add_token(TokenType.LT)
            case '>':
                if self._match('='):
                    self._add_token(TokenType.GTE)
                else:
                    self._add_token(TokenType.GT)
            case '&':
                if self._match('&'):
                    self._add_token(TokenType.AND)
                else:
                    raise LexerError("Expected '&&' for logical AND", self.line, self.start_column)
            case '|':
                if self._match('|'):
                    self._add_token(TokenType.OR)
                else:
                    raise LexerError("Expected '||' for logical OR", self.line, self.start_column)
            case '"':
                self._string()
            case ' ' | '\t' | '\r':
                # Ignore whitespace
                pass
            case '\n':
                self.line += 1
                self.column = 1
            case _:
                if c.isdigit():
                    self._number()
                elif c.isalpha() or c == '_':
                    self._identifier()
                else:
                    raise LexerError(f"Unexpected character: '{c}'", self.line, self.start_column)

    def _string(self) -> None:
        """Parse a string literal with escape sequence support."""
        result = []
        while self._peek() != '"' and not self._is_at_end():
            c = self._peek()
            if c == '\n':
                self.line += 1
                self.column = 1
            if c == '\\' and self._peek_next() != '\0':
                self._advance()  # consume backslash
                esc = self._advance()
                if esc == 'n':
                    result.append('\n')
                elif esc == 't':
                    result.append('\t')
                elif esc == '\\':
                    result.append('\\')
                elif esc == '"':
                    result.append('"')
                elif esc == 'r':
                    result.append('\r')
                elif esc == '0':
                    result.append('\0')
                else:
                    result.append('\\')
                    result.append(esc)
            else:
                result.append(self._advance())

        if self._is_at_end():
            raise LexerError("Unterminated string literal", self.line, self.start_column)

        # Consume closing quote
        self._advance()

        # Build string value from parsed escape sequences
        value = ''.join(result)
        self._add_token(TokenType.STRING, value)

    def _number(self) -> None:
        """Parse a numeric literal."""
        while self._peek().isdigit():
            self._advance()

        # Handle decimal numbers
        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()  # consume '.'
            while self._peek().isdigit():
                self._advance()

        # Try to convert to int first, then float
        text = self.source[self.start : self.current]
        try:
            if '.' in text:
                value = float(text)
            else:
                value = int(text)
        except ValueError:
            raise LexerError(f"Invalid number: {text}", self.line, self.start_column)

        self._add_token(TokenType.NUMBER, value)

    def _identifier(self) -> None:
        """Parse an identifier or keyword."""
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        text = self.source[self.start : self.current]

        # Check if it's a keyword
        if text in KEYWORDS:
            token_type = KEYWORDS[text]
        else:
            token_type = TokenType.IDENT

        self._add_token(token_type)

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of source."""
        return self.current >= len(self.source)

    def _peek(self) -> str:
        """Look at the current character without consuming it."""
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        """Look at the next character."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        """Consume current char if it matches expected, return success."""
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        self.column += 1
        return True

    def _advance(self) -> str:
        """Consume a character and return it."""
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def _add_token(self, token_type: TokenType, literal: object = None) -> None:
        """Add a token to the list."""
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line, self.start_column))


def tokenize(source: str) -> list[Token]:
    """Convenience function to tokenize source code."""
    return Lexer(source).tokenize()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    else:
        source = '''
            lowkey x: num = 42;
            lowkey name: txt = "bruh";
            spill_tea(x);
            // this is a comment
            sus (x > 10) {
                spill_tea("big number fr fr");
            }
        '''

    lexer = Lexer(source)
    try:
        tokens = lexer.tokenize()
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
    except LexerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)