# Flowcharts and node-and-arrow diagrams

For anything that's "boxes and arrows but not a tree", reach for TikZ with `positioning`, `arrows.meta`, and `shapes.geometric`.

## Canonical pattern (flowchart with decision diamond)

```latex
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{positioning, arrows.meta, shapes.geometric}

\begin{document}
\begin{tikzpicture}[
  node distance=12mm and 12mm,
  every node/.style={font=\small},
  block/.style={
    draw, rounded corners=2pt,
    minimum width=2.5cm, minimum height=8mm,
    align=center,
  },
  decision/.style={
    draw, diamond, aspect=2,
    minimum width=2cm, align=center,
  },
  arr/.style={-Stealth, thick},
]
  \node[block] (start) {Start};
  \node[block, below=of start] (read) {Read input};
  \node[decision, below=of read] (check) {Valid?};
  \node[block, below=of check] (done) {Done};
  \node[block, right=of check] (err) {Error};

  \draw[arr] (start) -- (read);
  \draw[arr] (read) -- (check);
  \draw[arr] (check) -- node[left] {yes} (done);
  \draw[arr] (check) -- node[above] {no} (err);
\end{tikzpicture}
\end{document}
```

## Building blocks

- **Relative placement** (requires `\usetikzlibrary{positioning}`):
  `right=of A`, `below=8mm of A`, `above right=of A`. Set the global gap with `node distance=20mm and 10mm` (vertical then horizontal).
- **Arrows**: `-Stealth` (filled, default), `-Latex` (classic), `Stealth-Stealth` (double), `-Stealth, dashed`. Label with `-- node[midway, above] {label}` or `-- node[pos=0.3, right] {x}`.
- **Right-angle routing**: `(A) |- (B)` (vertical first, then horizontal), `(A) -| (B)` (horizontal first, then vertical). Add `rounded corners=4pt` to soften the bend.
- **Anchors**: every node has `north/south/east/west/north east/...` anchors. `(A.south) -- (B.north)` attaches to a specific side.
- **Node shapes**: `diamond` (decision), `ellipse`, `trapezium`, `cylinder` — most need `\usetikzlibrary{shapes.geometric}`.
- **Colors**: `\definecolor{accent}{RGB}{60, 120, 200}`, then `fill=accent!15, draw=accent`. The `!N` syntax lightens (`blue!20` = 20% blue tinted with white) or darkens (`blue!50!black`).

## Pitfalls

- **Forgetting `\usetikzlibrary{positioning}`** — `right=of A` silently behaves wrong without it.
- **Quote marks in node labels** — TikZ uses `"name"` syntax in some contexts. Use `\node[block] (a) {Label};` and avoid raw `"` inside labels, or load `quotes` library.
- **Underscores in node names** — node names should not contain `_`; use letters and numbers.
- **Crossing edges** — TikZ doesn't auto-route. For visible "jump" over a crossing, paint a small white circle: `\draw[white, line width=4pt] (cross-point);` then redraw the cross-edge on top.

## When TikZ is the wrong tool

For trees, use `forest` (see `tree.md`). For many similar boxes in a regular grid, use TikZ `matrix`. For commutative diagrams, use `tikz-cd`.
