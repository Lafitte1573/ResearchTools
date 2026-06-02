# Code blocks, theorems, and box environments

## Code block — `listings` (works out of the box, no shell escape needed)

```latex
\usepackage{listings}
\usepackage{xcolor}

\definecolor{codebg}{RGB}{248, 248, 248}
\definecolor{codeborder}{RGB}{210, 210, 210}
\definecolor{keyword}{RGB}{0, 90, 180}

\lstdefinestyle{py}{
  language=Python,
  basicstyle=\ttfamily\small,
  keywordstyle=\color{keyword}\bfseries,
  commentstyle=\color{gray}\itshape,
  numbers=left, numberstyle=\tiny\color{gray}, numbersep=8pt,
  frame=single, rulecolor=\color{codeborder},
  backgroundcolor=\color{codebg},
  showstringspaces=false, breaklines=true,
  framesep=4pt, xleftmargin=18pt, framexleftmargin=4pt,
}

\begin{lstlisting}[style=py]
def train_step(model, batch):
    # forward pass
    logits = model(batch.x)
    loss = cross_entropy(logits, batch.y)
\end{lstlisting}
```

`minted` is prettier (Pygments-powered) but needs `pdflatex --shell-escape`. If shell escape isn't available, stay with `listings`. **In the context of running subagents, listings is the safe default** — they may not have shell-escape permission.

## Theorem-like environments — `amsthm`

```latex
\usepackage{amsthm}

\theoremstyle{definition}
\newtheorem{definition}{Definition}[section]
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]

\begin{definition}[Cross-Entropy Loss]
  For logits $z \in \mathbb{R}^C$, the loss is
  $-\sum_c \mathbf{1}[y=c] \log \operatorname{softmax}(z)_c$.
\end{definition}
```

The `proof` environment is also from `amsthm` and ends with a tombstone (■) by default.

## Callout boxes — `tcolorbox` (most flexible) or `mdframed` (lighter)

```latex
\usepackage[most]{tcolorbox}

\newtcolorbox{notebox}[1][]{
  colback=blue!5, colframe=blue!50!black,
  boxrule=0.5pt, arc=2pt,
  left=8pt, right=8pt, top=6pt, bottom=6pt,
  #1
}

\begin{notebox}[title=Note]
  All experiments run on a single A100 GPU.
\end{notebox}
```

For a simpler left-bar-only style, `mdframed` is enough:
```latex
\usepackage[framemethod=tikz]{mdframed}
\begin{mdframed}[
  topline=false, bottomline=false, rightline=false,
  linewidth=3pt, linecolor=gray!60,
  innerleftmargin=10pt,
]
  Pull-quote text.
\end{mdframed}
```

## Pitfalls

- **Spelling/typo risk in code bodies** — the subagent has to OCR the code from the image. Slow down and re-read the source code character by character. A common miss was `cross_entrypy` for `cross_entropy` (silent typo from fuzzy OCR).
- **Tabs inside `lstlisting`** — set `tabsize=4, showtabs=false` to avoid weird indentation.
- **Special characters** — `listings` handles them naturally; `minted` needs nothing special.
- **`\verb|...|` cannot be used inside another macro's argument** — use `\lstinline|...|` instead.
