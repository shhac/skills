# Feature Reference: Food & Drinks

Food images are common for emoji, stickers, and illustration. They combine organic shapes, glossy surfaces, layered construction, and atmospheric effects (steam, glow). The core challenge is making surfaces look appetizing — this comes from highlights and color.

## Decomposition

| Feature | What It Is | Key Challenge |
|---|---|---|
| Container/plate | Bowl, plate, cup, wrapper, shell | Simple shapes but sets the composition boundary |
| Primary food mass | The main body (bread, rice, cake, patty) | Organic shape with correct proportions |
| Toppings/garnish | Items placed on top (cheese, frosting, sauce, herbs) | Must overhang slightly; use `<clipPath>` for containment |
| Fillings/layers | Visible internal layers (sandwich fillings, cake layers) | Stacking order, thin shadow between each layer |
| Sauce/glaze | Wet coating, drips, pools | Semi-transparent fill, glossy highlights, drip paths |
| Surface texture | Crust, grain, seeds, char marks | Pattern fills, `feTurbulence`, or simplified dots/lines |
| Highlights/gloss | Specular reflections on wet or glossy surfaces | White ellipses/shapes at low opacity, positioned for light |
| Steam/aroma | Rising wisps from hot food | 2-3 wavy paths, white, low opacity, `feGaussianBlur` |
| Liquid (if visible) | Drink, soup, broth in a container | Colored fill with meniscus curve, surface highlight |
| Signature detail | The one feature that makes it THIS food | Exaggerate for recognition; never omit |

## Construction Approach: Shape-Building

Professional vector food illustration builds items from **overlapping basic shapes** rather than outline-drawing. Start with circles, ellipses, and rounded rectangles, then refine with Bezier adjustments.

### Construction patterns

**Round fruit (apple, cherry, orange):**
- Body: single ellipse or circle
- Depth: second offset darker ellipse clipped to body
- Stem: short curved `path`
- Leaf: two mirrored quadratic Beziers (`Q`) meeting at tip and base
- Highlight: small white ellipse, `opacity="0.6"`, upper-left

**Cupcake/muffin:**
- Wrapper: trapezoid with vertical line ridges
- Cake: rounded shape peeking above wrapper
- Frosting: overlapping ellipses or a single organic blob with `C` curves
- Cherry/topping: circle with `radialGradient` highlight, thin stem path

**Pizza slice:**
- Base shape: triangle with one curved edge (crust) — `L` for straight sides, `A` for crust arc
- Cheese layer: slightly smaller triangle with wavy `C` edges
- Toppings: circles (pepperoni), small organic shapes placed on surface

**Donut:**
- Outer ring: large circle
- Inner hole: smaller circle cut out with `<clipPath>` or same-color circle on top
- Icing: organic shape on top half with wavy bottom edge
- Sprinkles: tiny rotated rectangles scattered on icing

**Sushi:**
- Rice body: rounded rectangle with large `rx`/`ry`
- Nori wrap: dark rectangle band around middle
- Fish topping: organic `path` draped over top, slightly wider than rice

## Glossy & Wet Surfaces

The signature of food illustration is specular highlights. They make surfaces look fresh, wet, or glazed.

### Highlight techniques

**Radial gradient highlight (most common):**
```xml
<radialGradient id="gloss" cx="35%" cy="35%" r="50%">
  <stop offset="0%" stop-color="white" stop-opacity="0.8"/>
  <stop offset="100%" stop-color="white" stop-opacity="0"/>
</radialGradient>
<ellipse cx="80" cy="75" rx="25" ry="20" fill="url(#gloss)"/>
```
Position `cx`/`cy` at ~35% (upper-left) to simulate top-left lighting.

**Window-light catch (glossy candy, fruit):**
- Small white rounded rectangle, rotated ~15-30 degrees, `opacity="0.5-0.7"`
- Placed on upper-left quadrant
- Often paired with a smaller secondary highlight nearby

**Edge highlight (wet surfaces):**
- Thin white path following the upper contour of the shape
- `stroke-opacity="0.4-0.6"`, `stroke-width="1-2"`

### Highlight placement by surface type

| Surface | Highlight Shape | Position | Opacity |
|---|---|---|---|
| Apple/cherry | Small ellipse | Upper-left | 0.6-0.8 |
| Candy/glazed | Elongated rectangle + edge line | Top third | 0.5-0.7 |
| Sauce/syrup | Multiple small circles | Scattered | 0.3-0.5 |
| Frosted cake | Broad soft gradient | Upper half | 0.2-0.3 |
| Glass/liquid | Vertical stripe + surface ellipse | One side + top | 0.3-0.4 |

## Layered Food (Burgers, Sandwiches, Cakes)

