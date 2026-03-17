# Identifying Art Styles

Before recreating an image, identify its style. The style determines which SVG techniques to use and what level of detail is appropriate.

## Key Dimensions to Analyze

### 1. Line Work
- **Thick uniform outlines** — classic cartoon (Adventure Time, Powerpuff Girls)
- **Variable-weight brush strokes** — illustrated/hand-drawn (children's books, concept art)
- **Thin precise lines** — technical illustration, manga
- **No outlines** — flat design, paper cut-out style
- **Sketchy/rough lines** — sketch style, indie comics

### 2. Shape Language
- **Geometric** — circles, rectangles, clean curves (corporate illustration, icons)
- **Organic** — irregular shapes, natural curves (hand-drawn, watercolor)
- **Exaggerated** — oversized features, impossible proportions (cartoon, caricature)
- **Realistic proportions** — anatomically plausible (semi-realistic illustration)

### 3. Color Approach
- **Flat color** — solid fills, no gradients (flat design, classic cartoon)
- **Cel shading** — flat color with sharp shadow edges (anime, comic book)
- **Soft shading** — gradients and smooth transitions (painted, rendered)
- **Limited palette** — few colors, high contrast (poster, retro)
- **Full color** — wide range, naturalistic (realistic illustration)

### 4. Detail Level
- **Minimal** — essential shapes only (icons, emoji)
- **Moderate** — key details included (most cartoons, mascots)
- **High** — lots of texture, secondary details (detailed illustration)
- **Hyper** — every surface has detail (technical illustration)

## Common Style Combinations

| Style Name | Lines | Shapes | Color | Detail |
|-----------|-------|--------|-------|--------|
| Corporate flat | none/thin | geometric | flat | minimal |
| Cartoon | thick uniform | exaggerated | flat/cel | moderate |
| Hand-drawn illustration | variable brush | organic | soft shading | moderate-high |
| Manga/anime | thin precise | stylized | cel shading | moderate |
| Chibi/kawaii | thick uniform | very exaggerated | flat | minimal |
| Pixel art | none (pixel grid) | geometric | flat | varies |
| Watercolor | loose brush | organic | soft | moderate |
| Photographic/rendered | none | realistic | continuous-tone | high |

## How to Identify Style in Practice

1. **Zoom into an outline** — is it uniform width or does it vary? This is the single biggest style signal.
2. **Look at a shadow** — is it a sharp edge (cel) or a gradient (soft)?
3. **Count the colors** in one feature — 2-3 = flat/cel, 5+ = soft/rendered
4. **Check proportions** — are eyes huge? Heads oversized? This indicates exaggeration level.
5. **Look at the simplest feature** (nose, fingers) — how much detail is there? This sets the detail floor.

## Style Determines Technique

Once identified, the style tells you:
- Whether to use `stroke` (uniform) or filled shapes (variable) for outlines
- Whether to use flat `fill` or `radialGradient`/`linearGradient` for color
- How many detail elements to include per feature
- How geometric vs organic your paths should be

### Style → Technique File Mapping

| Identified Style | Read This File |
|---|---|
| Cartoon, hand-drawn illustration, manga/anime, chibi/kawaii, watercolor, sketchy | `styles/styles-line-and-brush.md` |
| Corporate flat, flat design, pixel art, logo, icon, diagrammatic | `styles/styles-geometric.md` |
| Photographic, semi-realistic, continuous-tone, rendered | `styles/styles-applying-to-lifelike.md` |

**Always also read `styles/styles-curves-and-shapes.md`** — it covers how to construct shapes with the right SVG path commands and applies to every style.
