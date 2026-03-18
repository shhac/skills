# SVG Effects: clipPath, mask & filter

These techniques add depth, atmosphere, and polish to SVG illustrations. They're used during composition (Phase 3) and during feature building when a feature needs clipping, soft edges, or artistic effects.

**For curve construction and filled shape techniques**, see `styles/styles-curves-and-shapes.md`. This file covers effects layered on top of shapes.

## clipPath — Hard Geometric Boundaries

`<clipPath>` defines a geometric boundary — content inside is visible, content outside is hidden. Binary: all-or-nothing.

### When to use
- Clipping features to a boundary (facial features to face shape, interior details to object silhouette)
- Window/cutout effects (vehicle windows, picture frames, masks)
- Constraining highlights, shadows, or patterns within a shape
- Hair shine that shouldn't bleed outside the hair silhouette

### Construction
```xml
<defs>
  <clipPath id="face-boundary">
    <path d="[face shape path]"/>
  </clipPath>
</defs>

<!-- Everything in this group is clipped to the face shape -->
<g clip-path="url(#face-boundary)">
  <path d="[eye shadows]" fill="rgba(0,0,0,0.1)"/>
  <path d="[highlight]" fill="white" opacity="0.2"/>
</g>
```

### Key details
- All shapes inside a `<clipPath>` are unioned — content shows through any of them
- `clipPathUnits="userSpaceOnUse"` (default) uses pixel coordinates
- `clip-rule="evenodd"` changes hole behavior for overlapping sub-paths
- **Performance:** fast (vector math, no pixel operations)

## mask — Soft Edges and Gradual Transparency

`<mask>` uses luminance (brightness) to control opacity at each pixel: white = fully visible, black = fully hidden, gray = proportional.

### When to use
- Gradual fade-outs (fog, atmospheric perspective, vignette)
- Soft-edged highlights or shadows
- Feathered shape edges (blurred mask shape)
- Any effect that needs partial transparency, not a crisp cut

### Patterns

**Linear fade-out:**
```xml
<defs>
  <linearGradient id="fadeGrad">
    <stop offset="0" stop-color="white"/>
    <stop offset="1" stop-color="black"/>
  </linearGradient>
  <mask id="fadeMask">
    <rect width="100%" height="100%" fill="url(#fadeGrad)"/>
  </mask>
</defs>
<g mask="url(#fadeMask)">
  <!-- content fades from visible to invisible -->
</g>
```

**Vignette (radial fade at edges):**
```xml
<defs>
  <radialGradient id="vignetteGrad">
    <stop offset="0.5" stop-color="white"/>
    <stop offset="1" stop-color="black"/>
  </radialGradient>
  <mask id="vignette">
    <rect width="100%" height="100%" fill="url(#vignetteGrad)"/>
  </mask>
</defs>
```

**Fog / atmospheric perspective:**
Apply to distant layers in landscapes — fade from visible (top/foreground) to hidden (bottom/background):
```xml
<defs>
  <linearGradient id="fogGrad" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="black"/>
    <stop offset="0.4" stop-color="black"/>
    <stop offset="0.8" stop-color="white"/>
    <stop offset="1" stop-color="white"/>
  </linearGradient>
  <mask id="fogMask">
    <rect width="100%" height="100%" fill="url(#fogGrad)"/>
  </mask>
</defs>
```

**Feathered shape edge:**
Apply a blur filter to the mask shape itself:
```xml
<mask id="softEdge">
  <circle cx="100" cy="100" r="80" fill="white" filter="url(#blur3)"/>
</mask>
```

### clipPath vs mask decision

| Need | Use |
|---|---|
| Geometric cutout, hard edge | `<clipPath>` |
| Fade, glow, soft edge, fog | `<mask>` |
| Contain pattern/highlight within a shape | `<clipPath>` |
| Depth-of-field, atmospheric effects | `<mask>` |
| Best performance | `<clipPath>` (vector math vs pixel ops) |

## filter — Artistic Effects

SVG filters are pixel-level operations applied at render time. They add shadows, blur, texture, wobble, and glow.

### Filter element sizing
```xml
<filter id="myFilter" x="-10%" y="-10%" width="120%" height="120%">
```
The default region extends 10% beyond the element. Expand for large blurs/shadows (e.g., `x="-25%" y="-25%" width="150%" height="150%"`).

### Drop Shadow
```xml
<filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
  <feOffset in="blur" dx="4" dy="4" result="shadow"/>
  <feFlood flood-color="rgba(0,0,0,0.5)" result="color"/>
  <feComposite in="color" in2="shadow" operator="in" result="coloredShadow"/>
  <feMerge>
    <feMergeNode in="coloredShadow"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

Modern shorthand (where supported):
```xml
<filter id="quickShadow">
  <feDropShadow dx="3" dy="3" stdDeviation="2" flood-color="rgba(0,0,0,0.4)"/>
