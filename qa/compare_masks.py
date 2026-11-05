#!/usr/bin/env python3
"""Compare *pre-registered*, equal-size orthographic silhouette masks.

Foreground is nontransparent alpha when transparency exists; otherwise white
luminance on black. See README.md. This never automatically rescales/rotates
a poor match into a high score.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def read_mask(path, *, invert=False):
    rgba = np.asarray(Image.open(path).convert("RGBA"))
    alpha = rgba[:, :, 3]
    if np.any(alpha < 250):
        foreground = alpha >= 128
    else:
        rgb = rgba[:, :, :3].astype(np.float32)
        lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
        foreground = lum >= 128
    if invert:
        foreground = ~foreground
    if not foreground.any():
        raise ValueError(f"Empty foreground mask: {path}")
    return foreground


def bbox(mask):
    yy, xx = np.nonzero(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())]


def score(reference, rendered):
    if reference.shape != rendered.shape:
        raise ValueError(f"Size mismatch (no auto-alignment): {reference.shape} vs {rendered.shape}")
    if not reference.any() or not rendered.any():
        raise ValueError("Neither mask may have an empty foreground")
    match = reference & rendered
    missed = reference & ~rendered
    extra = rendered & ~reference
    union = reference | rendered
    ry, rx = np.nonzero(reference)
    my, mx = np.nonzero(rendered)
    return {
        "iou": round(float(match.sum() / union.sum()), 6),
        "reference_coverage": round(float(match.sum() / reference.sum()), 6),
        "render_precision": round(float(match.sum() / rendered.sum()), 6),
        "missed_pixels": int(missed.sum()),
        "extra_pixels": int(extra.sum()),
        "reference_pixels": int(reference.sum()),
        "render_pixels": int(rendered.sum()),
        "reference_bbox_xyxy": bbox(reference),
        "render_bbox_xyxy": bbox(rendered),
        "centroid_offset_px_xy": [
            round(float(mx.mean() - rx.mean()), 3),
            round(float(my.mean() - ry.mean()), 3),
        ],
        "registered_same_view_and_scale": "USER MUST VERIFY; not inferred by this tool",
        "accuracy_certified": False,
    }


def overlay(reference, rendered):
    if reference.shape != rendered.shape:
        raise ValueError("Mask dimensions differ")
    rgb = np.full((*reference.shape, 3), 247, dtype=np.uint8)
    rgb[reference & rendered] = (65, 73, 82)   # overlap: dark gray
    rgb[reference & ~rendered] = (225, 65, 60)  # reference missing: red
    rgb[~reference & rendered] = (40, 110, 225) # model excess: blue
    return Image.fromarray(rgb, "RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--render", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="PNG overlay path; sidecar JSON is written")
    parser.add_argument("--invert-reference", action="store_true")
    parser.add_argument("--invert-render", action="store_true")
    args = parser.parse_args()
    reference = read_mask(args.reference, invert=args.invert_reference)
    rendered = read_mask(args.render, invert=args.invert_render)
    metrics = score(reference, rendered)
    metrics["source_reference"] = str(args.reference)
    metrics["source_render"] = str(args.render)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    overlay(reference, rendered).save(args.out)
    report_path = args.out.with_suffix(".json")
    report_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), **metrics}, indent=2))


if __name__ == "__main__":
    main()
