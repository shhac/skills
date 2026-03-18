# Feature Reference: Vehicles, Machines & Mechanical Objects

Vehicles and machines are **panel assemblies** — manufactured objects with crisp seam lines, reflective surfaces, and repeated elements. The key difference from organic subjects: precision matters. Panel lines, consistent geometry, and material-accurate gradients are what make a vehicle look like a vehicle rather than a blob.

## Decomposition

| Feature | What It Is | Key Challenge |
|---|---|---|
| Body panels | Hood, fenders, doors, roof, trunk | Each panel faces a different direction — different gradient per panel |
| Panel lines/seams | Gaps between panels | Very thin (0.5-1.5 stroke-width), slightly darker than paint — critical for recognition |
| Windows/glass | Windshield, side windows, rear window | Layered transparency: dark interior + tint + reflection gradient |
| Wheels | Tire + rim + spokes + hub | Radial symmetry — define once, `<use>` + `rotate`. Elliptical in perspective |
| Headlights/taillights | Light assemblies | Radial gradient glow extending beyond the housing |
| Bumpers/trim | Chrome or body-color trim pieces | Metallic gradients for chrome; body-color fill for painted |
| Grille | Front intake pattern | Repeated elements — `<pattern>` or `<use>` for slats/mesh |
| Mirrors | Side mirrors | Small shapes with reflective gradient, attached to body |
| Structural posts | A-pillar, B-pillar, C-pillar | Dark shapes between windows that make glass read as cut-in |
| Ground shadow | Shadow beneath vehicle | Elliptical gradient, anchors the vehicle to a surface |

## Pre-Drawing Checklist

### Perspective & Viewing Angle
- [ ] What view? (3/4 front, side profile, front, rear?)
- [ ] How much foreshortening? (Far side narrower than near side?)
- [ ] Which wheels are visible? How elliptical are they?
- [ ] Do parallel lines converge? Where's the implied vanishing point?

### Body & Panels
- [ ] What's the overall silhouette? (This carries most recognition — sedan, SUV, truck, sports car)
- [ ] Where are the panel lines? (Hood/fender seam, door edges, trunk)
- [ ] How many distinct body panels are visible?
- [ ] What color is the paint? Metallic, matte, or glossy?

### Glass & Interior
- [ ] How much interior is visible through windows?
- [ ] Where are window reflections? (Usually sky gradient at top)
- [ ] Are structural posts (pillars) visible between windows?

### Wheels
- [ ] How many wheels visible?
- [ ] Spoke pattern? (5-spoke, multi-spoke, solid disc?)
- [ ] Near wheel vs far wheel size difference? (Perspective)

### Lighting
- [ ] Where is the main light source?
- [ ] Which panels are bright vs shadowed?
- [ ] Are headlights/taillights active (glowing)?

## Reflective & Metallic Surfaces

### Car paint (glossy colored surface)

Car paint reflects the environment as stretched highlights. Layer these on each panel:

1. **Base color** — solid fill or subtle gradient
2. **Environment reflection** — broad light-to-medium gradient band (sky/ground reflection)
3. **Specular highlight** — tight bright gradient or semi-transparent white shape where direct light hits
4. **Shadow zone** — darker gradient at panel edges and under overhangs

```xml
<linearGradient id="paintPanel" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#2060A0"/>     <!-- sky reflection -->
  <stop offset="35%" stop-color="#1B4F8A"/>    <!-- base -->
  <stop offset="60%" stop-color="#1B4F8A"/>    <!-- base -->
  <stop offset="100%" stop-color="#0D2A4A"/>   <!-- ground shadow -->
</linearGradient>
<!-- Specular highlight overlay -->
<ellipse cx="200" cy="120" rx="80" ry="8" fill="white" opacity="0.25"/>
```

### Chrome (mirrors, bumpers, trim)

Chrome has **high-contrast alternating light/dark bands** — many gradient stops with rapid value changes:

