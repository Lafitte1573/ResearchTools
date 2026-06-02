# Styling

Cross-cutting style choices that apply to every chart type: theme, palette, font, axis scale, gridlines, and the final layout. The same data can look very different depending on these choices.

## Seaborn themes

The single most important styling decision. Pick one at the top of the script and stick with it:

```python
import seaborn as sns
sns.set_theme(style='whitegrid')   # default for most research figures
# OR
sns.set_theme(style='darkgrid')    # dark background, white gridlines
# OR
sns.set_theme(style='white')       # no gridlines, no background tint
# OR
sns.set_theme(style='dark')        # dark background, no gridlines
# OR
sns.set_theme(style='ticks')       # ticks on all 4 sides, no grid
```

`whitegrid` is the safest default — it gives a clean white background with subtle horizontal gridlines that don't compete with the data. `darkgrid` is good for presentations on a dark background but doesn't print well.

**Important:** call `sns.set_theme()` BEFORE `plt.subplots()`. Seaborn sets some default rcParams that affect newly created axes, not existing ones.

## Color palettes

The default seaborn palette (used when you call `sns.set_theme()` without specifying one) is a muted set of 6 colors:

```python
['#4C72B0',  # blue
 '#DD8452',  # orange
 '#55A868',  # green
 '#C44E52',  # red
 '#8172B3',  # purple
 '#937860']  # brown
```

These are research-paper standard. If the source image has a different palette, override:

```python
# Discrete palette of 4 colors from ColorBrewer
sns.set_palette(['#1b9e77', '#d95f02', '#7570b3', '#e7298a'])

# Sequential (for heatmaps, ordered categories)
sns.set_palette('viridis')

# Diverging (for correlations, signed values)
sns.set_palette('RdBu_r')
```

The palette can also be passed per-call: `sns.scatterplot(..., palette='tab10')`, `sns.barplot(..., palette='muted')`. The most common palettes you'll see in papers:

- `tab10` — bright primary colors (matplotlib default)
- `muted` — softer than tab10, good for line plots
- `deep` — slightly darker, the default for `sns.set_theme()`
- `pastel` — light tones, good for stacked bars with transparency
- `colorblind` — colorblind-friendly

## Fonts

For Latin scripts, the default is fine. For non-Latin (Chinese, Japanese, Korean, etc.):

```python
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
```

The compile script does NOT auto-detect this — you have to set it explicitly. Without it, Chinese characters render as empty boxes.

For specific font sizes:

```python
sns.set_theme(style='whitegrid', rc={
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
})
```

## Axis scale

Default is linear. Switch to log when the source has tick labels like `10⁰, 10¹, 10², 10³`:

```python
ax.set_yscale('log')
ax.set_xscale('log')
```

With log scale, the y-axis starts at 1, not 0. Don't try to set `ylim(0, ...)` — it will raise an error or look wrong.

For "1, 10, 100, 1000" tick labels, you can also set log-scale ticks explicitly:

```python
from matplotlib.ticker import LogLocator, FuncFormatter
ax.yaxis.set_major_locator(LogLocator(base=10))
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{int(y)}'))
```

## Tick rotation

Long category names on the x-axis need rotation:

```python
ax.set_xticklabels(labels, rotation=45, ha='right')
# OR
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
```

`ha='right'` aligns the right edge of the label to the tick, so the rotated text doesn't drift left of the tick. For 90° rotation, use `rotation=90, ha='center'`.

For multi-line labels, embed a newline:

```python
labels = ['Method A\n(year)', 'Method B\n(year)', ...]
```

This is cleaner than rotation when the labels are short enough to break.

## Gridlines

Disable gridlines (the whitegrid theme has horizontal ones by default):

```python
ax.grid(False)
# OR per-axis
ax.yaxis.grid(False)
ax.xaxis.grid(True)
```

Add custom gridlines:

```python
ax.grid(True, axis='y', linestyle=':', alpha=0.5, color='gray')
```

`linestyle=':'` (dotted) is more subtle than `'-'` (solid). `alpha=0.5` makes them less prominent.

## Removing spines

The top and right spines (axis lines) are usually noise. Remove them:

```python
sns.despine(ax=ax, top=True, right=True)   # default
sns.despine(ax=ax, top=True, right=True, left=True, bottom=True)  # all four
```

This is a stylistic choice; some research figures keep all four spines, especially in older papers. Default to removing top + right.

## Subplot alignment

When multiple panels need to align (e.g. share an x-axis at the same scale), use `sharex=True` (see `multi-panel.md`). The y-tick labels are aligned automatically.

For tight spacing between panels:

```python
fig.subplots_adjust(hspace=0.3, wspace=0.3)
```

Or use `constrained_layout=True` (recommended; it does this and more).

## Saving

Always end the script with:

```python
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

- `dpi=200` — good resolution for a 6×4 inch figure (1200×800 px). For publication, use 300+ dpi.
- `bbox_inches='tight'` — trims whitespace around the figure. Without it, the saved PNG has a lot of empty border.

NEVER use `plt.show()` in a script — it blocks in headless mode. The compile script greps for `plt.show()` and warns.

## Pitfalls

- **Calling `sns.set_theme()` after `plt.subplots()`.** The subplots are already created with the old theme. Move the `set_theme` call to the top of the file.
- **Mixing seaborn's `palette` argument with hex colors in the same script.** Seaborn's `palette` cycles through named colors; if you also pass `color='#4C72B0'` somewhere, the two will drift apart visually. Pick one approach and stick with it.
- **`bbox_inches='tight'` clipping the legend.** If a legend is outside the axes bbox, it may get clipped. Set `bbox_inches=None` and instead use `constrained_layout` + `bbox_extra_artists=[legend]` if you have a complex layout.
- **DPI mismatch.** If the source is at 200 dpi and you save at 100 dpi, the figure looks blurry. Match the source's effective resolution (or 200 as a default).
- **Chinese characters in PDF.** When saving to PDF (`plt.savefig('output.pdf')`), Chinese fonts may not embed. Use `plt.rcParams['pdf.fonttype'] = 42` to keep them as text. Or just save as PNG.

## Quick style template

For a typical research-paper look:

```python
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid', rc={
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
})

fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
# ... plot on ax ...
sns.despine(ax=ax)
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

This is a good starting point. Adjust the `figsize` and palette based on the source image.
