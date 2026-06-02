---
name: image-to-chart
description: 'When a user shows you a chart image (matplotlib / seaborn / research-paper figure) and wants Python code to reproduce it, use this skill. Triggers on requests like "recreate this chart in Python", "reproduce this figure with matplotlib", "用 Python 复现这张图", "写代码画出这个图", "给我 plot 代码", "重画". The skill writes matplotlib (with seaborn helpers), runs the script to render a PNG, visually compares the output against the original image, and iterates until the rendered chart visually matches. Defaults to estimating data values from the image; if the user supplies a CSV/XLSX, that data is used directly. Works for scatter, bar, line, heatmap, distribution (hist/KDE/violin/box), multi-panel grids, and specialized plots (radar, parallel coordinates, network, hexbin, residual). Not for: editing an existing matplotlib script, generating data without a target figure, or compiling non-Python chart code.'
---

# Image-to-Chart

Turn any chart image into runnable Python that reproduces it. The skill follows a tight visual feedback loop — **draft → render → compare against the original → refine** — and iterates until the rendered PNG visually matches the input. Most charts converge in 2–4 iterations.

## Why a feedback loop matters

Matplotlib is a large, opinionated library with many equivalent ways to draw the same chart. Tiny differences in `cmap`, `alpha`, `edgecolor`, `gridspec` width ratios, or `tight_layout` vs. `constrained_layout` produce visually different output. Trying to predict the final rendering by reading the source is unreliable. **The fastest path to a good result is to actually run the script, look at the rendered PNG, and iterate.** Compilation (i.e. `python3 script.py`) is cheap (sub-second for most figures). Use it freely.

## Workflow

1. **Look at the chart carefully.** Read it with the `Read` tool. Note exactly what is visible — the plot type(s), the panel layout, the color palette, the axis labels and tick values, the legend entries, any annotations or statistical overlays (regression lines, KDE curves, R² boxes, confidence bands). Identify the content type(s):
   - Scatter (with optional regression / density / categorical color) → `references/scatter.md`
   - Bar / horizontal bar / stacked bar / lollipop → `references/bar.md`
   - Line / multi-series line / area → `references/line.md`
   - Heatmap (correlation matrix, 2D density, hexbin) → `references/heatmap.md`
   - Distribution (histogram, KDE, violin, box) → `references/distribution.md`
   - Multi-panel figure (gridspec, subplots, side-by-side, 2×2 / 3×3) → `references/multi-panel.md`
   - Specialized (radar, parallel coordinates, network graph, PCA scatter, residual) → `references/specialized.md`
   - Cross-cutting style (seaborn themes, palettes, fonts, axis scales) → `references/styling.md`

2. **Check for user-supplied data.** If the user attached a `.csv` / `.xlsx` / `.json` alongside the image, read it and use it directly. Otherwise, **estimate data values from the image** — read axis tick labels, point positions, and bar heights, then synthesize a NumPy/Pandas DataFrame that reproduces the visual structure. Goal: visual match, not data fidelity.

3. **Read the matching reference file(s).** Each reference contains one canonical example, the matplotlib/seaborn calls to use, and the few pitfalls that actually break things. Do not skip this.

4. **Pick a starting template from `assets/`.** Copy it into a working directory and rename `chart.py`.

5. **Draft the script.** Get structure right first (right subplot grid, right plot types, right data columns). Color choices, exact tick values, and annotation placement come later.

6. **Compile and render.** Run `scripts/compile_and_preview.sh <file.py>`. The script invokes `python3 <file.py>`, which must end with `plt.savefig('output.png', dpi=200, bbox_inches='tight')` (no `plt.show()` — it blocks in headless mode). The script prints the PNG path on success, or the traceback on failure.

7. **Visually verify.** Open the rendered PNG with `Read` — every compile. **Do not trust assertions about the script alone.** The script can look right while the rendered PNG has a clipped colorbar, swapped axes, wrong alpha, or a misaligned legend. Specifically check:
   - **All panels are visible** in the rendered PNG (the most common silent failure — a panel that was supposed to be there but got replaced, or one that was supposed to share an axis but uses `subplots()` wrong)
   - **All textual content from the original is present** in the rendering (no missing titles, axis labels, legend entries, annotation boxes)
   - **Layout matches the original** (panel order, row/column count, relative sizes)
   - **Colors match** (palette choice, alpha, edge colors, marker shapes, line styles)
   - **Statistical overlays are correct** (regression line slope, R² annotation, confidence band, KDE curve shape, hexbin colormap range)

