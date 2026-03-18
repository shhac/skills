# Identifying Key Concepts for Narrow Focus

The biggest mistake is trying to recreate the whole image at once. Instead, decompose it into independent visual elements that can each be built, iterated, and perfected in isolation.

## How to Decompose

### 1. List Every Distinct Visual Element

Look at the image and list everything you can see as a separate "thing":
- Don't group by proximity — group by what IS it
- A hat is separate from hair, which is separate from the head
- Each eye is its own element (they are NOT identical — see feature sheets)
- Outlines/strokes are part of the element they define, not separate elements

### 2. Establish the Layer Stack (z-order)

Which elements are behind others? Common ordering for a character:
1. Back hair / back accessories (furthest back)
2. Ears (behind head)
3. Head/face shape
4. Facial features (eyes, nose, mouth) — on top of face
5. Front hair / bangs
6. Hat / headwear (on top of everything)

### 3. Identify Shared vs Independent Elements

Some elements interact:
- Ears connect to the head — the head's outline strokes affect where ears feel "attached"
- Hair flows over the forehead and interacts with the hat brim
- Eye outlines may be partially hidden by hat brim or hair

Plan to handle these interactions in the composite phase, not while building individual parts.

### 4. Determine What's Visible vs Hidden

Distinguish between **cropped out** and **obscured by another layer**:
- **Cropped out** (not in the image at all) — don't build it. If the body is cropped out below the chin, you don't need a neck.
- **Obscured by another layer** (present but hidden) — build a simplified version that extends under the covering layer. If the top of the head is hidden by a hat, the head shape should still be a complete closed curve — this prevents hard edges or gaps if layers shift during compositing. The hidden portion doesn't need full detail, just shape continuity.

## Common Decompositions by Subject

### Character/Face

| Element | Notes |
|---------|-------|
| Face shape | The "oval" + cheek/contour strokes + chin shadow |
| Left eye | Outline, sclera, pupil, highlight(s) |
| Right eye | NOT a mirror — study independently, build independently |
| Nose | Often very simple (dots, small shape) |
| Mouth | Lips, smile line, teeth/fangs |
| Left ear | Shape, inner shading, outline |
| Right ear | Study independently |
| Hair | Bangs, tufts, any visible hair |
| Hat/accessory | Dome, brim, details, badges |
| Eyebrows | If visible |

### Landscape/Scene

| Element | Notes |
|---------|-------|
| Sky / background | Usually a gradient; may include clouds, sun, stars |
| Distant layer | Mountains, city skyline, treeline — simplified silhouettes, muted colors |
| Midground | Main terrain, buildings, water — more detail than distant layer |
| Foreground | Closest elements — most detail, strongest contrast |
| Focal subject | The main point of interest (building, tree, figure) |
| Atmospheric effects | Fog, light rays, reflections — often semi-transparent overlays |

Depth comes from **overlapping silhouettes** and **color temperature** (distant = cooler/lighter, near = warmer/darker). Each depth layer is one SVG group.

### Building/Architecture

| Element | Notes |
|---------|-------|
| Primary structure | Main wall surfaces, roofline silhouette |
| Windows/doors | Often repeating — define one, use `<use>` to stamp copies |
| Structural details | Columns, beams, trim, gutters |
| Surface materials | Brick, wood, stone — approximate with `<pattern>` or subtle color variation, not individual units |
| Shadows | Cast shadows on walls, ground shadow — separate overlay shapes |
| Surroundings | Ground plane, sky, neighboring structures |

Respect the perspective: identify vanishing points early. Converging lines are critical — if the original has perspective, the SVG must too.

### Object/Product

Read `features/features-objects.md` for full guidance on complex object decomposition. The table below is a starting point — objects with visible internal structure need much deeper decomposition.

