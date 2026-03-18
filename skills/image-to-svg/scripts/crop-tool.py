#!/usr/bin/env python3
"""Crop tool for image-to-svg skill.

Manages feature-locations.yml: generates grid overlays, applies crops,
and provides semantic bounding box manipulation (pan, scale, tighten).

Usage:
    python3 crop-tool.py grid <image> [--step 100] [--output grid.png]
    python3 crop-tool.py crop <feature-locations.yml>
    python3 crop-tool.py show <feature-locations.yml> [--output boxes.png]
    python3 crop-tool.py pan <feature-locations.yml> <feature> <direction> <percent>
    python3 crop-tool.py scale <feature-locations.yml> <feature> <percent>
    python3 crop-tool.py tighten <feature-locations.yml> <feature> <percent>
    python3 crop-tool.py check <feature-locations.yml>

Commands:
    grid      Draw a coordinate grid on the image to help identify feature locations.
              Outputs a labeled grid image — read this to estimate bounding boxes.
    crop      Batch crop all features from the YAML file.
    show      Draw all bounding boxes on the image to visualize feature locations.
    pan       Move a feature's bounding box without changing its size.
              Directions: left, right, up, down. Percent is relative to box size.
    scale     Grow or shrink a feature's bounding box from its center.
              Positive percent grows (e.g., 20 = 20% larger), negative shrinks.
    tighten   Reduce all margins equally (opposite of scale). Useful for LOOSE crops.
    check     Run the clipping + tightness check on all crops (requires ImageMagick).
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def save_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def cmd_grid(args):
    """Draw a coordinate grid on the image."""
    image = args.image
    step = args.step
    output = args.output or f"{Path(image).stem}-grid.png"

    dims = subprocess.check_output(
        ['magick', 'identify', '-format', '%w %h', image]
    ).decode().strip().split()
    w, h = int(dims[0]), int(dims[1])

    draw_cmds = []

    # Vertical lines with labels
    for x in range(0, w + 1, step):
        draw_cmds.append(f"line {x},0 {x},{h}")
        if x % (step * 2) == 0:
            draw_cmds.append(f"text {x+3},14 '{x}'")

    # Horizontal lines with labels
    for y in range(0, h + 1, step):
        draw_cmds.append(f"line 0,{y} {w},{y}")
        if y % (step * 2) == 0:
            draw_cmds.append(f"text 3,{y+14} '{y}'")

    draw_str = " ".join(f"'{c}'" for c in draw_cmds)
    subprocess.run([
        'magick', image,
        '-fill', 'none', '-stroke', 'rgba(255,0,0,0.4)', '-strokewidth', '1',
        '-font', 'Helvetica', '-pointsize', '12',
        '-fill', 'rgba(255,0,0,0.7)', '-stroke', 'none',
        '-draw', " ".join(draw_cmds),
        output
    ], check=True)
    print(f"Grid image: {output} ({w}x{h}, step={step}px)")


def cmd_crop(args):
    """Batch crop all features from the YAML."""
    data = load_yaml(args.yaml)
    image = data['image']
    refs_dir = Path('refs')
    refs_dir.mkdir(exist_ok=True)

    for name, info in data['features'].items():
        x, y, w, h = info['box']
        subprocess.run([
            'magick', image, '-crop', f'{w}x{h}+{x}+{y}', '+repage',
            str(refs_dir / f'{name}.png')
        ], check=True)
        print(f"  cropped refs/{name}.png ({w}x{h} at +{x}+{y})")

    print(f"Done: {len(data['features'])} crops")


def cmd_show(args):
    """Draw all bounding boxes on the image."""
    data = load_yaml(args.yaml)
    image = data['image']
    output = args.output or f"{Path(image).stem}-boxes.png"

    colors = [
        'red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta',
        'yellow', 'lime', 'pink', 'teal', 'coral'
    ]

    draw_cmds = []
    for i, (name, info) in enumerate(data['features'].items()):
        x, y, w, h = info['box']
        color = colors[i % len(colors)]
        draw_cmds.append(f"stroke {color} fill none rectangle {x},{y} {x+w},{y+h}")
        draw_cmds.append(f"stroke none fill {color} text {x+3},{y+16} '{name}'")

    subprocess.run([
        'magick', image,
        '-strokewidth', '3', '-font', 'Helvetica', '-pointsize', '14',
        '-draw', " ".join(draw_cmds),
        output
    ], check=True)
    print(f"Boxes image: {output}")


def cmd_pan(args):
    """Pan a feature's bounding box."""
    data = load_yaml(args.yaml)
    name = args.feature

    if name not in data['features']:
        print(f"Error: feature '{name}' not in YAML", file=sys.stderr)
        sys.exit(1)

    box = data['features'][name]['box']
    x, y, w, h = box
    pct = args.percent / 100.0

    direction = args.direction
    if direction == 'right':
        x = int(x + w * pct)
    elif direction == 'left':
        x = int(x - w * pct)
    elif direction == 'down':
        y = int(y + h * pct)
    elif direction == 'up':
        y = int(y - h * pct)
    else:
        print(f"Error: direction must be left/right/up/down, got '{direction}'", file=sys.stderr)
        sys.exit(1)

    data['features'][name]['box'] = [x, y, w, h]
    save_yaml(args.yaml, data)
    print(f"Panned {name} {direction} {args.percent}%: [{box[0]},{box[1]},{box[2]},{box[3]}] → [{x},{y},{w},{h}]")


