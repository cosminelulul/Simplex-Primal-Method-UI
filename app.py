"""
simplex_primal_ui
~~~~~~~~~~~~~~~~~
Tkinter GUI for the Primal Simplex Method solver.

Depends on the ``simplex-primal`` package for all algorithm logic.
Run with:  python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction
import os

from simplex-primal import solve
from simplex-primal.core import format_fraction, format_fraction_plain

# Theme #

THEME = {
    "BG_DARK"        : "#1A1A1B",
    "BG_PANEL"       : "#111112",
    "BG_CARD"        : "#252527",
    "BG_INPUT"       : "#2E2E30",
    "ACCENT"         : "#7B68EE",
    "ACCENT2"        : "#45454E",
    "GREEN"          : "#3ecf8e",
    "YELLOW"         : "#f7c948",
    "TEXT_MAIN"      : "#F6E8E8",
    "TEXT_DIM"       : "#D1DCDF",
    "MONO_FONT"      : ("Consolas", 12),
    "MONO_BIG"       : ("Consolas", 13),
    "LABEL_FONT"     : ("Segoe UI", 14),
    "BTN_FONT"       : ("Segoe UI", 12, "bold"),
    "GRID_HDR_FONT"  : ("Segoe UI", 13, "bold"),
    "GRID_LABEL_FONT": ("Segoe UI", 13, "bold"),
    "GRID_ENTRY_FONT": ("Consolas", 13),
    "GRID_OPT_FONT"  : ("Segoe UI", 13),
    "TIPVAR_FONT"    : ("Segoe UI", 13),
    "SPINBOX_FONT"   : ("Segoe UI", 14),
}

T = THEME   # short alias

# Main UI class #


class SimplexUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Primal Simplex Method")
        self.configure(bg=T["BG_DARK"])
        self.geometry("1440x750")
        if os.path.exists("icon.ico"): self.iconbitmap("icon.ico")
        self.minsize(1300, 750)

        self._result   = None
        self._iter_idx = 0

        self._setup_styles()
        self._build_ui()

    # Style setup #

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        for name in ("Dark.Vertical.TScrollbar", "Dark.Horizontal.TScrollbar"):
            style.configure(
                name,
                background=T["BG_DARK"], troughcolor=T["BG_PANEL"],
                arrowcolor=T["ACCENT"],  bordercolor=T["BG_PANEL"],
                darkcolor=T["BG_DARK"],  lightcolor=T["BG_DARK"],
            )
            style.map(name, background=[("active", T["BG_CARD"]), ("!active", T["BG_DARK"])])

        style.configure("Dark.TNotebook", background=T["BG_DARK"], borderwidth=0)
        style.configure(
            "Dark.TNotebook.Tab",
            background=T["BG_PANEL"], foreground=T["TEXT_DIM"],
            padding=[12, 4], font=("Segoe UI", 9),
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", T["BG_CARD"])],
            foreground=[("selected", T["ACCENT"])],
        )

    # Layout helpers #

    def _card(self, parent, title):
        """Titled panel card — returns the inner content frame."""
        frame = tk.Frame(parent, bg=T["BG_PANEL"],
                         highlightbackground=T["ACCENT2"], highlightthickness=1)
        frame.pack(fill="x", pady=(0, 10))
        tk.Label(frame, text=f"  {title}", font=("Segoe UI", 12, "bold"),
                 bg=T["BG_PANEL"], fg=T["ACCENT"], anchor="w", pady=5).pack(fill="x")
        tk.Frame(frame, bg=T["ACCENT2"], height=1).pack(fill="x")
        inner = tk.Frame(frame, bg=T["BG_PANEL"], padx=10, pady=8)
        inner.pack(fill="x")
        return inner

    def _make_entry(self, parent, fg=None, width=5):
        """Styled numeric Entry with a default value of 0."""
        e = tk.Entry(parent, width=width,
                     font=T["GRID_ENTRY_FONT"],
                     bg=T["BG_INPUT"], fg=fg or T["TEXT_MAIN"],
                     insertbackground=fg or T["TEXT_MAIN"],
                     relief="flat", justify="center")
        e.insert(0, "0")
        return e

    def _make_option_menu(self, parent, choices, default, fg, font_key="GRID_OPT_FONT", width=3):
        """Styled OptionMenu — returns (StringVar, widget)."""
        var  = tk.StringVar(value=default)
        menu = tk.OptionMenu(parent, var, *choices)
        kw   = dict(bg=T["BG_INPUT"], fg=fg, activebackground=T["BG_CARD"],
                    relief="flat", font=T[font_key], width=width, highlightthickness=0)
        menu.config(**kw)
        menu["menu"].config(bg=T["BG_INPUT"], fg=fg, font=T[font_key])
        return var, menu

    def _make_scrolled_text(self, parent, font_key="MONO_BIG", pad=4):
        """Text widget with both scrollbars — returns the Text widget."""
        frame = tk.Frame(parent, bg=T["BG_DARK"])
        frame.pack(fill="both", expand=True, padx=8, pady=pad)
        text  = tk.Text(frame, font=T[font_key],
                        bg=T["BG_CARD"], fg=T["TEXT_MAIN"],
                        insertbackground=T["TEXT_MAIN"],
                        relief="flat", state="disabled", wrap="none",
                        selectbackground=T["ACCENT2"])
        sy = ttk.Scrollbar(frame, orient="vertical",   command=text.yview,
                            style="Dark.Vertical.TScrollbar")
        sx = ttk.Scrollbar(frame, orient="horizontal", command=text.xview,
                            style="Dark.Horizontal.TScrollbar")
        text.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right",  fill="y")
        sx.pack(side="bottom", fill="x")
        text.pack(fill="both", expand=True)
        return text

    # Top-level layout #

    def _build_ui(self):
        hdr = tk.Frame(self, bg=T["BG_DARK"], pady=10)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="Primal Simplex Method",
                 font=("Segoe UI", 16, "bold"),
                 bg=T["BG_DARK"], fg=T["ACCENT"]).pack(side="left")
        tk.Label(hdr, text="Tabular method with solution verification",
                 font=("Segoe UI", 12),
                 bg=T["BG_DARK"], fg=T["TEXT_DIM"]).pack(side="left", padx=14)

        tk.Frame(self, bg=T["ACCENT"], height=2).pack(fill="x", padx=20, pady=(0, 8))

        body = tk.Frame(self, bg=T["BG_DARK"])
        body.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        left = tk.Frame(body, bg=T["BG_DARK"], width=440)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=T["BG_DARK"])
        right.pack(side="left", fill="both", expand=True)

        self._build_input_panel(left)
        self._build_output_panel(right)

    # Input panel #

    def _build_input_panel(self, parent):
        dim = self._card(parent, "Problem dimensions")

        for label, attr, default in [("Variables (n):", "_n_var", 3),
                                      ("Constraints (m):", "_m_var", 3)]:
            row = tk.Frame(dim, bg=T["BG_PANEL"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=T["LABEL_FONT"],
                     bg=T["BG_PANEL"], fg=T["TEXT_DIM"], width=14, anchor="w").pack(side="left")
            var = tk.IntVar(value=default)
            setattr(self, attr, var)
            tk.Spinbox(row, from_=1, to=8, textvariable=var, width=7,
                       font=T["SPINBOX_FONT"], bg=T["BG_INPUT"], fg=T["TEXT_MAIN"],
                       insertbackground=T["TEXT_MAIN"],
                       buttonbackground=T["BG_CARD"], relief="flat").pack(side="left")

        row_opt = tk.Frame(dim, bg=T["BG_PANEL"])
        row_opt.pack(fill="x", pady=2)
        tk.Label(row_opt, text="Optimise:", font=T["LABEL_FONT"],
                 bg=T["BG_PANEL"], fg=T["TEXT_DIM"], width=14, anchor="w").pack(side="left")
        self._opt_var = tk.StringVar(value="MAX")
        for val in ("MAX", "MIN"):
            tk.Radiobutton(row_opt, text=val, variable=self._opt_var, value=val,
                           bg=T["BG_PANEL"], fg=T["TEXT_MAIN"],
                           selectcolor=T["BG_INPUT"], activebackground=T["BG_PANEL"],
                           font=T["LABEL_FONT"]).pack(side="left", padx=4)

        tk.Button(dim, text="⟳  Generate grid", font=T["BTN_FONT"],
                  bg=T["ACCENT2"], fg=T["TEXT_MAIN"], activebackground="#9a7fd0",
                  relief="flat", padx=10, pady=4,
                  command=self._generate_grid).pack(pady=(6, 0))

        self._grid_frame = self._card(parent, "Coefficients & types")

        btn_frame = tk.Frame(parent, bg=T["BG_DARK"])
        btn_frame.pack(fill="x", pady=4)
        tk.Button(btn_frame, text="▶   SOLVE", font=("Segoe UI", 11, "bold"),
                  bg=T["ACCENT"], fg="white", activebackground="#ff6a6a",
                  relief="flat", padx=16, pady=8,
                  command=self._solve).pack(fill="x")

        self._generate_grid()

    # Output panel #

    def _build_output_panel(self, parent):
        nb = ttk.Notebook(parent, style="Dark.TNotebook")
        nb.pack(fill="both", expand=True)

        # Simplex Table tab
        tab_iter = tk.Frame(nb, bg=T["BG_DARK"])
        nb.add(tab_iter, text="  Simplex Table  ")

        nav = tk.Frame(tab_iter, bg=T["BG_DARK"], pady=4)
        nav.pack(fill="x", padx=8)
        for label, delta in [("◀◀  First", "first"), ("◀  Back", -1),
                              ("Next  ▶",   +1),      ("Last  ▶▶", "last")]:
            tk.Button(nav, text=label, font=T["BTN_FONT"],
                      bg=T["BG_CARD"], fg=T["TEXT_MAIN"],
                      relief="flat", padx=8, pady=3,
                      command=lambda d=delta: self._nav(d)).pack(side="left", padx=2)
        self._iter_label = tk.Label(nav, text="–", font=("Segoe UI", 9, "bold"),
                                    bg=T["BG_DARK"], fg=T["YELLOW"])
        self._iter_label.pack(side="left", padx=12)

        self._iter_text = self._make_scrolled_text(tab_iter)

        # Solution & Verification tab
        tab_sol = tk.Frame(nb, bg=T["BG_DARK"])
        nb.add(tab_sol, text="  Solution & Verification  ")
        self._sol_text = self._make_scrolled_text(tab_sol, pad=8)

        # Full Log tab
        tab_log = tk.Frame(nb, bg=T["BG_DARK"])
        nb.add(tab_log, text="  Full Log  ")
        self._log_text = self._make_scrolled_text(tab_log, font_key="MONO_FONT", pad=8)

    # Grid generation #

    def _generate_grid(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        n, m  = self._n_var.get(), self._m_var.get()
        col_w = 5
        self._c_entries = []
        self._A_entries = []
        self._b_entries = []
        self._ct_vars   = []
        self._vt_vars   = []

        # Header row
        hdr = tk.Frame(self._grid_frame, bg=T["BG_PANEL"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="", width=4, bg=T["BG_PANEL"]).pack(side="left")
        for j in range(n):
            tk.Label(hdr, text=f"x{j+1}", font=T["GRID_HDR_FONT"],
                     bg=T["BG_PANEL"], fg=T["ACCENT"],
                     width=col_w, anchor="center").pack(side="left", padx=1)
        tk.Label(hdr, text=" b",    font=T["GRID_HDR_FONT"], bg=T["BG_PANEL"],
                 fg=T["GREEN"],  width=col_w+1, anchor="center").pack(side="left", padx=1)
        tk.Label(hdr, text=" type", font=T["GRID_HDR_FONT"], bg=T["BG_PANEL"],
                 fg=T["YELLOW"], width=5,       anchor="center").pack(side="left")

        # Objective (c) row
        c_row = tk.Frame(self._grid_frame, bg=T["BG_PANEL"], pady=2)
        c_row.pack(fill="x")
        tk.Label(c_row, text="c:", font=T["GRID_LABEL_FONT"],
                 bg=T["BG_PANEL"], fg=T["YELLOW"], width=4, anchor="e").pack(side="left")
        for _ in range(n):
            e = self._make_entry(c_row, width=col_w)
            e.pack(side="left", padx=1)
            self._c_entries.append(e)

        tk.Frame(self._grid_frame, bg=T["ACCENT2"], height=1).pack(fill="x", pady=4)

        # Constraint rows
        for i in range(m):
            row = tk.Frame(self._grid_frame, bg=T["BG_PANEL"], pady=1)
            row.pack(fill="x")
            tk.Label(row, text=f"R{i+1}:", font=T["GRID_LABEL_FONT"],
                     bg=T["BG_PANEL"], fg=T["TEXT_DIM"], width=4, anchor="e").pack(side="left")

            a_row = []
            for _ in range(n):
                e = self._make_entry(row, width=col_w)
                e.pack(side="left", padx=1)
                a_row.append(e)
            self._A_entries.append(a_row)

            b_entry = self._make_entry(row, fg=T["GREEN"], width=col_w + 1)
            b_entry.pack(side="left", padx=1)
            self._b_entries.append(b_entry)

            ct_var, ct_menu = self._make_option_menu(row, ("<=", ">=", "="), "<=", T["YELLOW"])
            self._ct_vars.append(ct_var)
            ct_menu.pack(side="left", padx=2)

        tk.Frame(self._grid_frame, bg=T["ACCENT2"], height=1).pack(fill="x", pady=4)

        # Variable type row
        vt_frame = tk.Frame(self._grid_frame, bg=T["BG_PANEL"])
        vt_frame.pack(fill="x", pady=2)
        tk.Label(vt_frame, text="Var type:", font=T["TIPVAR_FONT"],
                 bg=T["BG_PANEL"], fg=T["TEXT_DIM"], width=8).pack(side="left")
        for _ in range(n):
            vt_var, vt_menu = self._make_option_menu(
                vt_frame, (">=0", "<=0", "R"), ">=0", T["ACCENT"],
                font_key="TIPVAR_FONT", width=4,
            )
            self._vt_vars.append(vt_var)
            vt_menu.pack(side="left", padx=1)

    # Read & solve #

    def _read_grid(self):
        n, m = self._n_var.get(), self._m_var.get()
        try:
            c = [Fraction(self._c_entries[j].get()) for j in range(n)]
            A = [[Fraction(self._A_entries[i][j].get()) for j in range(n)] for i in range(m)]
            b = [Fraction(self._b_entries[i].get()) for i in range(m)]
        except Exception as e:
            messagebox.showerror("Input error", f"Invalid value in grid:\n{e}")
            return None
        return (c, A, b,
                [self._ct_vars[i].get() for i in range(m)],
                [self._vt_vars[j].get() for j in range(n)],
                self._opt_var.get())

    def _solve(self):
        data = self._read_grid()
        if data is None:
            return
        c, A, b, ct, vt, op = data
        self._result   = solve(c, A, b, ct, vt, opt=op)
        self._iter_idx = 0
        self._refresh_iter_view()
        self._refresh_sol_view()
        self._refresh_log_view()

    # Navigation (all four buttons funnel here) #

    def _nav(self, delta):
        if not self._result:
            return
        total = len(self._result["iterations"]) - 1
        if   delta == "first": self._iter_idx = 0
        elif delta == "last":  self._iter_idx = total
        else:                  self._iter_idx = max(0, min(total, self._iter_idx + delta))
        self._refresh_iter_view()

    # View refresh #

    def _refresh_iter_view(self):
        if not self._result:
            return
        iters          = self._result["iterations"]
        k, snap, total = self._iter_idx, iters[self._iter_idx], len(iters) - 1
        status_label   = {"optimal"  : "✅  OPTIMAL found",
                          "unbounded": "❌  UNBOUNDED",
                          "continue" : f"➡️  Continue to I_{k+1}"}.get(snap["status"], "")
        self._iter_label.config(text=f"Iteration  I_{k}  /  I_{total}    {status_label}")
        self._set_text(self._iter_text, self._build_table_text(snap))

    def _refresh_sol_view(self):
        if not self._result:
            return
        r    = self._result
        text = (r["sol_text"]                  if r["status"] == "optimal"   else
                "  ❌  Problem is unbounded."  if r["status"] == "unbounded" else
                f"  Status: {r['status']}")
        self._set_text(self._sol_text, text)

    def _refresh_log_view(self):
        if not self._result:
            return
        parts = [self._build_table_text(s) + "\n" for s in self._result["iterations"]]
        if self._result["status"] == "optimal":
            parts.append(self._result["sol_text"])
        self._set_text(self._log_text, "\n".join(parts))

    def _set_text(self, widget, txt):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", txt)
        widget.config(state="disabled")

    # Tableau text builder #

    def _build_table_text(self, snap):
        var_names                    = snap["var_names"]
        basis, CB, XB, A, c         = snap["basis"], snap["CB"], snap["XB"], snap["A"], snap["c"]
        z_j, delta, z_obj           = snap["z_j"], snap["delta"], snap["z_obj"]
        pc, pr, k                   = snap["pivot_col"], snap["pivot_row"], snap["k"]
        n, m                        = len(var_names), len(basis)

        # Column widths
        W_MIN = 7
        col_widths = [
            max(W_MIN, len(f"a{j+1}") + 2, len(f"Δ{j+1}") + 2,
                max(len(format_fraction(v)) for v in
                    [A[i][j] for i in range(m)] + [c[j], z_j[j], delta[j]]) + 2)
            for j in range(n)
        ]
        W = 9   # fixed width for CB / Basis / Xb columns

        def cell(v, w):      return format_fraction(v).center(w)
        def cols(strs, ws):  return "  ".join(s.center(w) for s, w in zip(strs, ws))
        def pad_left():      return f"  {'':>{W}}  {'':>{W}}  {'':>{W}}  "

        total_w = 3 * W + 6 + sum(w + 2 for w in col_widths)
        sep     = "-" * total_w

        lines = [f"\n  ╔{'=' * total_w}╗",
                 f"  ║   ITERATION  I_{k}".ljust(total_w + 4) + "║"]
        if pc is not None:
            lines.append(
                (f"  ║   Pivot: row={var_names[basis[pr]]}"
                 f"  col={var_names[pc]}"
                 f"  P={format_fraction(A[pr][pc])}").ljust(total_w + 4) + "║"
            )
        lines += [
            f"  ╚{'=' * total_w}╝\n",
            f"  {'c_j →':>{W}}  {'':>{W}}  {'':>{W}}  " + cols([format_fraction(c[j])    for j in range(n)], col_widths),
            f"  {'':>{W}}  {'B':>{W}}  {'Xb':>{W}}  "   + cols([f"a{j+1}"                for j in range(n)], col_widths),
            f"  {'CB':>{W}}  {'Basis':>{W}}  {'Xb':>{W}}  " + cols(var_names,            col_widths),
            "  " + sep,
        ]

        # Data rows
        for i in range(m):
            prefix = "► " if i == pr else "  "
            row    = (f"{prefix}{format_fraction(CB[i]):>{W}}"
                      f"  {var_names[basis[i]]:>{W}}  {format_fraction(XB[i]):>{W}}  ")
            cells  = []
            for j in range(n):
                raw = format_fraction(A[i][j])
                if   i == pr and j == pc: val = f"[{raw}]"
                elif j == pc:             val = f"*{raw}*"
                else:                     val = raw
                cells.append(val.center(col_widths[j]))
            lines.append(row + "  ".join(cells))

        lines.append("  " + sep)

        # z_j and Δ_j rows — single loop builds both simultaneously
        dj_cells, dj_idx = [], []
        for j in range(n):
            raw = format_fraction(delta[j])
            dj_cells.append((f"►{raw}◄"    if j == pc else raw).center(col_widths[j]))
            dj_idx.append((f"►Δ{j+1}◄"    if j == pc else f"Δ{j+1}").center(col_widths[j]))

        lines += [
            f"  {'':>{W}}  {'z_j':>{W}}  {format_fraction(z_obj):>{W}}  " + cols([format_fraction(z_j[j]) for j in range(n)], col_widths),
            f"  {'':>{W}}  {'Δ_j':>{W}}  {'':>{W}}  " + "  ".join(dj_cells),
            f"  {'':>{W}}  {'':>{W}}  {'':>{W}}  "    + "  ".join(dj_idx),
            "",
        ]

        status = snap["status"]
        if status == "continue" and pc is not None:
            lines += [f"  ➡️ Entering: {var_names[pc]}   (Δ{pc+1} = {format_fraction(delta[pc])})",
                      f"  ➡️ Leaving:  {var_names[basis[pr]]}   (min ratio)",
                      f"  ➡️ Pivot P = {format_fraction(A[pr][pc])}"]
        elif status == "optimal":
            lines += ["  ✅  All Δ_j satisfy the optimality criterion.",
                      f"  ✅  z* = f* = {format_fraction(z_obj)}"]
        elif status == "unbounded":
            lines.append("  ❌  Problem is unbounded (no finite optimum).")

        return "\n".join(lines)


# Entry point #

def main():
    SimplexUI().mainloop()

if __name__ == "__main__":
    main()
