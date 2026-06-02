"""Scatter plot — starting template.

Copy this file to a working directory, rename to chart.py, then edit
the data + labels + styling to match the source image.
See references/scatter.md for the full reference.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# --- Synthesize data in the same range as the source image ---
n = 80
x = rng.normal(0.8, 0.15, n)         # x-axis values
y = 150 + 100 * x + rng.normal(0, 20, n)  # y = linear trend + noise
c = rng.integers(5, 35, n)           # color (third variable)
s = 20 + 0.4 * rng.integers(20, 200, n)   # size (fourth variable), compressed scale

# --- Build the figure ---
fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
sc = ax.scatter(x, y, c=c, s=s, cmap='viridis', alpha=0.8, edgecolor='white')

# Optional: regression line + R² annotation
coef = np.polyfit(x, y, 1)
xs = np.array([x.min(), x.max()])
ax.plot(xs, np.polyval(coef, xs), 'r-', lw=1.5,
        label=f'Best fit (R² = {np.corrcoef(x, y)[0, 1]**2:.3f})')

# --- Labels + legend + colorbar ---
ax.set_xlabel('X label')
ax.set_ylabel('Y label')
ax.legend(loc='upper left')
fig.colorbar(sc, ax=ax, label='Color variable')

plt.savefig('output.png', dpi=200, bbox_inches='tight')
