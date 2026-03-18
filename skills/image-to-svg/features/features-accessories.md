# Feature Reference: Accessories & Clothing

Hats, glasses, jewelry, fabric accessories, tools, clothing details, badges, etc.

## Pre-Drawing Checklist (General)

- [ ] What is the accessory and what's its function in the image?
- [ ] What's the z-order? (hat on top of head, glasses over eyes, etc.)
- [ ] How does it interact with the features it overlaps?
- [ ] Does it partially hide other features? (hat brim over forehead, collar over chin)
- [ ] What's the material? How is that material depicted in this art style?

## Hats

### Specific Checklist
- [ ] Hat shape — dome, flat, brim style?
- [ ] How does the hat sit on the head? (tilted? straight?)
- [ ] Where does the brim end? Does it extend past the head?
- [ ] What's under the brim? (forehead visible? hair tufts?)
- [ ] Hat color — solid, gradient, texture?
- [ ] Details — logos, badges, ridges, stitching?
- [ ] Outline style — consistent with face outlines?

### SVG Construction
Hats are typically the topmost layer:
```xml
<g id="hat">
  <!-- Hat dome (outline then fill, or brush strokes) -->
  <!-- Hat brim (often a separate shape overlapping the dome) -->
  <!-- Details: ridges, logos, badges -->
  <!-- Highlight/shine -->
</g>
```

The brim and dome are usually separate `<path>` elements — the brim overlaps the dome at the join, and the hat-head junction should overlap the hair/head beneath.

## Glasses

### Specific Checklist
- [ ] Frame shape — round, rectangular, cat-eye, aviator?
- [ ] Frame thickness — thin wire, thick plastic?
- [ ] Lens — transparent, tinted, reflective sunglasses?
- [ ] Bridge between lenses — how does it sit on the nose?
- [ ] Temple arms — visible from this angle?
- [ ] How do frames interact with eye outlines?

### Frame Construction by Shape

**Round frames:**
Two `<circle>` or `<ellipse>` elements for lenses, bridge as a curved `<path>` between them:
```xml
<circle cx="170" cy="200" r="25" fill="none" stroke="#333" stroke-width="3"/>
<circle cx="240" cy="200" r="25" fill="none" stroke="#333" stroke-width="3"/>
<path d="M 195,205 Q 205,215 215,205" fill="none" stroke="#333" stroke-width="3"/>
```

**Rectangular frames:**
Two `<rect>` elements with `rx`/`ry` for rounded corners. For thick frames, use filled rectangles with inner cutouts via `<clipPath>`.

**Cat-eye:**
`<path>` with cubic Beziers — rounded bottom curves, upswept points at outer top corners.

**Aviator:**
Teardrop-shaped paths (wider at top, narrowing toward bottom), double bridge.

### Lens Effects

**Transparent lenses:**
Low-opacity fill over the lens area:
```xml
<circle cx="170" cy="200" r="23" fill="rgba(200,220,240,0.1)"/>
```

**Reflection highlight:**
Small white ellipse in the upper-left of each lens, `opacity="0.4-0.7"`. Optionally add a second smaller highlight nearby.

