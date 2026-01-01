# Robot Kinematics GUI

An interactive Python application for robot kinematics calculations featuring symbolic mathematics and a user-friendly graphical interface. Built with SymPy for symbolic computation and Tkinter for the GUI.


## Features
- **Two input modes:** add matrices one by one (Interactive Mode) or compute all Ti-1→i by filling a DH table (Table Mode).
- **Editable inputs:** update or delete any matrix if you enter wrong parameters.
- **Degree-based angles:** enter alpha and theta in degrees; output is shown as cos(theta), sin(theta) (no pi/180).
- **Matrix calculator:** evaluate expressions like `T01*T12`, `(T01*T12)**-1`, and transpose operations.
- **Forward kinematics:** compute T0N by multiplying all transformation matrices.
- **Pose extraction:** display the placement vector p and the rotation matrix R.
- **Symbolic support:** accepts symbolic variables (e.g., `theta1`, `d2`, `L1`) and simplifies results using SymPy.


## Requirements

- Python 3.7+
- NumPy
- SymPy
- Tkinter (usually included with Python)

## Installation

1. Clone this repository
2. Install required dependencies:
```bash
pip install numpy sympy
```

3. Run the robot GUI:
```bash
python dh-kinematics-gui
```

## Usage

Run the interactive GUI application:
```bash
python dh-kinematics-gui
```

The application will launch a Tkinter window where you can:
- Input Denavit-Hartenberg parameters (alpha, a, d, theta)
- Calculate transformation matrices symbolically
- View formatted matrix outputs
- Perform robotic kinematics calculations

## Key Functions

- `cosd(x)` / `sind(x)` - Trigonometric functions working with degrees
- `mDH_deg(alpha, a, d, theta)` - Modified DH transformation matrix calculation
- `strip_pi_over_180(expr)` - Simplify expressions for display
- `format_with_CS(expr_str)` - Format expressions with C/S notation and Greek symbols
- `format_matrix_clean(M)` - Pretty-print matrices with Unicode brackets
- `add_matrix_spacing(matrix_str)` - Add spacing for better readability

## Course Context

This project is part of BME401 - Robotics course covering fundamental concepts in robot kinematics and homogeneous transformations.

## Contributing

When contributing, please ensure:
- Code follows the existing style conventions
- Functions include detailed docstrings
- Matrix operations handle edge cases gracefully

## License

This project is developed for educational purposes as part of BME401 - Robotics course.

## Author

Developed as part of robotics coursework.

## Contact & Support

For issues or questions about the toolkit, please refer to the individual module documentation or docstrings.

---

**Last Updated**: January 2026
