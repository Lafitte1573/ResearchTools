# Multi-panel

Multi-panel figures combine several subplots into one figure. They appear in research papers everywhere: 2-panel (e.g. scatter + heatmap), 2×2 grids (hist + KDE + bar + scatter), 1×3 small multiples, 3×3 benchmark summaries, etc.

The key is picking the right `subplots` / `gridspec` shape and sharing axes when appropriate.

## Canonical example: 2×2 grid with mixed chart types

This is the kind of figure you see in ML papers: a 2×2 grid with a histogram (top-left), a KDE (top-right), a heatmap (bottom-left), and a scatter (bottom-right).

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)
n = 200
x = rng.normal(0, 1, n)
y = 0.6 * x + 0.4 * rng.normal(0, 1, n)

fig, axes = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)

# Top-left: histogram
axes[0, 0].hist(x, bins=30, color='#4C72B0', edgecolor='white')
axes[0, 0].set_title('Histogram of x')
axes[0, 0].set_xlabel('x'); axes[0, 0].set_ylabel('count')

# Top-right: KDE
sns.kdeplot(x=x, y=y, fill=True, cmap='Blues', ax=axes[0, 1])
axes[0, 1].set_title('2D KDE')
axes[0, 1].set_xlabel('x'); axes[0, 1].set_ylabel('y')

# Bottom-left: heatmap
corr = np.corrcoef(np.column_stack([x, y, rng.normal(size=(n, 4))]).T)
sns.heatmap(corr, ax=axes[1, 0], annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, cbar=False)
axes[1, 0].set_title('Correlation')

# Bottom-right: scatter
axes[1, 1].scatter(x, y, alpha=0.6, s=20, edgecolor='white')
axes[1, 1].set_title('Scatter x vs y')
axes[1, 1].set_xlabel('x'); axes[1, 1].set_ylabel('y')

plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

The two key calls:

1. **`plt.subplots(2, 2, ...)`** gives you a 2D array of axes. Index as `axes[row, col]`. If the shape is `(1, 3)`, you can index as `axes[0, 1]` or use `axes[1]` — both work.
2. **`constrained_layout=True`** is what you want when any panel has a colorbar, legend outside the axes, or rotated tick labels. It handles overlapping artists better than `tight_layout`.

## Vertical stack (2 panels, 1 column)

The simplest multi-panel: scatter on top, heatmap on bottom. From the README example:

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 9), constrained_layout=True)
# ... plot on ax1 (scatter) and ax2 (heatmap) ...
```

When you unpack `(ax1, ax2)`, you can refer to them by name. For 2×2 grids this is awkward (you'd need 4 names), so use the `axes[i, j]` form.

## Sharing axes

When panels share an x-axis or y-axis, use `sharex=True` or `sharey=True`:

```python
fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
# Now axes[0], axes[1], axes[2] all have the same y-axis ticks and limits.
# You only need to set_ylabel on axes[0] — the others inherit.
```

**Important:** with `sharey=True`, do NOT call `set_ylim` on individual axes; it will raise a warning. Set the ylim on any one of them and the rest follow.

For the x-axis (e.g. time series at the same time points), use `sharex=True`. For both: `sharex=True, sharey=True`.

## Different sizes: `gridspec`

When the source image has panels of different sizes (e.g. a tall plot on the left and two short plots stacked on the right), use `gridspec`:

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(10, 6), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1], height_ratios=[1, 1])

ax1 = fig.add_subplot(gs[:, 0])      # spans both rows, left column
ax2 = fig.add_subplot(gs[0, 1])      # top right
ax3 = fig.add_subplot(gs[1, 1])      # bottom right
```

`width_ratios=[2, 1]` makes the left column twice as wide as the right. `height_ratios=[1, 1]` (the default) means the two right columns are equal height. The `gs[:, 0]` slice means "all rows, column 0" — so ax1 takes up the entire left column.

## Inset axes (zoomed-in detail)

Sometimes the source image has a small "zoom" panel inside a larger one. Use `inset_axes`:

```python
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

axins = inset_axes(ax, width="40%", height="40%", loc='upper right')
ax.scatter(x, y, ax=axins)  # or whatever — same data, different view
axins.set_xlim(0.5, 1.0)    # zoomed region
axins.set_ylim(150, 250)
```

The first argument is the parent axes. `width="40%"` and `height="40%"` are relative to the parent's size. `loc='upper right'` is the corner of the parent where the inset sits.

## Pitfalls

- **`plt.subplots(1, 3)` returns a 1D array, not a 2D one.** Indexing as `axes[0, 1]` raises an error. Use `axes[1]` for 1D shapes.
- **`tight_layout()` breaks with colorbars.** When any panel has a `colorbar` call, `tight_layout` will overlap the colorbar with the next panel. Use `constrained_layout=True` and let matplotlib handle it.
- **Each panel doesn't get a title.** It's common to see multi-panel figures where only the top-left or only the bottom has labels. If the source image has per-panel titles, add `ax.set_title('...')` to each one.
- **`sharex=True` doesn't share x-limits across panels with different x-ranges.** If panel 1 is a histogram (x range 0-10) and panel 2 is a time series (x range 2010-2020), don't share x. The x-ranges are fundamentally different.
- **Forgetting to pass `ax=` to seaborn functions.** `sns.heatmap(corr)` will draw on the *current* axes — which may be the wrong one in a multi-panel figure. Always pass `ax=axes[i, j]` explicitly.
- **Colorbars collide with adjacent panels.** If the source has a colorbar inside the rightmost panel (not outside), that's fine. If it's outside, make sure the `constrained_layout` is enabled and the figure has enough room.

## When to use this reference

- The source image clearly has more than one chart panel.
- The panels are arranged in a grid (1×N, M×N, or with gridspec).
- The panels may be the same chart type (small multiples) or different (mixed).

If the source is a single panel, you're done — no need for `subplots`. If the panels are not aligned in a grid (e.g. an inset), use `inset_axes` instead.