</filter>
```

### Outer Glow (headlights, magic effects, neon)
```xml
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
  <feFlood flood-color="#00FFFF" result="color"/>
  <feComposite in="color" in2="blur" operator="in" result="coloredGlow"/>
  <feMerge>
    <feMergeNode in="coloredGlow"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

### Hand-Drawn Wobble
```xml
<filter id="wobble">
  <feTurbulence type="turbulence" baseFrequency="0.02"
    numOctaves="2" seed="42" result="noise"/>
  <feDisplacementMap in="SourceGraphic" in2="noise"
    scale="4" xChannelSelector="R" yChannelSelector="G"/>
</filter>
```

**feTurbulence parameters:**
- `baseFrequency`: scale of noise. 0.01-0.03 = gentle wobble, 0.05+ = fine grain
- `numOctaves`: detail layers. 1-2 for wobble, 4-5 for texture. Keep ≤ 3 for performance.
- `seed`: different seeds = different patterns
- `type`: `turbulence` for ripply distortion, `fractalNoise` for smoother textures

**feDisplacementMap parameters:**
- `scale`: displacement in pixels. 3-8 = subtle, 15-30 = dramatic

### Outline/Stroke Effect (via feMorphology)
```xml
<filter id="outline">
  <feMorphology in="SourceAlpha" operator="dilate" radius="4" result="dilated"/>
  <feFlood flood-color="#FF6B35" result="color"/>
  <feComposite in="color" in2="dilated" operator="in" result="outline"/>
  <feMerge>
    <feMergeNode in="outline"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

`feMorphology`: `erode` shrinks shapes, `dilate` expands them.

### Paper Texture
```xml
<filter id="paper">
  <feTurbulence type="fractalNoise" baseFrequency="0.04"
    numOctaves="5" seed="2" result="noise"/>
  <feDiffuseLighting in="noise" lighting-color="white" surfaceScale="2">
    <feDistantLight azimuth="45" elevation="60"/>
  </feDiffuseLighting>
</filter>
```

### Color Adjustments (feColorMatrix)
```xml
<!-- Desaturate -->
<feColorMatrix type="saturate" values="0"/>

<!-- Reduce opacity -->
<feColorMatrix type="matrix" values="
  1 0 0 0 0
  0 1 0 0 0
  0 0 1 0 0
  0 0 0 0.3 0"/>

<!-- Hue rotation -->
<feColorMatrix type="hueRotate" values="180"/>
```

## Performance Guidelines

### Cost ranking (cheap → expensive)
1. **feOffset, feFlood, feMerge** — nearly free
2. **feComposite, feMorphology, feColorMatrix** — cheap
3. **feGaussianBlur** — moderate (scales with stdDeviation)
4. **feDisplacementMap** — moderate
5. **feTurbulence** — expensive (scales with numOctaves and filter area)
6. **feDiffuseLighting, feSpecularLighting** — expensive

### Guidelines
- **2-4 filter primitives** per filter is ideal; 6-8 okay for static content; 10+ gets heavy
- Keep `numOctaves` ≤ 3 for feTurbulence in practice
- Minimize filter region — only expand when effects are clipped
- **At emoji scale (16-64px): skip filters entirely.** They're invisible at small sizes and add render cost.
- Test on mobile — hardware acceleration varies across browsers

## When to Use Each Technique

| Scenario | Technique |
|---|---|
| Constrain highlights/shadows within a shape | `<clipPath>` |
| Vehicle window cutout, wheel arch | `<clipPath>` |
| Hair shine that stays inside the hair | `<clipPath>` |
| Fog, atmospheric depth, gradual fade | `<mask>` with gradient |
| Soft-edged shadow or highlight | `<mask>` with blurred shape |
| Drop shadow for depth | `<filter>` with feGaussianBlur |
| Headlight/taillight glow | `<filter>` with feGaussianBlur + feMerge |
| Hand-drawn/sketchy edge feel | `<filter>` with feTurbulence + feDisplacementMap |
| Paper or canvas texture | `<filter>` with feTurbulence + feDiffuseLighting |
| Outline/stroke effect on a group | `<filter>` with feMorphology |

## Anti-Patterns

- **Using filters for effects achievable with shapes** — a gradient-filled ellipse is better than a blurred shape for most highlights
- **Stacking many filters on many elements** — filter each layer group, not each individual path
- **Forgetting to expand filter region** — large blurs get clipped at the default 120% boundary
- **Using filters at small display sizes** — below ~64px, filter effects disappear but render cost remains
- **feImage with external URLs** — blocked by CORS; use inline data URIs or same-origin only