Layered food is constructed bottom-to-top, with each layer as a separate `<g>` group.

### Burger construction order (bottom to top)
1. Bottom bun: rounded rectangle, flat top, rounded bottom
2. Lettuce: wavy-edged shape (small `C` curves along bottom, straight top)
3. Tomato: thin red ellipse
4. Patty: dark brown rounded rectangle, slightly wider than bun
5. Cheese: yellow shape, slightly wider, with droopy corners (small `C` curves hanging down sides)
6. Top bun: rounded top, flat bottom, sesame seeds (tiny ellipses on top)

**Key techniques:**
- Each layer overhangs slightly beyond the layer below
- Thin shadow at each layer boundary: dark semi-transparent path following the contour of the lower layer, `fill="#000" opacity="0.1"`
- Cheese/sauce drips: `path` with downward `C` curves from layer edges

## Texture Techniques

### Bread crust
- Slightly irregular outline using `C` curves (not a smooth arc)
- Scoring lines: `path` strokes with varying width
- Color variation: overlapping shapes in warm browns

### Rice/grain texture
- Define `<pattern>` containing 5-8 randomly positioned tiny ellipses
- Tile across the rice area
- Two layers at slightly different tones for depth

### Wood grain (cutting boards, chopsticks)
- Wavy horizontal lines in varying brown tones as a `<pattern>` fill
- Or `feTurbulence` with asymmetric `baseFrequency="0.01 0.1"` for elongated grain

## Steam, Smoke & Aroma

### Cartoon aroma lines (emoji style)
3 parallel wavy lines rising from hot food:
```xml
<path d="M 100,50 C 95,40 105,30 100,20 C 95,10 105,0 100,-10"
      fill="none" stroke="white" stroke-width="2"
      stroke-linecap="round" opacity="0.3"/>
```
- Each line is a simple `S`-curve path
- Opacity decreases from bottom to top (0.4 → 0.25 → 0.15)
- Lines widen and spread as they rise

### Realistic steam
- 3-5 wisps at different positions, widths, and opacities
- Apply `feGaussianBlur` with `stdDeviation="2-4"` to soften edges
- Bottom wisps: narrower, more opaque. Top wisps: wider, more transparent

### Placement
- Steam rises from the **top center** of hot food/drinks
- Wisps start narrow at the source, spread as they rise
- Never let steam overlap the food's key recognizable features

## Transparent & Translucent Materials

### Glass (cup, bottle)
1. Outer shape with very low opacity fill (`opacity="0.1-0.2"`, light blue or white)
2. Rim highlight: white stroke along top edge, `opacity="0.6"`
3. Side highlight: thin white vertical stripe on one side, `opacity="0.3-0.4"`
4. Contents visible through: draw behind the glass shape

### Liquid in a container
- Colored fill in the lower portion of the container
- Top surface: slight concave curve (meniscus) — arc or ellipse
- Surface highlight: horizontal white ellipse at liquid surface, `opacity="0.3"`
- Bubbles (carbonation): scattered tiny white circles, `opacity="0.2-0.4"`

### Ice cubes
- Slightly irregular quadrilateral path
- Very light blue fill, `opacity="0.3-0.5"`
- White highlight on one face
- Partially submerged: use `<clipPath>` of liquid level

## Emoji-Scale Recognition

At 16-32px display size, detail disappears. Food emoji work because of:

- **Maximum 4-5 colors** per item (including outline)
- **Bold outlines** (1-2px stroke) for legibility
- **Exaggerated signature features** — cherry on cupcake, sesame on bun, steam on coffee
- **Flat fills** over gradients (gradients are invisible at small sizes)
- **Canonical angle** — most food shown from 3/4 or front view, never ambiguous

| Item | Must-have features |
|---|---|
| Apple | Red circle, green leaf + stem, white highlight |
| Pizza | Triangle, yellow cheese, red circles, tan crust |
| Burger | Tan bun (sesame dots), brown patty, green lettuce |
| Cupcake | Swirled frosting, ridged wrapper, cherry |
| Sushi | White rice rectangle, dark nori band, colored fish |
| Coffee | White cup, brown liquid, 3 steam wisps |

**At emoji scale: no filters.** `feTurbulence`, `feGaussianBlur` etc. are invisible at 16-32px.

## Common Mistakes

- **Missing the signature highlight** — food without specular highlights looks flat and unappetizing
- **Uniform layer thickness** — in layered food, vary layer thickness and add overhangs
- **Steam overlapping key features** — steam should frame, not obscure
- **Symmetric organic shapes** — real food is slightly irregular; perfect circles look artificial
- **Too many toppings at small scale** — at emoji size, 2-3 toppings are enough to convey the idea
- **Forgetting the container** — food without a plate/bowl/wrapper looks like it's floating