```xml
<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#E8E8E8"/>
  <stop offset="15%" stop-color="#A0A0A0"/>
  <stop offset="30%" stop-color="#F0F0F0"/>
  <stop offset="50%" stop-color="#505050"/>
  <stop offset="70%" stop-color="#D8D8D8"/>
  <stop offset="85%" stop-color="#707070"/>
  <stop offset="100%" stop-color="#C0C0C0"/>
</linearGradient>
```

The key: chrome has **more stops with higher contrast between adjacent stops** than any other surface. The rapid value changes create the mirror-like impression.

### Brushed/matte metal
Same multi-stop approach but with **less contrast** and tighter clustering. Horizontal gradient direction suggests grain.

### Gold and bronze
- Gold: stops from #B88746 to #FDF5A6
- Bronze: stops in the #9E6941 range

## Panel Lines

Panel lines are the **single most important mechanical detail**. Without them, a car reads as a blob.

- Very thin: `stroke-width="0.5-1.5"`
- Slightly darker than surrounding paint
- Follow body curvature precisely

```xml
<path d="M 80,120 Q 120,115 180,118 Q 240,122 280,130"
      fill="none" stroke="#1a3055" stroke-width="0.8" opacity="0.6"/>
```

Where panels **overlap** (door edge over body), the line becomes a shadow — slightly wider with soft edge.

## Wheels

### Construction with `<defs>` + `<use>` + `rotate`

Wheels have radial symmetry. Define one spoke, repeat:

```xml
<defs>
  <path id="spoke" d="M -3,-38 L -2,-12 L 2,-12 L 3,-38 Z" fill="#888"/>
</defs>
<g transform="translate(100,200)">
  <circle r="45" fill="#333"/>      <!-- tire -->
  <circle r="35" fill="url(#chrome)"/>  <!-- rim -->
  <use href="#spoke" transform="rotate(0)"/>
  <use href="#spoke" transform="rotate(72)"/>
  <use href="#spoke" transform="rotate(144)"/>
  <use href="#spoke" transform="rotate(216)"/>
  <use href="#spoke" transform="rotate(288)"/>
  <circle r="8" fill="#666"/>       <!-- center cap -->
</g>
```

### Wheel assembly layers (back to front)
1. Tire: large circle, dark fill with subtle radial gradient
2. Rim outer lip: slightly smaller circle, metallic gradient
3. Spokes: repeated via `<use>` + `rotate`
4. Hub/center cap: small circle with detail
5. Brake disc (if visible through spokes): circle behind spokes

### Perspective on wheels
From a 3/4 view, wheels are ellipses. Near-side wheel is more circular; far-side is more compressed:
```xml
<!-- Near wheel -->
<g transform="translate(120,280) scale(1, 0.85)">...</g>
<!-- Far wheel -->
<g transform="translate(320,270) scale(1, 0.65)">...</g>
```

## Windows & Glass

Vehicle windows are layered surfaces. From back to front:

1. **Interior** — dark simplified shapes (seats, headrests)
2. **Glass tint** — semi-transparent dark overlay
3. **Reflection** — gradient from white (top) to transparent (bottom)
4. **Specular highlight streak** — thin white shape, `opacity="0.35"`
5. **Frame/pillar** — the structural border

Use `<clipPath>` to contain all window layers within the window shape:

```xml
<clipPath id="windowShape">
  <path d="M 150,80 Q 200,70 280,80 L 270,160 Q 200,165 155,160 Z"/>
</clipPath>
<g clip-path="url(#windowShape)">
  <rect width="400" height="300" fill="#1a1a1a"/>  <!-- interior -->
  <rect width="400" height="300" fill="#000" opacity="0.3"/>  <!-- tint -->
  <rect width="400" height="300" fill="url(#windowReflection)"/>  <!-- reflection -->
</g>
```

## Headlights & Taillights

### Glow technique
Layer the physical fixture with a radial gradient glow extending beyond it:

