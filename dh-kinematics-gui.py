import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sympy as sp

# -------------------- Degree trig functions --------------------
def cosd(x):
    return sp.cos(sp.pi * x / 180)


def sind(x):
    return sp.sin(sp.pi * x / 180)


def mDH_deg(alpha, a, d, theta):
    """Modified DH transformation matrix"""
    return sp.Matrix([
        [cosd(theta),               -sind(theta),                0,                        a],
        [sind(theta)*cosd(alpha),    cosd(theta)*cosd(alpha),   -sind(alpha), -sind(alpha)*d],
        [sind(theta)*sind(alpha),    cosd(theta)*sind(alpha),    cosd(alpha),  cosd(alpha)*d],
        [0,                          0,                          0,                        1]
    ])


def strip_pi_over_180(expr):
    """Replace cos(pi*X/180) -> cos(X), sin(pi*X/180) -> sin(X) for display"""
    X = sp.Wild('X')
    expr2 = expr.replace(sp.cos(sp.pi*X/180), sp.cos(X))
    expr2 = expr2.replace(sp.sin(sp.pi*X/180), sp.sin(X))
    return expr2


def format_with_CS(expr_str):
    """Replace cos/sin with C/S and theta/alpha with Greek symbols for compact display"""
    import re
    result = re.sub(r'cos\(', 'C(', expr_str)
    result = re.sub(r'sin\(', 'S(', result)
    # Replace theta and alpha with Greek symbols
    result = re.sub(r'theta', 'θ', result)
    result = re.sub(r'alpha', 'α', result)
    return result


