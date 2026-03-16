# File Structure & WIP Organization

## Standard Project Layout

```
{project-dir}/
├── original.png              # Source image — NEVER modify
├── refs/                     # Cropped reference images
│   ├── head-full.png         # Wide crop of entire head/subject
│   ├── left-eye.png          # Tight crop per feature
│   ├── right-eye.png
│   ├── nose-mouth.png
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

Use `~/Downloads/{project-name}/` or wherever the user's original image lives. Create a subdirectory named after the project:

```bash
mkdir -p ~/Downloads/goblin-svg/{refs,parts}
cp ~/Downloads/original-image.png ~/Downloads/goblin-svg/original.png
```

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

## Cleanup

- Keep `refs/` and `parts/` even after delivering the final SVG
- The user may want to adjust a single feature later
- Don't accumulate numbered versions (`wip-v1.png`, `wip-v2.png`) — overwrite `wip.png`
- Part renders (`parts/left-eye.png`) are also overwritten each iteration
