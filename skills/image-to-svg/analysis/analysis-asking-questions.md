# Asking the Right Questions

Before drawing ANYTHING, interrogate the reference image. The goal is to replace assumptions with observations. Most SVG quality issues come from drawing what you THINK is there rather than what IS there.

## Before Starting Any Feature

### Shape Questions
- What is the actual shape? Is it a circle, oval, or irregular path?
- Is it symmetric or asymmetric? In what way?
- What are the proportions? (wider than tall? by how much?)
- Where are the boundaries? Where does this feature start and end?

### Outline/Stroke Questions
- Is there an outline? Is it uniform thickness or does it vary?
- If it varies, WHERE is it thickest? Where is it thinnest?
- Is the outline a continuous line or separate brush strokes?
- Where do the strokes START and END? Do they connect to form a closed shape?
- Are there gaps in the outline? Where and why?
- What color is the outline? (pure black? dark grey? colored?)

### Color Questions
- What is the base color? (be specific — don't just say "green")
- Is the color uniform or does it have a gradient/variation?
- Where is it lighter? Where is it darker? What causes this?
- Are there shadows? Where are they cast from?

### Position Questions
- Where is this feature relative to neighboring features?
- How much space is between this and adjacent elements?
- Does this feature overlap with anything? What's on top?

### Obscured Content Questions
- Is part of this feature hidden behind another element?
- If so, what would the hidden portion look like? (e.g., the top of a head under a hat — it's still round, it doesn't stop flat at the hat brim)
- Should the shape extend continuously under the obscuring element?
- How much extra do I need to draw beyond what's visible?
- What's the simplest reasonable continuation of the shape into the hidden area?

## Feature-Specific Questions

### For Eyes (ask for EACH eye independently)
- How many highlight circles are in the pupil?
- Where exactly is each highlight positioned?
- Does the pupil touch the edge of the sclera, or is there a gap all around?
- How much gap on each side? (inner, outer, top, bottom)
- Which direction is the eye looking? How subtle is the gaze direction?
- Does the outline thickness change around the eye? How?
- How large is the pupil relative to the sclera?

### For Mouth
- Is it open or closed?
- Is the smile symmetric or asymmetric?
- Are teeth visible? How many? Which ones?
- Where does the mouth line start and end?
- How thick is the mouth line? Does it vary?

### For Outlines/Strokes Generally
- Is this an outline that encircles a shape, or a brush stroke that defines an edge?
- If brush strokes: where do they start? Where do they end? Where are the gaps?
- Do strokes from different features connect or overlap?
- What gives the strokes their "character"? Thickness variation? Curvature?

### For Architectural/Structural Elements
- Are the lines truly straight, or is there subtle curvature or distortion (perspective, lens, style)?
- What's the perspective — flat/orthographic, one-point, two-point? This determines how parallel lines converge.
- Are surfaces flat-colored or textured? If textured, can it be approximated with a pattern or gradient?
- Where are the hard edges (walls, rooflines) vs soft edges (shadows, reflections)?
- Are windows/doors identical and repeating? Use `<use>` to define once and stamp.

### For Natural/Organic Elements (landscapes, plants, animals)
- Is this element a distinct shape or a mass of similar shapes? (e.g., a single tree vs a forest canopy)
- How much simplification is appropriate? Count the number of meaningful color bands, not every leaf.
- Where does this element's silhouette overlap with the layer behind it?
- Does depth come from overlapping shapes, color change (atmospheric perspective), or size change?
- For animals: what are the major body masses? (head, torso, limbs — same decomposition as characters, just different anatomy)

### For Text and Typography
- Is the text a key element or incidental? (logo text vs a background sign)
- What's the approximate weight, style, and letter spacing?
- Trace as filled paths — do not use `<text>` elements (the font won't be available)
- Is the text on a curve, perspective-distorted, or flat?

## During Iteration

After each render, compare with the reference crop and ask:
- What's the most obvious difference?
- Is the SIZE right? (most common error: features too small or too large)
- Is the POSITION right?
- Is the COLOR right?
- Is the OUTLINE weight right?
- Am I adding details that aren't in the original?
- Am I missing details that ARE in the original?

## Common Assumption Traps

| Assumption | Reality |
|-----------|---------|
| "Both eyes are the same, just mirrored" | Highlights, outline weight, and gaze may differ |
| "The outline goes all the way around" | Many features have gaps — chin, between ears and face |
| "The outline is uniform thickness" | Almost never — look for where it's thicker and thinner |
| "The pupil is centered in the eye" | Usually shifted in the gaze direction |
| "The highlight is in the upper-right" | Check! Light direction varies |
| "The shape is a simple ellipse/circle" | Study the actual contour — it's usually more organic |
| "I need an outline everywhere" | Some edges are defined by color change alone, no stroke |
| "I only need to draw what's visible" | Hidden portions still need shape continuity — the head extends under the hat, the face extends under the hair. Build complete shapes, not hard-cut fragments |
| "The outline thickness varies dramatically" | Usually much more subtle than you think — check with the reference before exaggerating |
| "Parallel lines stay parallel" | In perspective views, they converge — check vanishing points |
| "The sky is one solid blue" | Almost always a gradient — lighter near the horizon, darker above |
| "I need to trace every leaf/brick/tile" | Use repeating patterns (`<pattern>`) or representative shapes — suggest the texture, don't replicate every instance |
| "Text can use a `<text>` element" | Fonts won't match — trace letterforms as `<path>` elements |
