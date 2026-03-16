# Feature Reference: Face Shape

The face shape is the foundation layer. Get it right before adding features on top.

## What "Face Shape" Includes

1. **The fill shape** — the colored area of the face (the "oval")
2. **Contour strokes** — brush marks that define the edges (NOT a full outline)
3. **Shadows** — subtle shading (chin shadow, cheek shading)

These are THREE separate concerns. Don't conflate them.

## Pre-Drawing Checklist

### Fill Shape
- [ ] What is the overall shape? (oval, round, egg-shaped, square-ish?)
- [ ] Is it wider than tall, or taller than wide? By how much?
- [ ] Is the forehead narrower than the cheeks?
- [ ] Is the chin narrower than the cheeks? Pointed or rounded?
- [ ] Is the top of the head visible, or hidden by hair/hat?

### Color
- [ ] What is the base skin color? (be specific — hex value)
- [ ] Is there a gradient? Where is it lighter vs darker?
- [ ] Where is the gradient center? (usually slightly above center)

### Contour Strokes — Critical Analysis
- [ ] Where do the strokes appear? (sides only? chin? forehead?)
- [ ] Where are there NO strokes? (gaps are intentional — they mean something)
- [ ] Do the strokes meet at the bottom/chin, or is there a gap?
- [ ] Where do the strokes start at the top? (ear level? forehead? hidden by hat?)
- [ ] What do the gaps communicate? (e.g., no chin stroke = chin shadow defines the edge instead)

### Stroke Interaction with Other Features
- [ ] Do the cheek strokes connect with the ears?
- [ ] Do strokes at the top interact with hair or hat?
- [ ] Does the stroke stopping point affect how ears read? (stopping at ear level makes ears feel "connected to" the head rather than "behind" it)

### Shadows
- [ ] Is there a chin shadow? What color? How subtle?
- [ ] Are there cheek shadows?
- [ ] Is the shadow a gradient, a solid shape, or an outline?

## SVG Construction

### Fill Shape
Use a `<path>` with bezier curves, not a simple `<ellipse>`. Real faces are organic shapes.

### Contour Strokes

**Key insight: contour strokes are NOT outlines.**

An outline traces the entire perimeter of the shape. Contour strokes are individual brush marks placed at specific edges. They:
- Start and end at specific points (they don't go all the way around)
- May leave gaps (e.g., open chin)
- Follow the face fill edge (straddle it — half inside, half outside)
- Have character: thickness variation, taper at ends

Use the actual face fill path coordinates for stroke paths:
```xml
<!-- Extract a segment of the face fill path for the stroke -->
<path d="M 98 240 C 82 262, 78 290, 84 320 C 90 352, 110 380, 138 402"
      fill="none" stroke="#3a3a3a" stroke-width="8" stroke-linecap="round"/>
```

This guarantees the stroke sits ON the face edge.

### Chin Shadow
Usually a subtle gradient or semi-transparent ellipse below the mouth:
```xml
<ellipse cx="256" cy="430" rx="80" ry="25" fill="#829555" opacity="0.3"/>
```

## Common Mistakes
- Drawing a complete outline around the face (the original almost certainly has gaps)
- Strokes floating outside the face edge (looks like a beard/shadow)
- Strokes going above where they should (above ear level = ears look disconnected)
- Adding a chin outline when the original uses shadow instead
- Making the shape too geometric (use organic bezier curves)
