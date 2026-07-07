#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from collections import deque
from pathlib import Path

from PIL import Image


def parse_names(raw: str | None, names_file: str | None) -> list[str]:
    if names_file:
        return [line.strip() for line in Path(names_file).read_text().splitlines() if line.strip()]
    if not raw:
        raise SystemExit("Provide --names or --names-file")
    return [part.strip() for part in raw.split(",") if part.strip()]


def is_key(r: int, g: int, b: int, tolerance: int = 35) -> bool:
    return g >= 80 and r <= 120 and b <= 130 and g - max(r, b) >= tolerance


def is_green_fringe(r: int, g: int, b: int) -> bool:
    return g > 24 and g > r + 10 and g > b + 10 and r < 140 and b < 150


def remove_connected_green(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    queue: deque[tuple[int, int]] = deque()
    seen = bytearray(w * h)

    def push(x: int, y: int) -> None:
        if x < 0 or y < 0 or x >= w or y >= h:
            return
        idx = y * w + x
        if seen[idx]:
            return
        r, g, b, _ = px[x, y]
        if not is_key(r, g, b):
            return
        seen[idx] = 1
        queue.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while queue:
        x, y = queue.popleft()
        px[x, y] = (0, 0, 0, 0)
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    # Remove key-colored edge pixels that remain attached to the transparent matte.
    for _ in range(3):
        to_clear: list[tuple[int, int]] = []
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0 or not is_green_fringe(r, g, b):
                    continue
                if (
                    (x > 0 and px[x - 1, y][3] == 0)
                    or (x + 1 < w and px[x + 1, y][3] == 0)
                    or (y > 0 and px[x, y - 1][3] == 0)
                    or (y + 1 < h and px[x, y + 1][3] == 0)
                ):
                    to_clear.append((x, y))
        if not to_clear:
            break
        for x, y in to_clear:
            px[x, y] = (0, 0, 0, 0)
    return rgba


def remove_any_green(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a and is_green_fringe(r, g, b):
                px[x, y] = (0, 0, 0, 0)
    return rgba


def low_count_runs(counts: list[int], threshold: int, min_width: int) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, count in enumerate(counts):
        if count <= threshold:
            if start is None:
                start = index
        elif start is not None:
            if index - start >= min_width:
                runs.append((start, index - 1))
            start = None
    if start is not None and len(counts) - start >= min_width:
        runs.append((start, len(counts) - 1))
    return runs


def midpoint(run: tuple[int, int]) -> int:
    return (run[0] + run[1] + 1) // 2


def row_bounds(src: Image.Image, rows: int) -> list[int]:
    rgb = src.convert("RGB")
    px = rgb.load()
    counts = [
        sum(1 for x in range(rgb.width) if not is_key(*px[x, y], tolerance=60))
        for y in range(rgb.height)
    ]
    runs = low_count_runs(counts, threshold=10, min_width=2)
    internal = [run for run in runs if run[0] > 0 and run[1] < rgb.height - 1]
    if len(internal) != rows - 1:
        return [round(i * rgb.height / rows) for i in range(rows + 1)]
    return [0, *[midpoint(run) for run in internal], rgb.height]


def column_bounds_for_row(src: Image.Image, y0: int, y1: int, cols: int) -> list[int]:
    rgb = src.convert("RGB")
    px = rgb.load()
    counts = [
        sum(1 for y in range(y0, y1) if not is_key(*px[x, y], tolerance=60))
        for x in range(rgb.width)
    ]
    runs = low_count_runs(counts, threshold=3, min_width=2)
    internal = [run for run in runs if run[0] > 0 and run[1] < rgb.width - 1]
    if len(internal) != cols - 1:
        return [round(i * rgb.width / cols) for i in range(cols + 1)]
    return [0, *[midpoint(run) for run in internal], rgb.width]


def square_crop(img: Image.Image, padding: int) -> Image.Image:
    rgba = img.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if bbox is None:
        return rgba
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(rgba.width, right + padding)
    bottom = min(rgba.height, bottom + padding)
    cropped = rgba.crop((left, top, right, bottom))
    side = max(cropped.width, cropped.height)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(cropped, ((side - cropped.width) // 2, (side - cropped.height) // 2))
    return square


def fit_contain(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = min(size[0] / img.width, size[1] / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(resized, ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2))
    return out


def parse_replacements(values: list[str]) -> dict[str, Path]:
    replacements: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Bad --replace value {value!r}; use name=/path/image.png")
        name, path = value.split("=", 1)
        replacements[name] = Path(path)
    return replacements


def main() -> None:
    parser = argparse.ArgumentParser(description="Split and clean a generated profile emoji atlas.")
    parser.add_argument("--atlas", required=True, help="Generated atlas image on a green background.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--names", help="Comma-separated shortcode names in atlas order.")
    parser.add_argument("--names-file", help="Text file with one shortcode name per line.")
    parser.add_argument("--cols", type=int, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--replace", action="append", default=[], help="Replacement cell as name=/path/image.png")
    parser.add_argument("--aggressive-green", action="append", default=[], help="Remove all green-ish pixels for this cell name.")
    parser.add_argument("--padding", type=int, default=12, help="Padding around tight square crops.")
    parser.add_argument("--no-square", action="store_true", help="Keep rectangular cell dimensions for individual PNGs.")
    parser.add_argument("--zip", dest="zip_path", help="Optional zip path containing only individual PNGs.")
    args = parser.parse_args()

    names = parse_names(args.names, args.names_file)
    expected = args.cols * args.rows
    if len(names) != expected:
        raise SystemExit(f"Expected {expected} names for {args.cols}x{args.rows}, got {len(names)}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    atlas_path = Path(args.atlas)
    shutil.copy2(atlas_path, out_dir / "source-atlas.png")

    source = Image.open(atlas_path).convert("RGBA")
    transparent_source = remove_connected_green(source)
    y_bounds = row_bounds(source, args.rows)
    replacements = parse_replacements(args.replace)
    aggressive = set(args.aggressive_green)

    transparent_atlas = Image.new("RGBA", source.size, (0, 0, 0, 0))
    poses = []
    output_paths: list[Path] = []

    for index, name in enumerate(names):
        row = index // args.cols
        col = index % args.cols
        x_bounds = column_bounds_for_row(source, y_bounds[row], y_bounds[row + 1], args.cols)
        box = (x_bounds[col], y_bounds[row], x_bounds[col + 1], y_bounds[row + 1])

        if name in replacements:
            replacement = remove_connected_green(Image.open(replacements[name]).convert("RGBA"))
            if name in aggressive:
                replacement = remove_any_green(replacement)
            atlas_cell = fit_contain(replacement, (box[2] - box[0], box[3] - box[1]))
            output_cell = replacement
            replacement_source = str(replacements[name])
        else:
            atlas_cell = transparent_source.crop(box)
            if name in aggressive:
                atlas_cell = remove_any_green(atlas_cell)
            output_cell = atlas_cell
            replacement_source = None

        transparent_atlas.alpha_composite(atlas_cell, (box[0], box[1]))
        final_cell = output_cell if args.no_square else square_crop(output_cell, args.padding)
        file_path = out_dir / f"{name}.png"
        final_cell.save(file_path)
        output_paths.append(file_path)

        pose = {
            "index": index,
            "row": row,
            "column": col,
            "name": name,
            "file": file_path.name,
            "source_box": list(box),
            "source_cell_size": [box[2] - box[0], box[3] - box[1]],
            "size": list(final_cell.size),
        }
        if replacement_source:
            pose["replacement_source"] = replacement_source
        poses.append(pose)

    transparent_atlas.save(out_dir / "atlas-transparent.png")

    preview_cell = 48
    preview = Image.new("RGBA", (args.cols * preview_cell, args.rows * preview_cell), (255, 255, 255, 255))
    for pose in poses:
        cell = Image.open(out_dir / pose["file"]).convert("RGBA")
        small = cell.resize((preview_cell, preview_cell), Image.Resampling.LANCZOS)
        preview.alpha_composite(small, (pose["column"] * preview_cell, pose["row"] * preview_cell))
    preview.save(out_dir / "emoji-48-preview.png")

    manifest = {
        "source_atlas": str(atlas_path),
        "columns": args.cols,
        "rows": args.rows,
        "atlas": "atlas-transparent.png",
        "preview_48px": "emoji-48-preview.png",
        "poses": poses,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    if args.zip_path:
        zip_path = Path(args.zip_path)
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in output_paths:
                zf.write(file_path, arcname=file_path.name)


if __name__ == "__main__":
    main()
