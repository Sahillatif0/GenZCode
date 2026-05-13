"""Recursive descent parser for GenZ/Brainrot language.

Converts a stream of tokens into an Abstract Syntax Tree (AST).
"""

import sys
import os
from pathlib import Path

# Add root to sys.path so we can find src
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Phase1_Lexical.lexer import Lexer, LexerError
from Phase1_Lexical.tokens import Token, TokenType
from Phase2_Syntax.genz_ast import (
    ASTNode, Program, VarDecl, FuncDecl, FuncParam, Assignment, PrintStmt,
    IfStmt, SwitchStmt, WhileStmt, ForStmt, ReturnStmt, BreakStmt, ContinueStmt, ExprStmt, Block,
    Binary, Unary, Literal, Variable, ArrayAccess, ArrayLiteral, FuncCall, Expr
)


class ParserError(Exception):
    """Raised when the parser encounters a syntax error."""

    def __init__(self, message: str, token: Token):
        self.token = token
        super().__init__(f"Parse error at '{token.lexeme}' (line {token.line}): {message}")


class Parser:
    """Recursive descent parser for GenZ language."""

    # Tokens that indicate the start of a new statement (synchronization set)
    STATEMENT_STARTERS = {
        TokenType.LOWKEY, TokenType.SPILL_TEA, TokenType.SUS,
        TokenType.KEEP_YAPPING, TokenType.YAPPING_THROUGH, TokenType.VIBE_CHECK,
        TokenType.SLAY, TokenType.BOUNCE, TokenType.NEXT_UP, TokenType.RATIO,
        TokenType.LBRACE, TokenType.RBRACE, TokenType.GOON,
        TokenType.TUNG_TUNG_TUNG_SAHUR, TokenType.SKIBIDI_TOILET,
        TokenType.OHIO, TokenType.GRIMACE_SHAKE, TokenType.EDGE,
    }

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors: list[ParserError] = []

    def parse(self) -> Program:
        """Parse the token stream into a Program AST."""
        statements: list[ASTNode] = []
        self.errors = []

        while not self._is_at_end():
            try:
                statements.append(self._statement())
            except ParserError as e:
                self.errors.append(e)
                self._synchronize()

        if self.errors:
            raise self.errors[0]

        return Program(statements=statements)

    # -------------------------------------------------------------------------
    # Declarations
    # -------------------------------------------------------------------------

    def _function_declaration(self) -> FuncDecl:
        """Parse: vibe_check ident ( params? ) { statements }"""
        # Note: vibe_check has already been consumed by the caller
        name = self._advance().lexeme
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parse_parameters()
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        self._consume(TokenType.LBRACE, "Expected '{' before function body")
        body = self._block()

        return FuncDecl(name=name, params=params, body=body)

    def _parse_parameters(self) -> list[FuncParam]:
        """Parse: param (',' param)*"""
        params: list[FuncParam] = []

        if not self._check(TokenType.RPAREN):
            while True:
                if self._check(TokenType.RPAREN):
                    break
                param_name = self._advance().lexeme
                self._consume(TokenType.COLON, "Expected ':' after parameter name")
                type_name = self._parse_type()
                params.append(FuncParam(name=param_name, type_name=type_name))

                if not self._match(TokenType.COMMA):
                    break

        return params

    def _variable_declaration(self) -> VarDecl:
        """Parse: lowkey ident ':' type ('=' expr)?"""
        name = self._advance().lexeme

        self._consume(TokenType.COLON, "Expected ':' after variable name")
        type_name = self._parse_type()

        initializer: Optional[Expr] = None
        if self._match(TokenType.ASSIGN):
            initializer = self._expression()

        self._consume(TokenType.SEMI, "Expected ';' after variable declaration")
        return VarDecl(name=name, type_name=type_name, initializer=initializer)

    def _parse_type(self) -> str:
        """Parse a type: num | txt | type[]"""
        if self._match(TokenType.NUM):
            base_type = "num"
        elif self._match(TokenType.TXT):
            base_type = "txt"
        else:
            raise self._error(f"Expected type (num or txt), got '{self._peek().lexeme}'")

        # Check for array suffix
        if self._match(TokenType.LBRACKET):
            self._consume(TokenType.RBRACKET, "Expected ']' after '[' in array type")
            return base_type + "[]"

        return base_type

    # -------------------------------------------------------------------------
    # Statements
    # -------------------------------------------------------------------------

    def _statement(self) -> ASTNode:
        """Parse any statement."""
        if self._match(TokenType.SPILL_TEA):
            return self._print_statement()
        elif self._match(TokenType.VIBE_CHECK):
            return self._function_declaration()
        elif self._match(TokenType.SUS):
            return self._if_statement()
        elif self._match(TokenType.KEEP_YAPPING):
            return self._while_statement()
        elif self._match(TokenType.YAPPING_THROUGH):
            return self._for_statement()
        elif self._match(TokenType.GOON):
            return self._goon_statement()
        elif self._match(TokenType.TUNG_TUNG_TUNG_SAHUR):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.RPAREN, "Expected ')' after 'tung_tung_tung_sahur'")
            self._consume(TokenType.SEMI, "Expected ';' after 'tung_tung_tung_sahur'")
            return PrintStmt(arguments=[Literal(value="Tung Tung Tung Sahur! Code is waking up...")])
        elif self._match(TokenType.SKIBIDI_TOILET):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.RPAREN, "Expected ')' after 'skibidi_toilet'")
            self._consume(TokenType.SEMI, "Expected ';' after 'skibidi_toilet'")
            return PrintStmt(arguments=[Literal(value="Memory flushed... clean as a whistle fr fr")])
        elif self._match(TokenType.OHIO):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.RPAREN, "Expected ')' after 'ohio'")
            self._consume(TokenType.SEMI, "Expected ';' after 'ohio'")
            return ExprStmt(expression=FuncCall(name="ohio", arguments=[]))
        elif self._match(TokenType.GRIMACE_SHAKE):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.RPAREN, "Expected ')' after 'grimace_shake'")
            self._consume(TokenType.SEMI, "Expected ';' after 'grimace_shake'")
            return ExprStmt(expression=FuncCall(name="grimace_shake", arguments=[]))
        elif self._match(TokenType.EDGE):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.RPAREN, "Expected ')' after 'edge'")
            self._consume(TokenType.SEMI, "Expected ';' after 'edge'")
            return PrintStmt(arguments=[Literal(value="Nearly there... edging the end...")])
        elif self._match(TokenType.SLAY):
            return self._return_statement()
        elif self._match(TokenType.BOUNCE):
            self._consume(TokenType.SEMI, "Expected ';' after 'bounce'")
            return BreakStmt()
        elif self._match(TokenType.NEXT_UP):
            self._consume(TokenType.SEMI, "Expected ';' after 'next_up'")
            return ContinueStmt()
        elif self._match(TokenType.RATIO):
            return self._switch_statement()
        elif self._match(TokenType.LBRACE):
            return self._block()
        elif self._match(TokenType.LOWKEY):
            return self._variable_declaration()
        else:
            # Could be an assignment or expression statement
            expr = self._expression()
            self._consume(TokenType.SEMI, "Expected ';' after expression")
            return ExprStmt(expression=expr)

    def _print_statement(self) -> PrintStmt:
        """Parse: spill_tea ( expr (',' expr)* ) ;"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'spill_tea'")

        arguments: list[Expr] = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        self._consume(TokenType.SEMI, "Expected ';' after 'spill_tea'")
        return PrintStmt(arguments=arguments)

    def _if_statement(self) -> IfStmt:
        """Parse: sus ( expr ) statement (deadass statement)?"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'sus'")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after condition")

        then_branch = self._statement()

        else_branch: Optional[ASTNode] = None
        if self._match(TokenType.DEADASS):
            else_branch = self._statement()

        return IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _while_statement(self) -> WhileStmt:
        """Parse: keep_yapping ( expr ) statement"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'keep_yapping'")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after condition")

        body = self._statement()

        return WhileStmt(condition=condition, body=body)

    def _for_statement(self) -> ForStmt:
        """Parse: yapping_through ( init ; condition ; update ) statement"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'yapping_through'")

        init: Optional[ASTNode] = None
        if not self._check(TokenType.SEMI):
            if self._match(TokenType.LOWKEY):
                init = self._variable_declaration()
            else:
                expr = self._expression()
                self._consume(TokenType.SEMI, "Expected ';' after for-loop init")
                init = ExprStmt(expression=expr)
        else:
            self._consume(TokenType.SEMI, "Expected ';' after for-loop init")

        condition: Optional[Expr] = None
        if not self._check(TokenType.SEMI):
            condition = self._expression()
        self._consume(TokenType.SEMI, "Expected ';' after for-loop condition")

        update: Optional[Expr] = None
        if not self._check(TokenType.RPAREN):
            update = self._expression()

        self._consume(TokenType.RPAREN, "Expected ')' after for-loop update")

        body = self._statement()

        return ForStmt(init=init, condition=condition, update=update, body=body)

    def _goon_statement(self) -> WhileStmt:
        """Parse: goon statement"""
        body = self._statement()
        return WhileStmt(condition=Literal(value=True), body=body)

    def _switch_statement(self) -> SwitchStmt:
        """Parse: ratio ( expr ) { bet value: statements nvm: statements }"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'ratio'")
        switch_expr = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after switch expression")
        self._consume(TokenType.LBRACE, "Expected '{' after switch")

        cases: list[tuple[Expr, list[ASTNode]]] = []
        default_case: Optional[list[ASTNode]] = None

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._match(TokenType.BET):
                # Case
                case_value = self._expression()
                self._consume(TokenType.COLON, "Expected ':' after case value")
                self._consume(TokenType.LBRACE, "Expected '{' after case colon")
                case_statements = self._parse_block_statements()
                cases.append((case_value, case_statements))
            elif self._match(TokenType.NVM):
                # Default case
                self._consume(TokenType.COLON, "Expected ':' after 'nvm'")
                self._consume(TokenType.LBRACE, "Expected '{' after nvm colon")
                default_case = self._parse_block_statements()
            else:
                raise self._error(f"Expected 'bet' or 'nvm' in switch, got '{self._peek().lexeme}'")

        self._consume(TokenType.RBRACE, "Expected '}' after switch")
        return SwitchStmt(expression=switch_expr, cases=cases, default=default_case)

    def _parse_block_statements(self) -> list[ASTNode]:
        """Parse statements until closing brace."""
        statements: list[ASTNode] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._statement())
        self._consume(TokenType.RBRACE, "Expected '}' after block")
        return statements

    def _return_statement(self) -> ReturnStmt:
        """Parse: slay expr? ;"""
        if self._check(TokenType.SEMI):
            self._advance()
            return ReturnStmt(value=None)

        value = self._expression()
        self._consume(TokenType.SEMI, "Expected ';' after 'slay'")
        return ReturnStmt(value=value)

    def _block(self) -> Block:
        """Parse: { statement* }"""
        statements: list[ASTNode] = []

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._statement())

        self._consume(TokenType.RBRACE, "Expected '}' after block")
        return Block(statements=statements)

    # -------------------------------------------------------------------------
    # Expressions (with precedence climbing)
    # -------------------------------------------------------------------------

    def _expression(self) -> Expr:
        """Parse an expression with lowest precedence."""
        return self._assignment()

    def _assignment(self) -> Expr:
        """Parse assignment expressions."""
        expr = self._or()

        if self._match(TokenType.ASSIGN):
            value = self._expression()
            # The target must be a Variable or ArrayAccess
            return Assignment(target=expr, value=value)

        return expr

    def _or(self) -> Expr:
        """Parse logical OR: and ('||' and)*"""
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous().lexeme
            right = self._and()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def _and(self) -> Expr:
        """Parse logical AND: equality ('&&' equality)*"""
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous().lexeme
            right = self._equality()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def _equality(self) -> Expr:
        """Parse equality: comparison (('==' | '!=') comparison)*"""
        expr = self._comparison()

        while self._match(TokenType.EQ, TokenType.NEQ):
            operator = self._previous().lexeme
            right = self._comparison()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def _comparison(self) -> Expr:
        """Parse comparison: term (('<' | '>' | '<=' | '>=') term)*"""
        expr = self._term()

        while self._match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            operator = self._previous().lexeme
            right = self._term()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def _term(self) -> Expr:
        """Parse addition/subtraction: factor (('+' | '-') factor)*"""
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().lexeme
            right = self._factor()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def _factor(self) -> Expr:
        """Parse multiplication/division/modulo: unary (('*' | '/' | '%') unary)*"""
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous().lexeme
            right = self._unary()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def _unary(self) -> Expr:
        """Parse unary: ('!' | '-')? primary"""
        if self._match(TokenType.NOT):
            operator = self._previous().lexeme
            operand = self._unary()
            return Unary(operator=operator, operand=operand)

        if self._match(TokenType.MINUS):
            operand = self._unary()
            return Unary(operator='-', operand=operand)

        return self._call()

    def _call(self) -> Expr:
        """Parse function calls: primary ( '(' args? ')' )?"""
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        """Finish parsing a function call."""
        arguments: list[Expr] = []

        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        return FuncCall(name=callee.name if isinstance(callee, Variable) else "<call>",
                       arguments=arguments)

    def _primary(self) -> Expr:
        """Parse primary expressions."""
        if self._match(TokenType.NUMBER):
            return Literal(value=self._previous().literal)

        if self._match(TokenType.STRING):
            return Literal(value=self._previous().literal)

        if self._match(TokenType.NO_CAP):
            return Literal(value=True)

        if self._match(TokenType.FR_FR):
            return Literal(value=False)

        if self._match(TokenType.LBRACKET):
            return self._array_literal()

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        if self._match(
            TokenType.IDENT,
            TokenType.RIZZ,
            TokenType.FANUM_TAX,
            TokenType.BALLERINA_CAPPUCCINA,
            TokenType.MEWING,
            TokenType.OHIO,
            TokenType.GRIMACE_SHAKE
        ):
            name = self._previous().lexeme

            # Check for array access: ident[expr]
            if self._match(TokenType.LBRACKET):
                index = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                array_var = Variable(name=name)
                return ArrayAccess(array=array_var, index=index)

            return Variable(name=name)

        raise self._error(f"Expected expression, got '{self._peek().lexeme}'")

    def _array_literal(self) -> ArrayLiteral:
        """Parse array literal: [ expr (',' expr)* ]"""
        elements: list[Expr] = []

        if not self._check(TokenType.RBRACKET):
            while True:
                elements.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RBRACKET, "Expected ']' after array elements")
        return ArrayLiteral(elements=elements)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the types and advance if so."""
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _check(self, type: TokenType) -> bool:
        """Check if current token is of given type without advancing."""
        if self._is_at_end():
            return False
        return self._peek().type == type

    def _advance(self) -> Token:
        """Advance and return the previous token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of tokens."""
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """Return current token without advancing."""
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """Return the most recently consumed token."""
        return self.tokens[self.current - 1]

    def _consume(self, type: TokenType, message: str) -> Token:
        """Consume a token of expected type or raise an error."""
        if self._check(type):
            return self._advance()
        raise self._error(message)

    def _error(self, message: str) -> ParserError:
        """Create a parser error at current token."""
        token = self._peek()
        return ParserError(message, token)

    def _synchronize(self) -> None:
        """Synchronize after an error by skipping tokens until a statement boundary."""
        self._advance()  # Skip the erroneous token

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMI:
                return

            if self._peek().type in self.STATEMENT_STARTERS:
                return

            self._advance()


def parse(source: str) -> Program:
    """Convenience function to parse source code."""
    from Phase1_Lexical.lexer import tokenize
    tokens = tokenize(source)
    return Parser(tokens).parse()


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
            sus (x > 10) {
                spill_tea("big number fr fr");
            }
        '''

    try:
        ast = parse(source)
        print("AST:")
        print(ast)
    except ParserError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)