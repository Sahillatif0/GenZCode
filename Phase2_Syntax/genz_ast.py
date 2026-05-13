"""AST node definitions for GenZ/Brainrot language.

This module defines all AST node classes that represent the parsed
program structure.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# Base Node
# =============================================================================

class ASTNode(ABC):
    """Base class for all AST nodes."""

    @abstractmethod
    def accept(self, visitor: ASTVisitor):
        """Accept a visitor for the visitor pattern."""
        pass


class ASTVisitor(ABC):
    """Base class for AST visitors."""

    @abstractmethod
    def visit_program(self, node: Program) -> object:
        pass

    @abstractmethod
    def visit_var_decl(self, node: VarDecl) -> object:
        pass

    @abstractmethod
    def visit_func_decl(self, node: FuncDecl) -> object:
        pass

    @abstractmethod
    def visit_assignment(self, node: Assignment) -> object:
        pass

    @abstractmethod
    def visit_print_stmt(self, node: PrintStmt) -> object:
        pass

    @abstractmethod
    def visit_if_stmt(self, node: IfStmt) -> object:
        pass

    @abstractmethod
    def visit_switch_stmt(self, node: SwitchStmt) -> object:
        pass

    @abstractmethod
    def visit_while_stmt(self, node: WhileStmt) -> object:
        pass

    @abstractmethod
    def visit_for_stmt(self, node: ForStmt) -> object:
        pass

    @abstractmethod
    def visit_return_stmt(self, node: ReturnStmt) -> object:
        pass

    @abstractmethod
    def visit_break_stmt(self, node: BreakStmt) -> object:
        pass

    @abstractmethod
    def visit_continue_stmt(self, node: ContinueStmt) -> object:
        pass

    @abstractmethod
    def visit_expr_stmt(self, node: ExprStmt) -> object:
        pass

    @abstractmethod
    def visit_block(self, node: Block) -> object:
        pass

    @abstractmethod
    def visit_binary(self, node: Binary) -> object:
        pass

    @abstractmethod
    def visit_unary(self, node: Unary) -> object:
        pass

    @abstractmethod
    def visit_literal(self, node: Literal) -> object:
        pass

    @abstractmethod
    def visit_variable(self, node: Variable) -> object:
        pass

    @abstractmethod
    def visit_array_access(self, node: ArrayAccess) -> object:
        pass

    @abstractmethod
    def visit_array_literal(self, node: ArrayLiteral) -> object:
        pass

    @abstractmethod
    def visit_func_call(self, node: FuncCall) -> object:
        pass


# =============================================================================
# Program Root
# =============================================================================

@dataclass
class Program(ASTNode):
    """Root node of the AST representing a complete program."""

    statements: list[ASTNode]

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_program(self)


# =============================================================================
# Declarations
# =============================================================================

@dataclass
class VarDecl(ASTNode):
    """Variable declaration: lowkey x: num = expr;"""

    name: str
    type_name: str  # 'num', 'txt', or array type string
    initializer: Optional[Expr] = None

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_var_decl(self)


@dataclass
class FuncDecl(ASTNode):
    """Function declaration: vibe_check func(a: num, b: num) { ... }"""

    name: str
    params: list[FuncParam]
    return_type: Optional[str] = None
    body: Optional[Block] = None

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_func_decl(self)


@dataclass
class FuncParam:
    """Function parameter: name: type"""
    name: str
    type_name: str


# =============================================================================
# Statements
# =============================================================================

@dataclass
class Assignment(ASTNode):
    """Assignment statement: x = expr; or arr[i] = expr;"""

    target: Expr  # Variable or ArrayAccess
    value: Expr

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_assignment(self)


@dataclass
class PrintStmt(ASTNode):
    """Print statement: spill_tea(expr1, expr2, ...);"""

    arguments: list[Expr]

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_print_stmt(self)


@dataclass
class IfStmt(ASTNode):
    """If-else statement: sus (condition) { ... } deadass { ... }"""

    condition: Expr
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_if_stmt(self)


@dataclass
class WhileStmt(ASTNode):
    """While loop: keep_yapping (condition) { ... }"""

    condition: Expr
    body: ASTNode

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_while_stmt(self)


@dataclass
class ForStmt(ASTNode):
    """For loop: yapping_through (init; condition; update) { ... }"""

    init: Optional[ASTNode] = None
    condition: Optional[Expr] = None
    update: Optional[Expr] = None
    body: ASTNode = None

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_for_stmt(self)


@dataclass
class SwitchStmt(ASTNode):
    """Switch statement: ratio (expr) { bet value: { ... } nvm: { ... } }"""

    expression: Expr
    cases: list[tuple[Expr, list[ASTNode]]]  # list of (case_value, statements)
    default: Optional[list[ASTNode]] = None  # nvm case

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_switch_stmt(self)


@dataclass
class ReturnStmt(ASTNode):
    """Return statement: slay expr;"""

    value: Optional[Expr] = None

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_return_stmt(self)


@dataclass
class BreakStmt(ASTNode):
    """Break statement: bestie;"""

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_break_stmt(self)


@dataclass
class ContinueStmt(ASTNode):
    """Continue statement: its_giving;"""

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_continue_stmt(self)


@dataclass
class ExprStmt(ASTNode):
    """Expression statement (for function calls without semicolon in expression context)."""

    expression: Expr

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_expr_stmt(self)


@dataclass
class Block(ASTNode):
    """Block statement: { statement* }"""

    statements: list[ASTNode]

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_block(self)


# =============================================================================
# Expressions (all return a value)
# =============================================================================

class Expr(ASTNode):
    """Base class for all expressions."""
    pass


@dataclass
class Binary(Expr):
    """Binary operation: left op right"""

    left: Expr
    operator: str
    right: Expr

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_binary(self)


@dataclass
class Unary(Expr):
    """Unary operation: op operand"""

    operator: str
    operand: Expr

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_unary(self)


@dataclass
class Literal(Expr):
    """Literal value: number, string, boolean"""

    value: object  # int, float, str, bool

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_literal(self)


@dataclass
class Variable(Expr):
    """Variable reference: name"""

    name: str

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_variable(self)


@dataclass
class ArrayAccess(Expr):
    """Array element access: arr[index]"""

    array: Variable
    index: Expr

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_array_access(self)


@dataclass
class ArrayLiteral(Expr):
    """Array literal: [expr1, expr2, ...]"""

    elements: list[Expr]

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_array_literal(self)


@dataclass
class FuncCall(Expr):
    """Function call: name(arg1, arg2, ...)"""

    name: str
    arguments: list[Expr]

    def accept(self, visitor: ASTVisitor):
        return visitor.visit_func_call(self)