"""Reproduction of Realchart2code-raw/2.png
2-panel figure: horizontal bar (left) + lollipop (right), both about PUBG weapons.

Source image: PUBG weapon stats.
- Left: Top 15 weapons by Damage Per Second, colored by weapon type
  (Shotgun=green, Pistol=orange, others=gray/blue), with value labels.
- Right: Kill Efficiency (Avg. Shots to Kill), lollipop chart with
  Automatic vs Non-Automatic color, value labels at each marker.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# --- Data: 15 PUBG weapons, ordered top-down as in source image ---
weapons = ['S686', 'S12K', 'MK14', 'Sawed-Off', 'Groza', 'M249', 'SLR',
           'Vector', 'M762', 'Uzi', 'SKS', 'M416', 'AUG A3', 'G36C', 'MP5K']
dps     = [1080, 792, 678, 640, 612, 600, 580, 569, 547, 542, 530, 502, 502, 502, 495]
# Category by weapon (for color in left panel)
category = ['Shotgun', 'Shotgun', 'Designed Marksman Rifle', 'Shotgun',
            'Assault Rifle', 'Light Machine Gun', 'Designed Marksman Rifle',
            'Submachine Gun', 'Assault Rifle', 'Submachine Gun',
            'Designed Marksman Rifle', 'Assault Rifle', 'Assault Rifle',
            'Assault Rifle', 'Submachine Gun']
# Kill efficiency (avg shots to kill), for the right panel. Source has
# Sawed-Off=1.5, S686=1, S12K=1, MK14=2.5, Groza=3, M249=3, SLR=2.5,
# Vector=4, M762=3, Uzi=5.5, SKS=2.5, M416=3, AUG A3=3, G36C=3, MP5K=4
shots_to_kill = [1.0, 1.0, 2.5, 1.5, 3.0, 3.0, 2.5, 4.0, 3.0, 5.5,
                 2.5, 3.0, 3.0, 3.0, 4.0]
# Fire mode: Automatic for most, Non-Automatic for some
fire_mode = ['Automatic', 'Automatic', 'Automatic', 'Non-Automatic',
             'Automatic', 'Automatic', 'Non-Automatic', 'Automatic',
             'Automatic', 'Automatic', 'Non-Automatic', 'Automatic',
             'Automatic', 'Automatic', 'Automatic']

# Color maps matching the source image
cat_colors = {
    'Submachine Gun': '#7F7F7F',          # gray
    'Assault Rifle':   '#5A8FB0',          # muted blue
    'Designed Marksman Rifle': '#9C9C9C',  # lighter gray
    'Light Machine Gun': '#7F7F7F',       # gray
    'Pistol':          '#F0A040',          # orange
    'Shotgun':         '#6FBA6F',          # green
}
fire_colors = {
    'Automatic':     '#E07856',   # salmon / coral
    'Non-Automatic': '#5A8FB0',   # muted blue (small dot in legend)
}

# --- Build the figure: 2 side-by-side panels ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)

# === LEFT: horizontal bar chart of DPS ===
# y positions: in matplotlib the first y-tick is at the bottom; we want S686 on
# TOP, so reverse the order and use invert_yaxis (handled below).
y = np.arange(len(weapons))
bar_colors = [cat_colors[c] for c in category]
bars = ax1.barh(y, dps, color=bar_colors, height=0.7, edgecolor='none')

# Add value labels at the end of each bar
for yi, v in zip(y, dps):
    ax1.text(v + 12, yi, str(v), va='center', ha='left', fontsize=8, color='black')

ax1.set_yticks(y)
ax1.set_yticklabels(weapons)
ax1.invert_yaxis()                                  # first weapon on top
ax1.set_xlabel('Damage Per Second (DPS)')
ax1.set_xlim(0, max(dps) * 1.18)
ax1.set_title('Top 15 PUBG Weapons by Damage Per Second', fontsize=11)
ax1.grid(axis='x', linestyle=':', alpha=0.5)
ax1.set_axisbelow(True)
# Remove top/right spines for a cleaner look
sns.despine(ax=ax1, top=True, right=True)

# Legend (one entry per category, ordered as in source)
from matplotlib.patches import Patch
legend_order = ['Submachine Gun', 'Assault Rifle', 'Designed Marksman Rifle',
                'Light Machine Gun', 'Pistol', 'Shotgun']
legend_patches = [Patch(facecolor=cat_colors[c], label=c) for c in legend_order]
ax1.legend(handles=legend_patches, loc='lower right', fontsize=8, frameon=True)

# === RIGHT: lollipop chart of Kill Efficiency ===
y2 = np.arange(len(weapons))
ax2.hlines(y2, 0, shots_to_kill, color=fire_colors['Automatic'], lw=1.5, alpha=0.9)
# Markers: same salmon color, with a small blue marker for non-automatic
marker_colors = [fire_colors['Automatic'] if fm == 'Automatic'
                 else fire_colors['Non-Automatic'] for fm in fire_mode]
ax2.scatter(shots_to_kill, y2, c=marker_colors, s=80, zorder=3, edgecolor='white',
            linewidth=0.5)

# Add value labels next to each marker
for yi, v in zip(y2, shots_to_kill):
    ax2.text(v + 0.12, yi, f'{v}', va='center', ha='left', fontsize=8)

ax2.set_yticks(y2)
ax2.set_yticklabels(weapons)
ax2.invert_yaxis()                                  # first weapon on top
ax2.set_xlabel('Kill Efficiency (Avg. Shots to Kill)')
ax2.set_xlim(0, max(shots_to_kill) * 1.18)
ax2.set_title('Kill Efficiency by Fire Mode', fontsize=11)
ax2.grid(axis='x', linestyle=':', alpha=0.5)
ax2.set_axisbelow(True)
sns.despine(ax=ax2, top=True, right=True)

# Legend: red = Automatic, blue = Non-Automatic
from matplotlib.lines import Line2D
legend_markers = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=fire_colors['Automatic'],
           markersize=8, label='Automatic'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=fire_colors['Non-Automatic'],
           markersize=8, label='Non-Automatic'),
]
ax2.legend(handles=legend_markers, loc='lower right', fontsize=8, frameon=True)

plt.savefig('output.png', dpi=200, bbox_inches='tight')