8. **Refine.** Edit the `.py`, re-run, re-render, re-verify. Stop when the rendered image is visually close to the original — pixel-perfect is not the goal, faithful reproduction is. **If two iterations in a row produce only cosmetic changes, you are done** — do not chase perfection.

## What "done" looks like

- All panels, labels, legends, and annotations from the original appear in the rendered PNG
- Layout and aspect ratio match
- Colors and statistical overlays match within reason
- A human glancing at the two side-by-side would recognize them as the same chart
- The script runs cleanly with `python3 script.py` and exits 0

## What to give the user at the end

- The final `.py` file path
- The rendered PNG so they can see the result
- The list of Python packages they need (`pip install matplotlib seaborn pandas numpy` for the default; add `networkx` / `scikit-learn` only if the figure uses them)
- Any data file you generated/used, so they can swap in real data later

If iterating with the user, present the rendered PNG and ask "good enough or want me to fix X?" — let them steer the final polish.

## Cross-cutting tips

- **Always end the script with `plt.savefig('output.png', dpi=200, bbox_inches='tight')`** — never `plt.show()`. The `compile_and_preview.sh` script greps for this and warns if it's missing.
- **Use `constrained_layout=True` (not `tight_layout`) for multi-panel figures** with colorbars, legends outside the axes, or rotated tick labels. It handles overlapping artists better.
- **Seaborn's `whitegrid` / `darkgrid` themes** set background color and gridlines globally. Use `sns.set_theme(style='whitegrid')` once at the top, then call `plt.subplots()` — this is faster than styling each axes.
- **For heatmaps**, prefer `sns.heatmap(..., annot=True, fmt='.2f', cmap='RdBu_r', center=0)` for correlation matrices. The `center=0` is what makes positive values warm and negative values cool.
- **For scatter with categorical color**, prefer `sns.scatterplot(..., hue='category', palette='tab10')` over manual `for` loops. It handles legend automatically.
- **For hexbin density**, use `plt.hexbin(x, y, gridsize=30, cmap='YlOrRd')` + `plt.colorbar()`. Don't try to synthesize it with `scatter` + `alpha`.
- **For Chinese / non-Latin text**, set `plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'Arial Unicode MS']` and `plt.rcParams['axes.unicode_minus'] = False`. The compile script does not auto-detect this.
- **Synthetic data is fine.** When estimating from an image, it's OK if your `np.random.normal(loc=120, scale=15, size=50)` doesn't exactly match the source's underlying distribution. The bar heights, axis ranges, and color categories need to match; the exact (x, y) point cloud does not.

## When the chart is ambiguous

If you cannot tell exactly what is in a region (overlapping points, small text, low-resolution axis labels):

1. **Do not invent precise data.** Inventing is worse than leaving placeholders — it produces a "looks plausible" reproduction that is wrong on inspection.
2. Note the assumption in a brief `# comment` in the `.py`.
3. Show the user the rendered output and explicitly call out the gap: *"I read this axis as 0-100 with ticks every 20 — is that right?"*

## References at a glance

| File | When to read |
|---|---|
| `references/scatter.md` | Scatter (regression, density, categorical color, sub-panel grids) |
| `references/bar.md` | Bar / horizontal / stacked / lollipop |
| `references/line.md` | Line / multi-series / area / step |
| `references/heatmap.md` | Heatmap (correlation, 2D density, hexbin) |
| `references/distribution.md` | Histogram, KDE, violin, box, swarm |
| `references/multi-panel.md` | gridspec, subplots, side-by-side, 2×2 / 3×3 layouts |
| `references/specialized.md` | Radar, parallel coordinates, network graph, PCA scatter, residual |
| `references/styling.md` | Seaborn themes, palettes, fonts, axis scales, common annotations |