| Element | Notes |
|---------|-------|
| Structural parts | Break into physical components — not "silhouette" but "canopy panels, ribs, shaft, handle" etc. Each structural part that's visually distinct is its own feature. |
| Visible surfaces | Each surface facing a different direction is a separate concern (exterior vs interior, top vs side, front vs back). Different surfaces have different lighting, color, and may show different structural elements. |
| Structural elements | Ribs, seams, edges, joints, mechanisms — these create the visual rhythm. Build as tapered filled shapes, not stroked lines. |
| Surface lighting | Each panel/facet gets its own fill value based on its angle to the light. Adjacent panels should differ in value. Curved surfaces get gradients. |
| Shadows from structure | Thin shadow shapes where structural elements (ribs, rims, edges) cast onto adjacent surfaces |
| Highlights/reflections | Specular highlights, glossy reflections — often simple ellipses or gradients |
| Labels/text | Trace as paths, not `<text>` elements |
| Context | Ground plane, background, other objects in scene |

**The silhouette-first decomposition (outline → fill → shadows → highlights) works for simple or flat objects.** For anything with structural complexity — furniture, vehicles, tools, instruments, architecture, containers — decompose by physical structure instead.

### Animal

| Element | Notes |
|---------|-------|
| Body mass | Torso/trunk — the largest shape |
| Head | Shape, ears, facial features (eyes, nose/snout, mouth) |
| Limbs | Legs, wings, fins — note which overlap the body |
| Tail | Position, curvature, interaction with body |
| Surface pattern | Fur, scales, feathers, spots, stripes — use `<pattern>` for repeating textures |
| Accessories | Collars, saddles, tags — same as character accessories |

Decompose like a character but with different anatomy. The same z-order principle applies: back limbs → body → front limbs → head.

### Logo/Icon

| Element | Notes |
|---------|-------|
| Background shape | Circle, rounded rect, or none |
| Primary symbol | The main graphic mark |
| Text/wordmark | Trace letterforms as `<path>` — match weight and spacing |
| Secondary elements | Taglines, borders, decorative elements |
| Color regions | Logos often have very few — precision matters |

Logos are usually geometric. Prefer SVG primitives (`<circle>`, `<rect>`, `<ellipse>`) over freehand paths where the shape is clearly geometric.

### Vehicle/Machine

See `features/features-vehicles.md` for full construction guidance. Key decomposition:

| Element | Notes |
|---------|-------|
| Body panels | Each panel facing a different direction needs its own gradient |
| Panel lines | Very thin seam lines between panels — critical for recognition |
| Windows/glass | Layered: dark interior + tint + reflection gradient + specular highlight |
| Wheels | Radial symmetry — `<defs>` + `<use>` + `rotate`; elliptical in perspective |
| Lights | Radial gradient glow extending beyond the physical housing |
| Chrome/trim | High-contrast multi-stop gradients |
| Ground shadow | Elliptical gradient beneath vehicle |

Vehicles are panel assemblies, not organic shapes. Panel lines and metallic gradients are what make them read as manufactured objects.

### Food/Drink

See `features/features-food-and-plants.md` for full construction guidance. Key decomposition:

| Element | Notes |
|---------|-------|
| Container/plate | Sets the composition boundary |
| Primary food mass | Organic shape — build from overlapping basic shapes |
| Toppings/layers | Stacking order matters; thin shadows between layers |
| Glossy highlights | White ellipses/shapes at low opacity — makes food look appetizing |
| Steam/aroma | 2-3 wavy white paths, low opacity |
| Signature detail | The one feature that makes it THIS food — never omit |

Food illustration is built from overlapping shapes, not outline drawing. Specular highlights are essential.

### Plant/Flower

See `features/features-food-and-plants.md` for construction guidance. Key decomposition:

| Element | Notes |
|---------|-------|
| Petals | Two-Bezier shapes; use `<use>` + `rotate` for radial symmetry |
| Center | Contrasting circle or cluster |
| Leaves | Bezier outline with gradient fill and vein paths clipped within |
| Stem | Slightly curved path with consistent or tapered width |
