
![GenZCode Studio Banner](images/Frame%20337453.png)

A complete compiler for a Gen-Z slang-based programming language built for academic purposes.

## How to Start

You can run GenZCode either inside the **Web IDE Studio** or directly via the **CLI compiler**.

### 1. Start via Docker (Recommended)
Launch the unified Web IDE and Flask backend server instantly with one command:
```bash
docker-compose up --build
```
Once started, visit:
- **Web IDE**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:5000](http://localhost:5000)

### 2. Start Locally (CLI & Dev Servers)

#### Run Frontend & Backend Locally:
```bash
# Start Flask backend (from project root)
python -m src.server

# Start Next.js frontend (from /gui directory)
cd gui
npm install
npm run dev
```

#### Run via Terminal Compiler:
```bash
# Run directly with interpreter
python -m src.main examples/hello.genz --interpret

# Compile to Python
python -m src.main examples/hello.genz -o output.py

# Run compiled Python
python output.py
```

#### Run Standalone Compiler Phases (Assignment Requirements):
Each phase can be run independently using its dedicated script.

```bash
# Phase 1: Lexical analysis
python Phase1_Lexical/lexer.py TestCases/full_test.genz

# Phase 2: Parsing (AST)
python Phase2_Syntax/parser.py TestCases/full_test.genz

# Phase 3: Semantic analysis
python Phase3_Semantic/semantic.py TestCases/full_test.genz

# Phase 4: Intermediate Code Generation (TAC)
python Phase4_ICG/ir_generator.py TestCases/full_test.genz

# Phase 5: Optimization
python Phase5_Optimization/optimizer.py TestCases/full_test.genz

# Phase 6: Code Generation (Stack Machine)
python Phase6_CodeGeneration/codegen.py TestCases/full_test.genz
```

## GenZ Syntax Examples

```javascript
// Variables
lowkey x: num = 42;
lowkey name: txt = "bruh";
lowkey nums: num[] = [1, 2, 3];

// Print
spill_tea("hello world");
spill_tea(x);

// Conditionals
sus (x > 10) {
    spill_tea("big number");
} deadass {
    spill_tea("small number");
}

// Loops
keep_yapping (x > 0) {
    spill_tea(x);
    x = x - 1;
}

// For loop (C-style)
yapping_through (lowkey i: num = 0; i < 5; i = i + 1) {
    spill_tea(i);
}

// Else-if chains
sus (x > 10) {
    spill_tea("big");
} deadass sus (x > 5) {
    spill_tea("medium");
} deadass {
    spill_tea("small");
}

// Functions
vibe_check factorial(n: num) {
    sus (n <= 1) {
        slay 1;
    } deadass {
        slay n * factorial(n - 1);
    }
}

// Control flow
bounce;       // break - bounce out
next_up;      // continue - next iteration

// Switch statement
ratio (x) {
    bet 1: { spill_tea("one"); }
    bet 2: { spill_tea("two"); }
    nvm: { spill_tea("other"); }
}

// Booleans
lowkey is_coding: num = no_cap;   // true
lowkey is_sus: num = fr_fr;        // false
```

## Keyword Reference

| GenZ | Traditional | Description |
|------|-------------|-------------|
| `lowkey` | `let/var` | Variable declaration |
| `num` | `int/float` | Numeric type |
| `txt` | `string` | String type |
| `sus` | `if` | Conditional |
| `deadass` | `else` | Else branch |
| `keep_yapping` | `while` | While loop |
| `spill_tea` | `print` | Output |
| `vibe_check` | `function` | Function declaration |
| `slay` | `return` | Return value |
| `bounce` | `break` | Exit loop |
| `next_up` | `continue` | Next iteration |
| `ratio` | `switch` | Switch statement |
| `bet` | `case` | Case in switch |
| `nvm` | `default` | Default case |
| `no_cap` | `true` | Boolean true |
| `fr_fr` | `false` | Boolean false |
| `goon` | `while true` | Enter an infinite loop |
| `rizz` | `add/mutate` | Mutates or returns numeric with +10.0 |
| `fanum_tax` | `sub/mutate` | Mutates or returns numeric with -20% tax |
| `mewing` | `sleep` | Pauses execution / Suspends thread |
| `skibidi` | `evil/loop` | Evil loop or bad condition state |
| `skibidi_toilet` | `garbage collect` | Cleans up and flushes virtual memory |
| `tung_tung_tung_sahur` | `initialize` | Wake up / Initialize execution |
| `ballerina_cappuccina` | `fancy exit` | Gracefully exit or return a fancy string |
| `ohio` | `runtime error` | Trigger chaotic state runtime exception |
| `grimace_shake` | `fatal error` | Trigger fatal poison crash exception |
| `yapping_through` | `for` | For loop (C-style) |

## Built-in Functions

- `print(a, b, ...)` - Print values
- `len(array)` - Array/string length
- `range(n)` - Generate [0, n)
- `abs(n)` - Absolute value
- `pow(a, b)` - a to the power of b
- `sqrt(n)` - Square root
- `str(n)` - Convert to string
- `num(s)` - Convert to number

## Project Structure

```
GenZCode/
├── src/
│   ├── lexer/         # Tokenization
│   ├── parser/        # AST generation
│   ├── semantic/      # Type checking
│   ├── generator/     # Python code gen
│   └── interpreter/   # Direct execution
├── tests/             # Test suite
└── examples/          # Sample programs
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Compiler Pipeline

```
Source Code (.genz)
    │
    ▼
[Lexer] ──► Tokens
    │
    ▼
[Parser] ──► AST
    │
    ▼
[Semantic Analyzer] ──► Validated AST + Symbol Table
    │
    ▼
[IR Generator] ──► Three-Address Code (TAC)
    │
    ▼
[Optimizer] ──► Optimized IR
    │
    ▼
[Code Generator] ──► Python code
    │
    ▼
[Interpreter] ──► Execute
```

Use `--phase <name>` to run individual phases: `lexer`, `parser`, or `semantic`

## For Course Assignment

This compiler demonstrates:
- Lexical analysis (tokenization)
- Parsing (recursive descent)
- AST representation
- Semantic analysis (type checking, scope)
- Code generation
- Interpretation

Built with Python for Compiler Construction course.

---

## Recent Updates & Web IDE Changelog

We have successfully designed, built, and shipped a modern, high-fidelity **Web-based IDE (GenZCode Studio)** along with substantial compiler upgrades. Below is the detailed record of commits from `270ada1` to `abe0313`:

### 1. Web IDE & Monaco Editor Integration
- **Next.js & Shadcn Dark Theme (`270ada1`, `d702be2`, `1e1995d`)**: Built an extremely premium, dark-themed studio using React, Next.js, and Shadcn UI.
- **Monaco Syntax Highlighter (`8cbbd12`, `576448b`)**: Integrated Microsoft's Monaco Editor with full custom language configurations for GenZCode.
- **Arc-Style Mica Glassmorphism (`371a309`, `35296a5`, `893d90c`, `e28086a`)**: Refined the layout with semi-transparent glass sidebar headers, rounded flush borders, and a beautiful editor window design.

### 2. File Explorer & Python Backend Proxy
- **Flask Execution Server (`de7e4bd`, `4bcaa70`)**: Developed a Flask backend integration to compile and execute GenZCode files asynchronously.
- **Interactive File Explorer (`6e418c2`, `78a8a9e`, `4bcaa70`)**: Added a Left Sidebar to create, select, rename, and delete multiple files natively, pre-populating with 7 fun GenZ examples.
- **Active Tab Headers (`03a4159`)**: Cleaned up the navigation header to show the currently active file centered in a sleek regular font.

### 3. Fuzzy Search Documentation Center
- **Interactive Docs Center (`0da1c9f`, `1ebf8ad`, `30b7e12`, `c2e06e7`, `4081a7e`)**: Developed an integrated, fuzzy-searchable documentation side-panel allowing users to search standard programming concepts and immediately find their GenZ equivalents.
- **Clean Layout & Zinc Tags (`2167289`, `c800c6c`, `143f7d9`, `05ac6c3`)**: Removed clutter, centered headings, and colorized variable outputs using sleek Zinc badges.

### 4. Brainrot Keyword Lexer & Parser Upgrades
- **11 Brand New Keywords Integrated**: Added support for `goon`, `rizz`, `fanum_tax`, `skibidi`, `skibidi_toilet`, `tung_tung_tung_sahur`, `mewing`, `edge`, `ohio`, `grimace_shake`, and `ballerina_cappuccina`.
- **`goon` Infinite Loops**: Mapped `goon { ... }` directly to `WhileStmt(Literal(True))` inside the parser, eliminating compilation syntax errors.
- **In-place Variable Mutation**: Configured `fanum_tax(x)` and `rizz(x)` to automatically mutate the referenced variable directly inside the interpreter's environment!

### 5. One Dark Pro Theme & Sizing Polish
- **Subtle Syntax Highlighter**: Replaced neon colors with a soft, elegant One Dark Pro style using gentle teal, warm gold, and light blue accents.
- **Sleek Zinc Scrollbars**: Implemented global CSS webkit scrollbars with compact dark tracks and floating hover-responsive pills.
- **Compact Run Button**: Decreased padding and height on the Run Code button to a sleek regular-weight `h-8` element.
