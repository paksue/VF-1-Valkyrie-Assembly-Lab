"""Generate reproducible VF-1 multi-angle renders and scene metrics.

Run with Blender's bundled Python (no third-party Python packages):
    blender --background --python qa/render_blender.py -- \
      --input dist/assets/vf1-valkyrie.glb --output qa/runs/baseline

The camera axes are provisional and MUST be visually calibrated to the
selected TV-series reference before any numerical accuracy claim.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


VIEW_DIRECTIONS = {
    "top": (0, 0, 1),
    "bottom": (0, 0, -1),
    "front": (0, -1, 0),
    "rear": (0, 1, 0),
    "side": (1, 0, 0),
    "other_side": (-1, 0, 0),
    "quarter": (1, -1, 0.8),
}


def get_args():
    raw = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="GLB/glTF or Blender .blend file")
    parser.add_argument("--output", required=True, help="Directory for PNGs + metrics.json")
    parser.add_argument("--size", type=int, default=1024, help="Square image size")
    parser.add_argument(
        "--views", nargs="+", default=["top", "side", "front", "rear", "quarter"],
        choices=tuple(VIEW_DIRECTIONS),
    )
    return parser.parse_args(raw)


def main():
    args = get_args()
    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if args.size < 128 or args.size > 4096:
        raise ValueError("--size must be between 128 and 4096")
    output.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    suffix = source.suffix.lower()
    if suffix == ".blend":
        bpy.ops.wm.open_mainfile(filepath=str(source))
    elif suffix in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        raise ValueError("Expected .blend, .glb or .gltf")

    scene = bpy.context.scene
    bpy.context.view_layer.update()
    meshes = [obj for obj in scene.objects if obj.type == "MESH" and not obj.hide_render]
    if not meshes:
        raise RuntimeError("No visible mesh objects to render")

    vertices = [
        obj.matrix_world @ Vector(corner)
        for obj in meshes
        for corner in obj.bound_box
    ]
    mins = Vector(tuple(min(v[i] for v in vertices) for i in range(3)))
    maxs = Vector(tuple(max(v[i] for v in vertices) for i in range(3)))
    center = (mins + maxs) / 2
    extents = maxs - mins
    longest = max(extents)
    if longest <= 1e-9 or not math.isfinite(longest):
        raise RuntimeError("Mesh bounds are empty or not finite")

    # Rendering: fixed ortho camera, shadow-free, alpha for segmentation.
    # Workbench is intentionally chosen for portability and low render cost.
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.03, 0.03, 0.03)
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.render.film_transparent = True
    scene.render.resolution_x = args.size
    scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"

    camera_data = bpy.data.cameras.new("QA_Orthographic_Camera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = longest * 1.3
    camera = bpy.data.objects.new("QA_Orthographic_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    for name in args.views:
        direction = Vector(VIEW_DIRECTIONS[name]).normalized()
        camera.location = center + direction * longest * 3
        # '-Z' is the camera forward axis and Y points toward screen top.
        up_axis = "Y" if abs(direction.z) < 0.99 else "Y"
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", up_axis).to_euler()
        scene.render.filepath = str(output / (name + ".png"))
        bpy.ops.render.render(write_still=True)

    payload = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "input": str(source),
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_units": "unverified; not a scale-accurate measurement",
        "camera_axes": VIEW_DIRECTIONS,
        "camera_type": "ORTHO",
        "ortho_scale": round(float(camera_data.ortho_scale), 6),
        "views_rendered": args.views,
        "image_px": args.size,
        "bbox_world_min": list(map(float, mins)),
        "bbox_world_max": list(map(float, maxs)),
        "bbox_world_extents": list(map(float, extents)),
        "mesh_objects": len(meshes),
        "vertex_count": sum(len(o.data.vertices) for o in meshes),
        "triangle_count": sum(sum(max(0, len(f.vertices) - 2) for f in o.data.polygons) for o in meshes),
        "animation_action_names": sorted(action.name for action in bpy.data.actions),
        "accuracy": "NOT_EVALUATED",
        "warnings": [
            "This report measures the input geometry, not similarity to TV-series references.",
            "Verify model axes, reference projection and real-world scale before comparing masks.",
            "The imported GLB may contain animation actions; this script does not select transformation poses.",
            "Axis-aligned bounds cannot reveal physical fit, penetrations or mechanical correctness.",
        ],
    }
    (output / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("VF1_QA_REPORT=" + json.dumps(payload))
    print("VF1_QA_IMAGES=" + str(output))


if __name__ == "__main__":
    main()