**Tinted lenses (sunglasses):**
Fill with a dark `<linearGradient>` (e.g., #1a1a2e to #2d2d44), add a diagonal white glare stripe across each lens:
```xml
<path d="M 155,190 L 175,195 L 172,198 L 152,193 Z"
      fill="white" opacity="0.3"/>
```

**Opaque/mirror sunglasses:**
Higher opacity gradient fill + stronger glare stripe.

### Glasses-Face Interaction
- Frames sit at the **browline** — top of frame aligns roughly with eyebrow line
- Bridge curves down to rest on the nose ridge
- From front view, temple arms are barely visible (just short lines at frame edges)
- In 3/4 view, near lens is larger, far lens is compressed
- For cartoon/anime styles, frames may be drawn "through" the face to preserve expression

## Jewelry

### Metallic Gradient Reference

**Gold:**
```xml
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#ffd587"/>
  <stop offset="25%" stop-color="#cfa344"/>
  <stop offset="50%" stop-color="#9a5f00"/>
  <stop offset="75%" stop-color="#ffd699"/>
  <stop offset="100%" stop-color="#f5be39"/>
</linearGradient>
```

**Silver:**
```xml
<linearGradient id="silver" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#e8e8e8"/>
  <stop offset="25%" stop-color="#b0b0b0"/>
  <stop offset="50%" stop-color="#808080"/>
  <stop offset="75%" stop-color="#d0d0d0"/>
  <stop offset="100%" stop-color="#c0c0c0"/>
</linearGradient>
```

**Chrome (high-contrast):**
```xml
<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#ffffff"/>
  <stop offset="20%" stop-color="#c0c0c0"/>
  <stop offset="40%" stop-color="#4a4a4a"/>
  <stop offset="60%" stop-color="#e0e0e0"/>
  <stop offset="80%" stop-color="#3a3a3a"/>
  <stop offset="100%" stop-color="#f0f0f0"/>
</linearGradient>
```

**Rose gold:** Stops mixing gold and pink: #e8b4b8, #daa06d, #b76e79, #f0c9c9

The key principle: **alternating light and dark tones** in the gradient creates the curved metallic surface impression. Chrome has the highest contrast; matte metals have lower contrast.

### Rings
- Band: `<circle>` or `<ellipse>` with `stroke` (band width) and `fill="none"`
- For a ring on a finger: draw only the visible top arc, bottom hidden behind finger
- With stone: geometric shape on top (circle, rotated square for diamond) with its own gradient

### Necklaces
- Chain: curved `<path>` with metallic gradient stroke following the neckline
- For detailed chains: `<pattern>` of small ellipse links applied along the path
- Pendant: shape hanging from the lowest point, connected by a small bail path

### Earrings
- **Stud:** small `<circle>` or shape at the earlobe
- **Drop/dangle:** `<line>` or chain from earlobe, terminating in a decorative shape
- **Hoop:** `<circle>` with `stroke` and `fill="none"`, top portion clipped behind the ear

### Paired accessories
Use `<use>` with `transform="scale(-1,1)"` to mirror earrings, cufflinks, etc. efficiently. Adjust position with `translate()`.

## Fabric Accessories — Scarves, Ribbons, Bows

### Scarf construction
- Outer edges: two parallel Bezier paths with similar curvature but offset
- Fill between them with fabric color
- Fold lines: additional Bezier paths between edges, lighter or darker shade
- Fringe: series of short `<line>` elements at ends

### Ribbon construction
- Narrow strip with twists — each visible face is its own `<path>`
- Front face: lighter fill. Back face: darker fill
- At twist points the path narrows to a point and the other face begins — this creates the 3D illusion

### Bow construction
- Two loop shapes: ellipse-like `<path>` elements (or rotated ellipses)
- Center knot: small `<rect>` or `<path>` overlapping the junction
- Tails: two `<path>` elements curving downward from behind the knot
- V-notch or angled cut at tail ends

### Showing drape and flow
- Curves follow gravity — downward arcs with varying curvature
- Folds radiate from tension points (pin, knot, shoulder)
- Shadow in fold valleys (darker gradient), highlight on fold peaks (lighter)
- For sheer fabrics: `fill-opacity="0.3-0.5"` with multiple overlapping layers where fabric doubles

## Clothing Details

### Specific Checklist
- [ ] What garments are visible?
- [ ] How do they fit? (loose, tight, oversized?)
- [ ] Wrinkles/folds — how are they depicted?
- [ ] Color and pattern?
- [ ] Pockets, buttons, zippers — which details are included?
- [ ] Where does clothing meet skin? How is that boundary drawn?

### Buttons and fasteners
- Button: small `<circle>` with two or four tiny dot holes
- Zipper: thin `<rect>` for the tape, tiny interlocking V shapes as `<pattern>`, small `<rect>` for the pull tab
- Buckle: `<rect>` frame with `<circle>` pin and `<line>` holes on the strap

### Pockets
- Usually just the outline `<path>` stitched onto the garment
- Add subtle shadow at the opening edge for depth

## Common Mistakes

- Accessories feel "floating" — not properly seated on the character
- Wrong z-order (hat behind hair instead of on top)
- Accessory outline style inconsistent with character outline style
- Too much detail on accessories vs the character's art style
- Forgetting how the accessory affects visibility of features beneath it
- Glasses frames without any lens effect — even minimal transparency or reflection helps
- Flat metallic surfaces — metals need multi-stop gradients with alternating light/dark
- Jewelry that's too complex for the art style — simplify to match
