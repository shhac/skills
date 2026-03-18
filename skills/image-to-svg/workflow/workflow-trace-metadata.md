# Trace Metadata Extraction

Auto-trace each feature crop with VTracer in polygon mode to extract structured metadata: color palettes, sub-element positions, sizes, and topology. This gives agents precise numeric data instead of requiring them to eyeball colors and positions from the raster image.

**This step is an enhancement, not a requirement.** If VTracer is not available, fall back to ImageMagick color extraction (see "Fallback" below).

## Why Polygon Mode

VTracer's polygon mode (`--mode polygon`) uses `L` (lineto) commands instead of `C` (curveto). The output is 4x more token-efficient and the paths are human-readable. Since agents rewrite from scratch using clean Bézier construction, the polygon approximation is fine — we only need approximate shapes, not smooth curves.

## Step 1: Trace Each Crop

```bash
# Trace a single feature crop
vtracer --input refs/{feature}.png --output /tmp/{feature}-trace.svg \
  --mode polygon --color_precision 6 --filter_speckle 4
```

**Settings rationale:**
- `--mode polygon` — 4x fewer tokens than spline mode
- `--color_precision 6` — 64 levels per channel, accurate enough for hex extraction (within 1-3 hex digits of source)
- `--filter_speckle 4` — keeps small but meaningful details (highlights, shadows). Increase to 15-25 for crops with noise.

For a typical 300x300 feature crop with 5-9 color regions, this produces ~9 paths at ~400-500 tokens.

## Step 2: Extract Metadata

Parse the traced SVG to extract structured metadata. This is a lightweight XML parse — no rendering needed.

```python
#!/usr/bin/env python3
"""Extract structured metadata from a VTracer polygon trace."""
import re
import sys
import xml.etree.ElementTree as ET

def extract_trace_metadata(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Get canvas size from viewBox or width/height
    viewbox = root.get('viewBox', '').split()
    if len(viewbox) == 4:
        canvas_w, canvas_h = float(viewbox[2]), float(viewbox[3])
    else:
        canvas_w = float(root.get('width', 300))
        canvas_h = float(root.get('height', 300))

    elements = []
    paths = root.findall('.//svg:path', ns) or root.findall('.//path')

    for path in paths:
        fill = path.get('fill', '#000000')
        d = path.get('d', '')

        # Extract all coordinates from path data
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', d)]
        if len(nums) < 2:
            continue

        xs = nums[0::2]
        ys = nums[1::2]
        if not xs or not ys:
            continue

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        h = max_y - min_y
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        area_pct = (w * h) / (canvas_w * canvas_h) * 100

        elements.append({
            'fill': fill,
            'center': (round(cx), round(cy)),
            'size': (round(w), round(h)),
            'area_pct': round(area_pct, 1),
        })

    # Sort by area descending (background first, small details last)
    elements.sort(key=lambda e: e['area_pct'], reverse=True)

    # Detect background (largest element)
    bg = elements[0]['fill'] if elements else '#FFFFFF'

    # Detect cutouts (element fully contained within another of different color)
    # Simplified: flag elements whose bounding box is within a larger element
    for i, el in enumerate(elements):
        el['has_cutout'] = False
        for j, other in enumerate(elements):
            if i != j and other['area_pct'] < el['area_pct']:
                if (abs(other['center'][0] - el['center'][0]) < el['size'][0] / 2 and
                    abs(other['center'][1] - el['center'][1]) < el['size'][1] / 2):
                    el['has_cutout'] = True
                    break

    # Output
    palette = list(dict.fromkeys(e['fill'] for e in elements))
    print(f"canvas: {int(canvas_w)}x{int(canvas_h)}")
    print(f"background: {bg}")
    print(f"palette: {', '.join(palette)}")
    print(f"elements: {len(elements) - 1}")  # exclude background

    for i, el in enumerate(elements[1:], 1):
        cutout = " [has cutout]" if el['has_cutout'] else ""
        print(f"  {i}. {el['fill']} center=({el['center'][0]},{el['center'][1]}) "
              f"size={el['size'][0]}x{el['size'][1]} ({el['area_pct']}%){cutout}")

if __name__ == '__main__':
    extract_trace_metadata(sys.argv[1])
```

