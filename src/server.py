import sys
import io
import contextlib
import json
from flask import Flask, request, jsonify
from src.lexer import tokenize
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.semantic.analyzer import SemanticAnalyzer
from src.generator.generator import generate_python
from src.ir.ir_generator import generate_ir
from src.optimizer.optimizer import optimize_ir
from src.codegen.stack_machine import generate_stack_code
from src.parser.ast import Program

app = Flask(__name__)

class PipelineEncoder(json.JSONEncoder):
    """Custom JSON encoder for pipeline objects."""
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if hasattr(obj, 'value') and hasattr(obj, 'name'):
            return {'name': obj.name, 'value': obj.value}
        return super().default(obj)

def ast_to_dict(node):
    """Convert AST node to a serializable dictionary."""
    if node is None:
        return None
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    if isinstance(node, (str, int, float, bool)):
        return node
    if hasattr(node, '__dataclass_fields__'):
        result = {'_type': type(node).__name__}
        for field_name in node.__dataclass_fields__:
            value = getattr(node, field_name)
            result[field_name] = ast_to_dict(value)
        return result
    if hasattr(node, '__dict__'):
        result = {'_type': type(node).__name__}
        for key, value in node.__dict__.items():
            if not key.startswith('_'):
                result[key] = ast_to_dict(value)
        return result
    return str(node)

def symbol_table_to_dict(st, include_builtins: bool = True):
    """Convert symbol table to serializable dictionary."""
    scopes = []
    current = st.current_scope
    builtin_names = {
        'print', 'len', 'str', 'num', 'range', 'abs', 'pow', 'sqrt',
        'input', 'int', 'float', 'bool', 'list', 'max', 'min', 'sum'
    }
    while current:
        scope_data = {
            'name': current.name,
            'symbols': {}
        }
        for name, symbol in current.symbols.items():
            # Filter out built-in functions unless include_builtins is True
            if not include_builtins and symbol.is_function and name in builtin_names:
                continue
            sym_data = {
                'name': symbol.name,
                'type': str(symbol.type_info),
                'is_function': symbol.is_function,
                'is_variadic': symbol.is_variadic,
                'is_builtin': symbol.is_function and name in builtin_names,
                'defined': symbol.defined,
            }
            if symbol.is_function:
                sym_data['param_types'] = [str(pt) for pt in symbol.param_types]
                sym_data['return_type'] = str(symbol.return_type) if symbol.return_type else None
            scope_data['symbols'][name] = sym_data
        scopes.append(scope_data)
        current = current.parent
    return {'scopes': list(reversed(scopes))}

@app.route('/')
def index():
    return jsonify({
        "service": "GenZCode Studio API",
        "status": "running",
        "endpoints": {
            "POST /run": "Execute GenZCode and return output",
            "POST /pipeline": "Run full compiler pipeline and return all stages"
        }
    })

@app.route('/run', methods=['POST'])
def run_code():
    if not request.is_json:
        return jsonify({"output": "Error: Request must be JSON"}), 400
    data = request.json
    if not data or "code" not in data:
        return jsonify({"output": "Error: Missing 'code' field in JSON body"}), 400
    code = data["code"]
    
    # Capture standard output
    output_buffer = io.StringIO()
    error_msg = None
    
    with contextlib.redirect_stdout(output_buffer):
        try:
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            Interpreter().interpret(ast)
        except Exception as e:
            error_msg = str(e)
            
    output = output_buffer.getvalue()
    
    if error_msg:
        if output:
            output += "\n"
        output += f"Error: {error_msg}"
        
    return jsonify({"output": output})

