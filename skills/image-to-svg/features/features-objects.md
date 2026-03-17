# Feature Reference: Complex Objects

Real-world objects have internal structure, multiple visible surfaces, perspective distortion, and lighting complexity. A silhouette with flat color reads as an icon. To produce a convincing recreation, decompose the object into its structural parts and build each with the appropriate curve techniques.

## The Structural Decomposition Mindset

### Beyond the Silhouette

A basic approach draws the outline and fills it. This fails for objects with visible internal structure because:
- The object's identity comes from its **parts and their relationships**, not just its outline
- Different surfaces face different directions, catching light differently
- Structural elements (ribs, seams, edges, joints) create visual rhythm
- The inside may be partially visible and looks fundamentally different from the outside

**Always ask:** What parts does this object have? What's the relationship between them? What would I see if I took it apart?

### Multi-Surface Visibility

Many objects show more than one surface from any viewing angle:
- **Inside vs. outside** — cups, umbrellas, bags, boxes, shoes
- **Top vs. side** — books, tables, buildings, cakes
- **Front vs. back** — chairs, picture frames, folded cloth

Each visible surface needs its own treatment because:
- They face different directions relative to the light
- They may have different colors, textures, or materials
- The transition between surfaces (the edge/rim) is a key visual element
- Perspective means surfaces have different amounts of foreshortening

### Perspective on Curved Surfaces

When an object is viewed at an angle:
- Surfaces facing toward the viewer are wider, more visible
- Surfaces facing away are foreshortened (compressed)
- Curved surfaces create a **gradual transition** from facing-toward to facing-away — this gradient is what makes them read as curved
- Ribs, seams, and structural lines follow the surface curvature — they **converge toward the edges** in perspective and are **wider apart in the center**

## Lighting on Faceted and Curved Surfaces

### Faceted Surfaces (panels separated by edges)

Adjacent panels face different directions, so each catches light at a different angle:
- Panels facing the light are brighter
- Panels facing away are darker
- **Alternating light/dark panels** is the visual signature of faceted objects (umbrella canopy, diamond facets, folded paper)
- The difference can be subtle (5-10% value shift) or dramatic — match the reference

### Curved Surfaces

Light across a smooth curve creates a gradient from highlight to shadow:
- **Highlight zone** — where the surface normal points most directly at the light
- **Midtone zone** — gradual transition
- **Shadow zone** — surface faces away from light
- **Reflected light** — subtle brightening at the very edge of the shadow side from environmental light bouncing back
- Use SVG gradients oriented along the curve's cross-section to simulate this

### Structural Elements Casting Shadows

Ribs, edges, and raised features cast **thin shadows** on adjacent surfaces:
- A rib on the inside of an umbrella casts a narrow shadow on the fabric panel next to it
- A rim casts a shadow on the interior
- These are small dark shapes — thin filled paths or narrow gradient overlays

## Worked Example: Umbrella

An umbrella demonstrates every structural challenge — multiple surfaces, faceted panels, curved ribs, a handle with a hook, and perspective distortion.

### Decomposition

| Feature | What It Is | Key Challenge |
|---|---|---|
| Canopy exterior | The visible outer dome | Faceted panels with scalloped bottom edge |
| Canopy interior | Inside surface (if visible from angle) | Concave panels, visible ribs, different lighting |
| Ribs (exterior) | Structural ridges on the outside | Radial lines that follow the dome curvature |
| Ribs (interior) | Structural spokes visible inside | Tapered, casting shadows on fabric panels |
| Scalloped edge | The wavy bottom hem of the canopy | Alternating concave arcs between rib endpoints |
| Shaft | The central pole | Slight taper, runs through the canopy |
| Handle | J-hook at the bottom | Smooth curves with natural thickness variation |
| Tip/ferrule | Small point at the apex | Teardrop or finial shape |
| Runner/mechanism | Where ribs attach to the shaft | Small mechanical cluster |

### Pre-Drawing Checklist

#### Perspective & Viewing Angle
- [ ] What angle are we viewing from? (Side? Below? Above at an angle?)
- [ ] How much of the interior is visible? (None? A sliver? The full underside?)
- [ ] Which direction does the umbrella face? (Tilted toward viewer? Away? Straight up?)
- [ ] How much foreshortening is there on the canopy? (A circle from directly below, an ellipse from the side)

#### Canopy Exterior
- [ ] How many panels are visible from this angle?
- [ ] Is the fabric taut or slightly loose between ribs?
- [ ] What's the color? Is it uniform, patterned, or translucent?
- [ ] How does light hit each visible panel? (Which panels are brighter, which darker?)
- [ ] Where is the highlight on the dome surface?
- [ ] Is there a visible edge/rim at the bottom, or does the fabric just end?

#### Canopy Interior (if visible)
- [ ] How much is visible? (Full underside, or just a rim of interior peeking out?)
- [ ] Is the interior lighter or darker than the exterior?
- [ ] Is the fabric translucent (backlit glow) or opaque?
- [ ] Can you see ribs? How prominent are they?
- [ ] Do the interior panels sag (concave between ribs)?
- [ ] Is there a shadow pattern from the ribs on the fabric?

#### Ribs
- [ ] How many ribs are visible?
- [ ] Are they thick or thin?
- [ ] Do they taper? (Usually thicker near the shaft, thinner at the edge)
- [ ] Are they the same color as the fabric or different? (Often darker, sometimes metallic)
- [ ] Do they curve to follow the canopy surface, or are they more rigid/straight?
- [ ] From this angle, what's the spacing between visible ribs? (Wider in the center, compressed at the edges due to perspective)

