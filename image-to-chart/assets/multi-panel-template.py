"""Multi-panel figure — starting template.

Copy this file to a working directory, rename to chart.py, then edit
the subplot grid + per-panel content to match the source image.
See references/multi-panel.md for subplots, gridspec, sharing axes, insets.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# --- Synthesize data ---
n = 200
x = rng.normal(0, 1, n)
y = 0.6 * x + 0.4 * rng.normal(0, 1, n)

# --- Build a 2x2 grid ---
fig, axes = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)

# Top-left: histogram
axes[0, 0].hist(x, bins=30, color='#4C72B0', edgecolor='white')
axes[0, 0].set_title('Histogram of x')
axes[0, 0].set_xlabel('x')
axes[0, 0].set_ylabel('count')

# Top-right: 2D KDE
sns.kdeplot(x=x, y=y, fill=True, cmap='Blues', ax=axes[0, 1])
axes[0, 1].set_title('2D KDE')
axes[0, 1].set_xlabel('x')
axes[0, 1].set_ylabel('y')

# Bottom-left: heatmap
corr = np.corrcoef(np.column_stack([x, y, rng.normal(size=(n, 4))]).T)
sns.heatmap(corr, ax=axes[1, 0], annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, cbar=False)
axes[1, 0].set_title('Correlation')

# Bottom-right: scatter
axes[1, 1].scatter(x, y, alpha=0.6, s=20, edgecolor='white')
axes[1, 1].set_title('Scatter x vs y')
axes[1, 1].set_xlabel('x')
axes[1, 1].set_ylabel('y')

plt.savefig('output.png', dpi=200, bbox_inches='tight')

# --- Alternative: 2-panel vertical stack ---
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 9), constrained_layout=True)
# # ... plot on ax1 (top) and ax2 (bottom) ...
