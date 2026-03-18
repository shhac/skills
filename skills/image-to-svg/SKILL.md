---
name: image-to-svg
description: Convert raster images (photos, illustrations, AI-generated art) into high-quality SVG recreations. Breaks the image into isolated features, builds each as a standalone SVG layer, then composites them. Use when the user wants to recreate an image as SVG, create vector versions of artwork, or extract specific elements from images as scalable graphics.
---

# Image to SVG

Recreate raster images as high-quality SVGs by decomposing, studying, and rebuilding each visual element independently.

## Core Principles

**Never try to reproduce the whole image at once.** The quality comes from isolating each feature, studying it closely against a cropped reference, and building it as a standalone SVG before compositing.

**Correctness over speed.** Every shortcut in this workflow compounds into visible quality loss in the final output. Batching crop verification, skipping programmatic checks, eyeballing coordinates instead of measuring, settling for "looks about right" instead of running the diff — each saves a minute but costs ten in rework or produces a visibly worse result. The value of this skill is in the output quality. Take the time to verify at every step.

## When to Use

- Converting an image (photo, illustration, AI art) to SVG
- Creating vector versions of logos, mascots, icons, or artwork
- Extracting specific elements from images as scalable graphics
- The user provides a reference image and wants an SVG recreation

## Instructions

You are converting a raster image into an SVG recreation. Follow the phases below in order.

This skill uses **incremental discovery** — reference files live in subdirectories adjacent to this skill (`analysis/`, `features/`, `styles/`, `workflow/`). Read them only when a specific phase or condition calls for them. **Do not read all reference files upfront.**

### Phase 0: Environment Setup

Read `workflow/workflow-dependencies.md` and run the dependency check script. Ensure required tools (`magick`, `rsvg-convert`, `xmllint`) are available. For optional tools (`vtracer`, `svgo`), check availability and note which enhancements are possible.

If `vtracer` is not installed and Python is available, **ask the user** where they'd like the virtual environment before creating one. See the dependencies file for the three options (project-local, shared skill venv, user-specified).

### Phase 1: Analyze the Image

**Initial analysis** — these are independent. Delegate to parallel subagents so each can focus fully on its concern:

1. **Identify the art style.** Spawn a subagent that reads `styles/styles-identification.md`, studies the image, and reports back with the style classification and reasoning (line work, shape language, color approach, detail level). The identified style determines which techniques you'll use later.
2. **Build your observation framework.** Spawn a subagent that reads `analysis/analysis-asking-questions.md`, studies the image, and reports back with answers to the key observation questions — especially the Construction and Structural questions for complex objects. This report informs the decomposition step.
3. **Handle transparency.** Check programmatically: `magick identify -format "%[channels]" original.png` — if it reports `srgba` or similar alpha channel, note whether the transparent background should be preserved in the final SVG (common for emoji/stickers) or filled with a solid color.

**Decompose** — depends on the observation framework above:

4. **Decompose into features.** Read `analysis/analysis-identifying-concepts.md`. Break the image into independent visual elements and establish a z-order (layer stack).

**Parallel preparation** — these all depend on the feature list from step 4 but are independent of each other. Run them in parallel:

