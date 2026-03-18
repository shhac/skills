# File Structure & WIP Organization

## Standard Project Layout

```
{project-dir}/
├── original.png              # Source image — NEVER modify
├── feature-locations.yml     # Bounding boxes for all features (source of truth for cropping)
├── crop-tool.py              # Crop utility (from skill's scripts/ directory)
├── extract-trace-metadata.py # Metadata extraction script (from workflow-trace-metadata.md)
├── refs/                     # Cropped reference images (generated from feature-locations.yml)
│   ├── head-full.png         # Wide crop of entire head/subject
│   ├── left-eye.png          # Tight crop per feature
│   ├── right-eye.png
│   ├── nose.png
│   ├── mouth.png
│   ├── left-ear.png
│   ├── right-ear.png
│   ├── hat.png
│   └── ...
├── parts/                    # Standalone SVGs for each feature
│   ├── face.svg              # Face shape + contour strokes + shadow
│   ├── face.png              # Latest render for comparison
│   ├── left-eye.svg
│   ├── left-eye.png
│   ├── right-eye.svg
│   ├── right-eye.png
│   └── ...
├── wip.png                   # Latest render of the composite (overwritten each iteration)
└── final.svg                 # Final composite SVG
```

## Naming Conventions

- **Reference crops:** `refs/{feature-name}.png`
- **Standalone SVGs:** `parts/{feature-name}.svg`
- **Renders of parts:** `parts/{feature-name}.png` (same name, different extension)
- **Composite WIP render:** `wip.png` (single file, overwritten each time)
- **Final output:** `final.svg`

## Where to Put the Project

Create a project directory adjacent to the original image. Derive the name from the image filename:

```bash
# If the original is at ~/Downloads/goblin.png → project dir is ~/Downloads/goblin-svg/
PROJECT_DIR="$(dirname "$ORIGINAL")/$(basename "$ORIGINAL" | sed 's/\.[^.]*$//')-svg"
mkdir -p "$PROJECT_DIR"/{refs,parts}
cp "$ORIGINAL" "$PROJECT_DIR/original.png"
```

If the user specifies a different output location, use that instead.

## WIP Renders

Every time you modify an SVG, render it immediately and view it:

```bash
# Check rsvg-convert is available
command -v rsvg-convert || echo "Install with: brew install librsvg (macOS) or apt install librsvg2-bin (Linux)"

# Render a standalone part
rsvg-convert -w 200 -h 200 parts/left-eye.svg -o parts/left-eye.png

# Render the composite
rsvg-convert -w 512 -h 512 final.svg -o wip.png
```

If `rsvg-convert` is not available and cannot be installed, fall back to opening the SVG in a browser for visual verification.

**Always render after every change.** Don't make multiple changes before rendering — you won't know which change caused which effect.

## Troubleshooting Render Failures

If `rsvg-convert` fails, check for these common SVG errors:
- **Missing namespace:** The root `<svg>` must include `xmlns="http://www.w3.org/2000/svg"`
- **Unclosed tags:** Every `<g>`, `<path>`, `<circle>` etc. must be closed (`/>` or `</g>`)
- **Invalid `d` attribute:** Path data must start with `M` or `m`. Common mistake: missing a space between coordinates or using commas inconsistently
- **Malformed gradients:** `<linearGradient>` and `<radialGradient>` must be inside a `<defs>` block and referenced by `id`

If the SVG is valid but renders blank, check that elements have either a `fill` or `stroke` attribute — SVG defaults to black fill with no stroke, but transparent/white elements on a white background appear invisible.

## Cleanup

- Keep `refs/` and `parts/` even after delivering the final SVG
- The user may want to adjust a single feature later
- Don't accumulate numbered versions (`wip-v1.png`, `wip-v2.png`) — overwrite `wip.png`
- Part renders (`parts/left-eye.png`) are also overwritten each iteration
