# Feature Reference: Body, Clothing & Hands

For full-body character SVGs. The body is where art style has the biggest impact on construction complexity — a chibi body might be 15 elements, a semi-realistic one 120+.

## Body Proportions by Art Style

Match the proportion system to the reference before drawing anything:

| Style | Head Heights | Key Simplifications |
|---|---|---|
| Chibi | 1.5-2.5 | No joints, blob limbs, dot hands, head is 40-50% of total |
| Cartoon | 2.5-3.5 | Simplified joints, tube limbs, 4-finger hands |
| Anime/stylized | 4-6 | Articulated joints, defined segments, full hands |
| Realistic | 7-8 | Full anatomy, muscle definition, detailed hands |

**Always measure the head-to-body ratio in the reference first.** This single measurement determines the entire construction approach.

## Pre-Drawing Checklists

### Torso
- [ ] Body shape — round, rectangular, what proportions?
- [ ] Clothing — what's worn? Tucked in? Layered?
- [ ] How does the torso connect to the head? (neck visible? how thick?)
- [ ] How does the torso connect to arms and legs?
- [ ] Waist definition — none (chibi), slight curve (cartoon), defined (anime)?

### Arms
- [ ] Position — at sides, crossed, raised, holding something?
- [ ] Proportions — length relative to body, thickness?
- [ ] Are hands visible? How detailed?
- [ ] Sleeves — where do they end? How do they interact with the arm?
- [ ] Which arm is in front, which behind the body?

### Legs
- [ ] Stance — together, apart, walking, sitting?
- [ ] Proportions — length relative to body?
- [ ] Are feet/shoes visible? What type?
- [ ] Pants/skirt covering legs? Where does clothing end?
- [ ] Which leg is in front?

### Hands (if visible)
- [ ] How many fingers? (4-finger cartoon, 5-finger, mitten)
- [ ] What gesture? (open, fist, pointing, holding)
- [ ] How simplified? (sausage tubes, articulated, realistic)
- [ ] Size relative to face? (cartoon hands are often oversized)

## The Neck-Shoulder Connection

This is the #1 failure point in character SVGs. Getting it wrong makes the head look disconnected.

### Key principles
- **Neck tapers** — slightly thinner at the top, widening into the shoulders. Never parallel lines.
- **Shoulders slope down** — the trapezius muscle creates a downward slope from neck to shoulder tip. Never horizontal.
- **Neck connects INTO shoulders** — the silhouette should be one smooth path from ear to shoulder tip, not a cylinder sitting on a platform.

### SVG construction order
1. Draw torso/shoulder shape first (establishes the base)
2. Neck emerges from the shoulder shape (not sitting on top of it)
3. Head overlaps the top of the neck
4. Ideally one continuous `<path>` for the neck-to-shoulder silhouette

### By style
- **Chibi:** Neck can be omitted — head sits directly on body
- **Cartoon:** Short neck, clear trapezius slope, one smooth path from ear to shoulder
- **Anime:** Slender neck, subtle muscle hints, visible collarbones in close-ups
- **Realistic:** Full muscle definition, visible tendons

## SVG Layering for Poses

SVG renders in document order — later elements paint over earlier ones. This is critical for overlapping limbs.

```xml
<g id="character">
  <g id="back-arm">...</g>      <!-- arm behind body -->
  <g id="back-leg">...</g>      <!-- leg behind body -->
  <g id="torso">...</g>
  <g id="clothing">...</g>
  <g id="front-leg">...</g>     <!-- leg in front -->
  <g id="front-arm">...</g>     <!-- arm in front -->
  <g id="head">...</g>
</g>
```

For complex poses (crossed arms, overlapping legs), split limbs into segments (upper arm, forearm, hand) and interleave them with the torso group as needed.

### Foreshortened limbs
When a limb points toward the viewer:
- Make it shorter and wider than normal
- Closer segments appear larger, farther segments smaller
- Use overlapping shapes rather than elongated ones
- Resist the urge to draw the limb at full length

## Hand Construction

### By style

**Mitten (chibi/super-deformed):**
Single rounded shape, thumb as a small bump. One `<path>`.

**4-finger cartoon (industry standard):**
- Palm as a rounded shape
- 4 sausage-shaped finger paths
- Thumb as a separate tapered path
- Fingers are thicker and stubbier than real proportions

**5-finger simplified (anime):**
- Palm + 5 tapered tube paths
- No knuckle detail
- Optional nail indicators as small curved lines at fingertips

**Semi-realistic:**
- Width variations at joints
- Nail overlays as small paths
- Middle finger roughly equals palm length

