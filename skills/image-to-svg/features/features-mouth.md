# Feature Reference: Mouth

## Pre-Drawing Checklist

### Shape
- [ ] Open or closed mouth?
- [ ] Symmetric or asymmetric? (smirk vs even smile)
- [ ] How wide is the mouth relative to the face?
- [ ] Where does the mouth line start and end (x coordinates)?
- [ ] What's the curvature? Gentle arc or dramatic curve?

### Line Quality
- [ ] How thick is the mouth line?
- [ ] Does the line thickness vary? Where?
- [ ] Is it a single stroke or multiple strokes?
- [ ] Does the line taper at the ends (brush-like) or end bluntly?

### Teeth
- [ ] Are teeth visible? How many?
- [ ] Which teeth — top row, bottom row, fangs?
- [ ] Size and shape of each visible tooth?
- [ ] Are teeth pure white or off-white?
- [ ] Do teeth have outlines? How thick?

### Lips
- [ ] Are lips visible as separate shapes, or is it just a line?
- [ ] Upper lip vs lower lip — which is more prominent?
- [ ] Lip color — same as face or different?

### Expression
- [ ] What emotion does the mouth convey?
- [ ] Is the expression from the mouth alone, or does it depend on other features?

## SVG Construction

For uniform-width mouth lines (most cartoon styles), a stroke path works:
```xml
<path d="M startX startY Q controlX controlY, endX endY"
      fill="none" stroke="#3a3a3a" stroke-width="5" stroke-linecap="round"/>
```

If the mouth line tapers at the ends (common in brush/hand-drawn styles), build it as a **filled tapered shape** instead — see `styles/styles-curves-and-shapes.md` for the centerline-to-filled-shape technique. A tapered mouth line is a thin filled path, not a stroked one.

For teeth, layer white filled shapes behind the mouth line:
```xml
<!-- Tooth shape -->
<path d="M x1 y1 L x2 y2 L x3 y3 Z" fill="white" stroke="#3a3a3a" stroke-width="2"/>
```

## Common Mistakes
- Making the mouth too small (measure against reference)
- Symmetric smile when the original is a smirk
- Teeth in the wrong position
- Missing the taper at the ends of the mouth line
- Mouth line too thin or too thick relative to other outlines
