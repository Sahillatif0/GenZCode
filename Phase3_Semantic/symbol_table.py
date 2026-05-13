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

    def push_scope(self, name: str = "local") -> Scope:
        """Enter a new scope."""
        new_scope = Scope(parent=self.current_scope, name=name)
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
                       param_types: list[TypeInfo], is_variadic: bool = False) -> Symbol:
        """Define a function (in global scope)."""
        # Check if already defined
        existing = self.global_scope.lookup(name)
        if existing and existing.is_function and existing.defined:
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