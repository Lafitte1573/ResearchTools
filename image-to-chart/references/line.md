# Line / multi-series / area

Line charts show how a value changes over a continuous axis — most often time, sometimes position or some other ordering. The chart is built from `(x, y)` pairs connected by line segments, optionally with markers at the data points and shaded regions underneath.

## Canonical example: multi-series line with shaded confidence band

This is the workhorse plot of ML papers — a training curve with mean ± std shaded:

```python
import numpy as np
import matplotlib.pyplot as plt

epochs = np.arange(1, 51)
np.random.seed(0)

# Three methods, each with mean + std across 5 seeds
def curve(loc, scale):
    mean = 0.3 + 0.7 * (1 - np.exp(-epochs / 10)) + np.random.normal(0, 0.02, len(epochs))
    std  = 0.05 * np.exp(-epochs / 30) + 0.02
    return mean, std

m1_mean, m1_std = curve(0.7, 0.05)
m2_mean, m2_std = curve(0.8, 0.04)
m3_mean, m3_std = curve(0.9, 0.03)

fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
ax.plot(epochs, m1_mean, '-',  color='#4C72B0', label='Method 1', lw=1.5)
ax.fill_between(epochs, m1_mean - m1_std, m1_mean + m1_std,
                color='#4C72B0', alpha=0.2)

ax.plot(epochs, m2_mean, '--', color='#DD8452', label='Method 2', lw=1.5)
ax.fill_between(epochs, m2_mean - m2_std, m2_mean + m2_std,
                color='#DD8452', alpha=0.2)

ax.plot(epochs, m3_mean, '-.', color='#55A868', label='Method 3', lw=1.5)
ax.fill_between(epochs, m3_mean - m3_std, m3_mean + m3_std,
                color='#55A868', alpha=0.2)

ax.set_xlabel('Epoch')
ax.set_ylabel('Validation Accuracy')
ax.set_xlim(1, 50)
ax.legend()
ax.grid(linestyle=':', alpha=0.5)
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Three things to notice:

1. **Line styles differentiate series.** The three methods use `'-'`, `'--'`, `'-.'`. Color alone is not always enough (papers must print in B&W too, and colorblind readers will struggle). The source image will tell you which line style was used.
2. **`fill_between` takes the lower and upper bound as separate args**, not a single "error" array. The fill color matches the line color, with `alpha=0.2` for a soft band.
3. **`np.exp(-epochs / 10)` is a common shape for "rises quickly then plateaus"** — useful when the source curve has that asymptotic look. If the source is more S-shaped, use a logistic; if it's a straight line, use linear interpolation.

## Multiple series in one `plot()` call

If you have many series with the same x-axis (e.g. one curve per method in a benchmark), it can be cleaner to use a single call:

```python
for name, (mean, std) in [('M1', (m1_mean, m1_std)), ('M2', (m2_mean, m2_std))]:
    ax.plot(epochs, mean, label=name, lw=1.5)
    ax.fill_between(epochs, mean - std, mean + std, alpha=0.2)
```

This produces the same chart but is easier to extend. The legend entry per series comes from the `label=` argument.

## Markers

If the source image shows dots at each data point, add `marker='o'` (or `'s'`, `'^'`, `'D'`, etc.) to the `plot` call:

```python
ax.plot(x, y, '-o', color='C0', lw=1, markersize=4)
```

The format string `'-o'` means "solid line, circle marker". Other combinations: `'--s'` (dashed + square), `':^'` (dotted + triangle), `'-.'` (dash-dot, no marker).

If there are only 5-10 data points, the markers carry most of the information and the line is just a guide. If there are 1000+ points, drop the markers — they overlap and look like noise.

## Area chart (filled line)

When the area under the line is filled all the way to zero (not just to a band), use `fill_between(x, y, 0)`:

```python
ax.fill_between(years, sales, 0, color='#4C72B0', alpha=0.4)
ax.plot(years, sales, color='#4C72B0', lw=2)  # outline on top
```

The order matters: fill first, then draw the outline. Otherwise the line is hidden by the fill.

Stacked area: same pattern with `fill_between(x, y_lower, y_upper)` where `y_lower` and `y_upper` are cumulative sums.

## Step plot

If the source image shows a piecewise-constant line (jumps, not slopes), use `step`:

```python
ax.step(x, y, where='post', color='C0', lw=1.5)
```

`where='post'` means the y-value changes at each x and stays constant until the next x. `where='pre'` does the opposite. `where='mid'` puts the step in the middle of each x-interval. The source image will tell you which one — look at whether the line jumps at the data points or between them.

## Pitfalls

- **Y-axis doesn't start at 0.** For a line chart, this is sometimes acceptable (a tiny dip might be important) but it visually exaggerates differences. Default to including 0 unless the source clearly doesn't.
- **X-axis is treated as numeric even when it's categorical.** If the x-axis is "Q1, Q2, Q3, Q4" or "Monday, Tuesday, ..." and you plot with those as strings, matplotlib will treat them as evenly-spaced numbers — and the spacing will be wrong if the order is alphabetical. Convert to `pd.Categorical(...).codes` or to integer positions with explicit tick labels.
- **The line is over the wrong band.** If you plot a `fill_between` band and then plot a single line, by default matplotlib draws them in the order you called. To make sure the line sits on top, pass `zorder=3` to the `plot` call (and `zorder=2` to the `fill_between`).
- **Too many series.** If the source image shows 20+ lines, the chart is unreadable anyway. Pick 4-6 representative ones and add a "(others omitted)" note.
- **The legend labels are in plot order.** When you call `ax.plot` 5 times, the legend follows that order. If you reorder, the legend reorders too — no extra work needed.

## When to use this reference

- The chart shows a continuous line (or lines) connecting points.
- The x-axis is continuous (time, position, iteration number, etc.).
- There is a clear "trend" or "over time" feel.

If the lines cross, you might be looking at a **multi-line with categorical series** — same machinery, but the legend groups them. If the lines have no markers and the y-axis is a density, you might be looking at a **KDE** — see `distribution.md`.
