"""Semantic analyzer for GenZ/Brainrot language.

Semantic Sam's work: type checking, scope management, and validation.
"""

from typing import Optional
from src.parser.ast import (
    ASTVisitor, Program, VarDecl, FuncDecl, FuncParam,
    Assignment, PrintStmt, IfStmt, SwitchStmt, WhileStmt, ForStmt, ReturnStmt,
    BreakStmt, ContinueStmt, ExprStmt, Block,
    Binary, Unary, Literal, Variable, ArrayAccess, ArrayLiteral, FuncCall, Expr
)
from .symbol_table import SymbolTable, SemanticError, TypeInfo, parse_type


class SemanticAnalyzer(ASTVisitor):
    """Performs semantic analysis on the AST."""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function: Optional[FuncDecl] = None
        self.errors: list[SemanticError] = []

    def analyze(self, ast: Program) -> SymbolTable:
        """Run semantic analysis on the AST."""
        # Reset state
        self.symbol_table = SymbolTable()
        self.current_function = None
        self.errors = []

        # Register built-in functions
        self._register_builtins()

        # First pass: collect all function declarations
        for stmt in ast.statements:
            if isinstance(stmt, FuncDecl):
                self._declare_function(stmt)

        # Second pass: analyze all statements
        for stmt in ast.statements:
            try:
                self.visit(stmt)
            except SemanticError as e:
                self.errors.append(e)

        if self.errors:
            raise self.errors[0]

        return self.symbol_table

    def _declare_function(self, func: FuncDecl) -> None:
        """Register a function without analyzing its body yet."""
        param_types = [parse_type(p.type_name) for p in func.params]
        return_type = parse_type(func.return_type) if func.return_type else None

        self.symbol_table.define_function(
            name=func.name,
            return_type=return_type,
            param_types=param_types
        )

    def _declare_builtin_function(self, name: str, param_count: int = -1) -> None:
        """Register a built-in function."""
        is_variadic = param_count < 0
        if is_variadic:
            param_types = []
        else:
            param_types = [TypeInfo(base_type="num") for _ in range(param_count)]
        self.symbol_table.define_function(
            name=name,
            return_type=TypeInfo(base_type="num"),
            param_types=param_types,
            is_variadic=is_variadic,
            is_builtin=True
        )

    def _register_builtins(self) -> None:
        """Register all built-in functions."""
        builtins = {
            'print': 0, 'len': 1, 'str': 1, 'num': 1,
            'range': -1, 'abs': 1, 'pow': 2, 'sqrt': 1,
            'input': 0,
            'ohio': 0, 'grimace_shake': 0, 'mewing': -1,
            'fanum_tax': 1, 'rizz': 1, 'ballerina_cappuccina': 0
        }
        for name, param_count in builtins.items():
            self._declare_builtin_function(name, param_count)

    def _get_expr_type(self, expr: Expr) -> TypeInfo:
        """Infer the type of an expression."""
        if isinstance(expr, Literal):
            if isinstance(expr.value, bool):
                return TypeInfo(base_type="num")  # booleans are num
            elif isinstance(expr.value, (int, float)):
                return TypeInfo(base_type="num")
            elif isinstance(expr.value, str):
                return TypeInfo(base_type="txt")
            else:
                return TypeInfo(base_type="num")

        elif isinstance(expr, Variable):
            symbol = self.symbol_table.lookup(expr.name)
            if symbol is None:
                raise SemanticError(f"Undefined variable: '{expr.name}'")
            return symbol.type_info

        elif isinstance(expr, ArrayAccess):
            array_symbol = self.symbol_table.lookup(expr.array.name)
            if array_symbol is None:
                raise SemanticError(f"Undefined array: '{expr.array.name}'")
            if not array_symbol.type_info.is_array:
                raise SemanticError(f"'{expr.array.name}' is not an array")

            # Validate index type
            index_type = self._get_expr_type(expr.index)
            if index_type.base_type != "num":
                raise SemanticError("Array index must be numeric")

            return TypeInfo(base_type=array_symbol.type_info.base_type)

        elif isinstance(expr, ArrayLiteral):
            if not expr.elements:
                raise SemanticError("Array literal cannot be empty")
            # All elements should have the same type
            return TypeInfo(base_type="num", is_array=True)

        elif isinstance(expr, Assignment):
            # Assignments evaluate to the value being assigned
            return self._get_expr_type(expr.value)

        elif isinstance(expr, Binary):
            left_type = self._get_expr_type(expr.left)
            right_type = self._get_expr_type(expr.right)

            # String concatenation
            if expr.operator == '+' and left_type.base_type == "txt":
                return left_type

            # Arithmetic operations
            if expr.operator in ['+', '-', '*', '/', '%']:
                if left_type.base_type != "num" or right_type.base_type != "num":
                    raise SemanticError(f"Cannot perform '{expr.operator}' on non-numeric types")
                return TypeInfo(base_type="num")

            # Comparison and logical operations
            if expr.operator in ['<', '>', '<=', '>=', '==', '!=', '&&', '||']:
                return TypeInfo(base_type="num")

            raise SemanticError(f"Unknown binary operator: '{expr.operator}'")

        elif isinstance(expr, Unary):
            if expr.operator == '!':
                return TypeInfo(base_type="num")
            elif expr.operator == '-':
                operand_type = self._get_expr_type(expr.operand)
                if operand_type.base_type != "num":
                    raise SemanticError("Cannot negate non-numeric value")
                return TypeInfo(base_type="num")

        elif isinstance(expr, FuncCall):
            func_symbol = self.symbol_table.lookup_function(expr.name)
            if func_symbol is None:
                raise SemanticError(f"Undefined function: '{expr.name}'")
            if not func_symbol.is_function:
                raise SemanticError(f"'{expr.name}' is not a function")
            return func_symbol.return_type or TypeInfo(base_type="num")

        raise SemanticError(f"Unknown expression type: {type(expr)}")

    # -------------------------------------------------------------------------
    # Visitor Methods
    # -------------------------------------------------------------------------

    def visit_program(self, node: Program) -> object:
        for stmt in node.statements:
            self.visit(stmt)
        return None

    def visit_var_decl(self, node: VarDecl) -> object:
        type_info = parse_type(node.type_name)
        symbol = self.symbol_table.define_variable(node.name, type_info)

        if node.initializer:
            init_type = self._get_expr_type(node.initializer)

            # Check type compatibility
            if type_info.is_array and isinstance(node.initializer, ArrayLiteral):
                pass  # Array literal assignment is fine
            elif type_info.is_array != init_type.is_array:
                raise SemanticError(
                    f"Cannot assign {init_type} to {type_info}"
                )
            elif type_info.base_type != init_type.base_type:
                raise SemanticError(
                    f"Type mismatch: expected {type_info}, got {init_type}"
                )

        return None

    def visit_func_decl(self, node: FuncDecl) -> object:
        # Enter function scope
        self.symbol_table.push_scope(name=node.name)

        # Set current function
        old_function = self.current_function
        self.current_function = node

        # Define parameters in scope
        for param in node.params:
            type_info = parse_type(param.type_name)
            self.symbol_table.define_variable(param.name, type_info)

        # Analyze body
        if node.body:
            for stmt in node.body.statements:
                self.visit(stmt)

        # Exit function scope
        self.symbol_table.pop_scope()
        self.current_function = old_function

        return None

    def visit_assignment(self, node: Assignment) -> object:
        target_type = self._get_expr_type(node.target)
        value_type = self._get_expr_type(node.value)

        if target_type.base_type != value_type.base_type:
            raise SemanticError(
                f"Type mismatch: cannot assign {value_type} to {target_type}"
            )

        return None

    def visit_print_stmt(self, node: PrintStmt) -> object:
        for arg in node.arguments:
            self._get_expr_type(arg)  # Validate expression
        return None

    def visit_if_stmt(self, node: IfStmt) -> object:
        # Check condition type
        cond_type = self._get_expr_type(node.condition)

        # Enter new scope for if block
        self.symbol_table.push_scope(name="if")
        self.visit(node.then_branch)
        self.symbol_table.pop_scope()

        # Else branch (if present)
        if node.else_branch:
            self.symbol_table.push_scope(name="else")
            self.visit(node.else_branch)
            self.symbol_table.pop_scope()

        return None

    def visit_switch_stmt(self, node: SwitchStmt) -> object:
        # Analyze switch expression
        switch_type = self._get_expr_type(node.expression)

        # Analyze each case
        for case_value, case_stmts in node.cases:
            case_type = self._get_expr_type(case_value)
            for stmt in case_stmts:
                self.visit(stmt)

        # Analyze default case
        if node.default:
            for stmt in node.default:
                self.visit(stmt)

        return None

    def visit_while_stmt(self, node: WhileStmt) -> object:
        # Check condition type
        cond_type = self._get_expr_type(node.condition)

        # Enter loop scope
        self.symbol_table.enter_loop()
        self.symbol_table.push_scope(name="while")

        # Analyze body
        self.visit(node.body)

        # Exit loop scope
        self.symbol_table.pop_scope()
        self.symbol_table.exit_loop()

        return None

    def visit_for_stmt(self, node: ForStmt) -> object:
        # Enter a scope for the for-loop (init variable should be scoped here)
        self.symbol_table.push_scope(name="for")

        # Analyze init
        if node.init:
            self.visit(node.init)

        # Check condition type
        if node.condition:
            self._get_expr_type(node.condition)

        # Enter loop scope for body
        self.symbol_table.enter_loop()
        self.symbol_table.push_scope(name="for_body")

        # Analyze update
        if node.update:
            self._get_expr_type(node.update)

        # Analyze body
        self.visit(node.body)

        # Exit loop and for scopes
        self.symbol_table.pop_scope()
        self.symbol_table.exit_loop()
        self.symbol_table.pop_scope()

        return None

    def visit_return_stmt(self, node: ReturnStmt) -> object:
        if self.current_function is None:
            raise SemanticError("'slay' outside of function")

        expected_type = None
        if self.current_function.return_type:
            expected_type = parse_type(self.current_function.return_type)

        if node.value is None:
            if expected_type is not None:
                raise SemanticError(f"Function must return {expected_type}")
        else:
            actual_type = self._get_expr_type(node.value)
            if expected_type and actual_type.base_type != expected_type.base_type:
                raise SemanticError(
                    f"Return type mismatch: expected {expected_type}, got {actual_type}"
                )

        return None

    def visit_break_stmt(self, node: BreakStmt) -> object:
        if not self.symbol_table.in_loop():
            raise SemanticError("'bounce' must be inside a loop")
        return None

    def visit_continue_stmt(self, node: ContinueStmt) -> object:
        if not self.symbol_table.in_loop():
            raise SemanticError("'next_up' must be inside a loop")
        return None

    def visit_expr_stmt(self, node: ExprStmt) -> object:
        # For expressions, do full analysis
        if isinstance(node.expression, FuncCall):
            return self.visit_func_call(node.expression)
        else:
            self._get_expr_type(node.expression)
        return None

    def visit_block(self, node: Block) -> object:
        for stmt in node.statements:
            self.visit(stmt)
        return None

    def visit_binary(self, node: Binary) -> object:
        self._get_expr_type(node)
        return None

    def visit_unary(self, node: Unary) -> object:
        self._get_expr_type(node)
        return None

    def visit_literal(self, node: Literal) -> object:
        self._get_expr_type(node)
        return None

    def visit_variable(self, node: Variable) -> object:
        self._get_expr_type(node)
        return None

    def visit_array_access(self, node: ArrayAccess) -> object:
        # Validate index type (done by _get_expr_type)
        self._get_expr_type(node)
        return None

    def visit_array_literal(self, node: ArrayLiteral) -> object:
        self._get_expr_type(node)
        return None

    def visit_func_call(self, node: FuncCall) -> object:
        # Check function exists
        func_symbol = self.symbol_table.lookup_function(node.name)
        if func_symbol is None:
            raise SemanticError(f"Undefined function: '{node.name}'")

        # Check argument count
        if not func_symbol.is_variadic and len(node.arguments) != len(func_symbol.param_types):
            raise SemanticError(
                f"Function '{node.name}' expects {len(func_symbol.param_types)} "
                f"arguments, got {len(node.arguments)}"
            )

        # Check argument types
        for i, (arg, expected) in enumerate(zip(node.arguments, func_symbol.param_types)):
            actual = self._get_expr_type(arg)
            if actual.base_type != expected.base_type:
                raise SemanticError(
                    f"Argument {i+1} to '{node.name}': expected {expected}, got {actual}"
                )

        return None

    def visit(self, node) -> object:
        """Visit a node (dispatch to appropriate method)."""
        return node.accept(self)


if __name__ == "__main__":
    import sys
    from src.lexer import tokenize
    from src.parser.parser import Parser

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    else:
        source = '''
            lowkey x: num = 42;
            lowkey name: txt = "bruh";
            vibe_check main() {
                spill_tea(x);
            }
        '''

    try:
        tokens = tokenize(source)
        ast = Parser(tokens).parse()
        analyzer = SemanticAnalyzer()
        symbol_table = analyzer.analyze(ast)
        print("Semantic analysis passed!")
        print()
        print(symbol_table.to_display_string())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)