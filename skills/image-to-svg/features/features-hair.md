# Feature Reference: Hair

Hair is one of the hardest features to get right — it's organic, interacts with multiple other elements, and varies enormously by style. Small construction mistakes are immediately visible because hair frames the face.

## Pre-Drawing Checklist

### What's Visible
- [ ] Full hair, tufts under a hat, bangs only, or something else?
- [ ] Does the hair define the forehead boundary?
- [ ] Is back hair visible behind the head?
- [ ] Are individual strands visible, or is it a solid mass?

### Shape & Volume
- [ ] How much volume does the hair have? (Tight to skull, moderate, large/fluffy?)
- [ ] What's the overall silhouette shape relative to the head?
- [ ] Is there a visible parting? Where?
- [ ] How far does the hair extend from the head outline?

### Style & Texture
- [ ] Straight, wavy, curly, or coily?
- [ ] Solid mass, clumped, or individual strands?
- [ ] Spiky/gravity-defying or following gravity?
- [ ] Are there distinct clumps/locks, and how many?

### Color & Lighting
- [ ] Base color — uniform or has variation?
- [ ] Is there a highlight/shine band? Where is it positioned?
- [ ] Are there lowlights (darker areas at roots, under overlaps)?
- [ ] Does the color change along the length? (ombre, tips, roots)

### Interactions
- [ ] How does the hair interact with the hat? (compressed underneath, tufts poking out sides/front?)
- [ ] How does it interact with ears? (behind, over, or tucked behind?)
- [ ] Does it overlap the forehead? By how much?
- [ ] Are hair outlines separate brush strokes or part of the hair fill?

## Construction Approach: Solid Mass vs Strands

### Solid Mass (most styles)

**Use for:** Cartoon, flat design, anime, chibi, any stylized work. This is the dominant approach for SVG.

Build the entire hair as 1-3 large filled shapes (the silhouette). All detail — highlights, shadow, texture — is layered on top of or clipped within this base shape.

```xml
<!-- Hair base: single filled path covering the entire hair area -->
<path d="M 150,60 C 100,55 60,80 55,140
         C 50,200 70,250 120,270
         C 130,275 140,260 150,240
         C 160,260 170,275 180,270
         C 230,250 250,200 245,140
         C 240,80 200,55 150,60 Z"
      fill="#4A2810"/>
```

### Individual Strands (semi-realistic only)

**Use for:** Realistic or semi-realistic portraits where the reference shows visible strand detail.

Each strand is a **filled tapered shape** (not a stroked path) — wider at the root, tapering to a point at the tip. Use the centerline-to-offset-curves technique from `styles/styles-curves-and-shapes.md`.

**Warning:** Strand-by-strand construction is extremely path-heavy (hundreds of paths). Only use it when the reference clearly shows individual strands. For most work, the hybrid approach below is better.

### Hybrid (best balance)

Solid mass base shape for coverage, then overlay strand groups for texture and depth. The mass provides coverage; the strand groups add visual interest without excessive path count.

1. Base silhouette (solid fill, mid-tone color)
2. Shadow shapes (darker, at roots and under overlaps)
3. Strand groups (5-15 tapered paths suggesting hair direction)
4. Highlight shapes (lighter, on outer curves where light catches)

## Layering Structure

Hair is split across multiple z-layers because it wraps around the head:

| Layer | Z-Order | Contains |
|---|---|---|
| Back hair | Behind head/ears | Hair visible behind the head silhouette |
| Head/face | Middle | Face shape, ears |
| Front hair | Above face | Bangs, side locks, any hair falling over the face |
| Hat (if present) | Top | Covers hair; tufts poke out from underneath |

This maps directly to SVG element ordering — earlier elements are behind later elements.

## Clumps & Bangs (Anime/Cartoon Style)

Anime and cartoon hair is drawn as discrete **clumps** rather than individual strands. Each clump is a ribbon shape — wider at the base, tapering to a point.

### Constructing a clump

Each clump is a closed filled path:

```xml
<!-- Single hair clump: wide at scalp, tapers to point -->
<path d="M 120,80 C 115,100 105,140 100,170
         C 108,145 118,105 125,80 Z"
      fill="#4A2810"/>
```

The outer edge curves one way, the inner edge curves back — creating a ribbon that narrows to a point.

### Bangs/fringe

- Bangs radiate from the parting point (near top of head)
- Each bang clump curves outward and downward, ending at or below eyebrow line
- Use 2-5 clumps for simple styles, more for detailed styles
- Vary clump width and length — uniform clumps look mechanical

### Spiky hair

- Same clump structure but with sharper control point angles
- Points extend outward/upward from the head
- Each spike widens at the base and sharpens at the tip
- More aggressive Bezier control point offsets for gravity-defying shapes

## Hair Shine & Highlights

The primary highlight band runs roughly horizontally across the upper portion of the hair, following the curvature of the skull — typically 1/3 to 1/2 way down from the crown.

### Highlight shapes by style

