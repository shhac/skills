# Feature Reference: Nose

Noses vary enormously across art styles — from a single dot to a complex 3D shape.

## Pre-Drawing Checklist

- [ ] What style is the nose? (dots/nostrils only? triangle? bridge line? full 3D?)
- [ ] How many elements make up the nose?
- [ ] Size relative to the face? Position relative to eyes and mouth?
- [ ] Color — same as face, darker, or with a separate outline?
- [ ] Is there a nose bridge line? How long? How thick?
- [ ] For nostrils: how many? What shape? How far apart?

## Common Styles

| Style | SVG Approach |
|-------|-------------|
| Two dots | Two small `<circle>` elements |
| Small triangle | `<path>` with three points |
| Bridge line | Single stroke `<path>` |
| Button nose | Small `<ellipse>` with shading |
| Realistic | Multiple paths for bridge, tip, nostrils |

## SVG Construction

For simple nostril dots:
```xml
<circle cx="leftX" cy="y" r="4" fill="#darkerThanFace"/>
<circle cx="rightX" cy="y" r="4" fill="#darkerThanFace"/>
```

## Common Mistakes
- Making the nose too prominent for the art style
- Wrong spacing between nostrils
- Wrong vertical position (too high or too low between eyes and mouth)
