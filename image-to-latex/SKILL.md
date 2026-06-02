---
name: image-to-latex
description: 'When a user shows you an image and wants LaTeX code for it, use this skill. Triggers on requests like "recreate this in LaTeX", "reproduce this figure", "turn this screenshot into LaTeX", "give me the LaTeX source for this image", "复现", "用LaTeX写出来", "重画", "重新排版". Works on any image type — equations/derivations, tables, tree diagrams, code blocks, flowcharts, theorem boxes, mixed page layouts. The skill writes LaTeX, compiles with pdflatex, renders to PNG, visually compares against the original, and refines until it matches. Not for: writing LaTeX from scratch without an image, extracting text from PDFs, or compiling existing .tex files.'
---

# Image-to-LaTeX

Turn any image into compilable LaTeX. The skill follows a tight visual feedback loop: **draft → compile → render to PNG → look at the result next to the original → refine.** Iterate until the rendered output is visually close to the input. Most documents converge in 2–4 iterations.

## Why a feedback loop matters

LaTeX is unforgiving — tiny differences in `text width`, `align`, escape characters, or package choice produce wildly different output. Trying to predict the final rendering by reading the source is unreliable. **The fastest path to a good result is to actually compile, look at the rendered image, and iterate.** You can see what is wrong much more clearly than you can predict it. Compilation is cheap (under a second for most documents). Use it freely.

## Workflow

1. **Look at the image carefully.** Read it with the `Read` tool. Note exactly what content is visible — if a region is blank, black, or low contrast, do not invent content for it. Identify the content type(s):
   - Tree / hierarchy / mind map → `references/tree.md`
   - Table (merged cells, colored headers) → `references/table.md`
   - Math equation / derivation / matrix → `references/math.md`
   - Code block / quote / theorem / box → `references/code-and-quote.md`
   - Flowchart / architecture diagram → `references/flowchart.md`
   - Page with several of the above → `references/mixed-page.md` plus the relevant single-type references

2. **Read the matching reference file(s).** Each reference contains one canonical example and the few pitfalls that actually break things. Do not skip this.

3. **Pick a starting template from `assets/`.** Copy it into a working directory.

4. **Draft the LaTeX.** Get structure right first (right nodes, right cells, right symbols). Refinement of spacing/colors comes later.

5. **Compile and render.** Run `scripts/compile_and_preview.sh <file.tex>`. It runs `pdflatex` (nonstop mode), converts the PDF to PNG via `sips`, and prints the PNG path. On failure it surfaces the first `!` error from the .log.

6. **Visually verify.** Open the rendered PNG with `Read` — every compile. **Do not trust assertions about the .tex file alone.** The .tex can look correct while the rendered PDF has invisible labels, missing text, or broken layout. Specifically check:
   - **All labels are visible** in the rendered PNG (the most common silent failure — invisible labels from missing `align=`, `\\[` collision, or a forest parser error)
   - **All textual content from the original is present** in the rendering (no missing rows, nodes, symbols)
   - **Structural relationships are correct** (branches connect to the right parents, table cells span the right rows/columns, equation alignment points match)
   - **Visual layout matches** (colors, box styles, alignment, density)

7. **Refine.** Edit the .tex, recompile, re-render, re-verify. Stop when the rendered image is structurally and visually close to the original — pixel-perfect is not the goal, faithful reproduction is. **If two iterations in a row produce only cosmetic changes, you are done** — do not chase perfection.

## What "done" looks like

- All textual content from the original appears in the rendering
- Structural relationships are correct
- A human glancing at the two side-by-side would recognize them as the same figure
- The output compiles cleanly with no errors (warnings are fine)

## What to give the user at the end

- The final `.tex` file path
- The rendered PNG so they can see the result
- The compile command (`pdflatex <file>`)
- A brief note of any packages they need

If iterating with the user, present the rendered PNG and ask "good enough or want me to fix X?" — let them steer the final polish.

## Cross-cutting tips

- **Use `\documentclass[border=10pt]{standalone}`** for any single figure/table/equation. For full pages, use `\documentclass[11pt, a4paper]{article}`.
- **Brackets `[...]` inside `forest`/`tikz` node labels** break the parser. Wrap the whole label in `{}` if it contains brackets, or use `\lbrack`/`\rbrack` near `\\` line breaks.
- **`align=left/center/right` plus `text width=Xcm`** is what enables word wrapping inside TikZ/forest nodes. Without `align=`, the node grows to fit content on one line.
- **Underscores in text mode** need `\_`. The `listings` package handles them inside code blocks.
- **For Chinese or non-Latin text**, use `xelatex` (with `ctex` or `fontspec`) — the compile script auto-detects this.

## When the image is ambiguous

If you cannot tell exactly what is in a region (small text, low resolution, blank/black area):

1. **Do not invent content.** Inventing is worse than leaving space — it produces a "looks plausible" reproduction that is wrong on inspection.
2. Note the assumption in a brief `% comment` in the .tex.
3. Show the user the rendered output and explicitly call out the gap: "I read this row as X — is that right?"

## References at a glance

| File | When to read |
|---|---|
| `references/tree.md` | Tree, hierarchy, taxonomy, mind map |
| `references/table.md` | Tables with merged cells, multi-row headers, color |
| `references/math.md` | Equations, derivations, alignments, matrices, cases |
| `references/code-and-quote.md` | Code snippets, quote blocks, theorem/proof/definition boxes |
| `references/flowchart.md` | Flowcharts, architecture diagrams, node-and-arrow graphs |
| `references/mixed-page.md` | Pages with several environments combined |
