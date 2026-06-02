# Mixed pages (multiple environments combined)

When the image shows a section of a real document — paragraphs mixed with figures, equations, tables, code blocks, lists — combine the patterns from the other references.

## Strategy

1. Read the single-type references for each environment in the image.
2. Start from an `article` class template, not `standalone`.
3. Get the section order and high-level layout right first; tune each environment one at a time.
4. **Iterate per-region** — fix the table, recompile and look, then move to the next piece.

## Article-class base

```latex
\documentclass[11pt, a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{microtype}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{booktabs, multirow, array}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{listings}
\usepackage[most]{tcolorbox}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=blue!50!black, urlcolor=blue!50!black}

\begin{document}
\maketitle

\section{Method}
% ... body ...

\end{document}
```

## Order of operations when reproducing a complex page

1. **Skeleton**: title, sections, paragraph breaks. Compile.
2. **Placeholders**: drop each environment as `\textit{[table here]}` etc. Compile.
3. **Build one at a time**, in source order. Compile after each.
4. **Tune spacing, colors, fonts** once structure is solid.

This staged approach keeps the document compilable at every step. If something breaks, you know which piece caused it.

## Pitfalls (these caused silent failures in iteration 1)

- **Inventing content that isn't in the source image.** When the input image has a black region or low contrast, the subagent may default to "writing what a paper page usually contains" (Method, baseline table, hyperparameters) instead of faithfully reporting what's actually visible. Look at the source image carefully. If a region is unreadable, note the assumption in a `% comment` and call it out to the user — don't fabricate the missing content.
- **Floats moving** — `figure` and `table` float by design. If the layout demands exact placement, load `float` and use `[H]`.
- **`\centering` inside floats, not `center`** — `\begin{center}` adds unwanted vertical space.
- **`\label` must come after `\caption`** — otherwise references are off by one.
- **`\\` in normal text** — use blank lines for paragraph breaks; `\\` is for forced line breaks (e.g. inside a table cell or `makecell`).
- **Custom styled headings** (colored bar, different font) — `\usepackage{titlesec}` then `\titleformat{\section}{...}{...}{1em}{}`.
