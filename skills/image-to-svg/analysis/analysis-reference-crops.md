# Creating Reference Crops

Tight crops of individual features from the original image are essential. Without them, you'll work from a vague memory of what the feature looks like, and the result will be "conceptually similar" rather than accurate.

## Why Crops Matter

- Forces you to actually LOOK at the specific feature rather than the whole image
- Reveals details you miss at full zoom: outline thickness variation, color subtleties, highlight positions
- Provides a direct comparison target when iterating on your SVG
- Prevents other features from "distracting" your understanding

## How to Crop

### Tools
```bash
# ImageMagick (preferred — precise pixel control)
magick original.png -crop WIDTHxHEIGHT+X+Y +repage refs/feature-name.png

# macOS sips (simpler but less precise)
sips -c HEIGHT WIDTH --cropOffset Y X original.png --out refs/feature-name.png
```

### Getting Coordinates Right

1. Check the image dimensions first: `sips -g pixelWidth -g pixelHeight original.png`
2. Estimate the center of the feature you want
3. Crop generously on the first pass — too tight is worse than too loose
4. Include some surrounding context (neighboring features help judge position)
5. Re-crop if the feature isn't well-centered

### What to Crop

For a character face, create crops for:
- `head-full.png` — entire head including hat, ears, chin (wide crop)
- `left-eye.png` — just the left eye with some surrounding face
- `right-eye.png` — just the right eye (do NOT assume it's a mirror)
- `nose-mouth.png` — nose and mouth together (they relate to each other)
- `left-ear.png` — left ear with some head/hat context
- `right-ear.png` — right ear
- `hat.png` — hat in isolation
- Any other distinct features (hair, accessories, etc.)

### File Organization

```
project-name/
├── original.png          # Original image (never modify)
├── refs/                 # Reference crops
│   ├── head-full.png
│   ├── left-eye.png
│   ├── right-eye.png
│   ├── nose-mouth.png
│   ├── left-ear.png
│   ├── right-ear.png
│   └── hat.png
├── parts/                # Standalone SVGs for each feature
│   ├── face.svg
│   ├── left-eye.svg
│   ├── right-eye.svg
│   └── ...
└── final.svg             # Composite result
```

## Verifying Crops

After creating crops, **view every single one** and confirm:
- **Is the ENTIRE feature visible?** No part of the subject cropped off at an edge. The most common error is clipping an ear tip, a hat brim, or the bottom of a chin. If any part of the feature touches the crop boundary, re-crop wider.
- The target feature is well-centered with surrounding context
- The image is large enough to see detail (at least 200x200px)
- The crop includes enough neighboring features to judge relative positioning

Re-crop immediately if any feature is partially cut off. A reference crop that's missing part of the subject will lead to an SVG that's missing that same part.
