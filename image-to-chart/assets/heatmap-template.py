"""Heatmap — starting template.

Copy this file to a working directory, rename to chart.py, then edit
the data matrix, labels, and colormap to match the source image.
See references/heatmap.md for correlation matrices, clustermap, and hexbin.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Synthesize a correlation matrix (8x8) ---
rng = np.random.default_rng(0)
n_vars = 8
n_samples = 200
data = rng.normal(size=(n_samples, n_vars))
# Inject some structure so the heatmap isn't random noise
data[:, 1] = 0.6 * data[:, 0] + 0.4 * rng.normal(size=n_samples)
data[:, 2] = -0.5 * data[:, 0] + 0.5 * rng.normal(size=n_samples)

labels = ['var1', 'var2', 'var3', 'var4', 'var5', 'var6', 'var7', 'var8']
corr = np.corrcoef(data.T)

# --- Build the figure ---
fig, ax = plt.subplots(figsize=(6.5, 6), constrained_layout=True)
sns.heatmap(corr, ax=ax,
            annot=True, fmt='.2f',
            cmap='RdBu_r', center=0,    # <-- diverging colormap, centered at 0
            xticklabels=labels, yticklabels=labels,
            cbar_kws={'label': 'Correlation'},
            square=True, linewidths=0.5, linecolor='white')
ax.set_title('Correlation Matrix')

plt.savefig('output.png', dpi=200, bbox_inches='tight')
