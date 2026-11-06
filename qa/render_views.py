"""Headless, isolated Blender reference renders.

Run in a background Blender process, NEVER by executing inside the user's live
Blender scene. Assumes model axes X=right, Y=rear (nose -Y), Z=up.
Example:
 blender --background --python qa/render_views.py -- \
   --input /path/to/VF1J.blend --collection "N1 newly traced replaceable components" \
   --out /path/to/qa-run --frame 1
"""
import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Existing .blend or .glb")
    parser.add_argument("--out", type=Path, required=True, help="New, empty output directory")
    parser.add_argument("--collection", help="Optional name of the actual model collection (exclude STUDIO)")
    parser.add_argument("--frame", type=int, default=1)
    parser.add_argument("--size", type=int, default=1024, help="Square render side in pixels")
    parser.add_argument("--margin", type=float, default=1.17)
    return parser.parse_args(argv)


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def load_model(source):
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".blend":
        bpy.ops.wm.open_mainfile(filepath=str(source))
    elif source.suffix.lower() == ".glb":
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        raise ValueError("Only .blend and .glb models are supported")


def model_meshes(collection_name):
    scene = bpy.context.scene
    if collection_name:
        selected = bpy.data.collections.get(collection_name)
        if selected is None:
            raise ValueError(f"Model collection not found: {collection_name}")
        meshes = [obj for obj in selected.all_objects if obj.type == "MESH"]
    else:
        meshes = [obj for obj in scene.objects if obj.type == "MESH" and not obj.hide_render]
    if not meshes:
        raise ValueError("No visible model meshes")
    include = {obj.name for obj in meshes}
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in include
    return meshes


def bounds(meshes):
    points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    low = Vector([min(v[i] for v in points) for i in range(3)])
    high = Vector([max(v[i] for v in points) for i in range(3)])
    return low, high, points


def make_mask_material():
    m = bpy.data.materials.new("QA black opaque silhouette")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0, 0, 0, 1)
    emission.inputs["Strength"].default_value = 1
    m.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return m


def projected_extent(points, camera):
    # Use actual world-space bounds projected into the camera's frame. Avoid
    # relying on object dimensions with unapplied scale or shared parents.
    inverse = camera.rotation_euler.to_matrix().inverted()
    local = [inverse @ (pt - camera.location) for pt in points]
    width = max(v.x for v in local) - min(v.x for v in local)
    height = max(v.y for v in local) - min(v.y for v in local)
    return width, height


def build_camera(scene, center, direction, points, margin, perspective=False):
    camera_data = bpy.data.cameras.new("QA fixed camera")
    camera = bpy.data.objects.new("QA fixed camera", camera_data)
    scene.collection.objects.link(camera)
    dist = max((max((p - center).length for p in points) * 4), 20.0)
    camera.location = center + direction.normalized() * dist
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    width, height = projected_extent(points, camera)
    if perspective:
        camera_data.type = "PERSP"
        camera_data.lens = 50
        # For perspective use a longer distance so all objects fit.
        camera.location = center + direction.normalized() * max(dist, 2.5 * max(width, height))
    else:
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = max(width, height) * margin
    camera_data.clip_end = 10000
    scene.camera = camera
    return camera, [round(width, 5), round(height, 5)]


def configure_render(scene, size):
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = min(scene.cycles.samples, 24)
        scene.cycles.use_denoising = True


def save_render(scene, out_path):
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    if not out_path.is_file():
        raise RuntimeError(f"Render did not produce file: {out_path}")


def main():
    args = arguments()
    if args.size < 128 or args.margin <= 1:
        raise ValueError("size must be >=128; margin must be >1")
    if args.out.exists() and any(args.out.iterdir()):
        raise FileExistsError(f"Refusing to overwrite existing QA run: {args.out}")
    args.out.mkdir(parents=True, exist_ok=True)
    source = args.input.resolve()
    sha256 = file_hash(source)
    load_model(source)
    scene = bpy.context.scene
    scene.frame_set(args.frame)
    bpy.context.view_layer.update()
    meshes = model_meshes(args.collection)
    low, high, points = bounds(meshes)
    center = (low + high) / 2
    dims = high - low
    configure_render(scene, args.size)
    override = make_mask_material()
    render_view_layer = bpy.context.view_layer
    entries = {}
    view_directions = {
        "top": Vector((0, 0, 1)),
        "front": Vector((0, -1, 0)),  # head-on toward nose
        "side": Vector((1, 0, 0)),    # from starboard
        "three_quarter": Vector((1, -1, 0.8)),
    }
    for name, direction in view_directions.items():
        camera, projected = build_camera(
            scene, center, direction, points, args.margin, perspective=name == "three_quarter"
        )
        render_view_layer.material_override = None
        beauty = args.out / (name + "_beauty.png")
        save_render(scene, beauty)
        render_view_layer.material_override = override
        mask = args.out / (name + "_mask.png")
        save_render(scene, mask)
        render_view_layer.material_override = None
        entries[name] = {
            "beauty": beauty.name,
            "mask": mask.name,
            "camera_type": camera.data.type,
            "camera_position_xyz": [round(x, 5) for x in camera.location],
            "camera_euler_xyz": [round(x, 7) for x in camera.rotation_euler],
            "orthographic_scale": round(camera.data.ortho_scale, 5) if camera.data.type == "ORTHO" else None,
            "projected_width_height": projected,
        }
        bpy.data.objects.remove(camera, do_unlink=True)
    report = {
        "run_started_utc": datetime.now(timezone.utc).isoformat(),
        "blender": bpy.app.version_string,
        "source": str(source),
        "source_sha256": sha256,
        "frame": args.frame,
        "collection": args.collection,
        "axis_contract": "X right; Y rear/nose -Y; Z up",
        "units_system": scene.unit_settings.system,
        "unit_scale": scene.unit_settings.scale_length,
        "model_bounds_min_xyz": [round(x, 6) for x in low],
        "model_bounds_max_xyz": [round(x, 6) for x in high],
        "model_bounds_xyz": [round(x, 6) for x in dims],
        "mesh_count": len(meshes),
        "pixel_size": args.size,
        "views": entries,
        "status": "Rendered; visual/reference accuracy NOT established",
    }
    (args.out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
