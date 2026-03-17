# Bringing Layers Together

After building each feature as a standalone SVG, combine them into the final composite.

## Compositing Process

### 1. Establish the Canvas
Choose a viewBox that fits all elements with appropriate padding:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
```

For emoji/icon use: 512x512 is standard.

### 2. Set Up the Layer Stack
Create `<g>` groups in z-order (back to front):
```xml
<!-- Back to front -->
<g id="left-ear">...</g>
<g id="right-ear">...</g>
<g id="face">...</g>
<g id="left-eye">...</g>
<g id="right-eye">...</g>
<g id="nose">...</g>
<g id="mouth">...</g>
<g id="hair">...</g>
<g id="hat">...</g>
```

### 3. Position Each Layer

If agents followed the shared-viewBox convention (all parts use the same `viewBox` and pre-positioned their features in canvas coordinates), **no transforms are needed** — just paste each group's content into the composite in z-order.

#### Fallback: Repositioning Layers

If parts were built at different scales or without shared coordinates, use transforms:
```xml
<g id="left-eye" transform="translate(120, 200)">
  <!-- Content from left-eye.svg, positioned relative to the group origin -->
</g>
```

If standalone SVGs were built at a different size:
```xml
<g id="left-eye" transform="translate(120, 200) scale(0.7)">
```

## Review Pass: Integration Issues

After initial compositing, check for these problems:

### Overlap Issues
- Do outlines from adjacent features overlap awkwardly?
- Do fills bleed into neighboring features?
- Is there unwanted layering (e.g., ear outline showing through face)?

### Gap Issues
- Are there gaps between features that should be seamless?
- Does the face fill fully cover the ear base?
- Does the hat brim sit properly on the head?

### Consistency Issues
- Are outline weights consistent across features?
- Is the color palette consistent? (same skin tone everywhere)
- Do all features use the same art style?

### Interaction Issues
- Do the face contour strokes stop at the right place relative to the ears?
- Does the hat brim properly cover the forehead?
- Do eye outlines interact correctly with the hat brim if they overlap?

## Adjusting After Compositing

When adjustments are needed:
1. **If the feature itself is wrong** — go back to the standalone SVG, fix it, re-export
2. **If the position is wrong** — adjust the `transform` or coordinates in the composite. Treat the largest or most central feature (face shape for characters, primary structure for objects) as the **anchor** — adjust other features relative to it, not the other way around.
3. **If the interaction is wrong** — adjust z-order, add `<clipPath>` to clip features to a boundary (e.g., facial features clipped to face shape, interior details to object silhouette), or modify the edges of interacting features

## Final Verification

1. Render the composite at target resolution: `rsvg-convert -w 512 -h 512 final.svg -o wip.png`
2. Read both the rendered composite and the original image, then compare:
   - Does the overall silhouette and color distribution match?
   - Are features in the right positions relative to each other?
   - Check individual features against their reference crops
3. Render at a small size (64x64 or 128x128) — does it still read clearly? Features that looked fine at 512px may merge or disappear at icon size.

## Keep the Parts

Always keep the `parts/` directory with standalone SVGs:
- Makes future edits easy (change just one eye without touching everything)
- Allows re-compositing at different sizes or arrangements
- Reference for future similar projects
