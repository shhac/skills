# Constructing Shapes with Curves

## The Core Principle: Filled Shapes Over Stroked Paths

SVG `stroke-width` is uniform along a path. Real objects have edges that taper, swell, and vary in thickness. **The professional approach is to build strokes and outlines as filled shapes** — closed paths where the geometry itself encodes the width variation.

This is not a workaround. It's how Illustrator, Inkscape, and every professional vector tool represent variable-width marks. A filled shape:
- Scales predictably at any size
- Renders identically across all browsers and tools
- Supports arbitrary width variation, tapers, and organic edges
- Is the only way to achieve brush-like quality in SVG

**Default to filled shapes for any edge that isn't perfectly uniform.** Only use `stroke` for truly uniform outlines in geometric/cartoon styles where the reference shows consistent width throughout.

## SVG Curve Commands: When to Use Each

### Cubic Bezier (`C` / `S`) — The Default Choice

```xml
<!-- C: two explicit control points -->
<path d="M 10,80 C 30,10 70,10 90,80"/>

<!-- S: smooth continuation (first control point auto-reflected) -->
<path d="M 10,80 C 30,10 70,10 90,80 S 150,10 170,80"/>
```

**Use for:** Almost everything. Organic curves, S-curves, flowing edges, complex silhouettes. Two control points give enough freedom to match any smooth curve segment. The `S` command maintains tangent continuity between segments — use it when a curve flows smoothly from one segment to the next.

**How control points work:** The curve starts tangent to the line from P0→P1 and ends tangent to the line from P2→P3. Pull control points further from the path to increase curvature; keep them close for gentle bends. Control points on opposite sides of the baseline create an S-curve.

### Quadratic Bezier (`Q` / `T`) — Simple Arcs

```xml
<!-- Q: one control point -->
<path d="M 10,80 Q 50,10 90,80"/>

<!-- T: smooth continuation (control point auto-reflected) -->
<path d="M 10,80 Q 50,10 90,80 T 170,80"/>
```

**Use for:** Simple arcs where you only need one "pull" direction. Good for scalloped edges (each scallop between two anchor points is one `Q` segment), dome arcs, and simple rounded features. The `T` command is useful for wave-like patterns where arcs alternate direction.

**Limitation:** Cannot create S-curves or inflection points within a single segment. If you need the curve to change direction, switch to `C`.

### Elliptical Arc (`A`) — Geometric Arcs

```xml
<!-- A: rx ry rotation large-arc-flag sweep-flag x y -->
<path d="M 10,80 A 80,80 0 0,1 170,80"/>
```

**Use for:** Circular or elliptical arcs where mathematical precision matters — wheels, clock faces, pie segments, rounded corners. The only SVG command that produces exact circles and ellipses.

**Avoid for:** Organic shapes. Arcs look mechanical because they have constant curvature. Real objects have curvature that varies continuously.

### Decision Table

| What You're Drawing | Command | Why |
|---|---|---|
| Smooth flowing edge (hair, fabric, organic silhouette) | `C` / `S` | Need full control over entry/exit tangents |
| Scalloped edge (umbrella canopy, lace, ruffles) | `Q` / `T` | Each scallop is a simple arc between two points |
| S-curve (body contour, flowing ribbon) | `C` | Only cubic bezier can inflect within a segment |
| Perfect circle or ellipse | `A` or `<circle>`/`<ellipse>` | Mathematical precision |
| Dome or arch | `Q` for simple, `C` for organic | `Q` if symmetric, `C` if the dome has character |
| Hook or spiral (handle, tendril, curl) | `C` chain | Needs tangent continuity through multiple segments |
| Straight-to-curve transition | `C` with first control on the line | Collinear first control point = straight start |

## Building Organic Filled Shapes

### The Pipeline: Centerline → Width Profile → Offset Curves → Closed Path

This is the fundamental technique for constructing any shape that has variable width — strokes, ribbons, stems, handles, ribs, structural elements.

**Step 1: Define the centerline.** This is the path the shape follows — an invisible skeleton. It can be a straight line, a curve, or a complex path.

**Step 2: Define the width profile.** How wide is the shape at each point along the centerline? Common profiles:
- **Tapered stroke:** thin → thick → thin (leaf, petal, brush mark)
- **Entry taper:** thin → thick (hair strand growing from root)
- **Exit taper:** thick → thin (pointed tip, pen stroke lifting)
- **Uniform:** constant width (structural beam, frame edge)
- **Swelling:** thin → thick → thin → thick (organic tendril, rope)

**Step 3: Trace offset curves.** Mentally (or computationally) trace two curves parallel to the centerline — one on each side — at the distance specified by the width profile. Where the profile says "wide," the offset curves are far apart. Where it says "thin," they converge.

**Step 4: Close into a filled path.** Trace the outer edge forward, curve around the end, trace the inner edge back, close at the start. Fill this path with no stroke.

```xml
<!-- A tapered brush stroke as a filled shape -->
<!-- Centerline goes roughly left-to-right, width swells in the middle -->
<path d="
  M 20,100
  C 30,95  50,70  80,68
  C 110,66 140,75 160,100
  C 140,80 110,74 80,72
  C 50,74  30,90  20,100
  Z"
  fill="#333" stroke="none"/>
```

The outer edge (first half) and inner edge (second half) share endpoints but diverge in the middle — creating the thick-to-thin variation.

### When to Use This Pipeline

Any time a shape is elongated and has character along its length:
- Brush strokes and ink marks
- Hair strands and fur tufts
- Structural ribs (umbrella, fan, leaf veins)
- Handles, stems, branches
- Ribbons, fabric folds, flowing scarves
- Tapered outlines on organic shapes

