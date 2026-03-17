# Line & Brush Work Techniques in SVG

## The Fundamental Problem

SVG `stroke-width` is uniform along a path. Real brush strokes taper, swell, and vary. There are several techniques to work around this.

**For curve construction techniques** (which SVG commands to use, how to build shapes from Beziers, the centerline-to-filled-shape pipeline), see `styles/styles-curves-and-shapes.md`. This file focuses on which *stroke technique* to apply; that file covers *how to construct the shapes*.

## Technique 1: Uniform Stroke with Round Caps

**Best for:** Cartoon styles with thick uniform outlines

```xml
<path d="M 10 50 Q 50 10, 90 50"
      fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>
```

The `round` linecap gives rounded endpoints that visually soften the start and end. This is the simplest technique and works well when the original has mostly uniform outlines.

**When to use:** The outline thickness looks consistent in the reference. The "character" comes from the path shape, not the line variation.

## Technique 2: Offset Shapes (Variable Outline)

**Best for:** Outlines that are thicker on one side (e.g., bottom-heavier eye outlines)

Draw two concentric shapes — a larger dark one and a smaller light one offset slightly:

```xml
<!-- Dark outer shape -->
<ellipse cx="100" cy="100" rx="90" ry="90" fill="#333"/>
<!-- Light inner shape, offset creates variable gap -->
<ellipse cx="102" cy="98" rx="80" ry="80" fill="white"/>
```

The offset direction controls where the outline is thickest:
- Shift inner **up** → thicker at bottom
- Shift inner **right** → thicker at left
- Combine for diagonal weighting

**Key learning:** Start with VERY subtle offsets (2-3px). Large offsets look broken, not stylized. Compare with the reference at each step.

## Technique 3: Filled Tapered Shapes

**Best for:** True brush strokes with dramatic taper (thick middle, pointed ends)

Draw the stroke as a filled `<path>` shaped like an elongated leaf:

```xml
<!-- Trace the outer edge, then the inner edge back, closing to points -->
<path d="
  M 50 100
  C 30 80, 20 50, 40 30
  C 45 35, 35 55, 45 80
  Z"
  fill="#333"/>
```

Construction approach:
1. Define the center line of where the stroke goes
2. Trace the outer edge (offset outward from center line)
3. At the end point, cross over to the inner edge
4. Trace the inner edge back (offset inward from center line)
5. Close at the start point

The distance between outer and inner edges controls thickness at each point.

**When to use:** The reference shows dramatic thickness variation along a single stroke — thick in the middle, thin/pointed at the ends. Common in hand-drawn and brush-ink styles.

## Technique 4: Path Following Face Edge

**Best for:** Contour strokes that need to sit exactly on the edge of a filled shape

Extract the relevant segment from the fill shape's path and use it as a stroke:

```xml
<!-- Face fill uses this path segment for its left edge -->
<path d="M 98 240 C 82 262, 78 290, 84 320 C 90 352, 110 380, 138 402"
      fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>
```

This guarantees the stroke sits exactly on the shape boundary — no floating, no beard effect.

## Technique 5: Layered Strokes for Width Variation

**Best for:** Moderate variation without the complexity of filled shapes

Layer multiple strokes of different widths and lengths on the same path:

```xml
<!-- Base: full length, thin -->
<path d="M 10 50 C 30 20, 70 20, 90 50"
      fill="none" stroke="#333" stroke-width="4" stroke-linecap="round"/>
<!-- Middle accent: shorter, thicker -->
<path d="M 30 35 C 40 25, 60 25, 70 35"
      fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>
```

## Choosing the Right Technique

| Reference Shows | Use |
|----------------|-----|
| Uniform outline, consistent width | Technique 1 (simple stroke) |
| Outline heavier on one side | Technique 2 (offset shapes) |
| Dramatic taper, brush-like marks | Technique 3 (filled tapered shapes) |
| Contour strokes on a shape edge | Technique 4 (path following) |
| Moderate variation, not extreme | Technique 5 (layered strokes) |

## Technique 6: Rough.js-Style Jittered Paths

**Best for:** Sketchy/hand-drawn feel, whiteboard style

The Rough.js library's algorithm works by:
1. Picking random points along the line at ~50% and ~75% marks
2. Jittering each point by a "roughness" factor
3. Fitting a curve through the jittered points
4. Drawing each line **twice** for extra sketchiness (overlapping imperfect lines)
5. For closed shapes: intentionally not closing the loop perfectly

You can apply this manually in SVG by adding slight imperfections:
```xml
<!-- Instead of a perfect circle -->
<circle cx="100" cy="100" r="50"/>
<!-- Use a slightly wobbly path -->
<path d="M 50 100 C 50 72, 72 49, 101 50 C 130 51, 151 73, 150 101
         C 149 129, 128 150, 100 150 C 71 151, 50 130, 50 100"/>
```

## Professional Workflow Note

Design tools can convert strokes to filled shapes (Illustrator's "Expand Appearance", Inkscape's "Stroke to Path", Figma's "Outline Stroke"). This is deliberate — filled shapes:
- Scale predictably at any size
- Render consistently across browsers
- Support variable width and organic edges

When recreating artwork manually, **filled shapes for outlines** is the professional standard for anything beyond simple uniform strokes.

**When in doubt, choose Technique 3 (filled tapered shapes).** It produces the highest quality output and handles every case. Techniques 1 and 5 are shortcuts — use them only when the reference clearly has uniform or nearly-uniform strokes. The extra effort of building filled shapes pays off dramatically in the final result.

## Anti-Patterns

- **Don't mix techniques randomly** — pick one per element and be consistent
- **Don't exaggerate variation** — if the reference has subtle variation, keep it subtle
- **Don't add character that isn't there** — if the original has uniform outlines, don't add brush taper
- **Don't outline everything** — check which edges have strokes and which don't
