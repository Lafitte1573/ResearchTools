"""Line chart — starting template.

Copy this file to a working directory, rename to chart.py, then edit
the x-axis, multiple series, and styling to match the source image.
See references/line.md for variants: shaded bands, step plots, area, markers.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# --- Data ---
x = np.linspace(0, 10, 100)
y1 = np.sin(x) + 0.1 * rng.normal(size=100)
y2 = np.cos(x) + 0.1 * rng.normal(size=100)

# --- Build the figure ---
fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
ax.plot(x, y1, '-',  color='#4C72B0', label='Series 1', lw=1.5)
ax.plot(x, y2, '--', color='#DD8452', label='Series 2', lw=1.5)

# --- Labels + legend + gridlines ---
ax.set_xlabel('X label')
ax.set_ylabel('Y label')
ax.legend()
ax.grid(linestyle=':', alpha=0.5)

plt.savefig('output.png', dpi=200, bbox_inches='tight')

# --- For a confidence band, add fill_between: ---
# mean = np.convolve(y1, np.ones(10)/10, mode='same')  # smoothed
# std  = ...
# ax.fill_between(x, mean - std, mean + std, color='#4C72B0', alpha=0.2)
