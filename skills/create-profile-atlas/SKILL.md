---
name: create-profile-atlas
description: Create or extend generated profile/portrait emoji atlases for Slack-style custom emoji. Use when making a first-run or extension set of pixel/profile/person/mascot emoji, generating a chroma-key atlas, splitting it into individual transparent PNGs, fixing green-screen/background artifacts, validating emoji-size readability, creating manifests/previews/zips, or optionally uploading custom emoji with agent-slack.
---

# Create Profile Atlas

## Core Rule

Generate the artwork. Do not manually draw expression overlays onto portraits. If an expression is wrong, regenerate that cell or a small replacement atlas, then replace the cell during post-processing.

## Workflow

1. **Collect inputs**
   - Subject reference image(s) or existing profile emoji.
   - Desired shortcode prefix, such as `pixel-paul` or `pixel-alex`.
   - Whether this is a **first-run** full set or an **extend** set.
   - Destination directory for final assets.

2. **Read pose guidance**
   - Read `references/pose-guide.md` before prompting generation.
   - Use its built-in poses unless the user gives a custom list.

3. **Prepare references**
   - Load local reference images with `view_image` before calling `image_gen`.
   - For extensions, load several existing successful sprites so identity, crop, palette, and pixel style stay anchored.
   - If matching Slack names/order, use `agent-slack emoji search/get` only when the user asks for Slack context; run it outside the sandbox.

4. **Generate an atlas**
   - Use built-in `image_gen` by default.
   - Prompt for a row/column atlas on a flat solid `#00ff00` chroma-key background.
   - Demand large, emoji-readable expression details. Tiny props fail at 48px.
   - Ask for green gutters between cells and no labels, borders, numbers, watermark, or grid lines.
   - If the generated file path is not locally discoverable, ask the user to pass the generated image back.

5. **Inspect the generated atlas**
   - Use `view_image` on the full generated atlas.
   - Regenerate any weak cell before slicing when details are too small, identity drifts, or an expression is ambiguous.
   - For one bad expression, generate a one-cell or small replacement atlas and use the postprocess script’s replacement option.

6. **Post-process deterministically**
   - Use `scripts/profile_atlas_postprocess.py` to split the atlas, remove green, create individual transparent PNGs, a transparent atlas, manifest, 48px preview, and optional zip.
   - The script needs Pillow. If `python` cannot import `PIL`, call `load_workspace_dependencies` and run the script with the bundled Python path.
   - Do not assume equal cell widths. Generated atlases often have uneven gutters; the script detects green separator bands per row.
   - Prefer tight square individual PNGs for Slack emoji. Do not resize before upload unless the user explicitly asks.

7. **Validate**
   - Inspect the transparent atlas, individual problem cells, and 48px preview with `view_image`.
   - Check for trapped green regions between disconnected details, especially around symbols like `Zzz`, motion marks, hearts, hands, explosions, and hair.
   - If a cell has no intended green content, rerun postprocess with `--aggressive-green <name>` for that cell.
   - If a cell has intended green content, avoid aggressive removal and regenerate with a different key color or cleaner separation if needed.

8. **Optional Slack upload**
   - If asked to upload, use `agent-slack emoji add <name> --image <path> --yes` outside the sandbox.
   - Check existing names first with `agent-slack emoji get ...`.
   - To replace one Slack emoji, remove then add the same shortcode. Confirm with `agent-slack emoji get <name>`.

## First-Run Pattern

Create a complete atlas from a subject reference:

```text
Use the provided subject image as the strict identity/style reference.
Create a <cols>x<rows> generated pixel-art Slack emoji atlas for shortcode prefix <prefix>.
Each cell is a close-cropped bust/face portrait on flat #00ff00, with green gutters.
Keep identity, hair, clothing cues, and crop consistent. Make expression-specific details oversized and readable at 48px.
No text, no labels, no grid lines, no borders, no watermark.
Atlas order: <pose list from pose-guide.md or user list>.
```

Then split:

```bash
python <skill>/scripts/profile_atlas_postprocess.py \
  --atlas <generated-atlas.png> \
  --out <output-dir> \
  --names <comma-separated-shortcodes> \
  --cols <cols> \
  --rows <rows> \
  --zip <output-dir>/<prefix>-images.zip
```

## Extend Pattern

Create only new poses while matching an existing set:

```text
Use the visible existing <prefix> emoji sprites as strict identity, crop, palette, and pixel-art style references.
Create a <n>-column by 1-row mini atlas for these new shortcodes: <names>.
Keep the same scale and close crop as the existing set. Put every cell on flat #00ff00 with green gutters.
Make each new prop/symbol oversized enough to survive at 48px.
```

For a weak cell, regenerate only that cell and pass it as a replacement:

```bash
python <skill>/scripts/profile_atlas_postprocess.py \
  --atlas <extension-atlas.png> \
  --out <output-dir> \
  --names <name1,name2,name3> \
  --cols 3 \
  --rows 1 \
  --replace name2=<replacement.png> \
  --aggressive-green name2
```

## Practical Lessons

- Big symbols matter: sweat beads, heart eyes, anger marks, `Zzz`, tears, fists, explosions, and clown/skull details should be large enough to read at 48px.
- The best atlas is generated cleanly; post-processing should only cut, key, crop, and compose.
- Uneven generated gutters are normal. Detect separators from green bands per row.
- Transparent previews on black can reveal green halos; white 48px previews reveal readability.
- Keep generated originals. Copy them into outputs or manifest paths, but do not delete the generator’s original file.
- If Slack upload fails because a name exists, ask whether to replace. Replacement is destructive: `emoji remove <name> --yes`, then `emoji add`.

## Bundled Resources

- `references/pose-guide.md`: reusable pose list and prompt notes.
- `scripts/profile_atlas_postprocess.py`: split atlas, remove chroma key, apply replacements, create preview/manifest/zip.
