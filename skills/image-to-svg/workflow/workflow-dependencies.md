# Dependencies

This skill requires several CLI tools. Check and install them at the start of every project — before cropping, tracing, or rendering.

## Required Tools

### ImageMagick 7 (`magick`)

Used for: cropping references, measuring coordinates, extracting color palettes, generating diffs, silhouette comparison.

```bash
command -v magick || echo "Install: brew install imagemagick (macOS) or apt install imagemagick (Linux)"

# Verify version 7+ (needed for -kmeans)
magick --version | head -1
```

### librsvg (`rsvg-convert`)

Used for: rendering SVGs to PNG at every iteration step.

```bash
command -v rsvg-convert || echo "Install: brew install librsvg (macOS) or apt install librsvg2-bin (Linux)"
```

### xmllint

Used for: validating SVG XML before rendering (catches malformed markup with clear error messages).

```bash
command -v xmllint || echo "Install: brew install libxml2 (macOS) or apt install libxml2-utils (Linux)"
```

Usually pre-installed on macOS and most Linux distributions.

## Optional Tools

### VTracer (Python: `vtracer`)

Used for: auto-tracing feature crops to extract structured metadata (color palettes, sub-element positions, sizes, topology). See `workflow/workflow-trace-metadata.md`.

```bash
# Check if available
python3 -c "import vtracer" 2>/dev/null && echo "vtracer available" || echo "vtracer not installed"
```

If not installed, see "Python Dependencies and Virtual Environments" below.

### SVGO (Node.js: `svgo`)

Used for: optimizing the final composite SVG before delivery (25-40% file size reduction).

```bash
command -v svgo || echo "Install: npm install -g svgo"
```

If Node.js is not available, skip the SVGO optimization step — the SVG is still valid without it. SVGO is a polish step, not a quality gate.

## Python Dependencies and Virtual Environments

Some tools require Python packages. These should be installed in a virtual environment to avoid polluting the system Python.

Current Python dependencies:
- `pyyaml` — parses `feature-locations.yml` for the batch crop script
- `vtracer` — auto-traces feature crops for metadata extraction

### Step 1: Ask the user where to create the venv

Before creating a virtual environment, ask the user which option they prefer:

1. **Project-local** (default) — `.venv/` inside the SVG project directory. Pros: self-contained, easy to clean up. Cons: one venv per project.
   ```bash
   python3 -m venv "$PROJECT_DIR/.venv"
   source "$PROJECT_DIR/.venv/bin/activate"
   ```

2. **Shared skill venv** — a single venv shared across all image-to-svg projects. Pros: install dependencies once, reuse everywhere. Cons: persists after projects are done.
   ```bash
   python3 -m venv ~/.local/share/image-to-svg-venv
   source ~/.local/share/image-to-svg-venv/bin/activate
   ```

3. **User-specified** — the user provides a path or different instructions (e.g., they use `uv`, `conda`, `poetry`, or have a system-wide Python where installing packages is acceptable).

Present all three options and let the user choose. If the user doesn't have a preference, use option 1 (project-local).

### Step 2: Install Python packages

```bash
pip install pyyaml vtracer
```

### Step 3: Verify

```bash
python3 -c "import yaml; print('pyyaml available')" 2>/dev/null || echo "pyyaml not available"
python3 -c "import vtracer; print('vtracer', vtracer.__version__)" 2>/dev/null || echo "vtracer not available"
```

### When the venv is not available

If the user declines to set up a venv, or Python is not available:
- **Batch cropping:** Fall back to running individual `magick ... -crop` commands manually from the `feature-locations.yml` values (the YAML is still the source of truth — just read the coordinates by eye).
- **Trace metadata:** Fall back to ImageMagick-only color extraction (`magick -kmeans`) which gives accurate colors but no sub-element spatial data.
- The skill still works — Python packages are enhancements, not requirements.

## Dependency Check Script

Run this at the start of every project to verify the environment:

```bash
echo "=== Required ==="
command -v magick      && echo "✓ ImageMagick $(magick --version | head -1 | awk '{print $3}')" || echo "✗ ImageMagick — install with: brew install imagemagick"
command -v rsvg-convert && echo "✓ rsvg-convert" || echo "✗ rsvg-convert — install with: brew install librsvg"
command -v xmllint     && echo "✓ xmllint" || echo "✗ xmllint — install with: brew install libxml2"

echo ""
echo "=== Optional ==="
python3 -c "import yaml" 2>/dev/null && echo "✓ pyyaml (Python)" || echo "○ pyyaml — pip install pyyaml (in a venv)"
python3 -c "import vtracer" 2>/dev/null && echo "✓ vtracer (Python)" || echo "○ vtracer — pip install vtracer (in a venv)"
command -v svgo        && echo "✓ SVGO $(svgo --version 2>/dev/null)" || echo "○ SVGO — npm install -g svgo"
```
