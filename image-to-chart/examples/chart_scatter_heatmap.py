"""Reproduction of Realchart2code-raw/1.png
2-panel figure: scatter (top) + correlation heatmap (bottom).

Source image: Valorant-style performance data.
- Top: KD vs ACS/Map, point size = Total Kills, color = Maps Played (viridis),
  red regression line annotated "Best fit line (R² = 0.669)".
- Bottom: 9x9 correlation heatmap with Reds colormap, annotated values.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
rng = np.random.default_rng(0)

# --- Top panel: scatter of KD vs ACS/Map ---
n = 80
kd = rng.normal(0.85, 0.18, n).clip(0.4, 1.4)              # x: Kill/Death ratio
acs = 150 + 100 * kd + rng.normal(0, 18, n)                # y: ACS/Map (linear in kd + noise)
maps_played = rng.integers(5, 35, n)                       # color
total_kills = rng.integers(80, 800, n)                     # size

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 9), constrained_layout=True)

sc = ax1.scatter(kd, acs, c=maps_played, s=10 + total_kills * 0.25,
                 cmap='viridis', alpha=0.8, edgecolor='white', linewidth=0.5)

# Regression line: a 0.669 R^2 line in roughly the data range
coef = np.polyfit(kd, acs, 1)
xs = np.array([0.4, 1.4])
ax1.plot(xs, np.polyval(coef, xs), 'r-', lw=1.5,
         label=f'Best fit line (R² = {np.corrcoef(kd, acs)[0, 1]**2:.3f})')

ax1.set_xlabel('Kill/Death Ratio (KD)')
ax1.set_ylabel('Average Combat Score per Map (ACS/Map)')
ax1.set_xlim(0.4, 1.4)
ax1.set_ylim(120, 260)
ax1.legend(loc='upper left', fontsize=9)
fig.colorbar(sc, ax=ax1, label='Maps Played')
ax1.set_title('Relationship between KD Ratio and ACS per Map\n'
              '(Point size = Total Kills, Color = Maps Played)',
              fontsize=10)

# --- Bottom panel: 9x9 correlation heatmap ---
# Synthesize 9 variables with a similar correlation structure as the source.
labels = ['K', 'D', 'A', 'KD', 'KDA', 'ACS/Map', 'K/Map', 'D/Map', 'A/Map']
n_vars = len(labels)
n_samples = 200
data = rng.normal(size=(n_samples, n_vars))
# Inject correlations so the heatmap has visible structure
data[:, 1] = 0.97 * data[:, 0] + 0.1 * rng.normal(size=n_samples)            # D ~ K
data[:, 2] = 0.87 * data[:, 0] + 0.2 * rng.normal(size=n_samples)            # A ~ K
data[:, 3] = -0.55 * data[:, 0] + 0.4 * rng.normal(size=n_samples)           # KD ~ -K
data[:, 4] = -0.6  * data[:, 0] + 0.5 * rng.normal(size=n_samples)           # KDA ~ -K
data[:, 5] = -0.4  * data[:, 0] + 0.7 * rng.normal(size=n_samples)           # ACS/Map ~ -K
data[:, 6] = -0.5  * data[:, 0] + 0.6 * rng.normal(size=n_samples)           # K/Map ~ -K
data[:, 7] = 0.1   * data[:, 0] + 0.99 * rng.normal(size=n_samples)          # D/Map independent
data[:, 8] = 0.3   * data[:, 0] + 0.9  * rng.normal(size=n_samples)          # A/Map partly K
corr = np.corrcoef(data.T)

sns.heatmap(corr, ax=ax2,
            annot=True, fmt='.2f',
            cmap='Reds',                       # sequential (per source image)
            vmin=-0.6, vmax=1.0,
            xticklabels=labels, yticklabels=labels,
            cbar_kws={'label': 'Correlation'},
            square=True, linewidths=0.5, linecolor='white',
            annot_kws={'size': 8})
ax2.set_title('Correlation Matrix of Valorant Performance Metrics', fontsize=10)
ax2.set_xlabel('Performance Metrics', fontsize=9)
ax2.set_ylabel('Performance Metrics', fontsize=9)
plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
plt.setp(ax2.get_yticklabels(), rotation=0)

plt.savefig('output.png', dpi=200, bbox_inches='tight')
