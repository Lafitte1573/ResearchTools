# Distribution

Distribution charts show how a variable is spread out: histogram, KDE (smoothed density), violin, box, and strip/swarm plots. The same data can be shown in many ways — the choice depends on the number of observations and what aspect of the distribution matters.

## Canonical example: violin + box + strip (overlaid)

This is the most informative distribution chart: violin shows the shape, box shows the quartiles, and strip shows every individual point.

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# Three groups with different distributions
group_a = rng.normal(loc=5,  scale=1.2, size=120)
group_b = rng.gamma(shape=2, scale=2,  size=120)
group_c = rng.normal(loc=7,  scale=0.8, size=120)

import pandas as pd
df = pd.DataFrame({
    'value': np.concatenate([group_a, group_b, group_c]),
    'group': ['A'] * 120 + ['B'] * 120 + ['C'] * 120,
})

fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
sns.violinplot(data=df, x='group', y='value', ax=ax,
               inner=None, color='lightgray', alpha=0.6)
sns.boxplot(data=df, x='group', y='value', ax=ax,
            width=0.2, showfliers=False,
            boxprops={'facecolor': 'white', 'edgecolor': 'black'})
sns.stripplot(data=df, x='group', y='value', ax=ax,
              size=2, color='black', alpha=0.5)
ax.set_ylabel('Value')
ax.set_xlabel('Group')
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Three things to notice:

1. **Three plots layered in the same axes**: violin (background), box (middle), strip (foreground). This is the most informative combination. Each layer adds information the previous one lacks.
2. **`inner=None` on the violin** suppresses the default quartile lines inside the violin — the box plot will draw those instead, so duplicating them is noise.
3. **`showfliers=False` on the box** hides outlier dots — the strip plot will show every point anyway.

## Histogram

For a single variable, a histogram is the most basic distribution chart:

```python
fig, ax = plt.subplots(figsize=(6, 4.5), constrained_layout=True)
ax.hist(data, bins=30, color='#4C72B0', edgecolor='white')
ax.set_xlabel('Value')
ax.set_ylabel('Count')
```

Add a KDE overlay with `scipy.stats.gaussian_kde` or seaborn's `kdeplot`:

```python
from scipy.stats import gaussian_kde
xs = np.linspace(data.min(), data.max(), 200)
ax.plot(xs, gaussian_kde(data)(xs) * len(data) * (data.max() - data.min()) / 30,
        color='black', lw=1.5)
```

The KDE must be scaled to match the histogram's density: `kde(x) * N * bin_width`. Or use seaborn's `histplot(..., kde=True, stat='density')` which does the scaling for you.

## Histogram with multiple groups

For multiple groups, use `histplot` with `hue`:

```python
sns.histplot(data=df, x='value', hue='group', bins=30, alpha=0.5,
             stat='density', common_norm=False, ax=ax)
```

`common_norm=False` is important when groups have different sizes — otherwise the densities are scaled so their integrals are 1 each, but the relative weighting is lost. Set it to `True` only if you want the densities on the same scale (typical for shape comparison).

For side-by-side bars per group, use `multiple='dodge'`. For stacked, `multiple='stack'`. For overlapping with transparency, `multiple='layer'` (the default).

## Box plot

When the source image has boxes with whiskers and no violin, use `boxplot` directly:

```python
sns.boxplot(data=df, x='group', y='value', ax=ax,
            showfliers=True, palette='pastel')
```

The default shows outliers as dots beyond the whiskers. `showfliers=False` hides them if the source image doesn't have them.

## Strip plot / swarm plot

Strip: scatter all points at their actual y-value, jittered on x. Swarm: like strip, but with non-overlapping points.

```python
sns.stripplot(data=df, x='group', y='value', ax=ax, jitter=0.1, size=3)
# OR
sns.swarmplot(data=df, x='group', y='value', ax=ax, size=3)
```

Swarm is slower for large datasets (>500 points) and looks bad. Strip with `jitter=0.1` is the safer default.

## Pitfalls

- **KDE bandwidth is too narrow or too wide.** Seaborn's `kdeplot` uses Scott's rule by default. If the source KDE is "spiky", decrease `bw_method=0.2`. If it's "smoothed into a single bump", increase to `bw_method=0.5`.
- **Violin scaling is wrong.** By default seaborn scales each violin so its area is 1 (`scale='area'`). To get them all the same width, use `scale='width'`. To get them all the same count, use `scale='count'`. The source image will tell you which — `scale='area'` (the default) is most common.
- **Box plot widths are too wide.** Default `width=0.8` is fine for sparse data, but in tight side-by-side panels it overlaps. Set `width=0.3` for compact panels.
- **Histogram bins are wrong.** `bins=30` is fine for 100+ points, but for 20 points it's too many. Use `bins='auto'` to let numpy decide, or `bins=int(np.sqrt(len(data)))` for Sturges' rule.
- **Y-axis starts at a negative value.** For a distribution, the y-axis should start at 0. Negative y values on a histogram are meaningless.
- **The strip plot's jitter puts points outside the violin.** Strip is jittered on x only; if the violin is narrow, points can stick out. Reduce `jitter=0.05` or use swarm.

## When to use this reference

- The chart shows the spread of a single variable (per group, or overall).
- The visual is box-like, violin-like, or shows individual points along an axis.
- There's no clear "x-y" relationship (if there is, you want a scatter).

If the chart shows a single smooth curve representing density, it might be a **KDE-only** plot — use `sns.kdeplot(x=data, fill=True)`. If it shows a histogram of two variables (a 2D histogram), see `heatmap.md` for hexbin.
