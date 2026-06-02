# Heatmap

A heatmap encodes a 2D grid of values as colors. The most common case is a **correlation matrix** (variables × variables), but heatmaps also appear for confusion matrices, attention maps, and any 2D data with `(i, j)` indices.

## Canonical example: correlation matrix with annotations

This is the second panel in the README's 2-panel example figure:

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Synthesize 8 variables with realistic correlations
rng = np.random.default_rng(0)
n_vars = 8
n_samples = 200
data = rng.normal(size=(n_samples, n_vars))
# Inject some correlation structure so the heatmap has visible structure
data[:, 1] = 0.6 * data[:, 0] + 0.4 * rng.normal(size=n_samples)
data[:, 2] = -0.5 * data[:, 0] + 0.5 * rng.normal(size=n_samples)
data[:, 3] = 0.7 * data[:, 1] + 0.3 * rng.normal(size=n_samples)

labels = ['KD', 'ACS', 'HS%', 'ADR', 'KPR', 'APR', 'FKPR', 'FDPR']
corr = np.corrcoef(data.T)

fig, ax = plt.subplots(figsize=(6.5, 6), constrained_layout=True)
sns.heatmap(corr, ax=ax,
            annot=True, fmt='.2f',
            cmap='RdBu_r', center=0,
            xticklabels=labels, yticklabels=labels,
            cbar_kws={'label': 'Correlation'},
            square=True, linewidths=0.5, linecolor='white')
ax.set_title('Correlation Matrix')
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Three things to notice:

1. **`cmap='RdBu_r'` with `center=0`** is the right combination for correlation. Positive values get warm (red), negative get cool (blue), and zero is white. The `_r` suffix reverses the default RdBu colormap so the convention is "red = high, blue = low" — which is what humans expect.
2. **`annot=True, fmt='.2f'`** writes the numeric value in each cell. For an 8×8 matrix this is fine; for a 50×50 matrix it becomes a wall of text — drop the annotations.
3. **`square=True, linewidths=0.5, linecolor='white'`** gives the matrix a "tile" appearance. The white lines between cells make the grid readable. Drop `linewidths` and the tiles fuse into a continuous color field.

## Pitfalls

- **Wrong colormap direction.** Default `RdBu` goes from red (low) to blue (high). For correlations you almost always want `RdBu_r` (reversed) so high values are red. The `_r` suffix is what most papers use.
- **Forgetting `center=0`.** Without it, `RdBu_r` will scale its midpoint to the data median — which is meaningless for correlations that are bounded in [-1, 1] and centered at 0. Always pass `center=0` for correlation-style heatmaps.
- **Annotations are unreadable.** With 50+ rows, the cell text becomes 4pt and unreadable. Drop `annot=True` for large matrices; rely on the color.
- **The colorbar is in a different units than the data.** If the data is a probability in [0, 1], set `vmin=0, vmax=1` explicitly. Otherwise the colorbar's auto-scaling will mislead readers.
- **X-labels are 0° by default.** Long variable names will collide. Set `ax.set_xticklabels(labels, rotation=45, ha='right')` to slant them.
- **The heatmap is upside down.** Seaborn's heatmap puts the first row of the input at the top. If the source image shows the first variable at the bottom (some papers do), call `corr = corr[::-1]` before plotting.
- **Confusion matrix needs different defaults.** A confusion matrix has integer values, not floats. Use `cmap='Blues'` (sequential, not diverging), `annot=True, fmt='d'` (integer formatting), and no `center`.

## Heatmap with row/column clustering (clustermap)

Some papers show variables clustered by similarity — similar variables end up adjacent. Seaborn's `clustermap` does this:

```python
sns.clustermap(corr, annot=True, fmt='.2f',
               cmap='RdBu_r', center=0,
               xticklabels=labels, yticklabels=labels,
               figsize=(7, 7))
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

`clustermap` returns a `ClusterGrid`, not an `Axes`. Don't try to set titles or labels on it the way you do on a regular heatmap. If the source image has reordered variables, this is what you want; if the variables are in the original order, stick with `heatmap`.

## Hexbin (2D density)

When the source image shows a scatter plot with too many points to see individual dots, it's often a hexbin:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
hb = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', mincnt=1)
ax.set_xlabel('x')
ax.set_ylabel('y')
fig.colorbar(hb, ax=ax, label='Count')
```

`gridsize=30` means 30×30 hexagons covering the plot area. Increase for more detail, decrease for coarser aggregation. `mincnt=1` hides empty hexagons (otherwise empty cells show as the colormap's lowest value, which is misleading).

Hexbin is preferred over `scatter` with `alpha` when there are 1000+ points: the density is computed explicitly and shown in the colorbar, instead of being guessed from overlap.

## Pitfalls (hexbin)

- **Wrong colormap.** Sequential (`YlOrRd`, `viridis`, `Blues`) — not diverging. Use a single hue gradient from light to dark; the count goes from 0 to N.
- **Empty cells are colored.** Set `mincnt=1` or the lowest color appears where there are no points.
- **Grid is too coarse or too fine.** `gridsize=30` is a good default. If the source image shows a tight, smooth density field, try `gridsize=50`. If the source shows chunky bins, try `gridsize=20`.

## When to use this reference

- The chart shows a 2D grid of colored cells.
- Each cell encodes a value (not a count or a probability density in the strict sense).
- The grid is labeled on both axes (variable names, time periods, class labels, etc.).

If the colors form a smooth gradient without visible cells (no grid lines, no labels), you might be looking at a **2D density** plot (KDE) — see `distribution.md` for KDE-related patterns.
