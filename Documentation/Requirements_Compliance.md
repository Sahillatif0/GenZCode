# Assignment Requirements Compliance Report

This document outlines how the **GenZCode** compiler project fulfills each of the 10 mandatory assignment requirements.

## 1. Complete Compiler Phases
**Status: ✅ FULFILLED**
The project implements all 6 mandatory phases:
- **Lexical Analysis**: `Phase1_Lexical/lexer.py`
- **Syntax Analysis**: `Phase2_Syntax/parser.py`
- **Semantic Analysis**: `Phase3_Semantic/semantic.py`
- **Intermediate Code Generation**: `Phase4_ICG/ir_generator.py`
- **Code Optimization**: `Phase5_Optimization/optimizer.py`
- **Target Code Generation**: `Phase6_CodeGeneration/codegen.py`

## 2. Separate Executable for Every Phase
**Status: ✅ FULFILLED**
Each phase is implemented as a standalone script that can be run from the command line.
- Example: `python Phase1_Lexical/lexer.py input.genz`
- Example: `python Phase6_CodeGeneration/codegen.py input.genz`

## 3. Proper Input Handling
**Status: ✅ FULFILLED**
Every module reads source code from a file passed as a command-line argument, processes it, and prints the resulting output (Tokens, AST, IR, or Target Code). Hardcoded strings are only used as fallbacks if no file is provided.

## 4. Symbol Table Management
**Status: ✅ FULFILLED**
Implemented in `Phase3_Semantic/symbol_table.py`. It handles:
- Scoping (Global and Function-level)
- Symbol types (num, txt, bool, arrays)
- Function parameters and return types

## 5. Error Handling
**Status: ✅ FULFILLED**
Comprehensive error reporting for:
- Lexical errors (invalid characters)
- Syntax errors (unexpected tokens, missing semicolons)
- Semantic errors (undefined variables, type mismatches, invalid break/continue)

## 6. Intermediate Code (TAC)
**Status: ✅ FULFILLED**
Generates Three-Address Code (TAC) in `Phase4_ICG`. Each instruction has at most one operator, suitable for optimization.

## 7. At Least 3 Optimization Techniques
**Status: ✅ FULFILLED**
Implemented in `Phase5_Optimization/optimizer.py`:
1. **Constant Folding**: Evaluates constant expressions at compile time.
2. **Copy Propagation**: Replaces redundant variable uses with their values.
3. **Dead Code Elimination**: Removes instructions that assign to temporaries that are never used.

## 8. Low-Level Target Code
**Status: ✅ FULFILLED**
Generates **Stack Machine instructions** in `Phase6_CodeGeneration`. This is a low-level, assembly-like representation (PUSH, LOAD, STORE, CALL, JMP) rather than high-level code.

## 9. Folder Structure
**Status: ✅ FULFILLED**
The project is organized into clear phase-based directories as requested:
- `Phase1_Lexical/`
- `Phase2_Syntax/`
- `Phase3_Semantic/`
- `Phase4_ICG/`
- `Phase5_Optimization/`
- `Phase6_CodeGeneration/`
- `TestCases/`
- `Documentation/`

## 10. Complete Documentation
**Status: ✅ FULFILLED**
- `Documentation/phases.md`: Explains how to run each phase.
- `Documentation/Requirements_Compliance.md`: This file.
- `README.md`: Overall project overview.
- `grammar.md`: Language specification.
