#!/usr/bin/env python3
"""
Village – Convert numbered folders of images (0–254) to RGB565 bitmap data for RP2350 LCD.

Input: A root folder containing subfolders "0", "1", … "254". Folder N becomes scene N (up to 255 scenes).
       Each subfolder holds numbered images (e.g. 000.png, 001.png); 1–120 frames per scene. Missing folders = 0 frames.
Output: C header + source and/or binary with multi-scene header. All scenes play at 24 fps on device.

Usage:
  python image_sequence_to_bitmap.py <input_root> [--output-dir DIR] [--width W] [--height H] [--name NAME] [--c-only | --bin-only]

Requires: Pillow (pip install Pillow)
"""

import argparse
import os
import re
import struct
import sys

NUM_SCENES = 255  # scenes 0..254
MIN_FRAMES = 1
MAX_FRAMES = 120


def rgb_to_rgb565(r, g, b):
    """Convert 8-bit RGB to 16-bit RGB565 (RRRRRGGGGGGBBBBB)."""
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def load_and_convert_frame(path, width, height):
    """Load image, resize to width x height, return list of RGB565 uint16 (row-major)."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("This script requires Pillow. Install with: pip install Pillow")

    img = Image.open(path)
    img = img.convert("RGB")
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())
    return [rgb_to_rgb565(r, g, b) for r, g, b in pixels]


def discover_frames(folder):
    """Return sorted list of image paths in folder. Supports 000.png, frame_001.png, etc."""
    if not os.path.isdir(folder):
        return []
    exts = {".png", ".jpg", ".jpeg", ".bmp"}
    paths = []
    for name in os.listdir(folder):
        base, ext = os.path.splitext(name)
        if ext.lower() not in exts:
            continue
        nums = re.findall(r"\d+", base)
        key = int(nums[0]) if nums else 0
        paths.append((key, os.path.join(folder, name)))
    paths.sort(key=lambda x: x[0])
    return [p[1] for p in paths]


def load_scenes(root_folder, width, height):
    """
    Load up to NUM_SCENES scenes from root_folder/0 .. root_folder/254.
    Missing or empty folders yield 0 frames (black on device). Present folders must have 1–120 frames.
    Returns list of NUM_SCENES lists of frames (each list may be empty).
    """
    scenes_frames = []
    for s in range(NUM_SCENES):
        sub = os.path.join(root_folder, str(s))
        paths = discover_frames(sub)
        if not paths:
            scenes_frames.append([])
            continue
        if len(paths) > MAX_FRAMES:
            sys.exit(f"Scene {s}: {len(paths)} frames (max {MAX_FRAMES}).")
        if len(paths) < MIN_FRAMES:
            sys.exit(f"Scene {s}: {len(paths)} frames (min {MIN_FRAMES}).")
        frames_data = [load_and_convert_frame(p, width, height) for p in paths]
        scenes_frames.append(frames_data)
    if sum(len(f) for f in scenes_frames) == 0:
        sys.exit("No scenes with images found. Add at least one folder 0..254 with 1–120 images.")
    return scenes_frames


def write_bin_output(scenes_frames, width, height, name, out_dir):
    """
    Binary format: BANM (4) + width (2) + height (2) + frame_count[255] (510) = 518 bytes,
    then for each scene 0..254: frame_count[s] frames of RGB565 (LE).
    """
    magic = b"BANM"
    frame_counts = [len(frames) for frames in scenes_frames]
    header = struct.pack("<4sHH", magic, width, height)
    header += struct.pack("<" + "H" * NUM_SCENES, *frame_counts)
    bin_path = os.path.join(out_dir, f"{name}.bin")

    with open(bin_path, "wb") as f:
        f.write(header)
        for frames in scenes_frames:
            for frame in frames:
                for word in frame:
                    f.write(struct.pack("<H", word))

    return bin_path


def write_c_output(scenes_frames, width, height, name, out_dir):
    """One .h and .c: frame_count[8], total words, and one big const array (scene 0, then 1, … 7)."""
    guard = f"BOOKNOOK_VILLAGE_{name.upper()}_H"
    h_path = os.path.join(out_dir, f"{name}.h")
    c_path = os.path.join(out_dir, f"{name}.c")

    frame_counts = [len(frames) for frames in scenes_frames]
    total_words = sum(fc * width * height for fc in frame_counts)

    with open(h_path, "w") as f:
        f.write(f"#ifndef {guard}\n#define {guard}\n\n")
        f.write(f"#define {name.upper()}_WIDTH   {width}\n")
        f.write(f"#define {name.upper()}_HEIGHT  {height}\n")
        f.write(f"#define {name.upper()}_SCENES  {NUM_SCENES}\n\n")
        f.write(f"extern const unsigned short {name}_frame_count[{NUM_SCENES}];\n")
        f.write(f"extern const unsigned short {name}_data[{total_words}];\n\n")
        f.write("#endif\n")

    with open(c_path, "w") as f:
        f.write(f'#include "{name}.h"\n\n')
        f.write(f"const unsigned short {name}_frame_count[{NUM_SCENES}] = {{\n")
        f.write("  " + ", ".join(str(c) for c in frame_counts) + "\n};\n\n")
        f.write(f"const unsigned short {name}_data[{total_words}] = {{\n")
        for scene_frames in scenes_frames:
            for frame in scene_frames:
                for j in range(0, len(frame), 12):
                    chunk = frame[j : j + 12]
                    line = ", ".join(f"0x{v:04X}" for v in chunk)
                    f.write(f"  {line},\n")
        f.write("};\n")

    return h_path, c_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert numbered folders 0–254 of images to RGB565 for RP2350 (up to 255 scenes, 24 fps)."
    )
    parser.add_argument(
        "input_root",
        help="Root folder containing subfolders 0, 1, … 254 (each with 1–120 numbered images; missing = 0 frames)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory (default: same as input_root)",
    )
    parser.add_argument("--width", "-W", type=int, default=240, help="Output width (default: 240)")
    parser.add_argument("--height", "-H", type=int, default=320, help="Output height (default: 320)")
    parser.add_argument(
        "--name", "-n",
        default="bitmap_anim",
        help="Base name for output files (default: bitmap_anim)",
    )
    out_type = parser.add_mutually_exclusive_group()
    out_type.add_argument("--c-only", action="store_true", help="Only emit C .h/.c files")
    out_type.add_argument("--bin-only", action="store_true", help="Only emit .bin file")
    args = parser.parse_args()

    root = os.path.abspath(args.input_root)
    if not os.path.isdir(root):
        sys.exit(f"Not a directory: {root}")

    out_dir = os.path.abspath(args.output_dir or root)
    os.makedirs(out_dir, exist_ok=True)

    width, height = args.width, args.height
    name = re.sub(r"[^a-zA-Z0-9_]", "_", args.name).strip("_") or "bitmap_anim"

    print(f"Loading up to {NUM_SCENES} scenes from {root} (folders 0–{NUM_SCENES-1}), {width}x{height} RGB565...")
    scenes_frames = load_scenes(root, width, height)
    for s in range(NUM_SCENES):
        n = len(scenes_frames[s])
        if n:
            print(f"  Scene {s}: {n} frames")

    emit_c = not args.bin_only
    emit_bin = not args.c_only

    if emit_c:
        h_path, c_path = write_c_output(scenes_frames, width, height, name, out_dir)
        print(f"C: {h_path}, {c_path}")
    if emit_bin:
        bin_path = write_bin_output(scenes_frames, width, height, name, out_dir)
        print(f"Binary: {bin_path}")

    total_frames = sum(len(f) for f in scenes_frames)
    total_bytes = total_frames * width * height * 2
    print(f"Done. {total_frames} frames total, {total_bytes} bytes. Play at 24 fps on device.")


if __name__ == "__main__":
    main()
