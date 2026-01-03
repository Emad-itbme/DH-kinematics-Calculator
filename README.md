# Robot Kinematics GUI

An interactive Python application for robot kinematics calculations featuring symbolic mathematics and a user-friendly graphical interface. Built with SymPy for symbolic computation and Tkinter for the GUI.

## Features

- **Modified Denavit-Hartenberg (mDH) transformation matrices** - Calculate 4×4 transformation matrices
- **Symbolic computation** using SymPy for exact algebraic results
- **Four comprehensive calculation modes** (see below)
- **Degree-based trigonometric functions** - Work with degrees instead of radians
- **Pretty matrix formatting** with Unicode brackets and Greek symbols
- **Real-time symbolic expression parsing** - Support for theta, alpha, cos(), sin(), pi, and custom symbols
- **Matrix operations** - Multiplication, transpose, inverse with clean algebraic notation

## Requirements

- Python 3.8+
- NumPy
- SymPy
- Tkinter (usually included with Python)

## Installation

1. Clone or download this repository
2. Navigate to the directory:
```bash
cd "path/to/Robot/"
```

3. Install required dependencies:
```bash
pip install numpy sympy
```

4. Run the application:
```bash
python dh-kinematics-gui.py
```

## Usage Guide

### Tab 1: Interactive Mode (Add Matrices One by One)
- **Purpose**: Create and manipulate DH transformation matrices individually
- **Features**:
  - Add matrices with DH parameters (α, a, d, θ)
  - Edit parameters using symbolic expressions (e.g., `theta`, `pi/2`, `cos(alpha)`)
  - Perform complex expressions: `T01*T12`, `T01^T` (transpose), `T01^-1` (inverse)
  - View formatted results with Unicode brackets
- **Workflow**: 
  1. Click "Add Matrix" to create new matrices
  2. Enter DH parameters for each matrix
  3. Enter mathematical expressions to combine matrices
  4. Click "Run Operation" to calculate results

### Tab 2: Table Mode (Input DH Table)
- **Purpose**: Input multiple DH parameters in a structured table format
- **Features**:
  - Add/remove DH parameter rows
  - Edit parameters directly in table cells
  - Calculate all transformation matrices at once
  - View cumulative transformations (T01, T02, T03, etc.)
- **Workflow**:
  1. Add DH parameter rows using "Add Row"
  2. Enter α, a, d, θ values for each joint/link
  3. Click "Calculate All" to compute matrices
  4. View results for all intermediate transformations

### Tab 3: Inverse Kinematics
- **Purpose**: Solve inverse kinematics problems given end-effector pose
- **Features**:
  - Define DH parameters for the robot
  - Specify target position (px, py, pz) and orientation
  - Solve for joint angles that achieve the target pose
  - Support for both rotation matrices and Euler angles
  - Display all solutions with numerical values
- **Workflow**:
  1. Add DH parameters for each joint
  2. Enter target end-effector position and rotation
  3. Click "Solve Inverse Kinematics"
  4. View joint angle solutions

### Tab 4: Matrix Calculator
- **Purpose**: General-purpose symbolic matrix operations with multiple matrices
- **Features**:
  - Create matrices of any dimension (M0, M1, M2, ...)
  - Interactive grid-based input for matrix values
  - Support for symbolic expressions in matrix cells
  - Perform operations between matrices: `M0*M1`, `M0^T`, `M0^-1`
  - Complex expressions: `(M0*M1)^T`, `M0^-1 + M2`, etc.
- **Workflow**:
  1. Click "Add Matrix" to create new matrices
  2. Enter dimensions and fill matrix values in grid
  3. Create multiple matrices as needed
  4. Enter expression to combine matrices
  5. Click "Run Operation" to calculate results

### Common Features (All Tabs)
- **Clear Results Button** - Clear output area
- **Symbolic Support**:
  - Variables: `theta`, `alpha`, `pi`
  - Functions: `cos()`, `sin()`, `sqrt()`, etc.
  - Custom symbols: Define your own variables
- **Expression Format**:
  - Multiplication: `A*B`
  - Transpose: `A^T`
  - Inverse: `A^-1`
  - Combined: `(A*B)^T*C^-1`

## Key Mathematical Functions

- `cosd(x)` / `sind(x)` - Trigonometric functions working with degrees
- `mDH_deg(alpha, a, d, theta)` - Modified DH transformation matrix (4×4)
- `safe_sympify(s)` - Parse symbolic expressions safely
- `format_matrix_clean(M)` - Pretty-print matrices with Unicode brackets
- `_process_matrix_expression(expr)` - Convert math notation (^T, ^-1) to Python/SymPy format

## Supported Symbolic Expressions

### Variables
```
theta, alpha, phi, psi, d, a, x, y, z
```

### Functions
```
cos, sin, tan, sqrt, exp, ln, log
```

### Operators
```
+ (addition)
- (subtraction)
* (multiplication)
/ (division)
^ (power/exponent, e.g., A^2)
^T (transpose for matrices)
^-1 (inverse for matrices)
```

## Matrix Notation

### Interactive Mode & Table Mode
- **T01** - Transformation matrix from frame 1 to frame 0
- **T12** - Transformation matrix from frame 2 to frame 1
- **T02** - Cumulative: T01 × T12

### Matrix Calculator Mode
- **M0, M1, M2, ...** - Arbitrary numbered matrices

## Example Workflows

### Forward Kinematics (3-DOF Robot)
1. Go to **Tab 2: Table Mode**
2. Add 3 rows with your DH parameters
3. Click "Calculate All"
4. View T03 for end-effector transformation

### Matrix Operations
1. Go to **Tab 4: Matrix Calculator**
2. Add matrices M0, M1, M2
3. Enter expression: `(M0*M1)^T*M2^-1`
4. Click "Run Operation"

## Course Context

This project is part of **BME401 - Robotics** course covering:
- Denavit-Hartenberg convention and parameters
- Homogeneous transformations
- Forward kinematics
- Inverse kinematics
- Symbolic robot modeling

## Technical Architecture

- **GUI Framework**: Tkinter with ttk styling
- **Math Engine**: SymPy for symbolic computation
- **Notation System**: Modified DH (mDH) convention
- **Font Standardization**: Arial 10 for consistency
- **Output Format**: Unicode-formatted matrices with proper alignment

## Contributing

When contributing, please ensure:
- Code follows existing style conventions (Arial 10 font, consistent indentation)
- Functions include detailed docstrings
- Matrix operations handle edge cases gracefully
- New features work across all tabs consistently

## Troubleshooting

**"Module not found" error**: Install dependencies with `pip install numpy sympy`

**GUI not appearing**: Ensure Tkinter is installed (comes with most Python installations)

**Symbolic expressions not working**: Check syntax - use standard math notation (parentheses required for function arguments)

**Matrix dimension errors**: Ensure matrices being multiplied have compatible dimensions

## License

This project is developed for educational purposes as part of BME401 - Robotics course.

## Author

Developed as part of robotics coursework at Boğaziçi University (2025-2026).

---

**Last Updated**: January 2026  
**Version**: 2.0 (with Tab 4 Matrix Calculator and enhanced UI)
