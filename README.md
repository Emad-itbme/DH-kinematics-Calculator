# Robot Kinematics GUI

An interactive Python application for robot kinematics calculations featuring symbolic mathematics and a user-friendly graphical interface. Built with SymPy for symbolic computation and Tkinter for the GUI.

## Features

- Modified Denavit-Hartenberg (mDH) transformation matrices
- Symbolic computation using SymPy
- Interactive GUI interface for real-time calculations
- Degree-based trigonometric functions
- Pretty matrix formatting with Unicode brackets and Greek symbols
- Clean, centered matrix visualization

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
