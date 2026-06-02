# Specialized

Charts that don't fit into scatter / bar / line / heatmap / distribution. The most common ones in research papers:

- **Radar / spider chart** — multivariate data on a polar axis.
- **Parallel coordinates** — multivariate data with one vertical axis per variable.
- **Network graph** — nodes and edges (graph structure).
- **PCA / t-SNE / UMAP scatter** — dimensionality reduction, often colored by cluster or label.
- **Residual / diagnostic plot** — predicted vs. actual, with a y=x reference line.

## Radar / spider chart

A radar chart places multiple variables on axes that radiate from a center point, like spokes on a wheel. Each observation is a closed polygon connecting its values on each axis.

```python
import numpy as np
import matplotlib.pyplot as plt

categories = ['Speed', 'Power', 'Accuracy', 'Endurance', 'Agility', 'Focus']
N = len(categories)

# Two players to compare
player_a = [8, 6, 9, 7, 8, 9]
player_b = [6, 8, 7, 8, 7, 7]

# Compute angle for each axis
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

# Close the polygon
player_a += player_a[:1]
player_b += player_b[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True),
                       constrained_layout=True)
ax.fill(angles, player_a, color='#4C72B0', alpha=0.25)
ax.plot(angles, player_a, color='#4C72B0', lw=1.5, label='Player A')
ax.fill(angles, player_b, color='#DD8452', alpha=0.25)
ax.plot(angles, player_b, color='#DD8452', lw=1.5, label='Player B')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_ylim(0, 10)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Three things to notice:

1. **`subplot_kw=dict(polar=True)`** is the key. It converts the axes from Cartesian to polar. The first angle is at 3 o'clock (east) and angles increase counter-clockwise — by default.
2. **Close the polygon by repeating the first point at the end.** `player_a += player_a[:1]` and `angles += angles[:1]`. Without this, the line doesn't close and the polygon has a gap.
3. **`set_xticks(angles[:-1])`** uses the original angles (not the closed ones) for the tick positions. The tick LABELS go on these positions.

## Pitfalls (radar)

- **First axis starts at 0° (east) by default**, not at the top. If the source image has the first category at the top, set `ax.set_theta_offset(np.pi / 2)` to rotate 90°.
- **Direction is counter-clockwise by default.** If the source is clockwise, set `ax.set_theta_direction(-1)`.
- **Filled area can hide the gridlines.** If the source has visible gridlines through the filled region, use `ax.fill(..., alpha=0.1)` or skip the fill.

## Parallel coordinates

When the source image has many vertical axes (one per variable) and lines connecting one observation across all of them, that's parallel coordinates:

```python
import pandas as pd
from pandas.plotting import parallel_coordinates

df = pd.DataFrame({
    'speed':     np.random.uniform(0, 10, 30),
    'power':     np.random.uniform(0, 10, 30),
    'accuracy':  np.random.uniform(0, 10, 30),
    'endurance': np.random.uniform(0, 10, 30),
    'class':     np.random.choice(['A', 'B', 'C'], 30),
})

fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
parallel_coordinates(df, 'class', color=['#4C72B0', '#DD8452', '#55A868'], ax=ax)
ax.set_ylabel('Value')
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Each line is one observation; the x-axis is the variable index, not a continuous variable. The first argument is the DataFrame; the second is the column to color by.

## Pitfalls (parallel coords)

- **All variables must be on the same scale.** If one variable ranges 0-1 and another 0-1000, the small one will be a flat line. Normalize each column to [0, 1] before plotting.
- **Too many lines = noise.** If there are 1000+ observations, sample down or use `alpha=0.05`.

## Network graph

When the source has nodes (circles) connected by lines, use `networkx`:

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.karate_club_graph()  # example graph with 34 nodes

fig, ax = plt.subplots(figsize=(7, 6), constrained_layout=True)
pos = nx.spring_layout(G, seed=0)  # force-directed layout

# Color by community
communities = nx.community.louvain_communities(G)
node_colors = []
for node in G.nodes():
    for i, comm in enumerate(communities):
        if node in comm:
            node_colors.append(i)
            break

nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap='tab10',
                       node_size=200, ax=ax)
nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
ax.set_axis_off()
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Three things to notice:

1. **`pos = nx.spring_layout(G, seed=0)`** is the layout. `seed=0` makes it reproducible — without it, every call gives a different layout. Other layouts: `nx.circular_layout`, `nx.kamada_kawai_layout`, `nx.spectral_layout`.
2. **`cmap='tab10'`** + integer node colors = categorical coloring. Each community gets its own color.
3. **`ax.set_axis_off()`** hides the matplotlib axes (the network has its own coordinate system).

## Pitfalls (network)

- **`spring_layout` is non-deterministic.** Always pass `seed=...` to get a stable layout.
- **Edge crossings are ugly.** If the source has a clear hierarchical structure, use `nx.nx_agraph.graphviz_layout(G, prog='dot')` (requires `pygraphviz`) for a tree layout.
- **Labels overlap on dense graphs.** For 100+ nodes, drop the labels entirely. Use `node_size=20` and `linewidths=0`.

## PCA / t-SNE scatter

Dimensionality reduction results are shown as a scatter where the x and y are the first two components:

```python
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris

data = load_iris()
X, y = data.data, data.target

pca = PCA(n_components=2)
X_2d = pca.fit_transform(X)

fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
for label in np.unique(y):
    mask = y == label
    ax.scatter(X_2d[mask, 0], X_2d[mask, 1], label=data.target_names[label], alpha=0.7)
ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
ax.legend()
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

For t-SNE / UMAP, swap `PCA` for `TSNE` or `umap.UMAP` — the rest is the same.

The x and y axis labels should be the explained variance ratio (for PCA) or just "t-SNE 1" / "t-SNE 2" (for t-SNE).

## Residual / diagnostic plot

A common pattern in regression papers: predicted vs. actual, with a y=x reference line:

```python
fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
ax.scatter(y_pred, y_actual, alpha=0.6, edgecolor='white')
lims = [min(y_pred.min(), y_actual.min()), max(y_pred.max(), y_actual.max())]
ax.plot(lims, lims, 'r--', lw=1, label='y = x (ideal)')
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.legend()
ax.set_aspect('equal')   # makes the y=x line actually 45°
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

`set_aspect('equal')` is what makes the reference line 45° instead of stretched. Without it, the line tilts to match the axes' aspect ratio, which looks wrong.

## When to use this reference

- The chart doesn't fit cleanly into scatter/bar/line/heatmap/distribution.
- The visual has polar axes, network structure, or dimensionality-reduction output.
- The chart is showing one of: multivariate comparison, graph structure, embedding, model diagnostics.

If the chart has axes that look like a clock face, it's a radar. If the visual is "lots of circles connected by lines", it's a network. If the x and y axes have percentage labels that sum to <100, it's a PCA. If the visual is "predicted on x, actual on y, with a diagonal line", it's a residual plot.
