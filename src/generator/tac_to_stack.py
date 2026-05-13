import re

class TACToStackConverter:
    """Converts Optimized Three-Address Code (TAC) into Stack Machine instructions."""

    def __init__(self):
        self.output = []

    def convert(self, tac_code: str) -> str:
        self.output = []
        self.output.append("; =============================================")
        self.output.append("; Stack Machine Code (Generated from Optimized IR)")
        self.output.append("; =============================================")
        self.output.append("")

        lines = tac_code.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith(';'):
                if stripped.startswith(';'):
                    self.output.append(stripped)
                continue

            # Function definitions
            if stripped.startswith('func '):
                func_match = re.match(r'func\s+(\w+)\((.*)\)', stripped)
                if func_match:
                    name, params = func_match.groups()
                    self.output.append(f"FUNC_START {name}")
                    param_list = [p.strip() for p in params.split(',') if p.strip()]
                    # Parameters are pushed in order, so store in reverse
                    for p in reversed(param_list):
                        self.output.append(f"STORE {p}")
                continue

            if stripped == 'endfunc':
                # We need to find the function name to end it, but FUNC_END usually just takes a name
                # For now we'll just emit a generic end if we don't track names
                self.output.append("FUNC_END") 
                self.output.append("")
                continue

            # Return
            if stripped.startswith('return '):
                val = stripped.replace('return ', '').strip()
                self._push_val(val)
                self.output.append("RETURN")
                continue

            # Print
            if stripped.startswith('print '):
                val = stripped.replace('print ', '').strip()
                self._push_val(val)
                self.output.append("PRINT")
                continue

            # Control Flow
            if stripped.startswith('ifnot '):
                # ifnot cond goto label
                m = re.match(r'ifnot\s+(\w+)\s+goto\s+(\w+)', stripped)
                if m:
                    cond, label = m.groups()
                    self.output.append(f"LOAD {cond}")
                    self.output.append(f"JMP_FALSE {label}")
                continue

            if stripped.startswith('goto '):
                label = stripped.replace('goto ', '').strip()
                self.output.append(f"JMP {label}")
                continue

            if stripped.endswith(':'):
                self.output.append(stripped)
                continue

            # Assignments and Expressions
            if '=' in stripped:
                # x = a op b  OR  x = a
                lhs, rhs = [x.strip() for x in stripped.split('=', 1)]
                
                # Check for binary op
                bin_match = re.match(r'(.+?)\s*([+\-*/%]|[<>!=]=|[<>])\s*(.+)', rhs)
                if bin_match:
                    left, op, right = bin_match.groups()
                    self._push_val(left)
                    self._push_val(right)
                    self.output.append(self._get_op_inst(op))
                    self.output.append(f"STORE {lhs}")
                else:
                    # Simple assignment or function call
                    if rhs.startswith('call '):
                        # call func(a, b)
                        call_match = re.match(r'call\s+(\w+)\((.*)\)', rhs)
                        if call_match:
                            name, args_str = call_match.groups()
                            args = [a.strip() for a in args_str.split(',') if a.strip()]
                            for a in args:
                                self._push_val(a)
                            self.output.append(f"CALL {name} {len(args)}")
                            self.output.append(f"STORE {lhs}")
                    else:
                        # x = 10 or x = y
                        self._push_val(rhs)
                        self.output.append(f"STORE {lhs}")
                continue

        self.output.append("HALT")
        return '\n'.join(self.output)

    def _push_val(self, val: str):
        val = val.strip()
        if val.startswith('"') or val.replace('.','',1).isdigit():
            self.output.append(f"PUSH {val}")
        else:
            self.output.append(f"LOAD {val}")

    def _get_op_inst(self, op: str) -> str:
        mapping = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD',
            '==': 'CMP_EQ', '!=': 'CMP_NEQ', '<': 'CMP_LT', '>': 'CMP_GT',
            '<=': 'CMP_LTE', '>=': 'CMP_GTE'
        }
        return mapping.get(op, f"UNKNOWN_OP_{op}")

def generate_stack_from_ir(ir_code: str) -> str:
    return TACToStackConverter().convert(ir_code)
