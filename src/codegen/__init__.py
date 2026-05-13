"""Target Code Generation for GenZ/Brainrot language.

Phase 6: Generates low-level Stack Machine instructions from the AST.
"""

from .stack_machine import StackMachineGenerator, generate_stack_code

__all__ = ["StackMachineGenerator", "generate_stack_code"]
