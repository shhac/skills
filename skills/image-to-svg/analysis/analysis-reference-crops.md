# Creating Reference Crops

Tight crops of individual features from the original image are essential. Without them, you'll work from a vague memory of what the feature looks like, and the result will be "conceptually similar" rather than accurate.

## Why Crops Matter

- Forces you to actually LOOK at the specific feature rather than the whole image
- Reveals details you miss at full zoom: outline thickness variation, color subtleties, highlight positions
- Provides a direct comparison target when iterating on your SVG
- Prevents other features from "distracting" your understanding

## The Feature Locations File

**All crop coordinates live in `feature-locations.yml`.** This file is the single source of truth for where every feature is in the original image. Crops are generated from it, and when a crop is wrong, you fix the numbers in the YAML and re-run — no re-estimating from the image.

### Step 1: Get image dimensions

```bash
magick identify -format "%w %h" original.png
```

### Step 2: Write `feature-locations.yml`

Study the original image and estimate bounding boxes for each feature. Record them as `x, y, width, height` in original image pixel coordinates, where `x, y` is the **top-left corner** of the crop region.

**The feature should dominate its crop.** Aim for the feature to occupy roughly 50-70% of the crop area, with 15-20% margin on each side. This means:

- **Too tight:** feature touches or is clipped at edges (< 5% margin on any side). Clipped crops are useless — the agent literally can't see what's cut off.
- **Just right:** feature is the clear star of the image, with enough surrounding context to judge position relative to neighbors. 15-20% margin on each side.
- **Too loose:** feature is a small element in a sea of surrounding image (< 30% of crop area). This is bad for two reasons: (1) trace metadata extraction picks up colors and shapes from neighboring features, polluting the palette; (2) the agent's reference is noisy — the eye shouldn't share its crop with the hat and other eye.

When in doubt, err slightly loose rather than tight — but not dramatically. A crop where the feature occupies 40% of the area is fine. A crop where it occupies 10% is too loose.

```yaml
# feature-locations.yml
# Bounding boxes in original image coordinates (pixels)
# Format: [x, y, width, height] where x,y is the top-left corner

image: original.png
dimensions: [2816, 1536]  # width, height — from magick identify

features:
  head-full:
    box: [800, 100, 1200, 1300]
    description: "entire head including hat, ears, chin"

  hat:
    box: [850, 100, 1100, 500]
    description: "hat in isolation, full brim and how it sits on head"

  left-eye:
    box: [1050, 500, 300, 250]
    description: "left eye with surrounding face context"

  right-eye:
    box: [1450, 500, 300, 250]
    description: "right eye with surrounding face context"

  nose:
    box: [1250, 650, 300, 250]
    description: "nose with surrounding context"

  mouth:
    box: [1100, 850, 600, 300]
    description: "mouth with surrounding context"

  left-ear:
    box: [750, 400, 350, 400]
    description: "left ear with head/hat context"

  right-ear:
    box: [1700, 400, 350, 400]
    description: "right ear with head/hat context"
```

**What to include per feature:**

For a character face:
- `head-full` — entire head including hat, ears, chin (wide crop)
- `left-eye` / `right-eye` — each eye with surrounding face (do NOT assume symmetry)
- `nose` — nose with surrounding context
- `mouth` — mouth with surrounding context
- `left-ear` / `right-ear` — each ear with some head/hat context
- `hat` — hat in isolation, including the full brim and how it sits on the head
- Any other distinct features (hair, accessories, etc.)

### Step 3: Crop all features from the YAML

```bash
# Read feature-locations.yml and crop each feature
# Using a simple parser since yq may not be available
python3 -c "
import yaml, subprocess, pathlib
pathlib.Path('refs').mkdir(exist_ok=True)
with open('feature-locations.yml') as f:
    data = yaml.safe_load(f)
image = data['image']
for name, info in data['features'].items():
    x, y, w, h = info['box']
    cmd = ['magick', image, '-crop', f'{w}x{h}+{x}+{y}', '+repage', f'refs/{name}.png']
    subprocess.run(cmd, check=True)
    print(f'  cropped refs/{name}.png ({w}x{h} at +{x}+{y})')
print(f'Done: {len(data[\"features\"])} crops')
"
```