Save this script to the project directory as `extract-trace-metadata.py` and run it on each trace:

```bash
python3 extract-trace-metadata.py /tmp/{feature}-trace.svg
```

### Example Output

For a traced eye crop:

```
canvas: 300x300
background: #F4D0A9
palette: #F4D0A9, #FDFDFE, #3B82F5, #1F3B61, #010202, #CC8967, #F9F9FA
elements: 7
  1. #FDFDFE center=(150,130) size=161x111 (19.9%) [has cutout]
  2. #3B82F5 center=(150,130) size=111x81 (10.0%)
  3. #1F3B61 center=(150,126) size=45x45 (2.2%)
  4. #CC8967 center=(96,175) size=51x12 (0.7%)
  5. #CC8967 center=(206,175) size=51x12 (0.7%)
  6. #010202 center=(150,126) size=25x25 (0.7%)
  7. #F9F9FA center=(140,118) size=13x13 (0.2%)
```

An agent reading this immediately knows: "white sclera with a cutout (ring shape), blue iris 111x81 centered at (150,130), dark pupil 25x25, two symmetric brown shapes at x=96 and x=206 (lash lines), tiny white highlight at (140,118)."

## Step 3: Record in the Feature Map

Add the trace metadata to the feature map from Phase 1 step 6. Each feature's entry gains a `trace:` block:

```
- left-eye: x:160 y:148 w:70 h:60 z:4
  trace:
    palette: #F4D0A9, #FDFDFE, #3B82F5, #1F3B61, #010202, #CC8967, #F9F9FA
    elements: 7
      1. #FDFDFE center=(150,130) size=161x111 (19.9%) [has cutout]
      2. #3B82F5 center=(150,130) size=111x81 (10.0%)
      ...
```

This metadata travels with the agent alongside the raster crop, feature map, and instructions. ~130 tokens per feature.

## Batch Processing

Trace and extract metadata for all crops at once:

```bash
for crop in refs/*.png; do
  feature=$(basename "$crop" .png)
  echo "=== $feature ==="
  vtracer --input "$crop" --output "/tmp/${feature}-trace.svg" \
    --mode polygon --color_precision 6 --filter_speckle 4
  python3 extract-trace-metadata.py "/tmp/${feature}-trace.svg"
  echo ""
done
```

## Fallback: ImageMagick-Only Color Extraction

If VTracer is not available, extract colors using ImageMagick's k-means clustering:

```bash
# Extract 10 dominant colors from a feature crop
magick refs/{feature}.png -resize 200x200 -kmeans 10 -unique-colors txt: \
  | tail -n +2 | tr -s ' ' | cut -d' ' -f3

# If -kmeans is not available (ImageMagick < 7.1), use quantization:
magick refs/{feature}.png -resize 200x200 +dither -colors 10 -unique-colors txt: \
  | tail -n +2 | tr -s ' ' | cut -d' ' -f3
```

This gives accurate hex values but no spatial information (positions, sizes, topology). Agents will still need to estimate sub-element positions from the raster image.

## Fallback: Pixel Sampling for Specific Colors

When you need the exact color at a specific coordinate (e.g., "what color is the pixel at the center of the iris"):

```bash
# Sample color at a specific pixel coordinate
magick refs/{feature}.png -format "%[pixel:u.p{150,130}]" info:

# Get the hex value specifically
magick refs/{feature}.png -depth 8 -crop 1x1+150+130 +repage txt: | tail -1 | grep -oP '#[0-9A-Fa-f]{6}'
```

Use this to verify or refine colors from the trace metadata or k-means extraction.