### Gesture construction
- **Pointing:** one finger extended, others curled (overlapping paths)
- **Fist:** rounded shape with thumb across front, knuckle ridge visible
- **Open hand:** fan arrangement — individual finger paths with `rotate` transforms
- **Holding object:** fingers wrap around, `<clipPath>` shows object between fingers

## Clothing Folds & Wrinkles

Folds originate from **tension points**: joints (elbows, knees, waist), gravity pull, and seams/fasteners.

### Fold types that matter for SVG

| Fold Type | Where It Appears | SVG Approach |
|---|---|---|
| Pipe fold | Hanging fabric (curtains, loose skirts) | Parallel curved paths with gradient between |
| U-shape/diaper | Fabric sagging between two support points | Nested U-shaped bezier paths |
| Zigzag | Compressed fabric (pushed sleeves, bent joints) | Alternating angled paths |
| Spiral | Gathered fabric (waistbands, twisted scarves) | Paths radiating from a center point |
| Half-lock | Deep crease at bend (elbow, knee) | Tight V or U nested paths at the bend |

### Construction approach
1. Draw the garment base shape as a filled `<path>`
2. Add fold lines as separate `<path>` elements (stroke only, no fill)
3. Shadow shapes between folds: darker fill, partial opacity
4. Highlight shapes on fold peaks: lighter fill or white, low opacity

### Material affects fold style

| Material | Folds | SVG Approach |
|---|---|---|
| Thick (denim, leather) | Few, wide, smooth | Fewer paths, gentle curves, wide spacing |
| Medium (cotton, linen) | Moderate, mixed | Balanced path count |
| Thin (silk, chiffon) | Many, tight, intricate | Many paths, tight curves |
| Stiff (armor, starched) | Angular, geometric | Sharper control points, less curvature |

## Clothing Patterns with `<pattern>`

### Stripes
```xml
<pattern id="stripes" patternUnits="userSpaceOnUse" width="10" height="10">
  <rect width="5" height="10" fill="#003366"/>
  <rect x="5" width="5" height="10" fill="#FFFFFF"/>
</pattern>
```
Use `patternTransform="rotate(45)"` for diagonal stripes. Slight rotation (5-10 degrees) adds realism even for "vertical" stripes.

### Polka dots
```xml
<pattern id="dots" patternUnits="userSpaceOnUse" width="20" height="20">
  <circle cx="10" cy="10" r="4" fill="white"/>
</pattern>
```

### Plaid
Layer semi-transparent horizontal and vertical stripes with accent lines.

### Applying patterns to garments
Define the garment shape, then clip the pattern to it:
```xml
<defs>
  <clipPath id="shirt-clip">
    <path d="[shirt outline]"/>
  </clipPath>
</defs>
<path d="[shirt]" fill="#basecolor"/>
<rect width="100%" height="100%" fill="url(#stripes)" clip-path="url(#shirt-clip)"/>
<path d="[fold shadows]" fill="rgba(0,0,0,0.15)"/>
```

## Shoes & Footwear

### By type

**Sneaker:** Rounded toe box, visible sole, lace area. Side view is most recognizable. Main body as one `<path>`, sole as separate darker `<path>`.

**Boot:** Taller upper extending above ankle. Add fold lines at ankle bend (zigzag folds).

**High heel:** Foot at an incline — sole curves up at back, separate heel `<path>` as tapered shape.

**Sandal:** Minimal — just sole `<path>` and strap paths.

### Construction order
1. Foot position (even if invisible under the shoe)
2. Sole — narrower at front, wider at back, slight curve
3. Upper — shape depends on shoe type
4. Details — laces, buckles, stitching

### Style simplification
- Chibi: shoes are simple rounded nubs
- Cartoon: recognizable silhouette, minimal detail
- Anime: clear sole line, simplified lace area
- Realistic: full construction with material textures

## Outline Consistency

Body outlines must match the face outline style throughout:
- Same color
- Similar thickness
- Same technique (filled shapes for variable width, strokes for uniform)

Inconsistency between face and body outline style is one of the most visible quality issues.

## Common Mistakes

- **Cylinder neck** — neck should taper, not be parallel lines
- **Horizontal shoulders** — shoulders slope downward from the neck
- **Head-on-a-stick** — neck must connect smoothly into shoulders, not sit on top
- **Wrong proportions for the style** — measure head heights before drawing
- **Inconsistent outline weight** between face and body
- **All limbs at full length** — foreshortened limbs need to be compressed
- **Uniform fold patterns** — vary fold depth and spacing; identical folds look mechanical
- **Pattern not following garment shape** — use `<clipPath>` to constrain patterns, and consider `patternTransform` for drape
- **Hands too detailed for the style** — match hand complexity to the art style level