### Practical Shortcut: Asymmetric Offset

Not every filled shape needs the full pipeline. For many organic outlines, you can trace the shape as a single closed path where **one side follows the object contour closely and the other side follows it at a varying distance**:

```xml
<!-- Face contour that's thicker at the jaw, thinner at the temple -->
<!-- Outer edge follows the face shape; inner edge follows with varying gap -->
<path d="
  M 120,50
  C 160,55  190,90  195,140
  C 200,190 180,240 140,260
  C 135,255 175,195 180,140
  C 185,95  160,60  125,55
  Z"
  fill="#333"/>
```

## Smooth Curves Through Known Points

When you know the points a curve should pass through (e.g., a series of coordinates along a canopy edge, or sampled points from a reference), you need to derive the Bezier control points. Direct cubic Bezier requires you to place control points *off* the curve, which is unintuitive when you're thinking in terms of "the curve goes through here, then here, then here."

### The Catmull-Rom Approach

For each segment between points P[i] and P[i+1], derive cubic Bezier control points using the neighboring points:

- **Control point 1** = P[i] + (P[i+1] - P[i-1]) / 6
- **Control point 2** = P[i+1] - (P[i+2] - P[i]) / 6

This produces a smooth curve that passes through every point with automatic tangent continuity. The tangent at each point is parallel to the line connecting its two neighbors.

### Practical Application

You don't need to compute this numerically. The principle is:

> At each point on the curve, the direction of the curve should be roughly parallel to the line connecting the previous point to the next point.

When placing `C` command control points:
- The first control point of a segment should "aim" in the direction the curve was traveling from the previous segment
- The second control point should "aim" backward from the direction the curve will travel into the next segment
- The distance of control points from the curve affects the "stiffness" — closer = tighter, farther = more flowing

## Common Shape Construction Patterns

### Dome / Canopy
A dome that isn't a perfect semicircle — slightly flattened, asymmetric, or with character:
```xml
<!-- Slight flat spot at top, steeper sides -->
<path d="M 20,200 C 20,100 80,40 200,35 C 320,40 380,100 380,200 Z"/>
```
Use `C` rather than `A` — real domes aren't perfect arcs. The control points let you shape the crown and shoulders independently.

### Scalloped Edge
A series of arcs dipping between anchor points (umbrella canopy bottom, lace, cloud):
```xml
<!-- Five scallops between six anchor points -->
<path d="M 40,200 Q 70,175 100,200 Q 130,175 160,200
         Q 190,175 220,200 Q 250,175 280,200 Q 310,175 340,200"/>
```
Vary the control point depth (175 vs 180 vs 170) slightly between scallops — identical scallops look mechanical.

### Hook / J-Curve (handles, hooks, question marks)
Build as a chain of `C` commands with tangent continuity. The hook is a filled shape — trace the outer edge of the curve, go around the tip, trace the inner edge back:
```xml
<!-- J-hook handle as filled shape -->
<path d="
  M 198,150 C 198,185 198,210 218,225
  C 232,235 242,225 238,212
  C 234,200 210,200 202,210
  C 202,195 202,175 202,150 Z"
  fill="#6B3A2A"/>
```

### Flowing Ribbon / Fabric
Ribbons have two edges that follow roughly parallel but diverging/converging paths. Build each edge as its own curve, then connect at the endpoints:
```xml
<!-- Ribbon with a twist -->
<path d="
  M 30,100 C 80,60  140,120 200,80
  C 210,85 150,130 90,70
  C 70,80  40,105  30,100 Z"
  fill="#C44"/>
```

### Organic Blob (irregular filled region)
For shapes that aren't geometric but have smooth edges (clouds, puddles, blobs), use a series of `C` commands forming a closed loop. Avoid making any segment too "perfect" — vary the curvature:
```xml
<path d="M 100,50 C 140,30 180,45 200,80
         C 220,115 200,160 160,170
         C 120,180 70,155 55,120
         C 40,85 60,55 100,50 Z"
  fill="#88C"/>
```

## Adding Life to Filled Shapes

### Subtle Edge Irregularity
Perfectly smooth bezier edges read as computer-generated. For organic subjects, add micro-variation by including extra anchor points with slightly offset control points. Don't add noise randomly — think about what would cause the irregularity (fabric tension, material grain, hand tremor in the original art).

### Interior Detail Through Layered Fills
A single flat-filled shape looks like clip art. Build depth with overlapping semi-transparent shapes:
- Base fill (solid color)
- Shadow region (darker, partial coverage)
- Highlight region (lighter, partial coverage)
- Reflected light (subtle warm tone on shadow side)

Each of these is its own filled path using the same curve techniques.

### Gradient Along Curved Surfaces
SVG `linearGradient` and `radialGradient` can simulate light falling across curved surfaces. Orient the gradient to match the light direction established in the reference image.

## Anti-Patterns

- **Using `stroke` for anything with width variation** — convert to a filled shape instead
- **Using `A` arcs for organic shapes** — they have constant curvature and look mechanical
- **Identical repeated curves** — vary scallop depth, rib spacing, or strand thickness slightly
- **Placing control points too far from the curve** — produces bulging, overshooting paths. Start with control points at ~1/3 the segment length from each endpoint
- **Forgetting to close filled shapes** — an unclosed `<path>` used as a fill will auto-close with a straight line, creating unexpected edges
- **Mixing stroked and filled approaches on the same element** — pick one technique per element for consistency