def format_matrix_clean(M):
    """Custom matrix formatter with clean bracket visualization and center alignment"""
    import re
    
    Md = M.applyfunc(strip_pi_over_180)
    # Convert to strings without pretty printing first
    rows = []
    
    for i in range(Md.shape[0]):
        row_items = []
        for j in range(Md.shape[1]):
            element = Md[i, j]
            # Convert to string and apply formatting
            elem_str = str(element)
            elem_str = format_with_CS(elem_str)
            row_items.append(elem_str)
        rows.append(row_items)
    
    # Find max width for each column
    col_widths = []
    for j in range(Md.shape[1]):
        max_width = max(len(rows[i][j]) for i in range(Md.shape[0]))
        col_widths.append(max_width)
    
    # Build formatted matrix
    lines = []
    for i, row in enumerate(rows):
        # Format each element with padding
        formatted_items = []
        for j, item in enumerate(row):
            formatted_items.append(item.rjust(col_widths[j]))
        
        # Add brackets
        if i == 0:
            bracket_left = '⎡'
            bracket_right = '⎤'
        elif i == len(rows) - 1:
            bracket_left = '⎣'
            bracket_right = '⎦'
        else:
            bracket_left = '⎢'
            bracket_right = '⎥'
        
        line = bracket_left + '  ' + '   '.join(formatted_items) + '  ' + bracket_right
        # Center the matrix line with padding (assume ~80 char width for output)
        padding = max(0, (80 - len(line)) // 2)
        line = ' ' * padding + line
        lines.append(line)
    
    return '\n'.join(lines)


def add_matrix_spacing(matrix_str):
    """Add spacing between matrix rows for better readability"""
    lines = matrix_str.split('\n')
    # Find bracket lines and content lines
    result_lines = []
    for i, line in enumerate(lines):
        result_lines.append(line)
        # Add spacing between content rows (not between bracket rows)
        if i < len(lines) - 1 and line.strip() and not line.strip().startswith('[') and not line.strip().startswith(']'):
            # Check if next line is not a bracket line
            if lines[i+1].strip() and not lines[i+1].strip().startswith('[') and not lines[i+1].strip().startswith(']'):
                result_lines.append('')  # Add blank line for spacing
    
    return '\n'.join(result_lines)


def pretty_matrix(M):
    """Pretty print matrix with clean Unicode brackets and C/S notation"""
    return format_matrix_clean(M)


def pretty_vector(v):
    """Pretty print vector with clean Unicode brackets and C/S notation"""
    return format_matrix_clean(v)


def safe_sympify(s, locals_dict=None):
    """Parse string as sympy expression, treating undefined names as symbols"""
    if locals_dict is None:
        locals_dict = {"pi": sp.pi}
    
    s = s.strip()
    if s == "":
        raise ValueError("Empty input.")
    
    import re
    # Replace shorthand notation: T/t followed by digits -> theta, A/a followed by digits -> alpha
    s_expanded = re.sub(r'\bT([0-9]*)\b', r'theta\1', s)       # T or T1, T2, etc.
    s_expanded = re.sub(r'\bt([0-9]*)\b', r'theta\1', s_expanded)  # t or t1, t2, etc.
    s_expanded = re.sub(r'\bA([0-9]*)\b', r'alpha\1', s_expanded)  # A or A1, A2, etc.
    s_expanded = re.sub(r'\ba([0-9]*)\b', r'alpha\1', s_expanded)  # a or a1, a2, etc.
    
    try:
        return sp.sympify(s_expanded, locals=locals_dict)
    except:
        undefined = []
        for match in re.finditer(r'\b[a-zA-Z_]\w*\b', s_expanded):
            name = match.group()
            if name not in locals_dict and name not in dir(sp):
                undefined.append(name)
        
        if undefined:
            extended_locals = dict(locals_dict)
            for name in set(undefined):
                extended_locals[name] = sp.Symbol(name, positive=True)
            return sp.sympify(s_expanded, locals=extended_locals)
        else:
            raise


# -------------------- Main GUI Application --------------------
class DHCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DH Robot Kinematics Calculator")
        self.geometry("1500x850")
        
        self._build_ui()
    
    def _build_ui(self):
        """Build main notebook with three tabs"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Interactive Mode
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="Interactive Mode (Add Matrices One by One)")
        self._build_interactive_tab(tab1)
        
        # Tab 2: Table Mode
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="Table Mode (Input DH Table)")
        self._build_table_tab(tab2)
        
        # Tab 3: Inverse Kinematics
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="Inverse Kinematics")
        self._build_inverse_kinematics_tab(tab3)
        
        # Tab 4: Matrix Calculator
        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="Matrix Calculator")
        self._build_matrix_calculator_tab(tab4)
    
    # ============== TAB 1: INTERACTIVE MODE ==============
    def _build_interactive_tab(self, parent):
        """Interactive mode - add matrices individually"""
        self.int_params = []
        self.int_matrices = []
        self.int_names = {}
        
        # Top buttons
        top = ttk.Frame(parent)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Button(top, text="Add Matrix", command=self._int_add_matrix).pack(side="left", padx=5)
        ttk.Button(top, text="Reset All", command=self._int_reset_all).pack(side="left", padx=5)
        ttk.Label(top, text="").pack(side="left", fill="x", expand=True)
        
        # Main split
        main = ttk.Frame(parent)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 15))
        
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)
        
        # Left: list of matrices
        list_frame = ttk.LabelFrame(left, text="Matrices", padding=10)
        list_frame.pack(fill="y", padx=0, pady=0)
        
        self.int_listbox = tk.Listbox(list_frame, height=16, width=15, font=("Courier", 10, "bold"))
        self.int_listbox.pack(fill="y", expand=False)
        self.int_listbox.bind("<<ListboxSelect>>", self._int_on_select)
        
        # Left: parameter editor
        editor = ttk.LabelFrame(left, text="Edit Parameters", padding=10)
        editor.pack(fill="x", pady=15)
        
        self.int_sel_label = ttk.Label(editor, text="Selected: -", font=("Arial", 10, "bold"))
        self.int_sel_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Label(editor, text="α:").grid(row=1, column=0, sticky="e", padx=4, pady=5)
        ttk.Label(editor, text="a:").grid(row=2, column=0, sticky="e", padx=4, pady=5)
        ttk.Label(editor, text="d:").grid(row=3, column=0, sticky="e", padx=4, pady=5)
        ttk.Label(editor, text="θ:").grid(row=4, column=0, sticky="e", padx=4, pady=5)
        
        self.int_alpha_entry = ttk.Entry(editor, width=15, font=("Arial", 10))
        self.int_a_entry = ttk.Entry(editor, width=15, font=("Arial", 10))
        self.int_d_entry = ttk.Entry(editor, width=15, font=("Arial", 10))
        self.int_theta_entry = ttk.Entry(editor, width=15, font=("Arial", 10))
        
        self.int_alpha_entry.grid(row=1, column=1, pady=5, padx=4)
        self.int_a_entry.grid(row=2, column=1, pady=5, padx=4)
        self.int_d_entry.grid(row=3, column=1, pady=5, padx=4)
        self.int_theta_entry.grid(row=4, column=1, pady=5, padx=4)
        
        btns = ttk.Frame(editor)
        btns.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(btns, text="Update", command=self._int_update).pack(side="left", padx=4)
        ttk.Button(btns, text="Print", command=self._int_print).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete", command=self._int_delete).pack(side="left", padx=4)
        
        # Right: operations and output
        ops = ttk.LabelFrame(right, text="Operations", padding=10)
        ops.pack(fill="x")
        
        self.int_op_choice = tk.StringVar(value="2")
        ttk.Radiobutton(ops, text="1: Matrix Calculator", variable=self.int_op_choice, value="1").pack(anchor="w", pady=3)
        ttk.Radiobutton(ops, text="2: Forward Kinematics", variable=self.int_op_choice, value="2").pack(anchor="w", pady=3)
        ttk.Radiobutton(ops, text="3: Position Vector", variable=self.int_op_choice, value="3").pack(anchor="w", pady=3)
        ttk.Radiobutton(ops, text="4: Rotation Matrix", variable=self.int_op_choice, value="4").pack(anchor="w", pady=3)
        
        # Format instructions
        ttk.Label(ops, text="Format: T01*T12, T01^T (transpose), T01^-1 (inverse), etc ", font=("Arial", 9), foreground="gray").pack(anchor="w", pady=(10, 0))
        
        expr_frame = ttk.Frame(ops)
        expr_frame.pack(fill="x", pady=10)
        ttk.Label(expr_frame, text="Expression:").pack(anchor="w")
        self.int_expr_entry = ttk.Entry(expr_frame, width=50, font=("Arial", 10))
        self.int_expr_entry.pack(fill="x", pady=(0, 5))
        ttk.Button(expr_frame, text="Run Operation", command=self._int_run_op).pack(anchor="e")
        
        # Output
        out_frame = ttk.LabelFrame(right, text="Results", padding=5)
        out_frame.pack(fill="both", expand=True, pady=10)
        
        # Clear button
        clear_frame = ttk.Frame(out_frame)
        clear_frame.pack(fill="x", pady=(0, 5))
        ttk.Button(clear_frame, text="Clear Results", command=lambda: self.int_output.delete("1.0", "end")).pack(anchor="e")
        
        self.int_output = scrolledtext.ScrolledText(out_frame, height=25, wrap="word", font=("Courier New", 10))
        self.int_output.pack(fill="both", expand=True)
        # Configure center alignment tag
        self.int_output.tag_configure("center", justify="center")
        
        self._int_write_output("DH Matrix Calculator\n\n")
    
    def _int_add_matrix(self):
        """Add new matrix in interactive mode"""
        idx = len(self.int_matrices)
        self.int_params.append({"alpha": "", "a": "", "d": "", "theta": ""})
        self.int_matrices.append(sp.eye(4))
        
        name = f"T{idx}{idx+1}"
        self.int_listbox.insert("end", name)
        self.int_listbox.select_set(idx)
        self._int_on_select(None)
    
    def _int_on_select(self, evt):
        """Select matrix in interactive mode"""
        sel = self.int_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        
        self.int_sel_label.config(text=f"Selected: T{idx}{idx+1}")
        p = self.int_params[idx]
        
        for entry in (self.int_alpha_entry, self.int_a_entry, self.int_d_entry, self.int_theta_entry):
            entry.delete(0, "end")
        
        self.int_alpha_entry.insert(0, p["alpha"])
        self.int_a_entry.insert(0, p["a"])
        self.int_d_entry.insert(0, p["d"])
        self.int_theta_entry.insert(0, p["theta"])
    
    def _int_update(self):
        """Update selected matrix in interactive mode"""
        sel = self.int_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        
        try:
            alpha = safe_sympify(self.int_alpha_entry.get())
            a = safe_sympify(self.int_a_entry.get())
            d = safe_sympify(self.int_d_entry.get())
            theta = safe_sympify(self.int_theta_entry.get())
            
            Ti = mDH_deg(alpha, a, d, theta)
            Ti = sp.simplify(Ti)
            
            self.int_matrices[idx] = Ti
            self.int_params[idx] = {"alpha": self.int_alpha_entry.get(), "a": self.int_a_entry.get(), 
                                   "d": self.int_d_entry.get(), "theta": self.int_theta_entry.get()}
            
            self._int_write_output(f"\nUpdated T{idx}{idx+1}:\n")
            self._int_write_output(pretty_matrix(Ti) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def _int_print(self):
        """Print selected matrix"""
        sel = self.int_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        self._int_write_output(f"\nT{idx}{idx+1} =\n{pretty_matrix(self.int_matrices[idx])}\n")
    
    def _int_delete(self):
        """Delete selected matrix"""
        sel = self.int_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        
        self.int_matrices.pop(idx)
        self.int_params.pop(idx)
        self.int_listbox.delete(idx)
        
        self.int_listbox.delete(0, "end")
        for i in range(len(self.int_matrices)):
            self.int_listbox.insert("end", f"T{i}{i+1}")
        
        for entry in (self.int_alpha_entry, self.int_a_entry, self.int_d_entry, self.int_theta_entry):
            entry.delete(0, "end")
        self.int_sel_label.config(text="Selected: -")
    
    def _int_reset_all(self):
        """Reset all in interactive mode"""
        self.int_matrices = []
        self.int_params = []
        self.int_listbox.delete(0, "end")
        for entry in (self.int_alpha_entry, self.int_a_entry, self.int_d_entry, self.int_theta_entry):
            entry.delete(0, "end")
        self.int_output.delete("1.0", "end")
        self._int_write_output("Reset complete.\n\n")
    
    def _int_run_op(self):
        """Run operation in interactive mode"""
        if not self.int_matrices:
            messagebox.showwarning("No matrices", "Add matrices first")
            return
        
        choice = self.int_op_choice.get()
        
        try:
            if choice == "1":
                expr = self.int_expr_entry.get().strip()
                if not expr:
                    return
                
                # Create matrix names dict
                names = {f"T{i}{i+1}": self.int_matrices[i] for i in range(len(self.int_matrices))}
                names["I"] = sp.eye(4)
                
                # Process expression with transpose and inverse operators
                result = self._process_matrix_expression(expr, names)
                
                self._int_write_output(f"\n{expr} =\n")
                if isinstance(result, sp.MatrixBase):
                    self._int_write_output(pretty_matrix(sp.simplify(result)) + "\n")
                else:
                    self._int_write_output(f"{result}\n")
            
            elif choice == "2":
                Tf = sp.eye(4)
                for M in self.int_matrices:
                    Tf = sp.simplify(Tf * M)
                self._int_write_output("\nForward Kinematics T0N =\n")
                self._int_write_output(pretty_matrix(Tf) + "\n")
            
            elif choice == "3":
                Tf = sp.eye(4)
                for M in self.int_matrices:
                    Tf = sp.simplify(Tf * M)
                self._int_write_output("\nPosition Vector p =\n")
                self._int_write_output(pretty_vector(Tf[:3, 3]) + "\n")
            
            elif choice == "4":
                Tf = sp.eye(4)
                for M in self.int_matrices:
                    Tf = sp.simplify(Tf * M)
                self._int_write_output("\nRotation Matrix R =\n")
                self._int_write_output(pretty_matrix(Tf[:3, :3]) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Operation error: {e}")
    
    def _process_matrix_expression(self, expr, names):
        """Process matrix expression with transpose (^T) and inverse (^-1) operators"""
        import re
        
        # Replace ^ operators: T01^T -> transpose, T01^-1 -> inverse
        # Handle ^T (transpose)
        expr_proc = re.sub(r'(T\d+)\^[Tt]', r'(\1.T)', expr)
        # Handle ^-1 (inverse)
        expr_proc = re.sub(r'(T\d+)\^-1', r'(\1)**(-1)', expr_proc)
        # Handle ^-1 with parentheses: (expr)^-1
        expr_proc = re.sub(r'\)(\^-1)', r')**(-1)', expr_proc)
        # Handle ^T with parentheses: (expr)^T
        expr_proc = re.sub(r'\)(\^[Tt])', r').T', expr_proc)
        
        # Evaluate the processed expression
        result = eval(expr_proc, {"__builtins__": {}}, names)
        return result
    
    def _int_write_output(self, text):
        """Write to interactive output"""
        self.int_output.insert("end", text)
        self.int_output.see("end")
    
    # ============== TAB 2: TABLE MODE ==============
    def _build_table_tab(self, parent):
        """Table mode - input DH table directly"""
        self.tbl_entry_fields = []
        self.tbl_row_labels = []  # Store row labels for cleanup
        self.tbl_num_rows = 3
        
        # Instructions
        # Top frame
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text="DH Parameters Table Input", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Table
        self.tbl_table_frame = ttk.Frame(top_frame)
        self.tbl_table_frame.pack(fill="both", expand=False, pady=10)
        table_frame = self.tbl_table_frame
        
        headers = ["Link", "α (Degree)", "a", "d", "θ (Degree)"]
        for col, header in enumerate(headers):
            ttk.Label(table_frame, text=header, font=("Arial", 10, "bold"), relief="solid", borderwidth=1).grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        
        self._tbl_create_rows(table_frame)
        
        # Buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Add Row", command=lambda: self._tbl_add_row(table_frame)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove Last Row", command=self._tbl_remove_row).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Calculate All", command=self._tbl_calculate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self._tbl_clear).pack(side="left", padx=5)
        
        # Output
        out_frame = ttk.LabelFrame(parent, text="Results", padding=10)
        out_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Clear button
        clear_frame = ttk.Frame(out_frame)
        clear_frame.pack(fill="x", pady=(0, 5))
        ttk.Button(clear_frame, text="Clear Results", command=lambda: self.tbl_output.delete("1.0", "end")).pack(anchor="e")
        
        self.tbl_output = scrolledtext.ScrolledText(out_frame, height=25, wrap="word", font=("Courier New", 10))
        self.tbl_output.pack(fill="both", expand=True)
        # Configure center alignment tag
        self.tbl_output.tag_configure("center", justify="center")
        
        self._tbl_write_output("DH Matrix Calculator (Table Method) \n\n")
    
    def _tbl_create_rows(self, parent):
        """Create table rows"""
        for row in range(1, self.tbl_num_rows + 1):
            label = ttk.Label(parent, text=f"T{row-1}{row}", relief="solid", borderwidth=1)
            label.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
            self.tbl_row_labels.append(label)
            row_entries = []
            for col in range(1, 5):
                entry = ttk.Entry(parent, width=12, font=("Arial", 10))
                entry.grid(row=row, column=col, padx=5, pady=5)
                row_entries.append(entry)
            self.tbl_entry_fields.append(row_entries)
    
    def _tbl_add_row(self, parent):
        """Add row in table mode"""
        self.tbl_num_rows += 1
        row = self.tbl_num_rows
        label = ttk.Label(parent, text=f"T{row-1}{row}", relief="solid", borderwidth=1)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
        self.tbl_row_labels.append(label)
        row_entries = []
        for col in range(1, 5):
            entry = ttk.Entry(parent, width=12, font=("Arial", 10))
            entry.grid(row=row, column=col, padx=5, pady=5)
            row_entries.append(entry)
        self.tbl_entry_fields.append(row_entries)
    
    def _tbl_remove_row(self):
        """Remove last row in table mode"""
        if self.tbl_num_rows > 1:
            # Remove label
            label = self.tbl_row_labels.pop()
            label.grid_forget()
            # Remove entries
            for entry in self.tbl_entry_fields[-1]:
                entry.grid_forget()
            self.tbl_entry_fields.pop()
            self.tbl_num_rows -= 1
    
    def _tbl_clear(self):
        """Clear table"""
        for row_entries in self.tbl_entry_fields:
            for entry in row_entries:
                entry.delete(0, "end")
        self.tbl_output.delete("1.0", "end")
        self._tbl_write_output("All cleared.\n\n")
    
    def _tbl_calculate(self):
        """Calculate in table mode"""
        try:
            dh_params = []
            for row_entries in self.tbl_entry_fields:
                if all(e.get().strip() == "" for e in row_entries):
                    continue
                alpha, a, d, theta = [safe_sympify(e.get().strip()) for e in row_entries]
                dh_params.append([alpha, a, d, theta])
            
            if not dh_params:
                messagebox.showwarning("Empty", "Enter DH parameters first")
                return
            
            self.tbl_output.delete("1.0", "end")
            self._tbl_write_output("=" * 80 + "\n")
            self._tbl_write_output("DH TRANSFORMATION MATRICES\n")
            self._tbl_write_output("=" * 80 + "\n\n")
            
            matrices = []
            for i, (alpha, a, d, theta) in enumerate(dh_params):
                Ti = mDH_deg(alpha, a, d, theta)
                Ti = sp.simplify(Ti)
                matrices.append(Ti)
                self._tbl_write_output(f"T{i}{i+1} =\n{pretty_matrix(Ti)}\n" + "-" * 80 + "\n")
            
            self._tbl_write_output("\n" + "=" * 80 + "\n")
            self._tbl_write_output("FORWARD KINEMATICS T0N\n")
            self._tbl_write_output("=" * 80 + "\n\n")
            
            forward = sp.eye(4)
            for Ti in matrices:
                forward = sp.simplify(forward * Ti)
            
            self._tbl_write_output("T0N =\n" + pretty_matrix(forward) + "\n\n")
            
            self._tbl_write_output("=" * 80 + "\nPOSITION VECTOR\n" + "=" * 80 + "\n\n")
            self._tbl_write_output("p =\n")
            self._tbl_write_output(pretty_vector(forward[:3, 3]) + "\n\n")
            
            self._tbl_write_output("=" * 80 + "\nROTATION MATRIX\n" + "=" * 80 + "\n\n")
            self._tbl_write_output("R =\n")
            self._tbl_write_output(pretty_matrix(forward[:3, :3]) + "\n\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {e}")
    
    def _tbl_write_output(self, text):
        """Write to table output"""
        self.tbl_output.insert("end", text)
        self.tbl_output.see("end")
    
    # ============== TAB 3: INVERSE KINEMATICS ==============
    def _build_inverse_kinematics_tab(self, parent):
        """Inverse Kinematics tab - solve for joint angles"""
        # Top section with instructions
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text="Inverse Kinematics Problem Solver", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(top_frame, text="Instructions: Define DH parameters, specify end-effector pose (position & orientation), and solve for joint angles.", 
                  font=("Arial", 10), foreground="gray").pack(anchor="w", pady=(0, 5))
        
        # Main container
        main = ttk.Frame(parent)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel: DH Table input
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", padx=(0, 15), expand=False)
        
        dh_frame = ttk.LabelFrame(left, text="DH Parameters", padding=10)
        dh_frame.pack(fill="both", padx=0, pady=0)
        
        # DH table header
        ttk.Label(dh_frame, text="Link", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(dh_frame, text="α (deg)", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(dh_frame, text="a", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Label(dh_frame, text="d", font=("Arial", 10, "bold")).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        ttk.Label(dh_frame, text="θ (var)", font=("Arial", 10, "bold")).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        
        self.ik_dh_entries = []
        self.ik_num_links = tk.IntVar(value=3)
        
        for i in range(3):
            self._ik_add_dh_row(dh_frame, i)
        
        # Add/remove buttons for DH table
        btn_frame = ttk.Frame(dh_frame)
        btn_frame.grid(row=10, column=0, columnspan=5, sticky="ew", pady=10)
        ttk.Button(btn_frame, text="Add Link", command=lambda: self._ik_add_dh_row_dynamic(dh_frame)).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Remove Link", command=self._ik_remove_dh_row).pack(side="left", padx=4)
        
        # End-effector target frame
        target_frame = ttk.LabelFrame(left, text="Target End-Effector Pose", padding=10)
        target_frame.pack(fill="x", padx=0, pady=15)
        
        ttk.Label(target_frame, text="Position (px, py, pz):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        px_frame = ttk.Frame(target_frame)
        px_frame.pack(fill="x", pady=3)
        ttk.Label(px_frame, text="px:").pack(side="left", padx=5)
        self.ik_px_entry = ttk.Entry(px_frame, width=15, font=("Arial", 10))
        self.ik_px_entry.pack(side="left", padx=5)
        self.ik_px_entry.insert(0, "1")
        
        py_frame = ttk.Frame(target_frame)
        py_frame.pack(fill="x", pady=3)
        ttk.Label(py_frame, text="py:").pack(side="left", padx=5)
        self.ik_py_entry = ttk.Entry(py_frame, width=15, font=("Arial", 10))
        self.ik_py_entry.pack(side="left", padx=5)
        self.ik_py_entry.insert(0, "0.5")
        
        pz_frame = ttk.Frame(target_frame)
        pz_frame.pack(fill="x", pady=3)
        ttk.Label(pz_frame, text="pz:").pack(side="left", padx=5)
        self.ik_pz_entry = ttk.Entry(pz_frame, width=15, font=("Arial", 10))
        self.ik_pz_entry.pack(side="left", padx=5)
        self.ik_pz_entry.insert(0, "0.5")
        
        ttk.Label(target_frame, text="Rotation Matrix (or Euler angles):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        ttk.Label(target_frame, text="Enter 9 elements for R, or leave empty for identity", font=("Arial", 9), foreground="gray").pack(anchor="w")
        
        self.ik_rot_entry = ttk.Entry(target_frame, width=30, font=("Arial", 10))
        self.ik_rot_entry.pack(fill="x", pady=3)
        self.ik_rot_entry.insert(0, "1,0,0,0,1,0,0,0,1")
        
        # Right panel: Solutions and results
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)
        
        # Solve button
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_frame, text="Solve Inverse Kinematics", command=self._ik_solve).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Results", command=self._ik_clear).pack(side="left", padx=5)
        
        # Results display
        results_frame = ttk.LabelFrame(right, text="Solutions", padding=5)
        results_frame.pack(fill="both", expand=True)
        
        # Clear button
        ik_clear_frame = ttk.Frame(results_frame)
        ik_clear_frame.pack(fill="x", pady=(0, 5))
        ttk.Button(ik_clear_frame, text="Clear Results", command=lambda: self.ik_output.delete("1.0", "end")).pack(anchor="e")
        
        self.ik_output = scrolledtext.ScrolledText(results_frame, height=30, wrap="word", font=("Courier New", 10))
        self.ik_output.pack(fill="both", expand=True)
        self.ik_output.tag_configure("header", foreground="darkblue", font=("Courier New", 10, "bold"))
        self.ik_output.tag_configure("solution", foreground="darkgreen")
        
        self._ik_write_output(" inverse kinematics problems.\n\n", "header")
    
    def _ik_add_dh_row(self, parent, row_idx):
        """Add a DH parameter row"""
        ttk.Label(parent, text=f"L{row_idx+1}").grid(row=row_idx+1, column=0, sticky="w", padx=5, pady=5)
        
        entries = []
        for col in range(1, 5):
            entry = ttk.Entry(parent, width=12, font=("Arial", 10))
            entry.grid(row=row_idx+1, column=col, padx=5, pady=5)
            entries.append(entry)
        
        # Set default values for a 3-link RR robot
        if row_idx == 0:
            entries[0].insert(0, "0")      # alpha
            entries[1].insert(0, "1")      # a
            entries[2].insert(0, "0")      # d
            entries[3].insert(0, "theta1") # theta
        elif row_idx == 1:
            entries[0].insert(0, "0")
            entries[1].insert(0, "1")
            entries[2].insert(0, "0")
            entries[3].insert(0, "theta2")
        elif row_idx == 2:
            entries[0].insert(0, "0")
            entries[1].insert(0, "0.5")
            entries[2].insert(0, "0")
            entries[3].insert(0, "theta3")
        
        self.ik_dh_entries.append(entries)
    
    def _ik_add_dh_row_dynamic(self, parent):
        """Add a new DH row dynamically"""
        row_idx = len(self.ik_dh_entries)
        
        ttk.Label(parent, text=f"L{row_idx+1}").grid(row=row_idx+1, column=0, sticky="w", padx=5, pady=5)
        
        entries = []
        for col in range(1, 5):
            entry = ttk.Entry(parent, width=12, font=("Arial", 10))
            entry.grid(row=row_idx+1, column=col, padx=5, pady=5)
            entries.append(entry)
        
        entries[0].insert(0, "0")
        entries[1].insert(0, "1")
        entries[2].insert(0, "0")
        entries[3].insert(0, f"theta{row_idx+1}")
        
        self.ik_dh_entries.append(entries)
        self.ik_num_links.set(row_idx + 1)
    
    def _ik_remove_dh_row(self):
        """Remove last DH row"""
        if len(self.ik_dh_entries) > 1:
            entries = self.ik_dh_entries.pop()
            for entry in entries:
                entry.grid_forget()
            self.ik_num_links.set(len(self.ik_dh_entries))
    
    def _ik_solve(self):
        """Solve inverse kinematics problem"""
        try:
            self._ik_write_output("Solving Inverse Kinematics...\n", "header")
            self._ik_write_output("=" * 80 + "\n\n")
            
            # Parse DH parameters
            dh_params = []
            theta_vars = []
            for entries in self.ik_dh_entries:
                alpha = safe_sympify(entries[0].get().strip())
                a = safe_sympify(entries[1].get().strip())
                d = safe_sympify(entries[2].get().strip())
                theta_expr = entries[3].get().strip()
                theta_sym = sp.Symbol(theta_expr)
                theta_vars.append(theta_sym)
                dh_params.append([alpha, a, d, theta_sym])
            
            # Build forward kinematics T0N
            self._ik_write_output("Step 1: Forward Kinematics (Symbolic)\n")
            self._ik_write_output("-" * 80 + "\n\n")
            
            T0N = sp.eye(4)
            for i, (alpha, a, d, theta) in enumerate(dh_params):
                Ti = mDH_deg(alpha, a, d, theta)
                T0N = sp.simplify(T0N * Ti)
                self._ik_write_output(f"T{i}{i+1} computed...\n")
            
            self._ik_write_output(f"\nT0N (first 2 rows):\n")
            self._ik_write_output(str(T0N[:2, :]) + "\n\n")
            
            # Parse target pose
            self._ik_write_output("Step 2: Target End-Effector Pose\n")
            self._ik_write_output("-" * 80 + "\n\n")
            
            px = float(self.ik_px_entry.get().strip())
            py = float(self.ik_py_entry.get().strip())
            pz = float(self.ik_pz_entry.get().strip())
            
            self._ik_write_output(f"Position: p = [{px}, {py}, {pz}]ᵀ\n\n")
            
            # Create target transformation matrix
            target_R_str = self.ik_rot_entry.get().strip()
            if target_R_str and target_R_str != "":
                try:
                    rot_vals = [float(x.strip()) for x in target_R_str.split(",")]
                    if len(rot_vals) == 9:
                        target_R = sp.Matrix(3, 3, rot_vals)
                    else:
                        self._ik_write_output("Warning: Invalid rotation matrix (need 9 values). Using identity.\n")
                        target_R = sp.eye(3)
                except:
                    self._ik_write_output("Warning: Could not parse rotation matrix. Using identity.\n")
                    target_R = sp.eye(3)
            else:
                target_R = sp.eye(3)
            
            target_T = sp.Matrix([
                [target_R[0, 0], target_R[0, 1], target_R[0, 2], px],
                [target_R[1, 0], target_R[1, 1], target_R[1, 2], py],
                [target_R[2, 0], target_R[2, 1], target_R[2, 2], pz],
                [0, 0, 0, 1]
            ])
            
            self._ik_write_output("Target Transformation Matrix:\n")
            self._ik_write_output(pretty_matrix(target_T) + "\n\n")
            
            # Set up equations: position constraints
            self._ik_write_output("Step 3: Solving Equations\n")
            self._ik_write_output("-" * 80 + "\n\n")
            
            px_expr = T0N[0, 3]
            py_expr = T0N[1, 3]
            pz_expr = T0N[2, 3]
            
            equations = [
                sp.Eq(px_expr, px),
                sp.Eq(py_expr, py),
                sp.Eq(pz_expr, pz)
            ]
            
            self._ik_write_output(f"Position Equations:\n")
            self._ik_write_output(f"  x: {px_expr} = {px}\n")
            self._ik_write_output(f"  y: {py_expr} = {py}\n")
            self._ik_write_output(f"  z: {pz_expr} = {pz}\n\n")
            
            # Attempt to solve
            self._ik_write_output("Solving system of equations...\n\n")
            
            try:
                solutions = sp.solve(equations, theta_vars, dict=True)
                
                if not solutions:
                    self._ik_write_output("No analytical solution found.\n")
                    self._ik_write_output("Note: Some problems may require numerical methods.\n", "solution")
                    return
                
                self._ik_write_output(f"Found {len(solutions)} solution(s):\n\n", "header")
                
                for sol_idx, sol in enumerate(solutions, 1):
                    self._ik_write_output(f"Solution {sol_idx}:\n", "solution")
                    self._ik_write_output("-" * 40 + "\n")
                    for var, val in sol.items():
                        self._ik_write_output(f"  {var} = {val}\n", "solution")
                    self._ik_write_output("\n")
                
            except Exception as solve_error:
                self._ik_write_output(f"Symbolic solver encountered issue: {solve_error}\n")
                self._ik_write_output("Try numerical approach or simplify problem.\n", "solution")
            
            self._ik_write_output("=" * 80 + "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"IK Calculation error: {e}")
            self._ik_write_output(f"ERROR: {e}\n")
    
    def _ik_clear(self):
        """Clear inverse kinematics output"""
        self.ik_output.delete("1.0", "end")
        self._ik_write_output("Cleared.\n\n", "header")
    
    def _ik_write_output(self, text, tag=""):
        """Write to IK output"""
        if tag:
            self.ik_output.insert("end", text, tag)
        else:
            self.ik_output.insert("end", text)
        self.ik_output.see("end")
    
    # ============== TAB 4: MATRIX CALCULATOR ==============
    def _build_matrix_calculator_tab(self, parent):
        """Matrix Calculator tab - add matrices one by one and perform multiple operations"""
        self.mc_matrices = []
        self.mc_names = {}
        
        # Top buttons
        top = ttk.Frame(parent)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Button(top, text="Add Matrix", command=self._mc_add_matrix).pack(side="left", padx=5)
        ttk.Button(top, text="Reset All", command=self._mc_reset_all).pack(side="left", padx=5)
        ttk.Label(top, text="").pack(side="left", fill="x", expand=True)
        
        # Main split
        main = ttk.Frame(parent)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 15))
        
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)
        
        # Left: list of matrices
        list_frame = ttk.LabelFrame(left, text="Matrices", padding=10)
        list_frame.pack(fill="y", padx=0, pady=0)
        
        self.mc_listbox = tk.Listbox(list_frame, height=16, width=15, font=("Courier", 10, "bold"))
        self.mc_listbox.pack(fill="y", expand=False)
        self.mc_listbox.bind("<<ListboxSelect>>", self._mc_on_select)
        
        # Left: matrix input editor
        editor = ttk.LabelFrame(left, text="Matrix Input", padding=10)
        editor.pack(fill="x", pady=15)
        
        self.mc_sel_label = ttk.Label(editor, text="Selected: -", font=("Arial", 10, "bold"), foreground="darkblue")
        self.mc_sel_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))
        
        # Dimension inputs with better layout
        dim_frame = ttk.Frame(editor)
        dim_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        ttk.Label(dim_frame, text="Rows:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.mc_rows_entry = ttk.Entry(dim_frame, width=6, font=("Arial", 10))
        self.mc_rows_entry.pack(side="left", padx=(0, 15))
        
        ttk.Label(dim_frame, text="Cols:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.mc_cols_entry = ttk.Entry(dim_frame, width=6, font=("Arial", 10))
        self.mc_cols_entry.pack(side="left", padx=(0, 10))
        
        ttk.Button(dim_frame, text="Create Grid", command=self._mc_create_grid, width=15).pack(side="left")
        
        # Matrix grid container (will hold Entry widgets)
        self.mc_grid_frame = ttk.Frame(editor)
        self.mc_grid_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 15), padx=5)
        self.mc_grid_entries = []
        
        # Action buttons
        btn_frame1 = ttk.Frame(editor)
        btn_frame1.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        ttk.Button(btn_frame1, text="Apply", command=self._mc_apply_matrix, width=10).pack(side="left", padx=2, fill="x", expand=True)
        ttk.Button(btn_frame1, text="Print", command=self._mc_print_matrix, width=10).pack(side="left", padx=2, fill="x", expand=True)
        ttk.Button(btn_frame1, text="Delete", command=self._mc_delete_matrix, width=10).pack(side="left", padx=2, fill="x", expand=True)
        
        # Right: operations and output
        ops = ttk.LabelFrame(right, text="Operations & Expression", padding=10)
        ops.pack(fill="x")
        
        ttk.Label(ops, text="Format: M0*M1, M0^T (transpose), M0^-1 (inverse), etc.", font=("Arial", 9), foreground="gray").pack(anchor="w", pady=(0, 10))
        
        expr_frame = ttk.Frame(ops)
        expr_frame.pack(fill="x", pady=10)
        ttk.Label(expr_frame, text="Expression:").pack(anchor="w")
        self.mc_expr_entry = ttk.Entry(expr_frame, width=50, font=("Arial", 10))
        self.mc_expr_entry.pack(fill="x", pady=(0, 5))
        ttk.Button(expr_frame, text="Run Operation", command=self._mc_run_operation).pack(anchor="e")
        
        # Output
        out_frame = ttk.LabelFrame(right, text="Results", padding=5)
        out_frame.pack(fill="both", expand=True, pady=10)
        
        # Clear button
        mc_clear_frame = ttk.Frame(out_frame)
        mc_clear_frame.pack(fill="x", pady=(0, 5))
        ttk.Button(mc_clear_frame, text="Clear Results", command=lambda: self.mc_output.delete("1.0", "end")).pack(anchor="e")
        
        self.mc_output = scrolledtext.ScrolledText(out_frame, height=25, wrap="word", font=("Courier New", 10))
        self.mc_output.pack(fill="both", expand=True)
        self.mc_output.tag_configure("center", justify="center")
        
        self._mc_write_output("Matrix Calculator\n\n")
    
    def _mc_add_matrix(self):
        """Add new matrix in matrix calculator mode - ask for dimensions and fill grid"""
        # Create a dialog to ask for dimensions
        dialog = tk.Toplevel(self)
        dialog.title("New Matrix")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter matrix dimensions:", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Rows and Cols input
        dim_frame = ttk.Frame(dialog)
        dim_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(dim_frame, text="Rows:", font=("Arial", 9)).pack(side="left", padx=(0, 5))
        rows_entry = ttk.Entry(dim_frame, width=5, font=("Arial", 10))
        rows_entry.pack(side="left", padx=(0, 20))
        rows_entry.insert(0, "2")
        
        ttk.Label(dim_frame, text="Cols:", font=("Arial", 9)).pack(side="left", padx=(0, 5))
        cols_entry = ttk.Entry(dim_frame, width=5, font=("Arial", 10))
        cols_entry.pack(side="left")
        cols_entry.insert(0, "2")
        
        # Grid container frame
        grid_label = ttk.Label(dialog, text="Matrix values:", font=("Arial", 10, "bold"))
        grid_label.pack(pady=(15, 5))
        
        grid_container = ttk.Frame(dialog)
        grid_container.pack(fill="both", expand=True, padx=20, pady=5)
        
        grid_entries = []
        
        def show_grid():
            """Show the grid based on dimensions"""
            try:
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
                if rows < 1 or cols < 1:
                    messagebox.showerror("Invalid", "Rows and Columns must be >= 1")
                    return
                
                # Clear existing grid
                for widget in grid_container.winfo_children():
                    widget.destroy()
                grid_entries.clear()
                
                # Create new grid
                for r in range(rows):
                    row_entries = []
                    for c in range(cols):
                        entry = ttk.Entry(grid_container, width=8, font=("Arial", 10))
                        entry.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
                        entry.insert(0, "0")
                        row_entries.append(entry)
                    grid_entries.append(row_entries)
                
                # Configure grid weights
                for r in range(rows):
                    grid_container.grid_rowconfigure(r, weight=1)
                for c in range(cols):
                    grid_container.grid_columnconfigure(c, weight=1)
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integers")
        
        def create_matrix():
            """Create matrix from grid values"""
            try:
                if not grid_entries:
                    messagebox.showerror("Error", "Please click 'Create Grid' first")
                    return
                
                # Read matrix from grid entries
                matrix_data = []
                for row_entries in grid_entries:
                    row_values = []
                    for entry in row_entries:
                        val = entry.get().strip()
                        if not val:
                            raise ValueError("Grid contains empty cells")
                        row_values.append(safe_sympify(val))
                    matrix_data.append(row_values)
                
                # Create the matrix
                idx = len(self.mc_matrices)
                M = sp.Matrix(matrix_data)
                self.mc_matrices.append(M)
                
                name = f"M{idx}"
                self.mc_listbox.insert("end", name)
                self.mc_names[name] = M
                self.mc_listbox.select_set(idx)
                self._mc_on_select(None)
                self._mc_write_output(f"Matrix {name} added ({M.shape[0]}×{M.shape[1]})\n\n")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid matrix values:\n{e}")
        
        # Button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Create Grid", command=show_grid, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Apply", command=create_matrix, width=15).pack(side="left", padx=5)
        
        dialog.focus()
    
    def _mc_on_select(self, evt):
        """Select matrix in matrix calculator mode"""
        sel = self.mc_listbox.curselection()
        if not sel:
            if self.mc_matrices:
                self.mc_listbox.select_set(0)
                sel = (0,)
            else:
                return
        idx = int(sel[0])
        
        name = f"M{idx}"
        self.mc_sel_label.config(text=f"Selected: {name}")
        
        # Update matrix editor
        M = self.mc_matrices[idx]
        self.mc_rows_entry.delete(0, "end")
        self.mc_cols_entry.delete(0, "end")
        self.mc_rows_entry.insert(0, str(M.shape[0]))
        self.mc_cols_entry.insert(0, str(M.shape[1]))
        
        # Recreate grid with current matrix values
        self._mc_create_grid()
        
        # Populate grid with matrix values
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                self.mc_grid_entries[i][j].delete(0, "end")
                self.mc_grid_entries[i][j].insert(0, str(M[i, j]))
    
    def _mc_create_grid(self):
        """Create grid of entry fields for matrix input"""
        try:
            rows = int(self.mc_rows_entry.get())
            cols = int(self.mc_cols_entry.get())
            
            if rows < 1 or cols < 1:
                messagebox.showerror("Invalid", "Rows and Columns must be >= 1")
                return
            
            # Clear existing grid - destroy all widgets in frame
            for widget in self.mc_grid_frame.winfo_children():
                widget.destroy()
            self.mc_grid_entries = []
            
            # Reset grid configuration
            for i in range(10):  # Reset up to 10 rows
                self.mc_grid_frame.grid_rowconfigure(i, weight=0)
            for j in range(10):  # Reset up to 10 columns
                self.mc_grid_frame.grid_columnconfigure(j, weight=0)
            
            # Create new grid
            for r in range(rows):
                row_entries = []
                for c in range(cols):
                    entry = ttk.Entry(self.mc_grid_frame, width=10, font=("Arial", 10))
                    entry.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                    entry.insert(0, "0")
                    row_entries.append(entry)
                self.mc_grid_entries.append(row_entries)
            
            # Configure grid weight
            for r in range(rows):
                self.mc_grid_frame.grid_rowconfigure(r, weight=1)
            for c in range(cols):
                self.mc_grid_frame.grid_columnconfigure(c, weight=1)
            
        except ValueError:
            messagebox.showerror("Error", "Enter valid row and column numbers")
    
    def _mc_apply_matrix(self):
        """Apply/save the matrix input from grid"""
        sel = self.mc_listbox.curselection()
        if not sel:
            if not self.mc_matrices:
                messagebox.showwarning("No matrices", "Add a matrix first")
                return
            self.mc_listbox.select_set(0)
            sel = (0,)
        
        idx = int(sel[0])
        
        if not self.mc_grid_entries:
            messagebox.showwarning("No grid", "Create a grid first using 'Create Grid'")
            return
        
        try:
            # Read matrix from grid entries
            matrix_data = []
            for row_entries in self.mc_grid_entries:
                row_values = []
                for entry in row_entries:
                    val = entry.get().strip()
                    if not val:
                        raise ValueError("Grid contains empty cells")
                    row_values.append(safe_sympify(val))
                matrix_data.append(row_values)
            
            M = sp.Matrix(matrix_data)
            self.mc_matrices[idx] = M
            self.mc_names[f"M{idx}"] = M
            
            # Update display with success message
            self._mc_write_output(f"\n✓ Matrix M{idx} applied ({M.shape[0]}×{M.shape[1]})\n")
            self._mc_write_output(pretty_matrix(M) + "\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid matrix values:\n{e}")
    
    def _mc_print_matrix(self):
        """Print selected matrix"""
        sel = self.mc_listbox.curselection()
        if not sel:
            if not self.mc_matrices:
                messagebox.showwarning("No matrices", "Add a matrix first")
                return
            self.mc_listbox.select_set(0)
            sel = (0,)
        
        idx = int(sel[0])
        M = self.mc_matrices[idx]
        self._mc_write_output(f"\nMatrix M{idx}:\n")
        self._mc_write_output(pretty_matrix(M) + "\n\n")
    
    def _mc_delete_matrix(self):
        """Delete selected matrix"""
        sel = self.mc_listbox.curselection()
        if not sel:
            if not self.mc_matrices:
                messagebox.showwarning("No matrices", "Add a matrix first")
                return
            self.mc_listbox.select_set(0)
            sel = (0,)
        
        idx = int(sel[0])
        self.mc_listbox.delete(idx)
        self.mc_matrices.pop(idx)
        
        # Rebuild names dict with new indices
        self.mc_names = {}
        for i, M in enumerate(self.mc_matrices):
            self.mc_names[f"M{i}"] = M
        
        # Update listbox
        self.mc_listbox.delete(0, "end")
        for i in range(len(self.mc_matrices)):
            self.mc_listbox.insert("end", f"M{i}")
        
        self.mc_sel_label.config(text="Selected: -")
        self._mc_write_output(f"✓ Matrix deleted. Remaining matrices re-indexed.\n\n")
    
    def _mc_reset_all(self):
        """Reset all matrices"""
        if messagebox.askyesno("Confirm", "Clear all matrices?"):
            self.mc_matrices = []
            self.mc_names = {}
            self.mc_listbox.delete(0, "end")
            self.mc_sel_label.config(text="Selected: -")
            self.mc_output.delete("1.0", "end")
            self._mc_write_output("All matrices cleared.\n\n")
    
    def _mc_parse_matrix(self, text_content):
        """Parse matrix from text content"""
        lines = text_content.strip().split("\n")
        matrix_data = []
        
        for line in lines:
            if line.strip():
                # Split by comma and parse each element
                elements = [safe_sympify(e.strip()) for e in line.split(",")]
                matrix_data.append(elements)
        
        if not matrix_data:
            raise ValueError("Empty matrix")
        
        # Check all rows have same length
        col_count = len(matrix_data[0])
        for row in matrix_data:
            if len(row) != col_count:
                raise ValueError(f"Row has {len(row)} columns, expected {col_count}")
        
        return sp.Matrix(matrix_data)
    
    def _mc_run_operation(self):
        """Run operation with expression"""
        if not self.mc_matrices:
            messagebox.showwarning("No matrices", "Add matrices first")
            return
        
        expr = self.mc_expr_entry.get().strip()
        if not expr:
            messagebox.showwarning("Empty expression", "Enter an expression to evaluate")
            return
        
        try:
            # Create matrix names dict
            names = dict(self.mc_names)
            
            # Process expression with transpose and inverse operators
            result = self._process_matrix_expression(expr, names)
            
            self._mc_write_output(f"\n{expr} =\n")
            if isinstance(result, sp.MatrixBase):
                self._mc_write_output(pretty_matrix(sp.simplify(result)) + "\n\n")
            else:
                self._mc_write_output(f"{result}\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Operation error:\n{e}")
    
    def _mc_write_output(self, text, tag=""):
        """Write to matrix calculator output"""
        if tag:
            self.mc_output.insert("end", text, tag)
        else:
            self.mc_output.insert("end", text)
        self.mc_output.see("end")


if __name__ == "__main__":
    app = DHCalculator()
    app.mainloop()
