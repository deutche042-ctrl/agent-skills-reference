# DOCX Code Block and Formula Insertion Guide

> **Core principle**: never write the ` ```python ` triple backticks or `$$`/`$` LaTeX markup directly into a docx paragraph—they are just plain text and will not be rendered.

All code-block and formula insertion is done through the three functions provided by **`scripts/code_formula.py`**:

| Function | Purpose |
|---|---|
| `add_code_block(doc, code, lang="")` | Gray-background code block (Courier New, with line numbers, no border) |
| `add_inline_formula(para, text)` | Inline formula within a paragraph (Times New Roman italic, coordinated with the body text) |
| `add_latex_formula(doc, latex, label="")` | Standalone displayed formula (LaTeX → native Word OMML, supporting fractions/superscripts-subscripts/radicals) |

**How to import:**
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../scripts"))
from code_formula import add_code_block, add_inline_formula, add_latex_formula
```

---

## 1. Code Block `add_code_block`

### Effect

```
  Code block  python
  1   from PIL import Image
  2   import numpy as np
  3
  4   # load the image and convert to grayscale
  5   img = Image.open("input.jpg").convert('L')
```

- A uniform light-gray background (`#F2F2F2`), no border of any kind, no dashed lines in either Word or WPS
- Label line: `Code block  {lang}`, 9pt, gray text
- Code lines: Courier New 9pt, right-aligned line numbers (gray), dark code content
- Implementation: paragraph `w:shd` shading, each line its own paragraph, zero spacing, visually joined into a single block

### Function Signature

```python
add_code_block(doc: Document, code: str, lang: str = "") -> None
```

| Parameter | Description |
|---|---|
| `doc` | python-docx `Document` object |
| `code` | Code string, multi-line, indentation preserved; leading/trailing blank lines are removed automatically |
| `lang` | Language annotation, affects the label display only, e.g. `"python"` / `"js"` / `"sql"` |

### Usage Example

```python
from docx import Document
from code_formula import add_code_block

doc = Document()
doc.add_paragraph("Below is a Python implementation of a Gaussian filter:")

add_code_block(doc, """\
import numpy as np

def gaussian_kernel(k: int, sigma: float) -> np.ndarray:
    ax = np.arange(1, k + 1)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-((xx - k)**2 + (yy - k)**2) / (2 * sigma**2))
    return kernel / kernel.sum()
""", lang="python")

doc.save("output.docx")
```

### Supported Comment Languages

The `lang` parameter affects the code label but not the code rendering (comment color has been unified to match the code):

| `lang` value | Example languages |
|---|---|
| `"python"` / `"shell"` / `"bash"` / `"r"` | Python, Shell scripts |
| `"js"` / `"javascript"` / `"ts"` / `"java"` / `"c"` / `"cpp"` | Front-end/back-end languages |
| `"sql"` / `"lua"` | Database/scripting languages |
| `"matlab"` | MATLAB |
| `""` (default) | No language annotation |

---

## 2. Inline Formula `add_inline_formula`

### Effect

Mixed with characters within a body paragraph: the standard deviation is *σ*, where *k* is the dimension of the convolution kernel.

- Times New Roman italic, **no font size set** (inherits the paragraph size, matching the height of surrounding text)
- Sets only the ASCII/hAnsi font, does not interfere with the East Asian font of Chinese characters
- No noticeable formatting break from the body text

### Function Signature

```python
add_inline_formula(para, text: str) -> run
```

| Parameter | Description |
|---|---|
| `para` | An existing python-docx `Paragraph` object (content is appended to it) |
| `text` | A Unicode math-symbol string, e.g. `"σ²"` / `"M ∈ ℝ^{m×n}"` |

### Usage Example

```python
# build a paragraph containing an inline formula
p = doc.add_paragraph("The standard deviation of the Gaussian filter is ")
add_inline_formula(p, "σ")
p.add_run(", the convolution kernel dimension is ")
add_inline_formula(p, "k")
p.add_run(", the discretization formula is shown in Equation (4-2).")
```

Rendered result: The standard deviation of the Gaussian filter is *σ*, the convolution kernel dimension is *k*, the discretization formula is shown in Equation (4-2).

### Quick Reference for Common Unicode Math Symbols

| Meaning | Symbol | Meaning | Symbol |
|---|---|---|---|
| Summation Σ | `Σ` | Standard deviation σ | `σ` |
| Matrix transpose Vᵀ | `Vᵀ` | Superscript ² ³ | `²` `³` |
| Subscript ₁ ₂ ₙ | `₁` `₂` `ₙ` | Infinity ∞ | `∞` |
| Multiply × | `×` | Divide ÷ | `÷` |
| ≤ ≥ ≠ ≈ | `≤` `≥` `≠` `≈` | Partial derivative ∂ | `∂` |
| α β γ δ | `α` `β` `γ` `δ` | π ε λ μ | `π` `ε` `λ` `μ` |
| ± | `±` | Norm ‖·‖ | `‖` `‖` |
| Element of ∈ | `∈` | Real numbers ℝ | `ℝ` |
| Gradient ∇ | `∇` | Integral ∫ | `∫` |

