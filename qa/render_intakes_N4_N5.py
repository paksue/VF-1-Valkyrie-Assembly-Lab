"""Make matched N4/N5 front-facing intake close-up renders, background only.

Uses same camera, exposure, and pixel dimensions for honest comparison.
Does NOT modify existing .blend files.
"""
from pathlib import Path
import bpy, json
from mathutils import Vector
root=Path(r"C:\Users\BlenderAI\Documents\VF1J_reference_build")
results={}
for version in ("N4","N5"):
    folder=root/("rebuild_"+version)
    source=folder/("VF1J_rebuild_"+version+".blend")
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene=bpy.context.scene
    scene.frame_set(1)
    target=Vector((0, .65, -.38))
    cam_data=bpy.data.cameras.new("QA front intake inspection")
    cam_data.type='ORTHO'
    cam_data.ortho_scale=4.7
    cam=bpy.data.objects.new("QA front intake inspection",cam_data)
    scene.collection.objects.link(cam)
    cam.location=Vector((0,-16,-.20))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.camera=cam
    scene.render.resolution_x=1100
    scene.render.resolution_y=700
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    if scene.render.engine=="CYCLES":
        scene.cycles.samples=28
        scene.cycles.use_denoising=True
    img=folder/"intakes_closeup_front.png"
    scene.render.filepath=str(img)
    bpy.ops.render.render(write_still=True)
    results[version]={"path":str(img),"size_bytes":img.stat().st_size}
    print("INTAKE_CLOSEUP_READY "+version,flush=True)
print("CLOSEUP_RESULTS="+json.dumps(results),flush=True)