5. **Create and verify reference crops.** Read `analysis/analysis-reference-crops.md`. Write `feature-locations.yml` with bounding boxes for every feature, then crop all features from it in one pass. **Run the programmatic edge-margin check on every crop** — this is the most common failure point. Fix any failing crops by adjusting the YAML and re-cropping (don't re-estimate from the image). Then visually verify each crop individually (one per Read call, not batched). Do not proceed to the build phase with any clipped crops.

6. **Measure and map coordinates programmatically.** Read `workflow/workflow-verification.md` for the measurement pipeline. Do NOT eyeball feature coordinates — small estimation errors compound across features and ruin proportions.
   - Determine canvas size (512x512 standard for emoji/icons; use original aspect ratio for other subjects)
   - Use ImageMagick to measure the original image dimensions and compute the scale factor to canvas
   - Identify **proportion anchors**: 3-5 key measured points (e.g., "head center at 35% of character height, chin at 52%, feet at 95%"). Express as ratios, not absolute pixels — ratios survive the canvas remapping.
   - Compute each feature's bounding box by measuring from the original and scaling to canvas coordinates
   - Record **inter-feature relationships** — not just individual bounding boxes but how features relate: "mouth width = 55% of face width", "gap between boots = 15% of body width", "ears extend 20% past hat brim edge". These relative measurements are what make proportions look right when features are built independently.
   - Record the feature map with measured coordinates, proportion ratios, relationships, and z-ordering. This map travels with every swarmed agent.

7. **Write a subject brief.** In 2-3 sentences, describe the personality, expression, and overall vibe of the subject ("a cheeky, confident goblin with a big happy grin and a proud crossed-arms stance"). This qualitative description travels with every agent alongside the measurements — it gives agents a target for the *feeling* of the subject, not just the geometry. Without it, agents produce features that are technically correct but lack the character's personality.

**After crops are verified** (step 5 must complete first):

8. **Extract trace metadata from crops.** If `vtracer` is available, read `workflow/workflow-trace-metadata.md`. Auto-trace each feature crop in polygon mode and extract structured metadata: color palettes, sub-element positions/sizes, area percentages, and topology hints. This gives agents precise numeric data (~130 tokens per feature) instead of requiring them to eyeball colors and positions from the raster image. Add the trace metadata to each feature's entry in the feature map.

   If `vtracer` is not available, fall back to ImageMagick color extraction:
   ```bash
   magick refs/{feature}.png -resize 200x200 -kmeans 10 -unique-colors txt: | tail -n +2 | tr -s ' ' | cut -d' ' -f3
   ```
   This gives accurate hex values but no spatial sub-element data.

### Phase 2: Build Each Feature (Agent Swarm)

Once the style is identified, reference crops verified, and the feature map established, **agent swarm the feature builds**. Each feature is independent — they can be built in parallel by separate agents, each working from its own reference crop.

#### Character/face images

For character or face images, read the relevant feature reference sheet from `features/` before building each element:

| Feature | Reference file |
|---|---|
| Eyes | `features/features-eyes.md` |
| Mouth | `features/features-mouth.md` |
| Nose | `features/features-nose.md` |
| Ears | `features/features-ears.md` |
| Face shape | `features/features-face-shape.md` |
| Hair | `features/features-hair.md` |
| Body | `features/features-body.md` |
| Accessories | `features/features-accessories.md` |
| Complex objects (held items, props) | `features/features-objects.md` |

Only read the reference sheets for features that exist in the image.

#### Non-character images (landscapes, logos, objects, abstract)

The `features/` reference sheets are character-specific. For other subjects, decompose by visual layer instead:

- **Logos/icons:** background shape, primary symbol, text (as traced paths — do not use `<text>` elements, since fonts won't match), secondary elements, border/frame
- **Landscapes/scenes:** sky/background, distant elements, midground, foreground, focal subject, atmospheric effects (fog, light rays)
- **Objects/products:** Read `features/features-objects.md` for detailed guidance on structural decomposition. Objects have internal structure, multiple visible surfaces, and perspective complexity that goes far beyond silhouette + fill. Decompose into structural parts (panels, ribs, joints, handles), not just color regions.
- **Vehicles/machines:** Read `features/features-vehicles.md`. Vehicles are panel assemblies — decompose by body panels, glass, wheels, lights, and trim. Panel lines and metallic gradients are critical.
- **Food/drinks:** Read `features/features-food.md`. Shape-building approach with glossy highlights, layered construction, and steam/aroma effects.
- **Plants/flowers:** Read `features/features-plants.md`. Radial petal symmetry with `<use>` + `rotate`, leaf construction with vein clipping.
- **Abstract/patterns:** base layer, repeating motifs (use `<pattern>` or `<use>` where possible), accent elements, overlay effects
- **Hybrid images:** For images that combine categories (character holding an object in a landscape), use the focal subject's decomposition as primary and treat secondary elements more simply.

The same principles apply: one crop per element, one standalone SVG per layer, same composite viewBox. Read `analysis/analysis-asking-questions.md` for each element — the shape, color, and position questions are universal.

#### Expression-critical features

Some features are disproportionately important because they define the character's personality or the object's identity. These get **extra comparison rigor** — more iteration passes, programmatic diff verification, and side-by-side checks before moving to composition:

- **Mouth/smile** — the single biggest driver of expression. Curvature, width, and upturn at corners must match closely.
- **Eye gaze** — pupil position and highlight placement determine where the character is looking and how it "feels."
- **Overall proportions** — head-to-body ratio, stance width, limb length. If these are off, no amount of detail fixes the result.
- **Signature features** — whatever makes this specific subject recognizable (a distinctive hat, a specific logo, a unique silhouette).

For these features, always run the programmatic diff (see "Render-Compare Loop" below) and iterate until the diff score converges, even if it means exceeding 3 passes.

#### Building each feature

For each feature:
1. Study the cropped reference image in isolation **and** the full original image for proportion context
2. Ask yourself the questions from `analysis/analysis-asking-questions.md`
3. **Consider what's hidden** — if this feature is partially obscured by another (head under hat, face under hair), the layer should still extend under the obscuring element. See "Handling Obscured Content" below.
4. Build as a standalone SVG in `parts/`
5. Apply the appropriate art style techniques — read `styles/styles-line-and-brush.md` for illustrated/cartoon styles, or `styles/styles-geometric.md` for flat/geometric styles, or `styles/styles-applying-to-lifelike.md` for photographic/realistic images. Read only the style file matching the style identified in Phase 1.
6. **Always read `styles/styles-curves-and-shapes.md`** for curve construction techniques. This applies to all styles — it covers how to actually build shapes with the right SVG path commands, when to use filled shapes vs strokes, and how to construct organic curves. This is the bridge between "what should it look like" and "how do I build it in SVG."
7. Render and compare — see "Render-Compare Loop" below

**Prefer complex construction over simple geometry** (except for images identified as geometric/flat style — defer to `styles/styles-geometric.md` for those). A filled shape built from cubic Beziers with proper width variation, per-panel lighting, and structural detail will always produce a more valuable result than a circle with a stroke. Only use SVG primitives (`<circle>`, `<rect>`, `<ellipse>`) when the reference image genuinely shows a perfect geometric shape or the style is explicitly flat/geometric. When in doubt, build the more complex version — the visual quality difference is substantial.

#### Agent Swarming

**One feature = one SVG = one agent. No exceptions.** Even trivially simple features (a nose that's just two dots, a sparkle, a small badge) get their own file and their own agent. The cost of an extra agent is low; the cost of coupled parts during compositing and future animation is high.

**Paired features are ALWAYS separate.** Left eye and right eye are separate agents writing separate SVGs. Same for left/right ears, left/right boots, left/right arms. They will be checked for consistency in the alignment phase (Phase 3) — that's where consistency is enforced, not by having one agent build both.

**Body parts are independent.** Arms are separate from the torso. Each leg is separate. The head is separate from the neck. Think of each part as something that might animate independently later — an arm could move while the body stays still, one ear could wiggle while the other doesn't.

If there are 5 features, spawn 5 agents. If there are 50 features, spawn 50 agents. The parallelism is the point. Each agent receives:
- The reference crop for its feature(s)
- **The full original image** — the crop is for detail, the full image is for proportion context. An agent building a mouth can't judge whether the grin is wide enough without seeing the full face.
- The **subject brief** from Phase 1 step 7 — the personality/expression/vibe target
- The identified art style description
- The relevant feature reference sheet (from `features/`)
- The relevant style technique file (`styles/styles-line-and-brush.md`, `styles/styles-geometric.md`, or `styles/styles-applying-to-lifelike.md`)
- The curve construction reference (`styles/styles-curves-and-shapes.md`) — **always included**
- The verification pipeline (`workflow/workflow-verification.md`) — **always included**
- The **feature map with measured coordinates, proportion anchors, and inter-feature relationships** from Phase 1 step 6
- The **trace metadata** for this feature from Phase 1 step 8 (color palette, sub-element positions/sizes, topology) — if available

**Describe features quantitatively, not qualitatively.** When briefing agents, text descriptions lose visual nuance — "wide grin" doesn't convey the exact curvature, "thick brim" is ambiguous. Instead use measurements: "mouth width = 55% of face width", "brim height = 5% of hat height, follows dome curvature". Adjectives fail; ratios survive.
- Whether this feature is **expression-critical** (see above) — if so, the agent should run the full programmatic diff loop
- Instructions to write its standalone SVG to `parts/{feature-name}.svg`

**All agents must use the same `viewBox` as the composite canvas** (e.g., `viewBox="0 0 512 512"`). Each agent positions its feature within the full canvas coordinates using the bounding box from the feature map. This ensures parts align without rescaling during composition.

Features that interact (e.g., face + ears, hair + hat) should be noted but built independently — interactions are resolved in Phase 4. For tightly coupled features (ears + face contour, hair + hat brim), include the neighboring feature's bounding box so the agent knows where the boundary sits.

#### Render-Compare Loop

Read `workflow/workflow-verification.md` for the full verification pipeline. The key insight: **don't rely on visual comparison alone** — the LLM is good at spotting catastrophic errors but bad at catching subtle proportion and curvature differences. Use programmatic diff to find errors precisely, then use the LLM to interpret and fix them.

After every SVG change:

1. **Validate** the SVG XML before rendering:
   ```bash
   xmllint --noout parts/{feature}.svg
   ```
   This catches unclosed tags, malformed attributes, and missing namespaces with clear error messages — far more helpful than `rsvg-convert`'s cryptic failures.

2. **Render** the SVG to PNG:
   ```bash
   rsvg-convert -w 512 -h 512 parts/{feature}.svg -o parts/{feature}.png
   ```
   If `rsvg-convert` is not installed, install it (`brew install librsvg` on macOS, `apt install librsvg2-bin` on Linux).

3. **Programmatic diff** — generate a visual diff image and numerical score comparing the rendered feature against the reference crop. See `workflow/workflow-verification.md` for ImageMagick commands. The diff image highlights exactly WHERE the SVG diverges — red areas show the biggest differences.

4. **Read the diff image** — use the highlighted differences to direct your corrections. This is far more effective than comparing two similar-looking images: ImageMagick finds the errors precisely, you interpret them and know how to fix the SVG.

5. **Visual sanity check** — also read both the rendered PNG and reference crop for qualitative assessment (colors, overall feel, details).

6. **Iterate** — fix the top issue highlighted by the diff, re-render, re-diff. Repeat.

**When to stop iterating:** Limit to 3-5 refinement passes for normal features. For **expression-critical features** (mouth, eyes, overall proportions), continue up to 10 passes — these define the character and are worth the extra iteration.

**Convergence targets (RMSE, normalized 0-1):**
- Expression-critical features: target RMSE < 0.15
- Standard features: RMSE < 0.25 is acceptable
- Background/simple fills: RMSE < 0.30 is acceptable
- Stop when two consecutive iterations improve by less than 0.02 — diminishing returns

These are guidelines, not hard gates. A feature at RMSE 0.18 that looks right is done; a feature at 0.12 that looks wrong needs a different approach. Trust the diff image over the number.

#### Handling Obscured Content

When a feature is partially hidden by another layer:
- **Imagine what's underneath.** A head wearing a hat still has a complete top — extend the head shape up under where the hat sits, even though it won't be visible in the final composite.
- **Simplify but don't omit.** The hidden portion doesn't need full detail, but the shape should be continuous. This prevents hard edges or gaps if layers shift during compositing.
- **Think in complete shapes.** A face path should be a complete closed curve, not one that stops where the hat brim sits.

### Phase 3: Class Alignment (Agent Swarm)

After all features are built individually, check paired and repeated features for consistency. **Agent swarm this** — one agent per class of similar features.

A "class" is a group of features that should share the same construction style:
- **Eyes class** — left eye + right eye
- **Ears class** — left ear + right ear
- **Boots/shoes class** — left boot + right boot
- **Arms class** — left arm + right arm (if pose shows both)
- **Any other repeated elements** — e.g., both wheels of a bike, multiple windows on a building

For images with multiple subjects, classes are per-subject: "character A eyes" and "character B eyes" are separate classes.

Each alignment agent receives both SVGs, both reference crops, and the full original image, and checks:

1. **Outline weight** — are paired features using the same stroke width or offset technique? (Most likely to drift between independent agents)
2. **Absolute size** — are they the same size, or intentionally different per the reference?
3. **Fill colors** — do both use exactly the same hex values?
4. **Construction technique** — did one use ellipses while the other used paths? This creates visual inconsistency even if dimensions match.
5. **Highlight count and position** — highlights are the most "creative" part and most likely to vary between agents.
6. **Proportional placement** — "both eyes should be equidistant from face center" type checks.

The alignment agent normalizes any unintentional inconsistencies — making paired features match while preserving intentional asymmetry from the reference (e.g., if the reference genuinely shows different-sized eyes, keep that).

### Phase 4: Composite and Iterate

Read `workflow/composition-bringing-layers-together.md`.

**This phase is not optional.** The first assembly is never the final output. Individual features built in isolation always have proportion and alignment issues that only become visible in context.

1. **Assemble** — combine standalone SVGs into the composite
2. **Apply effects** — read `styles/styles-effects.md` for `<clipPath>`, `<mask>`, and `<filter>` where needed
3. **Diff the composite against the original** — use the full-image programmatic diff from `workflow/workflow-verification.md`. This highlights exactly where the composite diverges from the original.
4. **Identify the top 3 discrepancies** from the diff — usually proportion errors (head too small, features shifted), expression mismatches (mouth curvature, gaze direction), or interaction issues (hat sitting wrong, limbs overlapping incorrectly).
5. **Fix each discrepancy** — either send targeted corrections back to the feature agent, or fix directly in the composite SVG. Re-render and re-diff after each fix.
6. **Repeat** until the composite diff stabilizes — at least 2 composite iterations, more if expression-critical features are off.
7. **Final small-size check:**
   ```bash
   rsvg-convert -w 64 -h 64 final.svg -o /tmp/small-check-64.png
   rsvg-convert -w 128 -h 128 final.svg -o /tmp/small-check-128.png
   ```
   Read both renders — does it still read clearly at icon size? Features that looked fine at 512px may merge or disappear.

### Phase 5: Deliver

Read `workflow/workflow-file-structure.md` for the expected project layout.

1. **Optimize the final SVG.** If `svgo` is available, run it with `cleanupIds` disabled to preserve named groups:
   ```bash
   svgo final.svg -o final.svg \
     --config='{"plugins":[{"name":"preset-default","params":{"overrides":{"cleanupIds":false,"collapseGroups":false,"convertShapeToPath":false}}}]}'
   ```
   This typically reduces file size by 25-40% (numeric precision, default attributes, path command optimization) without changing the visual output. If `svgo` is not available, skip this step — the SVG is still valid.

2. Keep the `parts/` directory with standalone SVGs for future edits
3. Provide the final composite SVG
4. Render a PNG at the target resolution for comparison
