# Math

`amsmath` is the default. Load it always:

```latex
\usepackage{amsmath, amssymb}
\usepackage{bm}      % \bm{x} for bold math (or use \boldsymbol)
```

## The four patterns that cover ~90% of paper figures

```latex
% 1. Aligned multi-line equation (numbered)
\begin{align}
  f(x) &= (x+1)^2 \\
       &= x^2 + 2x + 1
\end{align}

% 2. Numbered single equation
\begin{equation}
  \mathcal{L}(\bm{\theta}) = -\frac{1}{N} \sum_{i=1}^{N} \log p_{\bm{\theta}}(y_i \mid \bm{x}_i)
\end{equation}

% 3. Piecewise (cases) — \text{} keeps "if" in upright text mode
\begin{equation}
  \sigma(x) = \begin{cases}
    \dfrac{1}{1 + e^{-x}} & \text{if } x \geq 0, \\
    \dfrac{e^{x}}{1 + e^{x}} & \text{otherwise.}
  \end{cases}
\end{equation}

% 4. Matrix (pmatrix has parens; bmatrix has brackets; matrix has none)
\begin{equation}
  \nabla_{\bm{\theta}} \mathcal{L} = \begin{pmatrix}
    \partial \mathcal{L} / \partial \theta_1 \\
    \vdots \\
    \partial \mathcal{L} / \partial \theta_d
  \end{pmatrix} \in \mathbb{R}^{d \times 1}
\end{equation}
```

`align*` (with the asterisk) is the unnumbered version. `aligned` (no asterisk) is the same thing but lives inside another display environment.

## Symbol cheatsheet (the ones you actually need)

| Symbol | Code | | Symbol | Code |
|---|---|---|---|---|
| ∑ ∏ ∫ | `\sum \prod \int` | | → ⇒ | `\to \Rightarrow` |
| ∂ ∇ | `\partial \nabla` | | ≤ ≥ ≈ ≠ | `\leq \geq \approx \neq` |
| ℝ ℕ ℤ ℂ | `\mathbb{R}` etc. | | ∈ ⊂ ⊆ | `\in \subset \subseteq` |
| ∀ ∃ | `\forall \exists` | | · × | `\cdot \times` |
| Greek | `\alpha`...`\omega` (lowercase); `\Alpha`-style names don't exist for capital Greek that look like Latin | | **bold** | `\bm{x}` (load `bm`) |

## Pitfalls

- **`align` inside `equation`** is illegal. Use `aligned` inside `equation`, or `align` standalone.
- **Forgetting `\text{}`** around English words inside math — `if`, `otherwise`, `such that` get italicized as variable names.
- **`*` for multiplication** — use `\cdot` or `\times`. Bare `*` typesets as a superscript-ish character.
- **`\frac` chains getting tiny** — use `\dfrac` to force display-size fractions.
- **Subscripts/superscripts with limits** — inside `equation`/`align`, `\sum_{i=1}^{n}` automatically uses display style. Inline, wrap with `$\displaystyle ...$` to force it.
- **Custom function names** — `\operatorname{softmax}(x)`, not `softmax(x)` (the latter italicizes every letter).
- **Capital Greek that look like Latin** (Α Β Ε Η Ι Κ Μ Ν Ο Ρ Τ Χ Υ Ζ) — no macro exists; use the Latin letter.

## Equation numbering controls

- `\tag{...}` overrides the auto number: `\begin{equation} ... \tag{$\star$} \end{equation}`
- `\nonumber` (or `\notag`) suppresses one line's number inside `align`.
- `\label{eq:foo}` + `\eqref{eq:foo}` for cross-references.
