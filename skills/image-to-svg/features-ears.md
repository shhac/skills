# Feature Reference: Ears

Ears are tricky because they interact heavily with the head shape and any headwear.

## Pre-Drawing Checklist

### Shape
- [ ] What shape? (round, pointed, elf-like, realistic?)
- [ ] How large relative to the head?
- [ ] What angle do they point? (horizontal, upward, downward?)
- [ ] Are they symmetric or do left/right differ?

### Position & Attachment
- [ ] Where do the ears attach to the head? (what y-level?)
- [ ] Are they behind the head (z-order) or in front?
- [ ] How far do they extend from the head?
- [ ] Does the face outline stop at the ear attachment point?
- [ ] Does the ear outline connect to or overlap the face outline?

### Internal Detail
- [ ] Is there inner ear shading/detail?
- [ ] What color is the inner ear vs outer ear?
- [ ] How many layers of shape are there?

### Outline
- [ ] Does the ear have its own outline?
- [ ] Is the outline continuous or brush strokes?
- [ ] Outline thickness — uniform or variable?
- [ ] Does the ear outline interact with the face outline?

## Critical: Ear-Face Connection

The face outline strokes should typically STOP at the ear attachment point. This makes the ears feel like they grow FROM the head. If the face strokes go above the ears, the ears look like they're floating behind the head.

## SVG Construction

### Z-Order
Ears are usually drawn BEFORE the face (behind it in z-order):
```xml
<g id="left-ear">...</g>
<g id="right-ear">...</g>
<g id="face">...</g>  <!-- drawn on top, covers ear base -->
```

### Typical Structure
```xml
<g id="left-ear">
  <!-- Outline shape -->
  <path d="..." fill="#3a3a3a"/>
  <!-- Fill shape (slightly inset) -->
  <path d="..." fill="#skinColor"/>
  <!-- Inner ear shading -->
  <path d="..." fill="#darkerSkinColor"/>
</g>
```

## Common Mistakes
- Ears too small (they should be prominent in cartoon styles)
- Ears pointing in the wrong direction
- Face outline going above ear level (disconnects the ears)
- Identical left and right ears (study each independently)
- Inner ear detail missing or wrong color
