import re

class TACToPythonConverter:
    """Converts Three-Address Code (TAC) into equivalent Python code."""

    def __init__(self):
        self.output = []
        self.indent_level = 0

    def convert(self, tac_code: str) -> str:
        self.output = []
        self.indent_level = 0
        
        lines = tac_code.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith(';'):
                continue
                
            # Function definitions
            if stripped.startswith('func '):
                func_match = re.match(r'func\s+(\w+)\((.*)\)', stripped)
                if func_match:
                    name, params = func_match.groups()
                    self._emit(f"def {name}({params}):")
                    self.indent_level += 1
                continue
                
            if stripped == 'endfunc':
                self.indent_level -= 1
                self._emit("")
                continue
            
            # Control flow (only basic support for optimized IR)
            if stripped.startswith('ifnot '):
                # We can't easily translate goto to Python, 
                # but if it's optimized away, we don't need to.
                # If it's NOT optimized away, we'll emit a comment or a crude if.
                self._emit(f"# {stripped} (Control flow remains in IR)")
                continue
                
            if stripped.startswith('goto '):
                self._emit(f"# {stripped}")
                continue
                
            if stripped.endswith(':'): # Labels
                self._emit(f"# {stripped}")
                continue

            # Return
            if stripped.startswith('return '):
                val = stripped.replace('return ', '').strip()
                self._emit(f"return {val}")
                continue

            # Print
            if stripped.startswith('print '):
                val = stripped.replace('print ', '').strip()
                self._emit(f"print({val})")
                continue

            # Assignments and expressions
            if '=' in stripped:
                # Basic x = y or x = y + z
                self._emit(stripped)
                continue
                
            # Standalone calls
            if 'call ' in stripped:
                call_part = stripped.replace('call ', '').strip()
                self._emit(call_part)
                continue

        return '\n'.join(self.output)

    def _emit(self, code: str):
        indent = "    " * self.indent_level
        self.output.append(f"{indent}{code}")

def generate_python_from_ir(ir_code: str) -> str:
    converter = TACToPythonConverter()
    return converter.convert(ir_code)
