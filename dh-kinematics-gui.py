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
        """Build main notebook with two tabs"""
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
        
        self.int_listbox = tk.Listbox(list_frame, height=16, width=15, font=("Courier", 11, "bold"))
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
        
        self.int_output = scrolledtext.ScrolledText(out_frame, height=25, wrap="word", font=("Courier New", 14))
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
        
        ttk.Label(top_frame, text="DH Parameters Table Input", font=("Arial", 12, "bold")).pack(anchor="w")
        
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
        
        self.tbl_output = scrolledtext.ScrolledText(out_frame, height=25, wrap="word", font=("Courier New", 14))
        self.tbl_output.pack(fill="both", expand=True)
        # Configure center alignment tag
        self.tbl_output.tag_configure("center", justify="center")
        
        self._tbl_write_output("DH Matrix Calculator\n\n")
    
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


if __name__ == "__main__":
    app = DHCalculator()
    app.mainloop()
