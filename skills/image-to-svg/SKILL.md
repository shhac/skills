---
name: image-to-svg
description: Convert raster images (photos, illustrations, AI-generated art) into high-quality SVG recreations. Breaks the image into isolated features, builds each as a standalone SVG layer, then composites them. Use when the user wants to recreate an image as SVG, create vector versions of artwork, or extract specific elements from images as scalable graphics.
---

# Image to SVG

Recreate raster images as high-quality SVGs by decomposing, studying, and rebuilding each visual element independently.

## Core Principle

**Never try to reproduce the whole image at once.** The quality comes from isolating each feature, studying it closely against a cropped reference, and building it as a standalone SVG before compositing.

## When to Use

- Converting an image (photo, illustration, AI art) to SVG
- Creating vector versions of logos, mascots, icons, or artwork
- Extracting specific elements from images as scalable graphics
- The user provides a reference image and wants an SVG recreation

## Instructions

You are converting a raster image into an SVG recreation. Follow the phases below in order.

This skill uses **incremental discovery** — reference files live in subdirectories adjacent to this skill (`analysis/`, `features/`, `styles/`, `workflow/`). Read them only when a specific phase or condition calls for them. **Do not read all reference files upfront.**

### Phase 1: Analyze the Image

1. **Identify the art style.** Read `styles/styles-identification.md` and classify the image (cartoon, geometric, lifelike, etc.). The identified style determines which techniques you'll use later.

2. **Decompose into features.** Read `analysis/analysis-identifying-concepts.md`. Break the image into independent visual elements and establish a z-order (layer stack).

3. **Create reference crops.** Read `analysis/analysis-reference-crops.md`. Crop the original image into tight per-feature references and save to `refs/`.

4. **Establish canvas and coordinate system.** Determine the composite canvas size (512x512 is standard for emoji/icons; use the original image's aspect ratio for other subjects). Estimate each feature's bounding box within this canvas — approximate x, y, width, height from the original image proportions. Record these in a brief feature map that swarmed agents will use as their coordinate reference. Also determine z-ordering (what's behind what) — this drives the composite in Phase 3.

### Phase 2: Build Each Feature

Once the style is identified, reference crops verified, and the feature map established, **agent swarm the feature builds**. Each feature is independent — they can be built in parallel by separate agents, each working from its own reference crop.

Before starting each feature, read its reference sheet from `features/`:

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

Only read the reference sheets for features that exist in the image. Skip features that aren't present.

For each feature:
1. Study the cropped reference image in isolation
2. Ask yourself the questions from `analysis/analysis-asking-questions.md`
3. **Consider what's hidden** — if this feature is partially obscured by another (head under hat, face under hair), the layer should still extend under the obscuring element. See "Handling Obscured Content" below.
4. Build as a standalone SVG in `parts/`
5. Apply the appropriate art style techniques — read `styles/styles-line-and-brush.md` for illustrated/cartoon styles, or `styles/styles-geometric.md` for flat/geometric styles, or `styles/styles-applying-to-lifelike.md` for photographic/realistic images. Read only the style file matching the style identified in Phase 1.
6. Render, compare side-by-side with the reference crop, iterate

#### Agent Swarming

Spawn one agent per feature (or small group of related features). Each agent receives:
- The reference crop for its feature(s)
- The identified art style description
- The relevant feature reference sheet
- The **composite canvas size and this feature's bounding box** from the feature map (Phase 1 step 4)
- Instructions to write its standalone SVG to `parts/{feature-name}.svg`

**All agents must use the same `viewBox` as the composite canvas** (e.g., `viewBox="0 0 512 512"`). Each agent positions its feature within the full canvas coordinates using the bounding box from the feature map. This ensures parts align without rescaling during composition.

Features that interact (e.g., face + ears, hair + hat) should be noted but built independently — interactions are resolved in Phase 3. For tightly coupled features (ears + face contour, hair + hat brim), include the neighboring feature's bounding box so the agent knows where the boundary sits.

#### Handling Obscured Content

When a feature is partially hidden by another layer:
- **Imagine what's underneath.** A head wearing a hat still has a complete top — extend the head shape up under where the hat sits, even though it won't be visible in the final composite.
- **Simplify but don't omit.** The hidden portion doesn't need full detail, but the shape should be continuous. This prevents hard edges or gaps if layers shift during compositing.
- **Think in complete shapes.** A face path should be a complete closed curve, not one that stops where the hat brim sits.

### Phase 3: Composite

Read `workflow/composition-bringing-layers-together.md`.

1. Combine standalone SVGs into the final composite
2. Adjust relative positioning, z-ordering, and interactions between elements
3. Review pass: do overlapping elements work together?
4. Final render and comparison with original

### Phase 4: Deliver

Read `workflow/workflow-file-structure.md` for the expected project layout.

- Keep the `parts/` directory with standalone SVGs for future edits
- Provide the final composite SVG
- Render a PNG at the target resolution for comparison
