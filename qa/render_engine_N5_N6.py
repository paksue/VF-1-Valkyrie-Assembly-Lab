"""Matched N5/N6 starboard engine/leg housing closeups, no interactive scene changes."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector
ROOT=Path(r"C:\Users\BlenderAI\Documents\VF1J_reference_build")
result={}
for v in ("N5","N6"):
 folder=ROOT/("rebuild_"+v)
 bpy.ops.wm.open_mainfile(filepath=str(folder/("VF1J_rebuild_"+v+".blend")))
 scene=bpy.context.scene;scene.frame_set(1)
 target=Vector((1.55,3.68,-0.35))
 cam_data=bpy.data.cameras.new("QA matched starboard engine side")
 cam_data.type="ORTHO";cam_data.ortho_scale=6.6;cam_data.clip_end=1000
 cam=bpy.data.objects.new("QA matched starboard engine side",cam_data)
 scene.collection.objects.link(cam)
 cam.location=Vector((28,3.68,-0.10))
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 scene.camera=cam
 scene.render.resolution_x=1100;scene.render.resolution_y=650;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG"
 if scene.render.engine=="CYCLES":
  scene.cycles.samples=25;scene.cycles.use_denoising=True
 output=folder/"engine_side_closeup.png"
 scene.render.filepath=str(output)
 bpy.ops.render.render(write_still=True)
 result[v]={"path":str(output),"bytes":output.stat().st_size,"sha256":hashlib.sha256(output.read_bytes()).hexdigest()}
 print("ENGINE_SIDE_RENDER_READY "+v,flush=True)
print("ENGINE_SIDE_RESULT="+json.dumps(result),flush=True)
