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
Use `transform="translate(x, y)"` on each `<g>` to position the standalone SVG content within the composite canvas:
```xml
<g id="left-eye" transform="translate(120, 200)">
  <!-- Content from left-eye.svg, positioned relative to the group origin -->
</g>
```

Or directly adjust the coordinates of each element to fit the composite canvas.

### 4. Scale if Needed
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
2. **If the position is wrong** — adjust the `transform` or coordinates in the composite
3. **If the interaction is wrong** — adjust z-order, add clipping, or modify the edges of interacting features

## Final Verification

1. Render the composite at target resolution
2. Place it next to the original image
3. Squint at both — does the overall impression match?
4. Check individual features against their reference crops
5. Verify at small size (emoji size) — does it still read clearly?

## Keep the Parts

Always keep the `parts/` directory with standalone SVGs:
- Makes future edits easy (change just one eye without touching everything)
- Allows re-compositing at different sizes or arrangements
- Reference for future similar projects
