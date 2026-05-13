"""Code Optimization phase for GenZ/Brainrot language.

Phase 5 — Applies THREE optimization passes over Three-Address Code (TAC):

  1. Constant Folding
     Evaluates expressions whose operands are all constants at compile
     time so no runtime computation is needed.
     Example:  t0 = 5 + 3   →  t0 = 8

  2. Copy Propagation
     Replaces uses of a variable that is a simple copy of another
     variable (or constant) with the source value, reducing redundant
     loads.
     Example:  t1 = t0       (t0 is known to be 8)
               x  = t1 + 2  →  x = 8 + 2

  3. Dead Code Elimination
     Removes TAC instructions that assign to a temporary that is never
     subsequently read anywhere in the code.  Pure assignments whose
     result is never consumed are discarded.
     Example:  t99 = 42     (t99 never referenced again → removed)

Standalone usage:
    python -m src.optimizer.optimizer input.genz
    python src/optimizer/optimizer.py input.genz
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Allow running as a standalone script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class OptimizationReport:
    """Records what each optimization pass changed."""
    original_lines: int = 0
    constant_folds: list[str] = field(default_factory=list)
    copy_propagations: list[str] = field(default_factory=list)
    dead_code_removed: list[str] = field(default_factory=list)
    control_flow_changes: list[str] = field(default_factory=list)

    @property
    def optimized_lines(self) -> int:
        return (self.original_lines
                - len(self.dead_code_removed)
                - len(self.control_flow_changes))

    def summary(self) -> str:
        lines = [
            "=== Optimization Report ===",
            f"  Original instruction count : {self.original_lines}",
            f"  Constant folds applied     : {len(self.constant_folds)}",
            f"  Copy propagations applied  : {len(self.copy_propagations)}",
            f"  Dead code lines removed    : {len(self.dead_code_removed)}",
            f"  Control flow optimized     : {len(self.control_flow_changes)}",
            f"  Optimized instruction count: {self.optimized_lines}",
        ]
        if self.constant_folds:
            lines.append("\n  Constant Folds:")
            for cf in self.constant_folds:
                lines.append(f"    {cf}")
        if self.copy_propagations:
            lines.append("\n  Copy Propagations:")
            for cp in self.copy_propagations:
                lines.append(f"    {cp}")
        if self.dead_code_removed:
            lines.append("\n  Dead Code Removed:")
            for dc in self.dead_code_removed:
                lines.append(f"    {dc}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Pattern: <dest> = <operand1> <op> <operand2>
_BINARY_ASSIGN = re.compile(
    r"^(\w+)\s*=\s*(-?\d+\.?\d*)\s*([+\-*/%]|[<>!=]=|[<>])\s*(-?\d+\.?\d*)\s*$"
)
# Pattern: <dest> = <src>   (simple copy, src is a name or constant)
_COPY_ASSIGN = re.compile(r"^(\w+)\s*=\s*(\w+|-?\d+\.?\d*)\s*$")
# Pattern: <dest> = <op> <operand>  (unary)
_UNARY_ASSIGN = re.compile(r"^(\w+)\s*=\s*(-)\s*(-?\d+\.?\d*)\s*$")
# Lines that are labels (e.g. "L0:")
_LABEL = re.compile(r"^\w+:$")
# Lines that are comments (start with ";")
_COMMENT = re.compile(r"^;")
# Identify temporaries (t0, t1, ...)
_IS_TEMP = re.compile(r"^t\d+$")


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _eval_binary(left: str, op: str, right: str) -> str | None:
    """Safely evaluate a binary operation on two numeric constants."""
    try:
        l, r = float(left), float(right)
        if op == "+":
            result = l + r
        elif op == "-":
            result = l - r
        elif op == "*":
            result = l * r
        elif op == "/":
            if r == 0:
                return None   # Avoid division by zero
            result = l / r
        elif op == "%":
            if r == 0:
                return None
            result = l % r
        elif op == "==":
            result = 1 if l == r else 0
        elif op == "!=":
            result = 1 if l != r else 0
        elif op == ">":
            result = 1 if l > r else 0
        elif op == "<":
            result = 1 if l < r else 0
        elif op == ">=":
            result = 1 if l >= r else 0
        elif op == "<=":
            result = 1 if l <= r else 0
        else:
            return None
        # Return int string if no fractional part
        if isinstance(result, (int, float)) and result == int(result):
            return str(int(result))
        return str(result)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Optimization Pass 1 — Constant Folding
# ---------------------------------------------------------------------------

def _pass_constant_folding(
    lines: list[str], report: OptimizationReport
) -> list[str]:
    """Replace constant binary expressions with their computed value."""
    result = []
    for line in lines:
        stripped = line.strip()
        m = _BINARY_ASSIGN.match(stripped)
        if m:
            dest, left, op, right = m.groups()
            folded = _eval_binary(left, op, right)
            if folded is not None:
                new_line = f"{dest} = {folded}  ; folded from: {left} {op} {right}"
                report.constant_folds.append(f"{stripped}  ->  {dest} = {folded}")
                result.append(new_line)
                continue
        # Unary negation of a constant
        um = _UNARY_ASSIGN.match(stripped)
        if um:
            dest, _op, operand = um.groups()
            folded = str(-float(operand))
            if float(folded) == int(float(folded)):
                folded = str(int(float(folded)))
            new_line = f"{dest} = {folded}  ; folded from: -{operand}"
            report.constant_folds.append(f"{stripped}  ->  {dest} = {folded}")
            result.append(new_line)
            continue
        result.append(line)
    return result


# ---------------------------------------------------------------------------
# Optimization Pass 2 — Copy Propagation
# ---------------------------------------------------------------------------

def _pass_copy_propagation(
    lines: list[str], report: OptimizationReport
) -> list[str]:
    """Replace uses of copy variables with their source value.

    When we see  dest = src  where src is a simple name or constant,
    we record the mapping dest→src and substitute in subsequent lines.
    We invalidate the mapping if dest is ever reassigned.
    """
    copies: dict[str, str] = {}   # dest → src
    result = []

    for line in lines:
        stripped = line.strip()

        # Skip comments, labels, directives
        if _COMMENT.match(stripped) or _LABEL.match(stripped) or not stripped:
            result.append(line)
            continue

        # Strip inline comments for matching purposes
        code_part = stripped.split(";")[0].strip()

        # Check if this is a simple copy  (dest = src)
        cm = _COPY_ASSIGN.match(code_part)
        if cm:
            dest, src = cm.groups()
            # Resolve src through existing copies
            resolved_src = copies.get(src, src)
            if dest != resolved_src:
                copies[dest] = resolved_src
            else:
                copies.pop(dest, None)

        # Apply known copies to the RHS of this line
        new_code = code_part
        for var, replacement in copies.items():
            # Replace whole-word occurrences of var on the RHS
            # (i.e. after the first "=")
            if "=" in new_code:
                lhs, rhs = new_code.split("=", 1)
                new_rhs = re.sub(rf"\b{re.escape(var)}\b", replacement, rhs)
                if new_rhs != rhs:
                    report.copy_propagations.append(
                        f"{code_part}  ->  {lhs}={new_rhs.strip()}"
                    )
                new_code = lhs + "=" + new_rhs
            else:
                new_rhs = re.sub(rf"\b{re.escape(var)}\b", replacement, new_code)
                if new_rhs != new_code:
                    report.copy_propagations.append(
                        f"{code_part}  ->  {new_rhs}"
                    )
                new_code = new_rhs

        # Preserve trailing inline comments from original line
        inline_comment = ""
        if ";" in stripped:
            inline_comment = "  ;" + stripped.split(";", 1)[1]

        result.append(new_code + inline_comment)

    return result


# ---------------------------------------------------------------------------
# Optimization Pass 3 — Dead Code Elimination
# ---------------------------------------------------------------------------

def _collect_used_vars(lines: list[str]) -> set[str]:
    """Collect all variable/temp names that appear on a RHS or in control flow."""
    used: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or _COMMENT.match(stripped) or _LABEL.match(stripped):
            continue
        code_part = stripped.split(";")[0].strip()
        # Everything that is NOT a pure  dest = ...  assignment counts as a use
        # For assignments, the RHS contains uses
        if "=" in code_part:
            _lhs, rhs = code_part.split("=", 1)
            tokens = re.findall(r"\b[a-zA-Z_]\w*\b", rhs)
            used.update(tokens)
        else:
            # Whole instruction is a use (print, goto, ifnot, return, call…)
            tokens = re.findall(r"\b[a-zA-Z_]\w*\b", code_part)
            used.update(tokens)
    return used


def _pass_dead_code_elimination(
    lines: list[str], report: OptimizationReport
) -> list[str]:
    """Remove assignments to temporaries that are never used downstream.

    Only temporaries (t0, t1, ...) are candidates for elimination.
    Named user variables are never removed (they may have side-effects
    visible outside the current scope).
    """
    used_vars = _collect_used_vars(lines)
    result = []

    for line in lines:
        stripped = line.strip()
        if not stripped or _COMMENT.match(stripped) or _LABEL.match(stripped):
            result.append(line)
            continue

        code_part = stripped.split(";")[0].strip()
        cm = _COPY_ASSIGN.match(code_part)
        ba = _BINARY_ASSIGN.match(code_part)

        # A line is dead if it assigns ONLY to a temp that is never used
        lhs_match = re.match(r"^(t\d+)\s*=", code_part)
        if lhs_match:
            temp_name = lhs_match.group(1)
            if temp_name not in used_vars:
                report.dead_code_removed.append(stripped)
                continue   # ← Actually eliminate the line

        result.append(line)

    return result


# ---------------------------------------------------------------------------
# Optimization Pass 4 — Control Flow Optimization
# ---------------------------------------------------------------------------

def _collect_used_labels(lines: list[str]) -> set[str]:
    """Collect all labels that are targets of jumps."""
    used = set()
    for line in lines:
        m = re.search(r"goto\s+(\w+)", line)
        if m:
            used.add(m.group(1))
    return used

def _pass_control_flow_optimization(
    lines: list[str], report: OptimizationReport
) -> list[str]:
    """Optimize jumps and branches.
    1. ifnot 1 goto L -> remove
    2. ifnot 0 goto L -> goto L
    3. goto L followed by L: -> remove goto L
    4. Remove unused labels
    """
    changed = True
    current_lines = lines
    
    while changed:
        changed = False
        new_lines = []
        used_labels = _collect_used_labels(current_lines)
        
        i = 0
        while i < len(current_lines):
            line = current_lines[i]
            stripped = line.strip()
            
            # 1. Branch Folding: ifnot 1
            if stripped.startswith("ifnot 1 goto"):
                report.control_flow_changes.append(f"Removed unreachable branch: {stripped}")
                changed = True
                i += 1
                continue
            
            # 2. Branch Folding: ifnot 0
            if stripped.startswith("ifnot 0 goto"):
                target_label = stripped.split("goto")[-1].strip()
                new_line = f"goto {target_label}"
                report.control_flow_changes.append(f"Simplified branch: {stripped} -> {new_line}")
                new_lines.append(new_line)
                changed = True
                i += 1
                continue
                
            # 3. Unused Label Elimination
            if _LABEL.match(stripped):
                label = stripped[:-1]
                if label not in used_labels:
                    # If it has a comment, keep the comment but remove label
                    if ";" in line:
                        new_lines.append("; (removed label " + label + ") " + line.split(";", 1)[1])
                    else:
                        report.control_flow_changes.append(f"Removed unused label: {label}")
                    changed = True
                    i += 1
                    continue
            
            # 4. Redundant Jump Elimination
            m = re.match(r"^goto\s+(\w+)\s*(;.*)?$", stripped)
            if m:
                target = m.group(1)
                # Look ahead for next non-empty, non-comment line
                found_target = False
                for j in range(i + 1, len(current_lines)):
                    next_stripped = current_lines[j].strip()
                    if not next_stripped or next_stripped.startswith(";"):
                        continue
                    if next_stripped == f"{target}:":
                        found_target = True
                    break
                if found_target:
                    report.control_flow_changes.append(f"Removed redundant jump: {stripped}")
                    changed = True
                    i += 1
                    continue

            new_lines.append(line)
            i += 1
            
        current_lines = new_lines
        
    return current_lines


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def optimize_ir(
    ir_code: str, verbose: bool = False
) -> tuple[str, OptimizationReport]:
    """Apply all optimization passes iteratively until no more changes occur.
    
    Returns:
        (optimized_code, report)  where report details every change made.
    """
    lines = ir_code.split("\n")
    report = OptimizationReport(original_lines=len(lines))
    
    changed = True
    while changed:
        start_folds = len(report.constant_folds)
        start_copies = len(report.copy_propagations)
        start_dead = len(report.dead_code_removed)
        start_cf = len(report.control_flow_changes)
        
        # Pass 1: Constant Folding
        lines = _pass_constant_folding(lines, report)
        
        # Pass 2: Copy Propagation
        lines = _pass_copy_propagation(lines, report)
        
        # Pass 3: Dead Code Elimination
        lines = _pass_dead_code_elimination(lines, report)
        
        # Pass 4: Control Flow Optimization
        lines = _pass_control_flow_optimization(lines, report)
        
        if (len(report.constant_folds) == start_folds and
            len(report.copy_propagations) == start_copies and
            len(report.dead_code_removed) == start_dead and
            len(report.control_flow_changes) == start_cf):
            changed = False
            
    return "\n".join(lines), report


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from Phase1_Lexical.lexer import tokenize
    from Phase2_Syntax.parser import Parser
    from Phase4_ICG.ir_generator import generate_ir

    if len(sys.argv) < 2:
        print("Usage: python src/optimizer/optimizer.py <input.genz>")
        print("       python -m src.optimizer.optimizer <input.genz>")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = tokenize(source)
        ast = Parser(tokens).parse()
        ir_code = generate_ir(ast)

        print("=== Original Three-Address Code ===")
        print(ir_code)
        print()

        optimized_code, report = optimize_ir(ir_code)

        print("=== Optimized Three-Address Code ===")
        print(optimized_code)
        print()
        print(report.summary())

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