If Python with PyYAML is not available, crop manually with ImageMagick:

```bash
# Fallback: crop each feature individually from the YAML values
magick original.png -crop WIDTHxHEIGHT+X+Y +repage refs/feature-name.png
```

### Step 4: Verify crops (automated + visual)

See "Verifying Crops" below. Any crop that fails gets fixed by **editing the numbers in `feature-locations.yml`** and re-running step 3.

### Why This Matters

Without the YAML file, the agent estimates coordinates, runs a crop command, and the numbers are lost. If the crop is wrong, the agent re-estimates from scratch — often making the same error. With `feature-locations.yml`:

- The coordinate estimation step is **explicit and reviewable**
- When a crop fails, you adjust one number and re-run — no re-guessing
- The YAML becomes the foundation for the feature map (canvas coordinates come from scaling these)
- The verify→fix→re-crop loop is fast: edit a number, run the script, check the result

## Verifying Crops

**This is the most common failure point in the entire workflow.** Bad crops produce bad SVGs. Every minute spent verifying crops saves ten minutes of iteration later.

### Step 1: Programmatic clipping + tightness check

Run this on every crop. It checks two things:
- **Clipping** — is the feature cut off at any edge? (margin < 5% on any side)
- **Tightness** — does the feature dominate its crop? (feature should fill at least 30% of crop area)

Both problems are common and both degrade quality — clipping loses content, looseness pollutes trace metadata with neighboring features' colors and shapes.

```bash
# Automated clipping + tightness check for all crops:
for f in refs/*.png; do
  name=$(basename "$f")
  dims=$(magick identify -format "%w %h" "$f")
  w=${dims% *}; h=${dims#* }
  min_h=$((w * 5 / 100))  # 5% of width
  min_v=$((h * 5 / 100))  # 5% of height
  # Get margins AND trimmed content dimensions
  info=$(magick "$f" -fuzz 10% -trim -format "%X %Y %[fx:page.width-w-page.x] %[fx:page.height-h-page.y] %w %h" info:)
  read l t r b tw th <<< "$info"
  l=${l%.*}; t=${t%.*}; r=${r%.*}; b=${b%.*}; tw=${tw%.*}; th=${th%.*}
  # Check clipping (too tight)
  clip=""
  [ "$l" -lt "$min_h" ] 2>/dev/null && clip="${clip} left=${l}"
  [ "$t" -lt "$min_v" ] 2>/dev/null && clip="${clip} top=${t}"
  [ "$r" -lt "$min_h" ] 2>/dev/null && clip="${clip} right=${r}"
  [ "$b" -lt "$min_v" ] 2>/dev/null && clip="${clip} bottom=${b}"
  # Check tightness (too loose) — feature area vs crop area
  feat_pct=$((tw * th * 100 / (w * h)))
  loose=""
  [ "$feat_pct" -lt 30 ] 2>/dev/null && loose=" feature=${feat_pct}% of crop (want >=30%)"
  # Report
  if [ -n "$clip" ]; then
    echo "CLIP $name:$clip (min_h=${min_h}px min_v=${min_v}px)"
  elif [ -n "$loose" ]; then
    echo "LOOSE $name:$loose — crop tighter around the feature"
  else
    echo "PASS $name: L=${l} T=${t} R=${r} B=${b} feature=${feat_pct}%"
  fi
done
```

- **CLIP** = feature is cut off. Fix: extend the crop on the failing side.
- **LOOSE** = feature is a small part of the crop. Fix: tighten the crop around the feature. A loose crop means trace metadata will pick up colors and shapes from neighboring features, and the agent's reference is noisy.
- **PASS** = margins are adequate and feature dominates the crop.

