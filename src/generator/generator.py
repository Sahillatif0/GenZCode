"""Code generator for GenZ/Brainrot language.

Generator Gary's work: translate the AST into Python code.
"""

from typing import Optional
from src.parser.ast import (
    ASTVisitor, Program, VarDecl, FuncDecl, FuncParam,
    Assignment, PrintStmt, IfStmt, SwitchStmt, WhileStmt, ForStmt, ReturnStmt,
    BreakStmt, ContinueStmt, ExprStmt, Block,
    Binary, Unary, Literal, Variable, ArrayAccess, ArrayLiteral, FuncCall
)


class CodeGenerator(ASTVisitor):
    """Generates Python code from GenZ AST."""

    INDENT = "    "

    def __init__(self):
        self.output: list[str] = []
        self.indent_level = 0
        self.in_loop = False

    def generate(self, ast: Program) -> str:
        """Generate Python code from the AST."""
        self.output = []
        self.indent_level = 0
        self.in_loop = False

        # Visit the program
        self.visit_program(ast)

        return '\n'.join(self.output)

    def _emit(self, code: str) -> None:
        """Add a line of code to the output."""
        indent = self.INDENT * self.indent_level
        self.output.append(f"{indent}{code}")

    def _emit_no_indent(self, code: str) -> None:
        """Add code without indentation."""
        self.output.append(code)

    # -------------------------------------------------------------------------
    # Visitor Methods
    # -------------------------------------------------------------------------

    def _emit_brainrot_helpers(self) -> None:
        """Emit helper functions for brainrot builtins."""
        self._emit_no_indent("import time")
        self._emit("")
        self._emit_no_indent("")
        self._emit("def ohio():")
        self.indent_level += 1
        self._emit('raise RuntimeError("Down in Ohio, swag like Ohio. Chaotic state detected!")')
        self.indent_level -= 1
        self._emit("")
        self._emit("def grimace_shake():")
        self.indent_level += 1
        self._emit('raise RuntimeError("Code poisoned by Grimace Shake! Fatal crash...")')
        self.indent_level -= 1
        self._emit("")
        self._emit("def ballerina_cappuccina():")
        self.indent_level += 1
        self._emit('return "Fancy Ballerina Cappuccina"')
        self.indent_level -= 1
        self._emit("")
        self._emit("def mewing(ms=1000.0):")
        self.indent_level += 1
        self._emit("time.sleep(ms / 1000.0)")
        self.indent_level -= 1
        self._emit("")
        self._emit("def rizz(val):")
        self.indent_level += 1
        self._emit("return float(val) + 10.0")
        self.indent_level -= 1
        self._emit("")
        self._emit("def fanum_tax(val):")
        self.indent_level += 1
        self._emit("return float(val) * 0.8")
        self.indent_level -= 1
        self._emit("")
        self._emit("def tung_tung_tung_sahur():")
        self.indent_level += 1
        self._emit('print("Tung Tung Tung Sahur! Code is waking up...")')
        self.indent_level -= 1
        self._emit("")
        self._emit("def skibidi_toilet():")
        self.indent_level += 1
        self._emit('print("Memory flushed... clean as a whistle fr fr")')
        self.indent_level -= 1
        self._emit("")
        self._emit("def edge():")
        self.indent_level += 1
        self._emit('print("Nearly there... edging the end...")')
        self.indent_level -= 1
        self._emit("")
        self._emit("")
        self.indent_level = 0

    def visit_program(self, node: Program) -> object:
        # Add Python shebang and imports
        self._emit_no_indent("# Generated Python code from GenZ/Brainrot language")
        self._emit_no_indent("import sys")
        self._emit("")

        self._emit_brainrot_helpers()

        # Track if we have a main function
        has_main = False
        for stmt in node.statements:
            self.visit(stmt)
            # Add blank line after function declarations
            if isinstance(stmt, FuncDecl):
                if stmt.name == "main":
                    has_main = True
                self._emit("")

        # Call main() if it exists
        if has_main:
            self._emit("if __name__ == '__main__':")
            self.indent_level += 1
            self._emit("main()")
            self.indent_level -= 1

        return None

    def visit_var_decl(self, node: VarDecl) -> object:
        # Generate: var_name = initial_value
        if node.initializer:
            value = self._generate_expr(node.initializer)
        else:
            # Default values based on type
            if node.type_name == "txt":
                value = '""'
            elif node.type_name.endswith("[]"):
                value = "[]"
            else:
                value = "0"

        self._emit(f"{node.name} = {value}")
        return None

    def visit_func_decl(self, node: FuncDecl) -> object:
        # Generate Python function
        params = ", ".join(p.name for p in node.params)
        self._emit(f"def {node.name}({params}):")

        self.indent_level += 1

        # Generate function body
        if node.body:
            for stmt in node.body.statements:
                self.visit(stmt)
        else:
            self._emit("pass")

        self.indent_level -= 1
        return None

    def visit_assignment(self, node: Assignment) -> object:
        target = self._generate_expr(node.target)
        value = self._generate_expr(node.value)
        self._emit(f"{target} = {value}")
        return None

    def visit_print_stmt(self, node: PrintStmt) -> object:
        # Generate: print(arg1, arg2, ...)
        args = [self._generate_expr(arg) for arg in node.arguments]
        self._emit(f"print({', '.join(args)})")
        return None

    def visit_if_stmt(self, node: IfStmt) -> object:
        condition = self._generate_expr(node.condition)

        self._emit(f"if {condition}:")
        self.indent_level += 1
        self.visit(node.then_branch)
        self.indent_level -= 1

        if node.else_branch:
            self._emit("else:")
            self.indent_level += 1
            self.visit(node.else_branch)
            self.indent_level -= 1

        return None

    def visit_switch_stmt(self, node: SwitchStmt) -> object:
        switch_expr = self._generate_expr(node.expression)
        self._emit(f"_switch_value = {switch_expr}")

        # Generate if-elif chain for cases
        first = True
        for case_value, case_stmts in node.cases:
            case_expr = self._generate_expr(case_value)
            if first:
                self._emit(f"if _switch_value == {case_expr}:")
                first = False
            else:
                self._emit(f"elif _switch_value == {case_expr}:")

            self.indent_level += 1
            for stmt in case_stmts:
                self.visit(stmt)
            self.indent_level -= 1

        # Default case
        if node.default:
            self._emit("else:")
            self.indent_level += 1
            for stmt in node.default:
                self.visit(stmt)
            self.indent_level -= 1

        return None

    def visit_while_stmt(self, node: WhileStmt) -> object:
        condition = self._generate_expr(node.condition)
        # Remove outer parentheses for cleaner output
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1]

        self._emit(f"while {condition}:")
        self.indent_level += 1
        old_in_loop = self.in_loop
        self.in_loop = True
        self.visit(node.body)
        self.in_loop = old_in_loop
        self.indent_level -= 1

        return None

    def visit_for_stmt(self, node: ForStmt) -> object:
        init_code = ""
        if node.init:
            if isinstance(node.init, VarDecl):
                value = self._generate_expr(node.init.initializer) if node.init.initializer else ("0" if node.init.type_name == "num" else '""' if node.init.type_name == "txt" else "[]")
                init_code = f"{node.init.name} = {value}"
            elif isinstance(node.init, ExprStmt):
                init_code = self._generate_expr(node.init.expression)

        cond_code = self._generate_expr(node.condition) if node.condition else "True"
        if cond_code.startswith("(") and cond_code.endswith(")"):
            cond_code = cond_code[1:-1]

        update_code = ""
        if node.update:
            update_code = self._generate_expr(node.update)

        if init_code:
            self._emit(init_code)

        self._emit(f"while {cond_code}:")
        self.indent_level += 1
        old_in_loop = self.in_loop
        self.in_loop = True
        self.visit(node.body)
        if update_code:
            self._emit(update_code)
        self.in_loop = old_in_loop
        self.indent_level -= 1

        return None

    def visit_return_stmt(self, node: ReturnStmt) -> object:
        if node.value:
            value = self._generate_expr(node.value)
            self._emit(f"return {value}")
        else:
            self._emit("return")
        return None

    def visit_break_stmt(self, node: BreakStmt) -> object:
        self._emit("break")
        return None

    def visit_continue_stmt(self, node: ContinueStmt) -> object:
        self._emit("continue")
        return None

    def visit_expr_stmt(self, node: ExprStmt) -> object:
        if isinstance(node.expression, FuncCall):
            fn = node.expression
            if fn.name in ('rizz', 'fanum_tax') and fn.arguments:
                arg = fn.arguments[0]
                if isinstance(arg, Variable):
                    arg_code = self._generate_expr(arg)
                    if fn.name == 'rizz':
                        self._emit(f"{arg_code} = {arg_code} + 10.0")
                    else:
                        self._emit(f"{arg_code} = {arg_code} * 0.8")
                    return None
            expr_code = self._generate_expr(node.expression)
            self._emit(expr_code)
        else:
            expr_code = self._generate_expr(node.expression)
            self._emit(expr_code)
        return None

    def visit_block(self, node: Block) -> object:
        for stmt in node.statements:
            self.visit(stmt)
        return None

    # -------------------------------------------------------------------------
    # Expression Generation
    # -------------------------------------------------------------------------

    def _generate_expr(self, expr) -> str:
        """Generate Python code for an expression."""
        if isinstance(expr, Literal):
            if isinstance(expr.value, bool):
                return "True" if expr.value else "False"
            elif isinstance(expr.value, str):
                return repr(expr.value)
            else:
                return str(expr.value)

        elif isinstance(expr, Variable):
            return expr.name

        elif isinstance(expr, ArrayAccess):
            array_name = expr.array.name
            index = self._generate_expr(expr.index)
            return f"{array_name}[{index}]"

        elif isinstance(expr, ArrayLiteral):
            elements = [self._generate_expr(e) for e in expr.elements]
            return f"[{', '.join(elements)}]"

        elif isinstance(expr, Binary):
            left = self._generate_expr(expr.left)
            right = self._generate_expr(expr.right)
            # Convert GenZ operators to Python
            op = expr.operator
            if op == '&&':
                op = 'and'
            elif op == '||':
                op = 'or'
            return f"({left} {op} {right})"

        elif isinstance(expr, Unary):
            operand = self._generate_expr(expr.operand)
            if expr.operator == "!":
                return f"(not {operand})"
            else:
                return f"(-{operand})"

        elif isinstance(expr, FuncCall):
            args = [self._generate_expr(arg) for arg in expr.arguments]
            return f"{expr.name}({', '.join(args)})"

        elif isinstance(expr, Assignment):
            target = self._generate_expr(expr.target)
            value = self._generate_expr(expr.value)
            # For simple assignments like x = value, don't add extra parens
            # Just return the assignment expression (used in expression contexts)
            return f"{target} = {value}"

        else:
            return "<unknown_expr>"

    # -------------------------------------------------------------------------
    # Expression visitors (for AST traversal)
    # -------------------------------------------------------------------------

    def visit_binary(self, node: Binary) -> object:
        return self._generate_expr(node)

    def visit_unary(self, node: Unary) -> object:
        return self._generate_expr(node)

    def visit_literal(self, node: Literal) -> object:
        return self._generate_expr(node)

    def visit_variable(self, node: Variable) -> object:
        return self._generate_expr(node)

    def visit_array_access(self, node: ArrayAccess) -> object:
        return self._generate_expr(node)

    def visit_array_literal(self, node: ArrayLiteral) -> object:
        return self._generate_expr(node)

    def visit_func_call(self, node: FuncCall) -> object:
        return self._generate_expr(node)

    def visit(self, node) -> object:
        """Visit a node (dispatch to appropriate method)."""
        return node.accept(self)


def generate_python(ast: Program) -> str:
    """Convenience function to generate Python code."""
    return CodeGenerator().generate(ast)


if __name__ == "__main__":
    import sys
    from src.lexer import tokenize
    from src.parser.parser import Parser
    from src.semantic.analyzer import SemanticAnalyzer

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    else:
        source = 'spill_tea("Hello from standalone generator!");'

    try:
        tokens = tokenize(source)
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        code = generate_python(ast)
        print("--- Generated Python Code ---")
        print(code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)