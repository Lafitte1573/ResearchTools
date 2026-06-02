# Tree diagrams

Use the `forest` package. It is built on TikZ but understands tree structures natively, which makes it dramatically easier than raw TikZ for hierarchical layouts.

## Canonical pattern (paper taxonomy, left-to-right, elbow connectors)

```latex
\documentclass[border=10pt]{standalone}
\usepackage{forest}
\usepackage{xcolor}

\definecolor{leafborder}{RGB}{120, 165, 210}
\definecolor{leaffill}{RGB}{220, 233, 245}

\tikzset{
  rootbox/.style={draw, rounded corners=3pt, text width=1.7cm, align=center, font=\footnotesize, inner sep=4pt},
  l1box/.style  ={draw, rounded corners=3pt, text width=3.4cm, align=center, font=\footnotesize, inner sep=5pt},
  catbox/.style ={draw, rounded corners=3pt, text width=3.4cm, align=center, font=\footnotesize, inner sep=5pt},
  leafbox/.style={draw=leafborder, fill=leaffill, rounded corners=3pt,
                  text width=4.8cm, align=left, font=\scriptsize, inner sep=4pt},
}

\begin{document}
\begin{forest}
  for tree={
    grow'=east,                       % left-to-right; the apostrophe keeps sibling order
    parent anchor=east, child anchor=west,
    l sep=14pt, s sep=7pt,            % horizontal / vertical spacing
    edge={-, thin, draw=gray},
    edge path={\noexpand\path[\forestoption{edge}, rounded corners=4pt]
                 (!u.parent anchor) -- +(8pt,0) |- (.child anchor);},  % elbow connector
  },
  where level=0{rootbox}{},
  where level=1{l1box}{},
  where level=2{catbox}{},
  where n children=0{leafbox}{},      % applied last → any leaf gets this style
  [Root
    [Branch A [{Citation leaf [8]} {Citation leaf [9]}]]
    [Branch B [{Citation leaf [10]}]]
  ]
\end{forest}
\end{document}
```

## Key pitfalls (these caused silent failures in iterations 1 and 2)

- **Invisible labels in the rendered PDF.** The most common silent failure. If the rendered PNG shows empty boxes, the cause is almost always one of: (a) `align=` not set alongside `text width=` — without `align`, the node grows wide instead of wrapping and the text gets clipped; (b) a `\\` immediately followed by `[`, which LaTeX reads as the optional arg of `\\`; (c) the label got swallowed by a forest parser error; (d) you shrank the `text width` from the canonical value below and the text overflowed the box. After every compile+render, **look at the PNG** and confirm the labels are actually visible — don't trust the .tex alone.
- **Brackets `[` `]` inside labels break the forest parser** — forest uses `[` `]` to delimit children. The **default fix is to wrap the whole label in `{}`**: `[{Zhang et al. [8].}]`. The `{}` is the outer label, the inner `[8]` is just text. Do this for *every* label that contains brackets — citation numbers, equation refs, etc. Reach for `\lbrack` `\rbrack` only when you also need a `\\` line break *right before* the number (e.g. `LLMs\\\lbrack70--73\rbrack` to put `[70-73]` on its own line under "LLMs"). Using `\lbrack\rbrack` everywhere instead of `{}` is a common shortcut that often *also* works — but if the leaf text then disappears, the brackets were the cause.
- **Keep the canonical leafbox dimensions.** The `leafbox` style above uses `text width=4.8cm, align=center` (or `align=left`), `font=\scriptsize`. If you shrink `text width` to 3.6cm or change the alignment, multi-author citation strings like "Bai et al. [26], Wan et al. [27], Miao et al. [28, 28], Xu et al. [29]..." will get clipped and the leaf renders as an empty box. **Copy the `leafbox` style as-is** unless the source is genuinely different.
- **`grow=east` (no apostrophe) reverses sibling order.** Always `grow'=east`.
- **Forgetting `align=left/right/center`** — node grows to fit one line and overflows.
- **`where n children=0{...}`** must be the LAST `where` clause so it can override any level-based style for terminal nodes.

## What the inner syntax means

- `[{...}]` — child node whose label is `{...}` (the braces tell forest "this whole thing is the label"). The `[...]` outside is the child syntax; the `{...}` inside is the label. **Both layers are usually required when the label contains brackets.**
- `[A [B] [C]]` — A has two children B and C.
- `\\` inside a label is a manual line break.
- The `for tree={...}` block applies to every node; override per node by writing a style block right after the node.

## Paper-taxonomy pattern (the source from `evals/inputs/tree.jpg`)

For a tree like the LLM survey — one root, four `l1` branches, a `catbox` per subcategory, and a single `leafbox` per subcategory containing the citation string — use this structure. **Each label is wrapped in `{}`** so the citation brackets inside don't get parsed as forest children:

```latex
[\textbf{LLMs} [70--73]                        % root (use \lbrack\rbrack for the [70-73] on a 2nd line)
  [{Fundamental Problems}                       % l1 branch — outer {} wraps the label
    [{Supervised Fine-tuning} [{Zhang et al. [8].}]]
    [{Alignment} [{Shen et al. [9], Wang et al. [10], Liu et al. [11].}]]
    ...]
  [{Evaluation} [{Chang et al. [34], Guo et al. [35].}]]
  ...]
```

Two layers of `{}` per citation node: one for the category label, one for the leaf. Both are required.

## When forest is the wrong tool

If the diagram isn't strictly hierarchical (back edges, cross links, nodes that need exact pixel placement), use TikZ directly with `positioning` (see `flowchart.md`).
