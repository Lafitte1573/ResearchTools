# Tables

Default `tabular` is fine for grids; for publication quality use **booktabs** rules and **multirow** + **multicolumn** for merged cells. Vertical lines (`|l|c|c|`) look amateurish — don't use them.

## Canonical pattern (two-tier merged-cell header, colored last row)

```latex
\documentclass[border=10pt]{standalone}
\usepackage{booktabs}        % \toprule, \midrule, \bottomrule
\usepackage{multirow}        % vertical merge
\usepackage{colortbl, xcolor}  % \rowcolor, \cellcolor
\usepackage{makecell}        % \makecell for line breaks in narrow cells

\definecolor{headerblue}{RGB}{214, 230, 247}
\definecolor{oursgreen}{RGB}{217, 234, 211}

\begin{document}
\begin{tabular}{l c c c c}
  \toprule                                                       % ALWAYS use \toprule
  \rowcolor{headerblue}
  \multirow{2}{*}{\textbf{Model}}
    & \multicolumn{2}{c}{\textbf{In-domain}}
    & \multicolumn{2}{c}{\textbf{Out-of-domain}} \\
  \cmidrule(lr){2-3} \cmidrule(lr){4-5}                          % partial rules under sub-headers
  \rowcolor{headerblue}
    & \textbf{EM} & \textbf{F1} & \textbf{EM} & \textbf{F1} \\
  \midrule
  \multirow{2}{*}{BERT-base} & 0.81 & 0.79 & 0.67 & 0.65 \\
                            & 0.82 & 0.80 & 0.68 & 0.66 \\
  T5 & 0.83 & 0.81 & 0.70 & 0.68 \\
  \rowcolor{oursgreen}                                            % highlight last row
  \textbf{Ours} & \textbf{0.842} & \textbf{0.917} & \textbf{0.728} & \textbf{0.711} \\
  \bottomrule
\end{tabular}
\end{document}
```

## Pitfalls (silent failures from iteration 1)

- **Forgetting `\toprule`.** The booktabs trio is `\toprule` + `\midrule` + `\bottomrule`. Use all three. Skipping `\toprule` makes the table look broken even though it compiles.
- **`\multirow` cell visually clipped by the sub-header row.** When you merge a leftmost cell across two header rows, the second header row sometimes overlaps the bottom of the `\multirow` content. Fix by adding `\\[2ex]` (extra vertical space) after the first header row, or by using `\multirow{2}{*}[0.5ex]{...}` to push the content down.
- **Forgetting `\\` at end of last row** — leaves a small gap before `\bottomrule`.
- **Numeric alignment** — for decimal-point alignment use `siunitx`'s `S` column type.
- **Long header text colliding with column width** — wrap the header in `\multicolumn{1}{p{3cm}}{Long header}`.
- **`\hline` between every row** — use `booktabs` rules only. Vertical lines + `\hline` everywhere is the "homework" look.

## Quick lookup

| Want | Use |
|---|---|
| Horizontal merge (header spans 2+ columns) | `\multicolumn{2}{c}{label}` |
| Vertical merge (label spans 2+ rows) | `\multirow{2}{*}{label}` (empty `&` in the merged-into rows) |
| Partial horizontal rule under columns 2–3 | `\cmidrule(lr){2-3}` |
| Line break in a cell | `\makecell{Line 1\\Line 2}` (load `makecell`) |
| Shaded row | `\rowcolor{...}` at the start of the row |
| Shaded cell | `\cellcolor{...}` |
| Decimal-aligned numbers | `S` column type from `siunitx` |
