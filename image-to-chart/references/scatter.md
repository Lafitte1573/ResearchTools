# Scatter

The most common chart type in research papers. A scatter plot shows individual (x, y) points. Variants add **color** (categorical or continuous), **size** (encoding a third variable), and a **regression line** with a band of confidence.

## Canonical example: scatter + regression + color + size

This is the kind of figure that appears in the first example in `README.md`: a 2-panel figure with a scatter on top and a correlation heatmap on the bottom. The scatter alone looks like this:

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# Synthesize ~80 points in the same range as the source image
n = 80
x = rng.normal(0.8, 0.15, n)         # KD ratio
y = 150 + 100 * x + rng.normal(0, 20, n)   # ACS/Map
c = rng.integers(5, 35, n)           # Maps played (color)
s = rng.integers(20, 200, n)         # Total kills (size)

fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
sc = ax.scatter(x, y, c=c, s=s, cmap='viridis', alpha=0.8, edgecolor='white')

# Regression line
coef = np.polyfit(x, y, 1)
xs = np.array([x.min(), x.max()])
ax.plot(xs, np.polyval(coef, xs), 'r-', lw=1.5,
        label=f'Best fit line (R² = {np.corrcoef(x, y)[0, 1]**2:.3f})')

ax.set_xlabel('Kill/Death Ratio (KD)')
ax.set_ylabel('Average Combat Score per Map (ACS/Map)')
ax.legend(loc='upper left')
cbar = fig.colorbar(sc, ax=ax, label='Maps Played')
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Three things to notice in this canonical example:

1. **`s` is an array of per-point sizes**, not a single number. Each point gets its own size based on a third variable.
2. **`c` is an array of per-point colors**, paired with `cmap='viridis'`. The `colorbar` is built from the same `scatter` return value, so the legend on the colorbar matches the dots.
3. **The regression line** is computed with `np.polyfit` and the R² is computed manually from the correlation coefficient. This avoids pulling in `statsmodels` for what matplotlib can do on its own.

## Pitfalls

These are the things that actually break:

- **Size scale is squished.** If you pass `s=rng.integers(20, 200, n)` matplotlib uses those values as **point²** directly — so 20 looks like a 4.5pt dot and 200 looks like a 14pt dot, but the visual ratio of 10× is too aggressive. If the original image has roughly uniform-looking dots, pass values like `s=10 + 0.05 * s_raw` to compress the scale. If the original has dramatic size differences, keep the raw values.
- **Color overwrites hue.** If you pass `c='red'` as a string, every point is the same color. To use a colormap you must pass `c` as an array of numbers AND `cmap='viridis'`. To use a categorical palette, use `sns.scatterplot(..., hue='category', palette='tab10')` instead — it handles the legend automatically.
- **Colorbar tied to the wrong axis.** When you call `fig.colorbar(sc, ax=ax)`, the colorbar attaches to the right side of `ax`. In a multi-panel figure, pass the right axes: `fig.colorbar(sc, ax=ax1)` for the top scatter, `fig.colorbar(hm, ax=ax2)` for the bottom heatmap. Otherwise the colorbar floats in the wrong place.
- **`alpha < 0.5` makes overlapping points look like noise.** Density regions (where many points overlap) become nearly transparent and the figure looks sparse. Use `alpha=0.7-0.85` for typical research plots. Drop to `0.3-0.5` only when the source image itself looks heavily transparent.
- **`edgecolor` matters.** White edges (`edgecolor='white', linewidth=0.5`) make overlapping points distinguishable. Black edges look harsh. No edge at all and dense regions become blobs. Default to white unless the source clearly has a different style.
- **Regression R² is `r²` not `r`.** `np.corrcoef(x, y)[0, 1]` returns the correlation coefficient `r`. To get R², square it: `**2`. If the source image shows `R² = 0.669`, the regression line slope is whatever the data gives you — don't try to force a specific R².

## Categorical color (no colormap)

When the source has discrete groups (e.g. "control", "treatment A", "treatment B"), use seaborn's `scatterplot` with `hue`:

```python
import pandas as pd
df = pd.DataFrame({
    'x': x, 'y': y,
    'group': rng.choice(['control', 'treat_A', 'treat_B'], n),
})
sns.scatterplot(data=df, x='x', y='y', hue='group', palette='tab10',
                s=60, alpha=0.8, ax=ax)
ax.legend(title='Group')
```

This automatically creates a legend with one entry per group, using the right color swatches. Doing this with `plt.scatter` and a manual loop works but is more code for the same result.

## Sub-panel grid: small multiples

When the source image has a grid of related scatter plots (e.g. one per condition, all sharing y-axis), use `plt.subplots(n_rows, n_cols, sharey=True)`:

```python
fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True, constrained_layout=True)
for ax, condition in zip(axes, ['A', 'B', 'C']):
    sub = df[df.condition == condition]
    ax.scatter(sub.x, sub.y, alpha=0.7)
    ax.set_title(f'Condition {condition}')
    ax.set_xlabel('x')
axes[0].set_ylabel('y')
```

The first column gets the y-label; the other columns inherit the y-axis (and tick labels) from `sharey=True`. Don't repeat the y-label on every column.

## When to use this reference

- The chart shows individual data points (not bars or lines).
- The points are arranged in a 2D plane (not 1D-as-strip-plot or 1D-as-violin).
- You see a single panel, a panel grid (1×3, 2×2, 3×3), or a small-multiples layout.

If the points are connected by a line, you're looking at a **line** plot, not a scatter. If the points are colored by a single group and the plot is mostly about showing category differences, you might be looking at a **bar** chart. The visual cue is "individual dots, no connector".
