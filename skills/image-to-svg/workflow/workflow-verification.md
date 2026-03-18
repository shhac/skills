# Verification: Measurement and Programmatic Comparison

Visual comparison by the LLM is a vibe check — it catches catastrophic failures but passes subtle proportion and curvature errors. This file covers the programmatic pipeline that finds errors precisely.

**The core principle:** ImageMagick finds WHERE the errors are; you interpret them and know HOW to fix the SVG. Play to each tool's strengths.

## Prerequisites

Ensure ImageMagick is available:
```bash
command -v magick || echo "Install with: brew install imagemagick (macOS) or apt install imagemagick (Linux)"
```

## Phase 1: Measuring Feature Coordinates

**Do not eyeball coordinates.** Small estimation errors compound across features and ruin proportions.

### Step 1: Get image dimensions and compute scale factor

```bash
# Get original image dimensions
magick identify -format "%w %h" original.png

# Compute scale factor to canvas (e.g., 512x512)
# If original is 2816x1536 and canvas is 512x512:
# scale_x = 512 / 2816 = 0.1818
# scale_y = 512 / 1536 = 0.3333
# Use the smaller scale to preserve aspect ratio, then center
```

### Step 2: Measure the subject's bounding box

```bash
# Trim to non-background pixels and get bounding box
# The +0+0 at the end is the offset from the original top-left
magick original.png -fuzz 10% -trim -format "%wx%h%O" info:
```

This tells you where the actual subject sits within the image. Map these coordinates to canvas space using the scale factor.

### Step 3: Establish proportion anchors

After cropping features, measure key reference points:

```bash
# Measure where a feature sits in the original
# Example: find the top of the hat
magick refs/hat.png -trim -format "width:%w height:%h offset:%O" info:
```

Express proportions as **ratios of the subject height**, not absolute pixels:
- "Head center at 30% of subject height"
- "Chin at 50%"
- "Feet at 95%"
- "Head width is 40% of subject width"

These ratios are more robust than pixel estimates and survive canvas remapping.

### Step 4: Build the feature map

Record measured coordinates and ratios in a structured format that agents can use:

```
Canvas: 512x512
Subject bounding box (canvas coords): x:80 y:10 w:352 h:492

Proportion anchors:
- Hat top: y=10 (2% of subject height)
- Eye line: y=168 (33%)
- Chin: y=268 (53%)
- Feet bottom: y=502 (98%)
- Subject center x: 256

Feature map:
- hat:       x:108 y:10  w:296 h:126  z:7
- face:      x:128 y:100 w:256 h:200  z:3
- left-eye:  x:160 y:148 w:70  h:60   z:4
- right-eye: x:270 y:148 w:70  h:60   z:4
- mouth:     x:185 y:220 w:140 h:50   z:5  [expression-critical]
- ...
```

## Per-Feature Verification: The Diff Loop

After each SVG iteration, run this pipeline instead of (or in addition to) visual comparison.

### Step 1: Render the feature SVG

```bash
rsvg-convert -w 512 -h 512 parts/{feature}.svg -o parts/{feature}.png
```

### Step 2: Extract the feature's region from the rendered PNG

Crop the rendered full-canvas PNG to the feature's bounding box so it matches the reference crop dimensions:

```bash
magick parts/{feature}.png -crop {w}x{h}+{x}+{y} +repage /tmp/{feature}-rendered-crop.png
```

### Step 3: Resize the reference crop to match

The reference crop from the original image may be at a different resolution. Resize to match:

```bash
magick refs/{feature}.png -resize {w}x{h}! /tmp/{feature}-ref-resized.png
```

### Step 4: Generate visual diff and numerical score

```bash
# Visual diff — red highlights show differences
magick compare /tmp/{feature}-ref-resized.png /tmp/{feature}-rendered-crop.png /tmp/{feature}-diff.png

# Numerical similarity score (lower = more similar)
magick compare -metric RMSE /tmp/{feature}-ref-resized.png /tmp/{feature}-rendered-crop.png null: 2>&1
```

### Step 5: Read the diff image

Read `/tmp/{feature}-diff.png`. Red/bright areas show where the SVG diverges from the reference. Use this to direct your corrections:
- Red along the top edge → the shape is too short/tall
- Red on one side → the shape is shifted or asymmetric
- Red in the interior → color or gradient mismatch
- Red at the outline → curvature or thickness doesn't match

### Step 6: Iterate

Fix the top issue from the diff, re-render, re-diff. Track whether the RMSE score is decreasing. If it stops improving after a fix, the remaining differences may be acceptable or require a different construction approach.

### Silhouette comparison (shape-focused)

When you want to isolate shape errors from color errors:

```bash
# Convert both to black silhouettes on white
magick /tmp/{feature}-ref-resized.png -threshold 50% /tmp/{feature}-ref-silhouette.png
magick /tmp/{feature}-rendered-crop.png -threshold 50% /tmp/{feature}-rendered-silhouette.png

# Diff the silhouettes
magick compare /tmp/{feature}-ref-silhouette.png /tmp/{feature}-rendered-silhouette.png /tmp/{feature}-shape-diff.png
```

Shape is harder to get right and more impactful than color — use this when proportions feel off.

## Composite Verification

After assembling the composite, diff the entire result against the original.

### Full-image diff

```bash
# Render composite
rsvg-convert -w 512 -h 512 final.svg -o wip.png

# Resize original to match canvas
magick original.png -resize 512x512 /tmp/original-resized.png

# Generate diff
magick compare /tmp/original-resized.png wip.png /tmp/composite-diff.png

# Numerical score
magick compare -metric RMSE /tmp/original-resized.png wip.png null: 2>&1
```

### Reading the composite diff

Read `/tmp/composite-diff.png` and identify the **top 3 areas** with the most red/bright pixels. These are your priority fixes. Common patterns:

- **Entire feature is shifted** — the bounding box was wrong; adjust position in the composite
- **One feature is the wrong size** — proportion error; rebuild at correct scale
- **Expression is off** — mouth curvature, eye position; send back to the feature agent with the diff image as guidance
- **Colors don't match** — wrong fill values; compare hex codes directly

### Convergence

Track the RMSE score across composite iterations. The goal isn't zero (pixel-perfect matching is impossible and unnecessary), but the score should decrease with each fix and stabilize. When two consecutive iterations produce similar scores, the remaining differences are likely acceptable.

## When Programmatic Diff Isn't Available

If ImageMagick isn't installed and can't be installed, fall back to visual comparison — but be extra rigorous:

1. Read both images at the same time
2. Focus on **proportions first** — relative sizes, spacing, alignment
3. Check specific measurements: "Is the mouth width at least 60% of the face width?"
4. Use the original image as ground truth, not your mental model of what it should look like
5. Compare specific regions rather than the whole image at once

Visual comparison is better than nothing, but it will miss the subtle errors that programmatic diff catches. Flag this to the user if ImageMagick is unavailable.