def cmd_scale(args):
    """Scale a feature's bounding box from its center."""
    data = load_yaml(args.yaml)
    name = args.feature

    if name not in data['features']:
        print(f"Error: feature '{name}' not in YAML", file=sys.stderr)
        sys.exit(1)

    box = data['features'][name]['box']
    x, y, w, h = box
    pct = args.percent / 100.0

    dw = int(w * pct)
    dh = int(h * pct)
    new_x = x - dw // 2
    new_y = y - dh // 2
    new_w = w + dw
    new_h = h + dh

    data['features'][name]['box'] = [new_x, new_y, new_w, new_h]
    save_yaml(args.yaml, data)
    print(f"Scaled {name} {'+' if args.percent > 0 else ''}{args.percent}%: [{x},{y},{w},{h}] → [{new_x},{new_y},{new_w},{new_h}]")


def cmd_tighten(args):
    """Tighten a feature's bounding box (reduce margins equally)."""
    data = load_yaml(args.yaml)
    name = args.feature

    if name not in data['features']:
        print(f"Error: feature '{name}' not in YAML", file=sys.stderr)
        sys.exit(1)

    box = data['features'][name]['box']
    x, y, w, h = box
    pct = args.percent / 100.0

    dw = int(w * pct)
    dh = int(h * pct)
    new_x = x + dw // 2
    new_y = y + dh // 2
    new_w = w - dw
    new_h = h - dh

    if new_w <= 0 or new_h <= 0:
        print(f"Error: tightening by {args.percent}% would make the box empty", file=sys.stderr)
        sys.exit(1)

    data['features'][name]['box'] = [new_x, new_y, new_w, new_h]
    save_yaml(args.yaml, data)
    print(f"Tightened {name} {args.percent}%: [{x},{y},{w},{h}] → [{new_x},{new_y},{new_w},{new_h}]")