#### Shaft
- [ ] What material? (Wood, metal, plastic?)
- [ ] Is it visible above the canopy (through the tip) and below (to the handle)?
- [ ] Is it straight or does it have any taper/character?
- [ ] What color relative to the handle and canopy?

#### Handle
- [ ] What style? (J-hook, straight, T-handle, knob?)
- [ ] How tight is the hook curve?
- [ ] Does it taper? Where is it thickest?
- [ ] Material and color? (Wood, rubber, plastic, bamboo?)
- [ ] Is there a ferrule or end cap?

### SVG Construction Strategy

#### Canopy: Faceted Panels as Individual Fills

**Do not draw the canopy as a single filled circle or dome.** Each visible panel should be its own `<path>`, because panels catch light differently.

The canopy panels are **pie-slice-like wedges** bounded by:
- Two rib lines radiating from the center
- The scalloped bottom edge between those ribs
- The dome curvature at the top

From a side/angled view, panels are **not equal width** — panels facing the viewer are wider, panels curving away are narrow (foreshortened). Getting this uneven spacing right is what makes the umbrella look 3D rather than flat.

Each panel gets a slightly different fill value:
```xml
<!-- Lighter panel (facing toward light) -->
<path d="M 200,60 C 190,100 160,170 130,200
         Q 165,180 200,200
         C 200,150 200,100 200,60 Z"
      fill="#E85050"/>

<!-- Darker panel (facing away from light) -->
<path d="M 200,60 C 200,100 200,150 200,200
         Q 235,180 270,200
         C 240,170 210,100 200,60 Z"
      fill="#C03030"/>
```

#### Scalloped Edge: Quadratic Beziers Between Rib Endpoints

The bottom of the canopy isn't a smooth arc — it dips up between each rib and down at each rib tip. Each scallop is one `Q` command with the control point pulled upward (toward the dome center):

```xml
<!-- Scalloped bottom edge of the canopy -->
<path d="M 60,210 Q 95,190 130,210 Q 165,188 200,210
         Q 235,190 270,210 Q 305,188 340,210"
      fill="none" stroke="#333" stroke-width="2"/>
```

**Vary the scallop depths slightly** — identical scallops look mechanical. Pull the control point higher for wider panels, slightly lower for narrower ones.

In practice, the scalloped edge is usually part of each panel's closed path (the bottom boundary), not a separate stroke.

#### Ribs: Tapered Filled Shapes

Ribs are structural elements with physical presence. Build each as a **filled shape** using the centerline-to-offset-curves technique from `styles/styles-curves-and-shapes.md`:

- Thicker near the shaft/hub
- Thinner at the canopy edge
- Follows the curvature of the canopy surface

```xml
<!-- Single rib: tapered filled shape following the dome curvature -->
<path d="M 198,65 C 195,100 170,160 128,202
         C 170,158 195,95 202,65 Z"
      fill="#555"/>
```

On the interior, add a thin shadow path beside each rib (offset slightly in the light direction) to give them dimensionality.

#### Interior Panels: Concave Between Ribs

If the interior is visible, each panel between two ribs is **concave** (the opposite of the exterior). The fabric sags inward between the rigid rib supports.

Build each interior panel with curves that bow **inward** — control points pulled toward the shaft. These are typically darker than the exterior and may have a slightly different hue (less saturated, more shadowed).

#### Handle: Filled Shape with Smooth Curves

The handle is a **filled closed path** built with cubic Beziers, not a stroked curve. See the hook/J-curve pattern in `styles/styles-curves-and-shapes.md`.

Key characteristics:
- Natural thickness variation (thicker at the bend, slightly thinner along straight sections)
- Smooth entry from the shaft (no abrupt width change)
- Material feel through color and subtle gradients (wood grain = linear gradient, rubber = flat matte)

#### Tip: Small Detailed Shape

A teardrop or pointed finial at the apex. Use a small filled path with cubic Beziers — not a circle. Real tips have a slight point or elongation.

### Layer Order (back to front)

1. Canopy interior panels (if visible)
2. Interior ribs (if visible)
3. Shaft (behind canopy)
4. Canopy exterior panels (back panels first, then front)
5. Exterior ribs
6. Scalloped edge detail / hem
7. Tip/ferrule
8. Shaft (below canopy)
9. Handle

The shaft may need to be split into two layers — the portion above/inside the canopy (behind) and the portion below (in front of nothing, but z-ordered correctly relative to the handle).

## General Object Principles

These patterns from the umbrella apply to any complex object:

### 1. Faceted Surfaces Need Per-Panel Treatment
Whenever an object has panels, facets, or faces (boxes, gems, folded paper, lanterns, polyhedra), build each face as its own path with its own fill value.

### 2. Structural Elements Are Features, Not Lines
Ribs, seams, edges, and joints should be **filled shapes with taper and curvature**, not stroked lines. They have physical width and follow the parent surface.

### 3. Inside ≠ Outside
Any object where the interior is visible needs separate treatment for interior surfaces. The interior is typically:
- Darker (in shadow)
- Different texture or material
- Opposite curvature (convex outside → concave inside)
- Has visible structural elements not seen from outside

### 4. Perspective Unequals Things
Equal-in-reality features become **unequal in the image** due to perspective:
- Equal-width panels become unequal widths
- Equal-spacing ribs become compressed at the edges
- Circular rims become ellipses
- Match the unequal spacing from the reference — don't regularize it

### 5. Light Tells the Shape Story
Two adjacent surfaces reading as "the same brightness" collapses the 3D form. Ensure every surface that faces a different direction has a different value, even if subtle.