---

## 3. Standalone Displayed Formula `add_latex_formula`

### Effect

Displayed centered, a native Word OMML formula object (editable in Word's equation editor):

$$H[i,j] = \frac{1}{2\pi\sigma^2} e^{-\frac{(i-k-1)^2+(j-k-1)^2}{2\sigma^2}} \quad (4\text{-}2)$$

- Calls `latex2mathml` to convert LaTeX to MathML, then converts it to OMML XML and injects it into the Word paragraph
- Supports: fractions `\frac`, superscripts/subscripts `^` `_`, radicals `\sqrt`, summation/integral symbols, multi-level nesting
- The number `label` is appended in small gray text to the right of the formula

### Function Signature

```python
add_latex_formula(doc: Document, latex: str, label: str = "") -> None
```

| Parameter | Description |
|---|---|
| `doc` | python-docx `Document` object |
| `latex` | The LaTeX formula string (without the `$$` wrappers), e.g. `r"\frac{a}{b}"` |
| `label` | The formula number, e.g. `"(4-2)"`; leave empty to show no number |

### Usage Example

```python
# Gaussian filter kernel
add_latex_formula(
    doc,
    r"H[i,j] = \frac{1}{2\pi\sigma^2} e^{-\frac{(i-k-1)^2+(j-k-1)^2}{2\sigma^2}}",
    label="(4-2)",
)

# SVD decomposition
add_latex_formula(doc, r"M = U \Sigma V^T", label="(1)")

# quadratic formula
add_latex_formula(doc, r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", label="(2)")

# Euler's identity (no number)
add_latex_formula(doc, r"e^{i\pi} + 1 = 0")
```

### Quick Reference for Common LaTeX Syntax

| Effect | LaTeX | Effect | LaTeX |
|---|---|---|---|
| Fraction | `\frac{numerator}{denominator}` | Superscript | `x^{2}` or `x^2` |
| Subscript | `x_{i}` or `x_i` | Super- and subscript | `x_i^2` |
| Radical | `\sqrt{x}` | n-th root | `\sqrt[n]{x}` |
| Summation | `\sum_{i=1}^{n}` | Integral | `\int_a^b` |
| Greek letters | `\alpha` `\beta` `\sigma` `\pi` | Special symbols | `\pm` `\times` `\leq` |
| Norm | `\| x \|` | Upright text | `\text{MSE}` |
| Ellipsis | `\ldots` `\cdots` | Spacing | `\,` `\;` `\quad` |
| Auto-sizing brackets | `\left( \right)` | Matrix | `\begin{pmatrix}...\end{pmatrix}` |

### Supported MathML Structures

Through the LaTeX → MathML → OMML conversion chain, the following MathML elements are all supported:

| MathML | OMML | Description |
|---|---|---|
| `<mfrac>` | `<m:f>` | Fraction |
| `<msup>` | `<m:sSup>` | Superscript |
| `<msub>` | `<m:sSub>` | Subscript |
| `<msubsup>` | `<m:sSubSup>` | Super- and subscript |
| `<msqrt>` | `<m:rad>` | Square root |
| `<mroot>` | `<m:rad>` | n-th root |
| `<mi>` / `<mn>` / `<mo>` | `<m:r>` | Variable/number/operator |

---

## 4. Complete Usage Template

Combining the three functions to simulate a paper paragraph:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "path/to/scripts"))

from docx import Document
from code_formula import add_code_block, add_inline_formula, add_latex_formula

doc = Document()

# 1. body paragraph containing an inline formula
p = doc.add_paragraph("Let the convolution kernel size be ")
add_inline_formula(p, "k×k")
p.add_run(", the standard deviation ")
add_inline_formula(p, "σ")
p.add_run(", the Gaussian filter discretization formula is as follows:")

# 2. standalone displayed formula (numbered)
add_latex_formula(
    doc,
    r"H[i,j] = \frac{1}{2\pi\sigma^2} e^{-\frac{(i-k-1)^2+(j-k-1)^2}{2\sigma^2}}",
    label="(4-2)",
)

# 3. explanatory paragraph after the formula
p2 = doc.add_paragraph("where ")
add_inline_formula(p2, "σ")
p2.add_run(" is the variance and ")
add_inline_formula(p2, "k")
p2.add_run(" is the dimension of the convolution kernel matrix. The Python implementation is as follows:")

# 4. code block
add_code_block(doc, """\
def gaussian_kernel(k: int, sigma: float) -> np.ndarray:
    ax = np.arange(1, k + 1)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-((xx - k)**2 + (yy - k)**2) / (2 * sigma**2))
    return kernel / kernel.sum()
""", lang="python")

doc.save("output.docx")
```

---

## 5. Installing Dependencies

```bash
uv add latex2mathml   # or pip install latex2mathml
# python-docx and lxml are already installed in the project
```

`code_formula.py` dependencies: `python-docx`, `lxml`, `latex2mathml` (only `add_latex_formula` needs it).
