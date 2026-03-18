# Feature Reference: Plants & Flowers

Plants use radial symmetry, organic curves, and layered depth. The key SVG techniques are `<use>` + `rotate` for petal/leaf repetition and `<clipPath>` for containing vein detail within leaf boundaries.

## Decomposition

| Feature | What It Is | Key Challenge |
|---|---|---|
| Petals | Individual petal shapes arranged radially | Two-Bezier petal path; use `<use>` + `rotate` for symmetry |
| Flower center | Stamen/pistil cluster or contrasting disc | Circle or cluster of small circles; color contrast with petals |
| Leaves | Flat green shapes with vein detail | Bezier outline, gradient fill, vein paths clipped within |
| Stems | Connecting structure | Slightly curved path; consistent width or slight taper |
| Thorns/spines | Small pointed projections on stems | Tiny triangle paths positioned along stem |
| Bark/trunk | Woody stem structure for trees | Brown fill with grain pattern or line texture |
| Fruit/berries | Produced by the plant | Small colored circles/ellipses in clusters |
| Pot/vase (if present) | Container context | Simple geometric shape; ceramic/terracotta coloring |

## Flower Construction

### Single petal
Two cubic Bezier curves sharing start and end points with different control points — wide at middle, pointed at tip and base:
```xml
<path d="M 0,0 C 10,-20 30,-20 40,0 C 30,20 10,20 0,0 Z" fill="#FF69B4"/>
```

### Flower assembly
Define one petal in `<defs>`, stamp with `<use>` + `rotate`:
```xml
<defs>
  <path id="petal" d="M 0,-10 C 8,-35 15,-35 0,-55 C -15,-35 -8,-35 0,-10 Z" fill="#FF69B4"/>
</defs>
<g transform="translate(100,100)">
  <use href="#petal" transform="rotate(0)"/>
  <use href="#petal" transform="rotate(72)"/>
  <use href="#petal" transform="rotate(144)"/>
  <use href="#petal" transform="rotate(216)"/>
  <use href="#petal" transform="rotate(288)"/>
  <circle r="8" fill="#FFD700"/>  <!-- center -->
</g>
```

Rotation increment = 360 / number_of_petals. For 5 petals: 72 degrees. For 6: 60. For 8: 45.

### Petal depth and overlap
- Rear petals: slightly darker fill (drawn first in SVG order)
- Front petals: full color (drawn last, highest z-order)
- Thin dark shapes at petal bases for inter-petal shadow
- For flowers where not all petals are identical (roses, orchids), draw each petal individually rather than using `<use>`

### Petal variation by flower type
- **Simple/daisy:** Elongated elliptical petals, all similar, evenly spaced
- **Rose:** Overlapping curved petals spiraling inward, each slightly different
- **Tulip:** 3-6 large cupping petals forming a bowl shape
- **Sunflower:** Many thin ray petals around a large textured disc center

## Leaf Construction

### Basic leaf
Two mirrored quadratic Beziers forming a pointed shape:
```xml
<path d="M 0,50 Q 25,0 50,50 Q 25,100 0,50 Z" fill="#228B22"/>
```

For more organic shapes, use cubic Beziers (`C`) for independent control over each side's curvature.

### Leaf color
Add a `linearGradient` — lighter along the center vein, darker at the edges:
```xml
<linearGradient id="leafGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#1B5E20"/>
  <stop offset="50%" stop-color="#43A047"/>
  <stop offset="100%" stop-color="#1B5E20"/>
</linearGradient>
```

### Leaf veins
- Central vein: tapered filled path from base to tip (or a stroke that thins toward the tip)
- Side veins: thinner paths branching at 30-45 degree angles from the central vein
- Clip all veins to the leaf body with `<clipPath>` so they don't bleed outside

```xml
<clipPath id="leaf-clip">
  <path d="[leaf outline]"/>
</clipPath>
<g clip-path="url(#leaf-clip)">
  <path d="[central vein]" stroke="#2E7D32" stroke-width="1.5"/>
  <path d="[side veins]" stroke="#2E7D32" stroke-width="0.8"/>
</g>
```

### Compound leaves (fern, palm)
- Main stem: curved `path` stroke
- Leaflets: small leaf shapes placed along the stem using `<use>` with transforms
- Each leaflet rotated to follow the stem angle at its attachment point

## Stem Construction

- **Simple:** slightly curved `path` with `stroke-width="2-4"`, dark green
- **Organic:** use a filled tapered shape (wider at base, thinner at top) per `styles/styles-curves-and-shapes.md`
- **With thorns:** small triangular `path` shapes positioned along the stem
- **Branching:** main stem splits into sub-paths at branch points

## Tree & Bush Construction

### Tree canopy
- **Simple/cartoon:** overlapping circles or ellipses in varying greens (3-5 shapes)
- **More organic:** single cloud-like blob shape using `C` curves
- Layer 2-3 green tones: darker at base/interior, lighter at top where light hits

### Trunk
- Brown rectangle or slightly tapered `path`
- Wood texture: subtle `<pattern>` or a few vertical stroke lines
- Roots (if visible): branching `path` strokes at the base

### Bush/shrub
- Similar to canopy but wider and lower to the ground
- More irregular silhouette than a tree canopy
- Flowers or berries as small colored dots scattered on the surface

## Potted Plant Context

When a plant is in a pot or vase:
- Pot is usually a simple geometric shape (trapezoid, cylinder, rounded rectangle)
- Terracotta: warm brown/orange with subtle gradient
- Ceramic: smoother fill, possible pattern, highlight stripe
- Soil visible at the top: dark brown fill with slight texture
- The plant emerges from the pot — some overlap at the rim

## Emoji-Scale Recognition

| Item | Must-have features |
|---|---|
| Flower | 5 colored petals in a ring, contrasting center circle |
| Herb/leaf | Green elongated shape, central vein line |
| Tree | Green blob canopy on brown rectangle trunk |
| Cactus | Green column(s) with arms, small lines for spines |

At small sizes: flat fills, bold outlines, no vein detail or gradients.

## Common Mistakes

- **Identical petals** — vary size, angle, or color slightly between petals for natural look (unless the style is explicitly geometric)
- **Flat green everywhere** — use 2-3 green tones to distinguish light-catching surfaces from shadowed ones
- **Veins outside the leaf** — always use `<clipPath>` to contain vein paths
- **Stems too straight** — real stems have slight curves; use a gentle Bezier, not a straight line
- **Forgetting petal overlap shadows** — thin dark shapes between overlapping petals add depth
- **Tree canopy as a perfect circle** — use irregular organic shapes unless the style is geometric
