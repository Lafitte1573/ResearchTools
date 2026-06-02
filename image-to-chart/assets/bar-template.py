"""Bar chart — starting template.

Copy this file to a working directory, rename to chart.py, then edit
the categories, values, and styling to match the source image.
See references/bar.md for vertical / horizontal / stacked / lollipop variants.
"""
import numpy as np
import matplotlib.pyplot as plt

# --- Data ---
categories = ['A', 'B', 'C', 'D']
values     = [23, 45, 12, 38]
x = np.arange(len(categories))

# --- Build the figure ---
fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
ax.bar(x, values, color='#4C72B0', edgecolor='white', width=0.7)

# --- Labels + gridlines ---
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_ylabel('Value')
ax.set_ylim(0, max(values) * 1.15)
ax.grid(axis='y', linestyle=':', alpha=0.5)
ax.set_axisbelow(True)  # gridlines behind the bars

plt.savefig('output.png', dpi=200, bbox_inches='tight')

# --- For horizontal bars, swap to: ---
# fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
# y = np.arange(len(categories))
# ax.barh(y, values, color='#4C72B0', height=0.7)
# ax.set_yticks(y)
# ax.set_yticklabels(categories)
# ax.invert_yaxis()    # first category on top
# ax.set_xlabel('Value')
