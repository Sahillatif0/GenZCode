"""Symbol table and scope management for GenZ/Brainrot language.

Semantic Sam's domain: tracking variable and function symbols,
managing scopes, and type information.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TypeInfo:
    """Type information for symbols."""
    base_type: str  # 'num', 'txt'
    is_array: bool = False
    array_size: Optional[int] = None  # None means dynamic size

    def __str__(self) -> str:
        if self.is_array:
            return f"{self.base_type}[]"
        return self.base_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeInfo):
            return False
        return (self.base_type == other.base_type and
                self.is_array == other.is_array)


@dataclass
class Symbol:
    """A symbol in the symbol table."""
    name: str
    type_info: TypeInfo
    is_function: bool = False
    is_variadic: bool = False
    is_constant: bool = False
    param_types: list[TypeInfo] = field(default_factory=list)
    return_type: Optional[TypeInfo] = None
    defined: bool = False


class Scope:
    """A scope that holds symbols."""

    def __init__(self, parent: Optional[Scope] = None, name: str = "global"):
        self.parent = parent
        self.name = name
        self.symbols: dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> None:
        """Add a symbol to this scope."""
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope or parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope only (no parent)."""
        return self.symbols.get(name)

    def is_defined(self, name: str) -> bool:
        """Check if a symbol is defined in any scope."""
        return self.lookup(name) is not None


class SymbolTable:
    """Main symbol table managing all scopes."""

    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        self.loop_depth = 0  # Track nested loops for break/continue
        self._scope_history: list[Scope] = []  # Keep all scopes for inspection
        self._builtin_names: set[str] = set()  # Track which functions are builtins

    def push_scope(self, name: str = "local") -> Scope:
        """Enter a new scope."""
        new_scope = Scope(parent=self.current_scope, name=name)
        self._scope_history.append(new_scope)
        self.current_scope = new_scope
        return new_scope

    def pop_scope(self) -> Scope:
        """Exit current scope and return to parent."""
        if self.current_scope.parent is None:
            raise RuntimeError("Cannot pop global scope")
        self.current_scope = self.current_scope.parent
        return self.current_scope

    def define_variable(self, name: str, type_info: TypeInfo) -> Symbol:
        """Define a variable in the current scope."""
        if self.current_scope.lookup_local(name) is not None:
            raise SemanticError(f"Variable '{name}' already defined in this scope")
        symbol = Symbol(name=name, type_info=type_info, defined=True)
        self.current_scope.define(symbol)
        return symbol

    def define_function(self, name: str, return_type: Optional[TypeInfo],
                       param_types: list[TypeInfo], is_variadic: bool = False,
                       is_builtin: bool = False) -> Symbol:
        """Define a function (in global scope)."""
        # Check if already defined
        existing = self.global_scope.lookup(name)
        if existing and existing.is_function and existing.defined and not is_builtin:
            raise SemanticError(f"Function '{name}' already defined")

        symbol = Symbol(
            name=name,
            type_info=TypeInfo(base_type="function"),
            is_function=True,
            is_variadic=is_variadic,
            defined=True,
            param_types=param_types,
            return_type=return_type
        )
        self.global_scope.define(symbol)
        if is_builtin:
            self._builtin_names.add(name)
        return symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in all scopes."""
        return self.current_scope.lookup(name)

    def lookup_function(self, name: str) -> Optional[Symbol]:
        """Look up a function (in global scope only)."""
        return self.global_scope.lookup(name)

    def enter_loop(self) -> None:
        """Enter a loop (for break/continue validation)."""
        self.loop_depth += 1

    def exit_loop(self) -> None:
        """Exit a loop."""
        self.loop_depth -= 1

    def in_loop(self) -> bool:
        """Check if currently inside a loop."""
        return self.loop_depth > 0

    def get_variables(self) -> list[dict]:
        """Get all user-defined variables from global scope."""
        variables = []
        for name, symbol in self.global_scope.symbols.items():
            if not symbol.is_function:
                variables.append({
                    'name': name,
                    'type': str(symbol.type_info),
                    'is_constant': symbol.is_constant
                })
        return variables

    def get_functions(self) -> list[dict]:
        """Get all user-defined functions from global scope."""
        functions = []
        for name, symbol in self.global_scope.symbols.items():
            if symbol.is_function and name not in self._builtin_names:
                param_types = [str(pt) for pt in symbol.param_types]
                return_type = str(symbol.return_type) if symbol.return_type else "void"
                functions.append({
                    'name': name,
                    'params': param_types,
                    'return_type': return_type,
                    'is_variadic': symbol.is_variadic
                })
        return functions

    def get_builtins(self) -> list[dict]:
        """Get all built-in functions."""
        builtins = [
            {'name': 'print', 'params': ['...'], 'return_type': 'void', 'is_builtin': True},
            {'name': 'len', 'params': ['txt/num[]'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'str', 'params': ['num'], 'return_type': 'txt', 'is_builtin': True},
            {'name': 'num', 'params': ['txt'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'range', 'params': ['num', 'num'], 'return_type': 'num[]', 'is_builtin': True},
            {'name': 'abs', 'params': ['num'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'pow', 'params': ['num', 'num'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'sqrt', 'params': ['num'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'input', 'params': [], 'return_type': 'txt', 'is_builtin': True},
            {'name': 'ohio', 'params': [], 'return_type': 'void', 'is_builtin': True},
            {'name': 'grimace_shake', 'params': [], 'return_type': 'void', 'is_builtin': True},
            {'name': 'mewing', 'params': ['num'], 'return_type': 'void', 'is_builtin': True},
            {'name': 'rizz', 'params': ['num'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'fanum_tax', 'params': ['num'], 'return_type': 'num', 'is_builtin': True},
            {'name': 'ballerina_cappuccina', 'params': [], 'return_type': 'txt', 'is_builtin': True},
        ]
        return builtins

    def get_all_symbols(self) -> dict:
        """Get complete symbol table data for UI display."""
        return {
            'variables': self.get_variables(),
            'functions': self.get_functions(),
            'builtins': self.get_builtins()
        }

    def to_display_string(self) -> str:
        """Generate a string representation for display."""
        lines = []
        variables = self.get_variables()
        functions = self.get_functions()
        builtins = self.get_builtins()

        if variables:
            lines.append("Variables:")
            for v in variables:
                const_marker = " (constant)" if v.get('is_constant') else ""
                lines.append(f"  {v['name']}: {v['type']}{const_marker}")

        if functions:
            lines.append("\nFunctions:")
            for f in functions:
                params = ", ".join(f['params']) if f['params'] else "()"
                lines.append(f"  {f['name']}({params}) -> {f['return_type']}")

        if builtins:
            lines.append("\nBuilt-in Functions:")
            for b in builtins:
                params = ", ".join(b['params']) if b['params'] else "()"
                lines.append(f"  {b['name']}({params}) -> {b['return_type']}")

        return "\n".join(lines) if lines else "No symbols defined"


class SemanticError(Exception):
    """Raised when semantic analysis fails."""

    def __init__(self, message: str, node: Optional[object] = None):
        self.message = message
        self.node = node
        super().__init__(f"Semantic error: {message}")


def parse_type(type_str: str) -> TypeInfo:
    """Parse a type string into TypeInfo."""
    if type_str.endswith('[]'):
        base = type_str[:-2]
        return TypeInfo(base_type=base, is_array=True)
    return TypeInfo(base_type=type_str, is_array=False)