@app.route('/pipeline', methods=['POST'])
def pipeline():
    """Run the full compiler pipeline and return all stages with detailed data."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.json
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in JSON body"}), 400
    code = data["code"]

    stages = []
    output_buffer = io.StringIO()
    execution_output = ""
    error_msg = None

    try:
        # Stage 1: Lexical Analysis
        tokens = tokenize(code)
        token_data = []
        for t in tokens:
            token_data.append({
                'type': t.type.name,
                'lexeme': t.lexeme,
                'literal': t.literal,
                'line': t.line,
                'column': t.column
            })
        stages.append({
            'name': 'lexer',
            'title': 'Lexical Analysis',
            'description': 'The lexer scans the raw source code character by character, grouping them into meaningful tokens. It recognizes keywords like lowkey, sus, and spill_tea; identifiers; numbers; strings; operators; and punctuation. Comments are stripped and whitespace is ignored.',
            'tokens': token_data,
            'status': 'success'
        })

        # Stage 2: Parsing
        ast = Parser(tokens).parse()
        ast_dict = ast_to_dict(ast)
        stages.append({
            'name': 'parser',
            'title': 'Syntax Analysis (Parsing)',
            'description': 'The parser takes the token stream and builds an Abstract Syntax Tree (AST) using recursive descent parsing. It validates grammar rules, handles operator precedence, and constructs a hierarchical representation of the program structure.',
            'ast': ast_dict,
            'status': 'success'
        })

        # Stage 3: Semantic Analysis
        analyzer = SemanticAnalyzer()
        symbol_table = analyzer.analyze(ast)
        st_dict = symbol_table_to_dict(symbol_table)
        stages.append({
            'name': 'semantic',
            'title': 'Semantic Analysis',
            'description': 'The semantic analyzer traverses the AST to perform type checking, scope resolution, and symbol table construction. It validates that variables are declared before use, types match in assignments, function calls have correct arguments, and break/continue statements appear inside loops.',
            'symbol_table': st_dict,
            'status': 'success'
        })

        # Stage 4: Intermediate Code (IR) Generation
        ir_code = generate_ir(ast)
        stages.append({
            'name': 'intermediate',
            'title': 'Intermediate Code (IR)',
            'description': 'The intermediate code generator produces a three-address code (TAC) representation. This platform-independent representation breaks complex expressions into simple instructions with at most one operator per instruction, making it ideal for optimization and easier code generation.',
            'ir_code': ir_code,
            'status': 'success'
        })

        # Stage 5: Optimized IR
        optimized_ir, report = optimize_ir(ir_code)
        stages.append({
            'name': 'optimizer',
            'title': 'Optimization Pass',
            'description': 'The optimization pass applies various compiler optimizations to the intermediate code: constant folding, copy propagation, and dead code elimination.',
            'ir_code': ir_code,
            'optimized_ir': optimized_ir,
            'optimization_report': report.summary(),
            'status': 'success'
        })

        # Stage 6: Code Generation (Target Code)
        from src.generator.tac_to_python import generate_python_from_ir
        from src.generator.tac_to_stack import generate_stack_from_ir
        
        # We now generate target code from the OPTIMIZED IR instead of the raw AST
        # to ensure optimizations are reflected in the final output.
        python_code = generate_python_from_ir(optimized_ir)
        stack_code = generate_stack_from_ir(optimized_ir)
        
        stages.append({
            'name': 'generator',
            'title': 'Code Generation',
            'description': 'The code generator now consumes the Optimized IR to emit efficient Python and Stack Machine code. Redundant logic identified during optimization is removed from the final target.',
            'python_code': python_code,
            'stack_code': stack_code,
            'status': 'success'
        })

        # Stage 7: Execution / Interpretation
        with contextlib.redirect_stdout(output_buffer):
            Interpreter().interpret(ast)
        execution_output = output_buffer.getvalue()
        stages.append({
            'name': 'interpreter',
            'title': 'Execution (Interpretation)',
            'description': 'The interpreter walks the AST and executes it directly without compiling to machine code.',
            'output': execution_output,
            'status': 'success'
        })

    except Exception as e:
        error_msg = str(e)
        # Add error to the last stage attempted
        if stages:
            stages[-1]['status'] = 'error'
            stages[-1]['error'] = error_msg

    return jsonify({
        'stages': stages,
        'error': error_msg,
        'output': execution_output
    })


# =============================================================================
# =============================================================================
# Helper functions for the web pipeline
# =============================================================================

def get_ir(ast):
    return generate_ir(ast)

def get_optimized_ir(ir_code):
    optimized, _ = optimize_ir(ir_code)
    return optimized

def get_stack_code(ast):
    return generate_stack_code(ast)


@app.route('/phase', methods=['POST'])
def run_phase():
    """Run a specific compiler phase and return results."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.json
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in JSON body"}), 400

    code = data["code"]
    phase = data.get("phase", "lexer")

    try:
        if phase == "lexer":
            tokens = tokenize(code)
            token_data = []
            for t in tokens:
                token_data.append({
                    'type': t.type.name,
                    'lexeme': t.lexeme,
                    'literal': t.literal,
                    'line': t.line,
                    'column': t.column
                })
            return jsonify({
                'phase': 'lexer',
                'tokens': token_data,
                'status': 'success'
            })

        elif phase == "parser":
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            return jsonify({
                'phase': 'parser',
                'ast': ast_to_dict(ast),
                'status': 'success'
            })

        elif phase == "semantic":
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            analyzer = SemanticAnalyzer()
            symbol_table = analyzer.analyze(ast)
            return jsonify({
                'phase': 'semantic',
                'symbol_table': symbol_table_to_dict(symbol_table),
                'status': 'success'
            })

        elif phase == "intermediate":
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast)
            ir = generate_ir(ast)
            return jsonify({
                'phase': 'intermediate',
                'ir_code': ir,
                'status': 'success'
            })

        elif phase == "optimizer":
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast)
            ir = generate_ir(ast)
            optimized, report = optimize_ir(ir)
            return jsonify({
                'phase': 'optimizer',
                'ir_code': ir,
                'optimized_ir': optimized,
                'optimization_report': report.summary(),
                'status': 'success'
            })

        elif phase == "generator":
            tokens = tokenize(code)
            ast = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast)
            python_code = generate_python(ast)
            stack_code = generate_stack_code(ast)
            return jsonify({
                'phase': 'generator',
                'python_code': python_code,
                'stack_code': stack_code,
                'status': 'success'
            })

        else:
            return jsonify({"error": f"Unknown phase: {phase}"}), 400

    except Exception as e:
        return jsonify({
            'phase': phase,
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
