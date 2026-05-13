"""Intermediate Code Generation (IR) for GenZ/Brainrot language.

Phase 4: Generates Three-Address Code (TAC) from the AST.
"""

from .ir_generator import IRGenerator, generate_ir

__all__ = ["IRGenerator", "generate_ir"]
