# Creating Reference Crops

Tight crops of individual features from the original image are essential. Without them, you'll work from a vague memory of what the feature looks like, and the result will be "conceptually similar" rather than accurate.

## Why Crops Matter

- Forces you to actually LOOK at the specific feature rather than the whole image
- Reveals details you miss at full zoom: outline thickness variation, color subtleties, highlight positions
- Provides a direct comparison target when iterating on your SVG
- Prevents other features from "distracting" your understanding

## The Feature Locations File

**All crop coordinates live in `feature-locations.yml`.** This file is the single source of truth for where every feature is in the original image. Crops are generated from it, and when a crop is wrong, you fix the numbers in the YAML and re-run — no re-estimating from the image.

The `scripts/crop-tool.py` script (bundled with this skill) handles all crop operations: grid overlay, batch cropping, bounding box visualization, and semantic adjustments (pan, scale, tighten). Copy it to the project directory or reference it from the skill location.

### Step 1: Generate a coordinate grid

Before estimating bounding boxes, generate a grid overlay on the original image. This gives you labeled pixel coordinates to reference:

```bash
python3 crop-tool.py grid original.png --step 100
```

This produces `original-grid.png` with red gridlines every 100px and coordinate labels. Read this image — it makes estimating bounding boxes much more accurate than guessing from the raw image. For high-resolution images (> 2000px), use `--step 200` or `--step 250` to keep the grid readable.

### Step 2: Write `feature-locations.yml`

Using the grid image as reference, estimate bounding boxes for each feature. Record them as `x, y, width, height` in original image pixel coordinates, where `x, y` is the **top-left corner** of the crop region.

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

### Step 3: Apply crops

```bash
python3 crop-tool.py crop feature-locations.yml
```

This reads every feature from the YAML and crops them all to `refs/`. Re-run this after any YAML changes.

**Optional: visualize bounding boxes** before cropping to spot obviously wrong boxes:

```bash
python3 crop-tool.py show feature-locations.yml
```

This draws all bounding boxes on the image with color-coded labels. Read the output image to verify boxes are roughly in the right place before spending time on individual crop verification.

If Python with PyYAML is not available, crop manually with ImageMagick using the YAML values:

```bash
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
python3 crop-tool.py check feature-locations.yml
```

- **CLIP** = feature is cut off. Fix: extend the crop on the failing side.
- **LOOSE** = feature is a small part of the crop. Fix: tighten the crop around the feature. A loose crop means trace metadata will pick up colors and shapes from neighboring features, and the agent's reference is noisy.
- **PASS** = margins are adequate and feature dominates the crop.

**Do not skip this step.**

### Step 2: Fix failing crops

Use the crop tool's semantic commands to adjust bounding boxes — no manual coordinate arithmetic needed:

**For CLIP failures** (feature cut off at an edge):

```bash
# Scale the box larger (grows from center) — percent or pixels
python3 crop-tool.py scale feature-locations.yml left-eye 30%
python3 crop-tool.py scale feature-locations.yml left-eye 80px

# Or pan it toward the clipped side
python3 crop-tool.py pan feature-locations.yml left-eye up 15%
python3 crop-tool.py pan feature-locations.yml left-eye up 50px
```

**For LOOSE failures** (feature is too small in the crop):

```bash
# Tighten the box (shrink from edges equally)
python3 crop-tool.py tighten feature-locations.yml left-eye 25%
python3 crop-tool.py tighten feature-locations.yml left-eye 60px
```

**After adjusting, re-crop and re-check:**

```bash
python3 crop-tool.py crop feature-locations.yml
python3 crop-tool.py check feature-locations.yml
```

Repeat until all crops pass. You can also edit `feature-locations.yml` directly if you prefer — the semantic commands just save the coordinate arithmetic.

**Quick reference:**

**Quick reference:**

| Problem | Command | What it does |
|---|---|---|
| Feature clipped at top | `pan ... up 15%` or `pan ... up 50px` | Moves box up |
| Feature clipped overall | `scale ... 30%` or `scale ... 80px` | Grows box from center |
| Feature too small in crop | `tighten ... 25%` or `tighten ... 60px` | Shrinks box from edges |
| Feature off-center | `pan ... right 10%` or `pan ... right 30px` | Moves box right |
| Need to see all boxes | `show ...` | Draws all boxes on image |

Use `%` when you're thinking relatively ("move it a bit"), `px` when you can read exact pixel offsets from the grid image.

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