- **Zigzag band** — Horizontal band with jagged top/bottom edges (classic anime)
- **Smooth curved band** — Follows skull curvature with soft edges (semi-realistic)
- **Scattered spots** — Small highlights at bends/curves of individual clumps
- **Line highlights** — Thin lighter paths following hair grain direction

### SVG construction

The cleanest approach: draw the highlight as a separate lighter-colored path, then clip it to the hair silhouette so it doesn't bleed outside:

```xml
<clipPath id="hair-clip">
  <path d="[hair silhouette path]"/>
</clipPath>

<!-- Highlight clipped to hair boundary -->
<path d="M 80,120 C 100,110 150,105 200,110 C 220,112 230,118 240,125
         L 240,135 C 220,128 150,115 80,130 Z"
      fill="#FFFFFF" opacity="0.25"
      clip-path="url(#hair-clip)"/>
```

For soft-edged highlights (more realistic), use `<mask>` with gradient fills instead of `<clipPath>`.

**Placement rules:**
- Highlights go on the outer/top surfaces where light catches — never in shadowed areas
- Each clump can have its own mini-highlight at its curve point
- The highlight band follows the 3D curvature of the skull, not a flat horizontal line

## Color & Gradients

### Uniform color (cartoon/flat)
- Single `fill` on the base shape
- Shadows as separate darker paths
- Highlights as separate lighter paths with reduced opacity

### Multi-tone (semi-realistic)
- Base fill in mid-tone
- Lowlights: Darker shapes at roots, under overlaps, between clumps
- Highlights: Lighter shapes on outer curves, light-catching surfaces
- Each tone is its own SVG element: base → lowlights → highlights

### Gradient techniques
- `<linearGradient>` for overall color shifts (ombre: dark roots to lighter tips)
- `<radialGradient>` for localized shine spots at bend points
- Use `gradientUnits="userSpaceOnUse"` when you need precise gradient positioning

## Hair Type Construction

### Straight hair
- Fewest control points — nearly straight Bezier segments with minimal handle deflection
- Clumps hang parallel, following gravity
- Clean sharp edges on clump boundaries
- Highlight band is relatively straight across the hair

### Wavy hair
- S-curve construction: alternating Bezier curves creating sinusoidal flow
- Use `C` then `S` (smooth continuation) for each wave cycle
- Waves become more pronounced at the ends (further from scalp)
- Clumps follow the same wave pattern but offset slightly from each other

### Curly hair
- Highest control point density — tight successive curves with large handle offsets
- Each curl is a series of overlapping C-curves forming a spiral or ringlet
- Significantly more volume — silhouette extends further from the head
- Individual curls overlap extensively, so z-ordering of curl elements matters
- For tight curls: consider using `<use>` to reuse curl shapes with transforms
- Shadows are deeper and more frequent due to overlapping surfaces

### Very short / buzzcut
- Single shape with a subtle gradient or stipple-like texture
- No individual strands or clumps — texture suggested, not drawn
- The head shape shows through more — less silhouette extension

## Interactions with Other Features

### Hat interaction
- Hair compresses/flattens where the hat sits — don't draw full volume under the hat
- Visible hair: tufts at the sides, bangs peeking out front, hair flowing out back
- Hat must be higher z-order than hair
- Side tufts originate from beneath the hat edge, not floating disconnected

### Ear interaction
- Hair behind ears: drawn in the back hair layer, visible on both sides of the head
- Hair over ears: front hair layer covers the ear; ear may peek through gaps
- Hair tucked behind ear: path routes behind the ear shape, reappears below
- Offset slightly from the ear boundary for a natural look

### Forehead boundary
- The hairline shape determines how much forehead is visible
- Bangs may fully cover the forehead (no forehead path needed) or partially reveal it
- Hairline styles: widow's peak, straight, rounded, receding — match the reference

### Wind effects
- Clumps extend and curve in the wind direction
- Windward side: more compressed clumps. Leeward: fanned out, longer
- Add thin flyaway strands breaking away from the main mass
- Flyaways must originate from the main hair body, never float independently

## Common Mistakes

- **Over-detailing for the style** — individual strands in a flat cartoon
- **Under-detailing for the style** — flat blob for semi-realistic work
- **Ignoring the skull** — hair that doesn't follow head curvature looks like a floating wig
- **Perfect symmetry** — real hair is almost never symmetric; slight asymmetry looks natural
- **Wrong flow direction** — all hair originates from the scalp and flows outward/downward
- **Flat highlights** — highlight bands should follow skull curvature, not be flat horizontal stripes
- **Disconnected flyaways** — loose strands must originate from the main mass
- **Drawing hair that doesn't interact with the hat brim**
- **Wrong z-ordering** — back hair behind head, front hair above face, hat above all
- **Matching clump sizes exactly** — vary width and length for natural appearance

## Performance Notes

Hair can easily become the most path-heavy feature in a portrait SVG. Manage complexity:
- Use `<clipPath>` to contain highlight/shadow shapes within the hair silhouette rather than tracing each one precisely
- Reuse shapes with `<use>` for repetitive curls or strand groups
- Match detail level to the art style — don't add strand detail that won't be visible at the target display size
