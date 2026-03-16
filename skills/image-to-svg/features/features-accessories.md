# Feature Reference: Accessories & Clothing

Hats, glasses, jewelry, tools, clothing details, badges, etc.

## Pre-Drawing Checklist (General)

- [ ] What is the accessory and what's its function in the image?
- [ ] What's the z-order? (hat on top of head, glasses over eyes, etc.)
- [ ] How does it interact with the features it overlaps?
- [ ] Does it partially hide other features? (hat brim over forehead, collar over chin)
- [ ] What's the material/texture? How is it depicted in this art style?

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

## Glasses

### Specific Checklist
- [ ] Frame shape — round, square, cat-eye?
- [ ] Frame thickness?
- [ ] Lens — transparent, colored, reflective?
- [ ] Bridge between lenses?
- [ ] How do frames interact with eye outlines?

## Clothing

### Specific Checklist
- [ ] What garments are visible?
- [ ] How do they fit? (loose, tight, oversized?)
- [ ] Wrinkles/folds — how are they depicted?
- [ ] Color and pattern?
- [ ] Pockets, buttons, zippers — which details are included?
- [ ] Where does clothing meet skin? How is that boundary drawn?

## Common Mistakes
- Accessories feel "floating" — not properly seated on the character
- Wrong z-order (hat behind hair instead of on top)
- Accessory outline style inconsistent with character outline style
- Too much detail on accessories vs the character's art style
- Forgetting how the accessory affects visibility of features beneath it
