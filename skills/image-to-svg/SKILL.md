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

## Workflow Overview

### Phase 1: Analyze the Image
Read: @analysis-identifying-concepts.md
Read: @analysis-reference-crops.md
Read: @analysis-asking-questions.md

1. **Identify the art style** — Read @styles-identification.md
2. **Decompose into features** — Break the image into independent visual elements
3. **Create reference crops** — Crop the original image into tight per-feature references
4. **Establish layer order** — Determine z-ordering (what's behind what)

### Phase 2: Build Each Feature

Once the style is identified and reference crops are verified, **agent swarm the feature builds**. Each feature is independent — they can be built in parallel by separate agents, each working from its own reference crop.

Read the relevant feature reference sheet before starting each element:
- @features-eyes.md
- @features-mouth.md
- @features-nose.md
- @features-ears.md
- @features-face-shape.md
- @features-hair.md
- @features-body.md
- @features-accessories.md

For each feature:
1. Study the cropped reference image in isolation
2. Ask yourself the questions from @analysis-asking-questions.md
3. **Consider what's hidden** — if this feature is partially obscured by another (head under hat, face under hair), the layer should still extend under the obscuring element. Don't hard-cut at the boundary. See "Handling Obscured Content" below.
4. Build as a standalone SVG in `parts/`
5. Render, compare side-by-side with the reference crop, iterate
6. Apply the appropriate art style techniques from @styles-line-and-brush.md or @styles-geometric.md

#### Agent Swarming

Spawn one agent per feature (or small group of related features). Each agent receives:
- The reference crop for its feature(s)
- The identified art style description
- The relevant feature reference sheet
- The target canvas size and approximate position within the final composite
- Instructions to write its standalone SVG to `parts/{feature-name}.svg`

Features that interact (e.g., face + ears, hair + hat) should be noted but built independently — interactions are resolved in Phase 3.

#### Handling Obscured Content

When a feature is partially hidden by another layer:
- **Imagine what's underneath.** A head wearing a hat still has a complete top — extend the head shape up under where the hat sits, even though it won't be visible in the final composite.
- **Simplify but don't omit.** The hidden portion doesn't need full detail, but the shape should be continuous. This prevents hard edges or gaps if layers shift during compositing.
- **Think in complete shapes.** A face path should be a complete closed curve, not one that stops where the hat brim sits.

### Phase 3: Composite
Read: @composition-bringing-layers-together.md

1. Combine standalone SVGs into the final composite
2. Adjust relative positioning, z-ordering, and interactions between elements
3. Review pass: do overlapping elements work together?
4. Final render and comparison with original

### Phase 4: Deliver
- Keep the `parts/` directory with standalone SVGs for future edits
- Provide the final composite SVG
- Render a PNG at the target resolution for comparison

## File Structure
Read: @workflow-file-structure.md

## Art Style Techniques
Read: @styles-line-and-brush.md
Read: @styles-geometric.md
Read: @styles-applying-to-lifelike.md
