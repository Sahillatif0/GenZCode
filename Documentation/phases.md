# GenZCode — Phase Documentation

This directory contains the 6 mandatory phases of the compiler, each runnable as a standalone script.

## Phase 1: Lexical Analysis
**Location:** `Phase1_Lexical/lexer.py`
**Description:** Converts raw GenZ source code into a stream of tokens.
**Usage:** `python Phase1_Lexical/lexer.py examples/hello.genz`

## Phase 2: Syntax Analysis (Parsing)
**Location:** `Phase2_Syntax/parser.py`
**Description:** Builds an Abstract Syntax Tree (AST) from the token stream.
**Usage:** `python Phase2_Syntax/parser.py examples/hello.genz`

## Phase 3: Semantic Analysis
**Location:** `Phase3_Semantic/semantic.py`
**Description:** Performs type checking and symbol table management.
**Usage:** `python Phase3_Semantic/semantic.py examples/hello.genz`

## Phase 4: Intermediate Code Generation (ICG)
**Location:** `Phase4_ICG/ir_generator.py`
**Description:** Generates Three-Address Code (TAC) representation.
**Usage:** `python Phase4_ICG/ir_generator.py examples/hello.genz`

## Phase 5: Optimization
**Location:** `Phase5_Optimization/optimizer.py`
**Description:** Applies constant folding, copy propagation, and dead code elimination.
**Usage:** `python Phase5_Optimization/optimizer.py examples/hello.genz`

## Phase 6: Code Generation
**Location:** `Phase6_CodeGeneration/codegen.py`
**Description:** Generates low-level Stack Machine target instructions.
**Usage:** `python Phase6_CodeGeneration/codegen.py examples/hello.genz`
