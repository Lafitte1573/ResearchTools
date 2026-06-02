# Bar

Bar charts encode a value as the length of a rectangle. They come in four flavors that all use the same primitives but render very differently:

- **Vertical bar** — categories on x-axis, value on y-axis (`plt.bar`)
- **Horizontal bar** — categories on y-axis, value on x-axis (`plt.barh`)
- **Stacked bar** — multiple series per category, stacked on top of each other (`bottom=`)
- **Lollipop** — a thin line + a marker instead of a thick bar (`plt.hlines` + `plt.scatter`)

The matplotlib primitives are the same in all four cases. The differences are the **orientation** and the **series-to-x-position** mapping.

## Canonical example: vertical grouped bar

This is the most common research-paper style. A few categories on the x-axis, with multiple series per category shown side-by-side:

```python
import numpy as np
import matplotlib.pyplot as plt

categories = ['Method A', 'Method B', 'Method C', 'Method D']
x = np.arange(len(categories))
width = 0.35

# Two series: train accuracy and test accuracy
train_acc = [82.3, 85.1, 87.9, 89.2]
test_acc  = [78.4, 83.7, 86.5, 88.1]

fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
ax.bar(x - width/2, train_acc, width, label='Train', color='#4C72B0')
ax.bar(x + width/2, test_acc,  width, label='Test',  color='#DD8452')

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_ylabel('Accuracy (%)')
ax.set_ylim(0, 100)
ax.legend()
ax.grid(axis='y', linestyle=':', alpha=0.5)
plt.savefig('output.png', dpi=200, bbox_inches='tight')
```

Two things to notice:

1. **The two bars per category are offset by `width/2`**. The first series sits at `x - width/2`, the second at `x + width/2`, with `width` controlling the bar thickness. If you forget the offset, the two series overlap and you only see one.
2. **Colors are sampled from seaborn's default palette** (`#4C72B0`, `#DD8452`, etc.) but written as hex codes. This is what a typical research paper looks like.

## Horizontal bar (`barh`)

When the category labels are long or there are many categories, the bars go horizontal:

```python
fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
y = np.arange(len(categories))
ax.barh(y, values, color='#4C72B0')
ax.set_yticks(y)
ax.set_yticklabels(categories)
ax.invert_yaxis()    # <-- the first item appears on TOP, not bottom
ax.set_xlabel('Score')
```

**Critical pitfall**: by default matplotlib puts the **first** y-tick at the **bottom**. If the source image shows the first category at the top (which is what almost every paper does), you must call `ax.invert_yaxis()` or the chart will read bottom-to-top. This is the single most common horizontal-bar bug.

Also: in `barh`, the size argument is `height=`, not `width=`. If you copy a vertical bar and just rename to `barh`, the bars will be thin lines.

## Stacked bar

Multiple series per category, stacked into one column:

```python
fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
ax.bar(x, s1, label='Group 1', color='#4C72B0')
ax.bar(x, s2, bottom=s1, label='Group 2', color='#DD8452')  # <-- bottom=
ax.bar(x, s3, bottom=np.array(s1) + np.array(s2), label='Group 3', color='#55A868')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
```

The `bottom=` parameter is the key. Each subsequent series is drawn on top of the sum of all previous ones. If you forget `bottom=`, the second series will cover the first.

For horizontal stacked bars, use `left=` instead of `bottom=`.

## Lollipop

When the bar chart has many categories and the bars look like thin sticks with a dot at the end, you have a lollipop chart. Built from `hlines` + `scatter`:

```python
fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
y = np.arange(len(categories))
values = [3.2, 5.1, 2.8, 6.4, 4.7]

ax.hlines(y, 0, values, color='gray', lw=1.5)         # the stick
ax.scatter(values, y, color='#4C72B0', s=80, zorder=3) # the candy
ax.set_yticks(y)
ax.set_yticklabels(categories)
ax.invert_yaxis()  # first category on top, like a horizontal bar
ax.set_xlabel('Value')
```

`zorder=3` on the scatter makes sure the dot sits on top of the line. Without it, the line can draw over the dot and you get a "candy with a stick through it".

## Pitfalls

- **Wrong y-axis baseline.** Bars always start at 0. If you set `ax.set_ylim(50, 100)`, the bar chart will visually lie — a 60% bar and a 90% bar will look the same size. Use `ax.set_ylim(0, ...)` or omit the lower bound.
- **Bar order in a `barh` is bottom-up by default.** Most papers show top-down. Fix with `ax.invert_yaxis()`.
- **Grouped bars overlap if you forget the x-offset.** Two `ax.bar(x, ...)` calls with no offset will draw one bar on top of the other; you'll only see the second series. Always offset by `±width/2` for two series.
- **Stacked bars need `bottom=` (or `left=`).** Forgetting this gives you overlapping bars instead of a stack.
- **Long category labels collide.** For 5+ categories with multi-word labels, switch to `barh` (horizontal). Don't rotate x-tick labels 90° — it makes them hard to read.
- **Color order doesn't match the legend.** When you call `ax.bar(...)` for each series, the legend follows the order you called them in. Don't pass `color=` in random order — pass it consistently.

## When to use this reference

- The chart shows rectangles of varying length (or height).
- Categories are discrete (e.g. method names, group names, time periods).
- The values are bounded and ordered (e.g. accuracy, count, score).

If the rectangles are filled with a gradient or color-encodes a value, you might be looking at a **heatmap** instead. If the chart is a single tall rectangle showing a distribution, it's a **histogram** — see `distribution.md`.
