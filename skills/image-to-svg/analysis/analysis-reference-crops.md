# Creating Reference Crops

Tight crops of individual features from the original image are essential. Without them, you'll work from a vague memory of what the feature looks like, and the result will be "conceptually similar" rather than accurate.

## Why Crops Matter

- Forces you to actually LOOK at the specific feature rather than the whole image
- Reveals details you miss at full zoom: outline thickness variation, color subtleties, highlight positions
- Provides a direct comparison target when iterating on your SVG
- Prevents other features from "distracting" your understanding

## How to Crop

### Tools

Check which tools are available before cropping:

```bash
# Preferred: ImageMagick (cross-platform, precise pixel control)
command -v magick && magick original.png -crop WIDTHxHEIGHT+X+Y +repage refs/feature-name.png

# Fallback on macOS: sips (built-in, simpler but less precise)
command -v sips && sips -c HEIGHT WIDTH --cropOffset Y X original.png --out refs/feature-name.png
```

If neither is available, install ImageMagick (`brew install imagemagick` on macOS, `apt install imagemagick` on Linux).

### Getting Coordinates Right

1. Check the image dimensions first: `magick identify original.png` (or `sips -g pixelWidth -g pixelHeight original.png` on macOS)
2. Estimate the center of the feature you want
3. **Crop generously** — too tight is worse than too loose. Include a margin of at least 15-20% around the feature on all sides. A crop that's 50% background is fine; a crop that clips the feature is useless.
4. Include some surrounding context (neighboring features help judge position)
5. Re-crop if the feature isn't well-centered

### What to Crop

For a character face, create crops for:
- `head-full.png` — entire head including hat, ears, chin (wide crop)
- `left-eye.png` — just the left eye with some surrounding face
- `right-eye.png` — just the right eye (do NOT assume it's a mirror)
- `nose.png` — nose with surrounding context
- `mouth.png` — mouth with surrounding context
- `left-ear.png` — left ear with some head/hat context
- `right-ear.png` — right ear
- `hat.png` — hat in isolation, including the full brim and how it sits on the head
- Any other distinct features (hair, accessories, etc.)

### File Organization

See `workflow/workflow-file-structure.md` for the full project layout. Crops go in `refs/`, named `{feature-name}.png`.

## Verifying Crops

**This is the most common failure point in the entire workflow.** Bad crops produce bad SVGs. Every minute spent verifying crops saves ten minutes of iteration later.

### Step 1: Programmatic edge-margin check

Run this on every crop to detect whether non-background content touches the crop edges. If the margin on any side is too small, the feature is likely clipped:

```bash
# Check margins around the feature (how much background padding exists on each side)
# Trim to non-background pixels, then compute margin on each side
magick refs/{feature}.png -fuzz 10% -trim -format \
  "left=%X top=%Y right=%[fx:page.width-w-page.x] bottom=%[fx:page.height-h-page.y]" info:
```

**Interpret the output:**
- Each value is the margin in pixels between the feature content and the crop edge
- If ANY margin is less than 5% of the crop dimension → **the feature is likely clipped. Re-crop wider.**
- Example: for a 300x280 crop, 5% margin = 15px horizontal, 14px vertical. If `top=3` → the top is clipped.

```bash
# Automated pass/fail check for all crops at once:
for f in refs/*.png; do
  name=$(basename "$f")
  dims=$(magick identify -format "%w %h" "$f")
  w=${dims% *}; h=${dims#* }
  min_h=$((w * 5 / 100))  # 5% of width
  min_v=$((h * 5 / 100))  # 5% of height
  margins=$(magick "$f" -fuzz 10% -trim -format "%X %Y %[fx:page.width-w-page.x] %[fx:page.height-h-page.y]" info:)
  read l t r b <<< "$margins"
  l=${l%.*}; t=${t%.*}; r=${r%.*}; b=${b%.*}  # truncate to int
  fail=""
  [ "$l" -lt "$min_h" ] 2>/dev/null && fail="${fail} left=${l}"
  [ "$t" -lt "$min_v" ] 2>/dev/null && fail="${fail} top=${t}"
  [ "$r" -lt "$min_h" ] 2>/dev/null && fail="${fail} right=${r}"
  [ "$b" -lt "$min_v" ] 2>/dev/null && fail="${fail} bottom=${b}"
  if [ -n "$fail" ]; then
    echo "FAIL $name:$fail (min_h=${min_h}px min_v=${min_v}px)"
  else
    echo "PASS $name: L=${l} T=${t} R=${r} B=${b}"
  fi
done
```

Any crop that prints `FAIL` needs re-cropping — extend the crop by at least 50% on the failing side. **Do not skip this step.**

### Step 2: Visual verification — ONE crop at a time

After the programmatic check passes, verify each crop visually. **Read each crop individually** — do NOT batch multiple crops into a single Read call. Batching causes you to scan quickly and miss problems.

For EACH crop, read it and confirm:

1. **Is the ENTIRE feature visible?** No part of the subject clipped at any edge. The most common errors:
   - Eye tops cut off by hat brim (the crop captured the brim but not enough face below/above)
   - Ear bases clipped where they connect to the face
   - Hat brim bottom edge not visible
   - Chin cut off at bottom
2. **Is there visible margin on ALL FOUR sides** between the feature and the crop boundary? If the feature touches any edge, re-crop wider.
3. **Is the feature the primary subject of the crop**, not a tiny element in the corner? The feature should be centered and prominent.
4. **Is the image large enough** to see detail (at least 200x200px)?
5. **Does the crop include enough neighboring context** to judge relative positioning?

### Step 3: Re-crop failures immediately

Do not continue to the build phase with clipped crops. Re-crop wider — add 50% more padding on the clipped side. Then re-run both the programmatic check and the visual verification on the new crop.

**A reference crop that's missing part of the subject will produce an SVG that's missing that same part.** This is not recoverable later — the agent building from this crop literally cannot see what's been cut off.

### Common Cropping Failures

| Failure | Why It Happens | How to Prevent |
|---|---|---|
| Eye top clipped by hat brim | Crop Y coordinate started too low | Extend crop upward — include more hat even if it's "not the eye" |
| Ear base clipped | Crop didn't extend far enough down where ear meets face | Extend crop downward to include the face-ear connection |
| Hat brim bottom clipped | Crop focused on dome, forgot the brim sits lower | Extend crop below the brim to show how it sits on the head |
| Feature tiny in corner | Crop centered on wrong point | Re-center the crop on the actual feature |
| Assumed crop was fine without viewing | Verified wider shots and assumed individual crops matched | ALWAYS verify each individual crop — wider shots don't guarantee narrow crops are correct |

### The "View Every Single One" Rule

This means:
- Read `refs/left-eye.png` → check it → confirm or re-crop
- Read `refs/right-eye.png` → check it → confirm or re-crop
- Read `refs/left-ear.png` → check it → confirm or re-crop
- ... and so on for EVERY crop

**Not** "read 4 crops at once and scan quickly." The purpose is to spend 5-10 seconds per crop evaluating against the criteria above. This feels slow but it prevents the most common source of quality loss in the entire pipeline.
