# Feature Reference: Eyes

Eyes carry the most character in a face. Small errors are immediately noticeable. Always build each eye as a standalone SVG and compare against its cropped reference.

## Pre-Drawing Checklist

Study the cropped reference and answer ALL of these before writing any SVG:

### Shape & Size
- [ ] Is the eye circular, oval, or another shape?
- [ ] What are the proportions? (wider than tall? taller than wide?)
- [ ] How large is the eye relative to the face? (cartoon eyes are often 30-40% of face width)

### Outline
- [ ] What is the outline thickness? Is it uniform or variable?
- [ ] If variable: where is it thickest? thinnest? by how much?
- [ ] Is the outline a closed ring, or does it have gaps?
- [ ] What technique creates the thickness variation? (offset shapes? brush stroke?)

### Sclera (White)
- [ ] Is it pure white or off-white?
- [ ] Is there any shading on the white?

### Pupil/Iris
- [ ] How large is the pupil relative to the sclera? (percentage of eye area)
- [ ] Is the pupil shifted from center? In which direction? By how much?
- [ ] Does the pupil touch the sclera edge anywhere, or is there a gap all around?
- [ ] What is the gap size on each side? (inner, outer, top, bottom)
- [ ] Is the pupil pure black, or does it have color/gradient?
- [ ] Is there a visible iris ring, or is it all one dark mass?

### Highlights
- [ ] How many highlight circles/dots are there? (usually 1-2)
- [ ] Where is each one positioned? (upper-left? upper-right? center?)
- [ ] How large is each highlight relative to the pupil?
- [ ] Are highlights pure white or slightly transparent?

### Gaze Direction
- [ ] Which direction is the eye looking?
- [ ] How subtle is the gaze shift? (barely off-center vs dramatically shifted)
- [ ] Do both eyes look in the same direction?

## SVG Construction

### Recommended Layer Order (bottom to top)
1. Dark outline shape (ellipse or path)
2. White sclera shape (slightly smaller, possibly offset)
3. Dark pupil/iris (positioned according to gaze)
4. Highlight circle(s) on top

### Outline Technique: Offset Ellipses

For an outline that's heavier at the bottom:
```xml
<!-- Outer dark shape -->
<ellipse cx="100" cy="100" rx="90" ry="92" fill="#3a3a3a"/>
<!-- Inner white, shifted slightly up-right = thicker outline at bottom-left -->
<ellipse cx="102" cy="98" rx="80" ry="82" fill="white"/>
```

The offset between outer and inner controls thickness variation:
- `cx` offset: shifts thickness left/right
- `cy` offset: shifts thickness up/down
- Radius difference: controls base thickness

**Start subtle** (2-3px offset). Dramatic offsets make the eye look asymmetric rather than "weighted."

### Common Mistakes
- Making the outline variation too dramatic (looks broken, not brush-like)
- Pupil too small relative to sclera (cartoon eyes often have huge pupils)
- Highlight in the wrong position (always verify against reference)
- Assuming both eyes are identical (they rarely are)
- Adding secondary highlights that don't exist in the reference

## Right Eye: NOT Just a Mirror

After building the left eye, study the right eye reference independently. Check:
- Is the outline weight distribution the same or different?
- Is the highlight in the same relative position?
- Is the gaze shift the same magnitude?
- Is the pupil the same size?

Build the right eye from scratch using the right eye reference crop, not by flipping the left eye SVG.