def cmd_check(args):
    """Run clipping + tightness check on all crops."""
    data = load_yaml(args.yaml)
    results = {'pass': [], 'clip': [], 'loose': []}

    for name in data['features']:
        crop_path = f"refs/{name}.png"
        if not Path(crop_path).exists():
            print(f"SKIP {name}: refs/{name}.png not found (run 'crop' first)")
            continue

        dims = subprocess.check_output(
            ['magick', 'identify', '-format', '%w %h', crop_path]
        ).decode().strip().split()
        w, h = int(dims[0]), int(dims[1])
        min_h = w * 5 // 100
        min_v = h * 5 // 100

        info = subprocess.check_output([
            'magick', crop_path, '-fuzz', '10%', '-trim',
            '-format', '%X %Y %[fx:page.width-w-page.x] %[fx:page.height-h-page.y] %w %h',
            'info:'
        ]).decode().strip().split()

        l, t, r, b = int(float(info[0])), int(float(info[1])), int(float(info[2])), int(float(info[3]))
        tw, th = int(float(info[4])), int(float(info[5]))

        clip = []
        if l < min_h: clip.append(f"left={l}")
        if t < min_v: clip.append(f"top={t}")
        if r < min_h: clip.append(f"right={r}")
        if b < min_v: clip.append(f"bottom={b}")

        feat_pct = tw * th * 100 // (w * h) if w * h > 0 else 0

        if clip:
            print(f"CLIP {name}: {' '.join(clip)} (min_h={min_h}px min_v={min_v}px)")
            results['clip'].append(name)
        elif feat_pct < 30:
            print(f"LOOSE {name}: feature={feat_pct}% of crop (want >=30%) — tighten the box")
            results['loose'].append(name)
        else:
            print(f"PASS {name}: L={l} T={t} R={r} B={b} feature={feat_pct}%")
            results['pass'].append(name)

    total = len(results['pass']) + len(results['clip']) + len(results['loose'])
    print(f"\n{len(results['pass'])}/{total} passed, {len(results['clip'])} clipped, {len(results['loose'])} loose")


def main():
    parser = argparse.ArgumentParser(description='Crop tool for image-to-svg skill')
    sub = parser.add_subparsers(dest='command', required=True)

    # grid
    p = sub.add_parser('grid', help='Draw coordinate grid on image')
    p.add_argument('image', help='Source image path')
    p.add_argument('--step', type=int, default=100, help='Grid spacing in pixels (default: 100)')
    p.add_argument('--output', help='Output path (default: {image}-grid.png)')
    p.set_defaults(func=cmd_grid)

    # crop
    p = sub.add_parser('crop', help='Batch crop all features from YAML')
    p.add_argument('yaml', help='feature-locations.yml path')
    p.set_defaults(func=cmd_crop)

    # show
    p = sub.add_parser('show', help='Draw bounding boxes on image')
    p.add_argument('yaml', help='feature-locations.yml path')
    p.add_argument('--output', help='Output path (default: {image}-boxes.png)')
    p.set_defaults(func=cmd_show)

    # pan
    p = sub.add_parser('pan', help='Pan a bounding box (move without resizing)')
    p.add_argument('yaml', help='feature-locations.yml path')
    p.add_argument('feature', help='Feature name')
    p.add_argument('direction', choices=['left', 'right', 'up', 'down'])
    p.add_argument('percent', type=float, help='Percent of box size to move')
    p.set_defaults(func=cmd_pan)

    # scale
    p = sub.add_parser('scale', help='Scale a bounding box from center')
    p.add_argument('yaml', help='feature-locations.yml path')
    p.add_argument('feature', help='Feature name')
    p.add_argument('percent', type=float, help='Percent to grow (positive) or shrink (negative)')
    p.set_defaults(func=cmd_scale)

    # tighten
    p = sub.add_parser('tighten', help='Tighten a bounding box (reduce margins)')
    p.add_argument('yaml', help='feature-locations.yml path')
    p.add_argument('feature', help='Feature name')
    p.add_argument('percent', type=float, help='Percent to reduce by')
    p.set_defaults(func=cmd_tighten)

    # check
    p = sub.add_parser('check', help='Run clipping + tightness check')
    p.add_argument('yaml', help='feature-locations.yml path')
    p.set_defaults(func=cmd_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
