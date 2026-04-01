# Simplex-Primal-Method-UI
An UI implementation of **Primal Simplex Method**, usind [simplex-primal](https://github.com/cosminelulul/simplex-primal) library
Enter your LP problem, hit **SOLVE**, and step through every tableau iteration with full pivot annotations and a final solution verification.

---

## Features
- Live iteration navigator (step forward/backward through the simplex table)
- **Simplex Table** tab — annotated tableau with pivot row/column highlighted
- **Solution & Verification** tab — optimal values + `S·X_B = b` check
- **Full Log** tab — entire computation in one scrollable view
- Supports MAX and MIN, all constraint types (`<=`, `>=`, `=`), and variable types (`>=0`, `<=0`, unrestricted `R`)

---

## Requirements

- Python 3.9+
- `simplex-primal` (link above fo the library and how to install it)

---

## Installation

```bash
# 1. Install the solver library
pip install git+https://github.com/cosminelulul/simplex-primal.git

# 2. Clone this repo
git clone https://github.com/cosminelulul/simplex-primal-ui.git
cd simplex-primal-ui

# 3. Run the app
python app.py
```

---

## Usage

1. Set **n** (number of variables) and **m** (number of constraints).
2. Choose **MAX** or **MIN**.
3. Click **⟳ Generate grid** to build the coefficient table.
4. Fill in the `c` (objective) row, the `A` matrix, and the `b` vector.
5. Set constraint types (`<=`, `>=`, `=`) and variable types (`>=0`, `<=0`, `R`).
6. Click **▶ SOLVE**.

Use the **◀◀ / ◀ / ▶ / ▶▶** buttons to step through iterations.

---

## Notes:

This UI is intentionally a **thin shell**.  
All LP logic lives in `simplex-primal`

```python
from simplex_primal import solve          # solver
from simplex_primal.core import format_fraction, format_fraction_plain
```

`app.py` is responsible only for:
- Rendering the input grid
- Calling `solve(...)`
- Displaying the returned iteration snapshots and solution text

---

## License

[MIT License](LICENSE)