**Do not skip this step.**

### Step 2: Fix failing crops via the YAML

When a crop fails:

**For CLIP failures:**
1. **Identify which side failed** — the output tells you (e.g., `top=3` means the top margin is only 3px)
2. **Open `feature-locations.yml`** and adjust the bounding box:
   - Top clipped → decrease `y` and increase `height` (extend upward)
   - Bottom clipped → increase `height` (extend downward)
   - Left clipped → decrease `x` and increase `width` (extend left)
   - Right clipped → increase `width` (extend right)
   - **Extend by at least 50% more than the current margin on the failing side**

**For LOOSE failures:**
1. The feature occupies too little of the crop — surrounding content dominates
2. **Open `feature-locations.yml`** and tighten the bounding box:
   - Increase `x` and decrease `width` (narrow horizontally)
   - Increase `y` and decrease `height` (narrow vertically)
   - Center the box on the feature, aiming for 15-20% margin on each side
3. Be careful not to over-tighten into a CLIP — check again after adjusting
3. **Re-run the crop script** (step 3 above) — it re-crops everything from the YAML
4. **Re-run the margin check** — repeat until all crops pass

This loop is fast because you're editing numbers, not re-estimating from the image.

### Step 3: Visual verification — ONE crop at a time

After the programmatic check passes, verify each crop visually. **Read each crop individually** — do NOT batch multiple crops into a single Read call. Batching causes you to scan quickly and miss problems.

For EACH crop, read it and confirm:

1. **Is the ENTIRE feature visible?** No part of the subject clipped at any edge. The most common errors:
   - Eye tops cut off by hat brim (the crop captured the brim but not enough face below/above)
   - Ear bases clipped where they connect to the face
   - Hat brim bottom edge not visible
   - Chin cut off at bottom
2. **Is there visible margin on ALL FOUR sides** between the feature and the crop boundary? If the feature touches any edge, re-crop wider.
3. **Does the feature dominate the crop?** It should be the clear primary subject — centered, prominent, filling most of the frame. If you can see more of neighboring features than the target feature, the crop is too loose. A "left eye" crop shouldn't include the hat, the other eye, and half the mouth.
4. **Is the image large enough** to see detail (at least 200x200px)?
5. **Does the crop include some neighboring context** to judge relative positioning? Some context is good (the brow above an eye, the cheek beside a nose), but the target feature should dominate.

If any crop fails visual verification, fix it via the YAML (step 2 above) and re-verify.

### Common Cropping Failures

| Failure | Why It Happens | YAML Fix |
|---|---|---|
| Eye top clipped by hat brim | `y` too low, `height` too small | Decrease `y` by 50-100px, increase `height` to match |
| Ear base clipped | `height` too small, didn't extend to face-ear connection | Increase `height` by 30-50% |
| Hat brim bottom clipped | Focused on dome, forgot brim sits lower | Increase `height` to include brim + margin below |
| Feature tiny in corner | `x,y` centered on wrong point | Re-center: adjust `x,y` to the feature's actual center minus half of `width,height` |
| Assumed crop was fine without viewing | Skipped visual verification | ALWAYS verify each individual crop |

### The "View Every Single One" Rule

This means:
- Read `refs/left-eye.png` → check it → confirm or fix YAML and re-crop
- Read `refs/right-eye.png` → check it → confirm or fix YAML and re-crop
- Read `refs/left-ear.png` → check it → confirm or fix YAML and re-crop
- ... and so on for EVERY crop

**Not** "read 4 crops at once and scan quickly." The purpose is to spend 5-10 seconds per crop evaluating against the criteria above. This feels slow but it prevents the most common source of quality loss in the entire pipeline.

**A reference crop that's missing part of the subject will produce an SVG that's missing that same part.** This is not recoverable later — the agent building from this crop literally cannot see what's been cut off.
