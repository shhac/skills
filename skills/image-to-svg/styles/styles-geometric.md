# Geometric & Diagrammatic Styles

**For curve construction techniques** (which SVG commands to use, how to build custom paths when primitives aren't enough), see `styles/styles-curves-and-shapes.md`.

## When the Style is Geometric

Some images use clean geometric shapes rather than organic brush work:
- Corporate illustrations and icons
- Flat design / material design
- Infographics and diagrams
- Pixel art (grid-aligned)
- Logo design

## SVG Approach for Geometric Styles

### Use Primitives
Prefer SVG primitives over paths when the shape IS geometric:
```xml
<rect x="10" y="10" width="80" height="60" rx="8" fill="#4A90D9"/>
<circle cx="50" cy="50" r="30" fill="#E74C3C"/>
<ellipse cx="50" cy="50" rx="40" ry="25" fill="#2ECC71"/>
```

### Clean Paths
When you need paths, use clean control points:
```xml
<!-- Smooth, deliberate curves — not organic wobble -->
<path d="M 0 50 Q 50 0, 100 50 Q 50 100, 0 50 Z" fill="#333"/>
```

### No Stroke Variation
Geometric styles typically use:
- Uniform `stroke-width` (no variation)
- Sharp corners (`stroke-linejoin="miter"`) or consistent rounding
- Consistent stroke across all elements

### Flat Color
- No gradients (or very subtle ones)
- Solid fills with distinct colors
- Shadows as separate flat shapes (not gradients)

## Diagrammatic / Technical Illustration

### Characteristics
- Precise alignment and spacing
- Labels and annotations
- Consistent line weights
- Grid-aligned elements

### SVG Approach
- Use `transform` for precise positioning
- Consistent `stroke-width` across all elements
- Consider using `<use>` for repeated elements
- Align to a grid (round coordinates to whole numbers)

## Common Mistakes
- Adding organic wobble to geometric shapes
- Using gradients in a flat-color style
- Inconsistent corner radius across shapes
- Mixing geometric and organic techniques in the same image
