"""Distribution chart — starting template.

Copy this file to a working directory, rename to chart.py, then edit
the data + grouping to match the source image.
See references/distribution.md for hist / KDE / violin / box / strip variants.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# --- Synthesize data for 3 groups ---
n = 120
df = pd.DataFrame({
    'value': np.concatenate([
        rng.normal(loc=5, scale=1.2, size=n),
        rng.gamma(shape=2, scale=2,  size=n),
        rng.normal(loc=7, scale=0.8, size=n),
    ]),
    'group': ['A']*n + ['B']*n + ['C']*n,
})

# --- Build the figure ---
fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)

# Pick the layers that match the source image. Common combos:
#   violin alone         -> sns.violinplot(...)
#   box alone            -> sns.boxplot(...)
#   violin + box + strip -> all three (overlaid)
#   hist + KDE           -> sns.histplot(..., kde=True, stat='density')
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
