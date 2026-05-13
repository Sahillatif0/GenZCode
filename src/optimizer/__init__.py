"""Code Optimization phase for GenZ/Brainrot language.

Phase 5: Applies optimization passes over Three-Address Code (TAC).
"""

from .optimizer import optimize_ir, OptimizationReport

__all__ = ["optimize_ir", "OptimizationReport"]