```xml
<radialGradient id="headlightGlow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0%" stop-color="#FFFFEE" stop-opacity="1"/>
  <stop offset="30%" stop-color="#FFFF88" stop-opacity="0.6"/>
  <stop offset="100%" stop-color="#FFCC00" stop-opacity="0"/>
</radialGradient>

<!-- Housing + lit surface + glow halo -->
<path d="..." fill="url(#chrome)"/>
<ellipse cx="100" cy="100" rx="10" ry="8" fill="#FFFFCC"/>
<ellipse cx="100" cy="100" rx="30" ry="25" fill="url(#headlightGlow)"/>
```

### Filter-based glow alternative
```xml
<filter id="glowFilter">
  <feGaussianBlur stdDeviation="4" result="blur"/>
  <feMerge>
    <feMergeNode in="blur"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

### Light color reference
| Light Type | Color Range |
|---|---|
| Headlights | White/yellow: #FFFFEE to #FFDD44 |
| Taillights | Red: #FF4444 to #FF0000 |
| Turn signals | Amber: #FFA500 |
| DRL strips | White, thin LED paths with glow |

## Perspective: The 3/4 View

The 3/4 front view (~30-45 degrees from front, slightly above) is most common because it shows three surfaces: front, side, and top.

SVG is 2D — create the illusion through:

1. **Manual foreshortening** — the far side is narrower/shorter than near side
2. **Converging lines** — panel lines, belt lines, roof lines converge toward the far side
3. **Scale differences** — far wheel smaller, far mirror smaller
4. **Overlap** — near-side elements overlap far-side, reinforcing depth

For side profiles: no perspective foreshortening needed. All wheels are circles. Simplest view.

For front views: bilateral symmetry — define one half, mirror with `transform="scale(-1,1)"`.

## Heavy Machinery, Robots & Spacecraft

### Hard surface construction principles

Hard surface objects have:
- **Crisp edges** with sharp transitions between surfaces
- **Panel breaks** at every joint, access panel, or material change
- **Repetitive structural elements** — bolts, rivets, vents
- **Material variety** — painted metal, bare metal, rubber, glass

### Construction approach: blockout → panels → surface → detail

1. **Blockout** — primary shapes defining silhouette and mass
2. **Panel breaks** — subdivide into manufactured panels
3. **Surface treatment** — metallic gradients, flat fills, rubber textures
4. **Detail pass** — rivets, bolts, vents, lights, warning stripes

### Repeated mechanical elements

| Element | SVG Approach |
|---|---|
| Gear teeth | `<defs>` + `<use>` + `rotate` at equal intervals |
| Rivets | Small circle with highlight in `<defs>`, stamped with `<use>` |
| Bolt heads | Hexagonal `<polygon>` with subtle gradient |
| Warning stripes | `<pattern>` with rotated yellow/black rectangles |
| Track/tread links | Define one link, `<use>` + `translate` along tread path |
| Solar panels | `<pattern>` for cell grid, `<use>` for panel arrays |

```xml
<!-- Warning stripe pattern -->
<pattern id="warningStripes" width="20" height="20"
         patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="10" height="20" fill="#FFD700"/>
  <rect x="10" width="10" height="20" fill="#222"/>
</pattern>
```

## Ground Shadow

A vehicle without a ground shadow looks like it's floating. Add an elliptical gradient shadow beneath:

```xml
<radialGradient id="groundShadow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0%" stop-color="#000" stop-opacity="0.3"/>
  <stop offset="100%" stop-color="#000" stop-opacity="0"/>
</radialGradient>
<ellipse cx="200" cy="310" rx="150" ry="15" fill="url(#groundShadow)"/>
```

## Common Mistakes

- **Missing panel lines** — a smooth body without seams reads as a toy, not a vehicle
- **Uniform paint across all panels** — panels facing different directions need different gradient orientations
- **Perfect circles for wheels in perspective** — they should be ellipses from any non-side view
- **Flat chrome** — chrome needs high-contrast multi-stop gradients, not a single silver fill
- **Windows as painted surfaces** — glass needs the layered treatment (interior + tint + reflection)
- **Floating without ground shadow** — even a subtle one anchors the vehicle
- **Over-detailing at small scale** — at emoji size, silhouette + color + a few key features (wheels, windows) is enough
