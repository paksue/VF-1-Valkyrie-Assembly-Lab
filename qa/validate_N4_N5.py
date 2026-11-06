"""Evidence-based acceptance checks for real Blender N4 -> N5 iterations.

This is a *self-regression + mechanical structure check*, not a Macross
source-accuracy certificate. Execute in an isolated background Blender process.
"""
from pathlib import Path
import bpy,numpy as np,json,hashlib

ROOT=Path(r"C:\Users\BlenderAI\Documents\VF1J_reference_build")
P=ROOT/"qa_reference"
result={"scope":"Blender N4 vs N5 shape regression and real inlet geometry checks; NOT a VF-1J reference accuracy grade"}
for view,stem in [("top","model_top_mask"),("side","model_side_mask")]:
    a=np.load(P/("vf1a_N4_"+stem+".npy"))
    b=np.load(P/("vf1a_N5_"+stem+".npy"))
    if a.shape!=b.shape:raise RuntimeError("Reference projected mask mismatch")
    union=a|b
    result[view]={
      "N4_pixels":int(a.sum()),
      "N5_pixels":int(b.sum()),
      "changed_pixels":int((a^b).sum()),
      "self_silhouette_iou":round(float((a&b).sum()/union.sum()),7),
      "note":"N4↔N5 projection overlap only; reference drawing is not a mask ground truth"
    }
model=ROOT/"rebuild_N5"/"VF1J_rebuild_N5.blend"
bpy.ops.wm.open_mainfile(filepath=str(model))
scene=bpy.context.scene
scene.frame_set(1)
geometry={}
for label in ("LEFT","RIGHT"):
    front=bpy.data.objects.get(label+" engine six traced cross sections")
    surround=bpy.data.objects.get(label+" N5 rounded rectangle air intake surround")
    duct=bpy.data.objects.get(label+" N5 inner intake walls")
    throat=bpy.data.objects.get(label+" N5 recessed black intake throat")
    if any(obj is None for obj in [front,surround,duct,throat]):
        raise RuntimeError("Intake mesh or engine shell missing: "+label)
    y_front=min(v.co.y for v in front.data.vertices)
    cap_count=sum(1 for poly in front.data.polygons if all(abs(front.data.vertices[i].co.y-y_front)<1e-5 for i in poly.vertices))
    if cap_count!=0:raise RuntimeError(label+" engine shell still has face covering the intake")
    if len(surround.data.vertices)!=56 or len(surround.data.polygons)!=28:
        raise RuntimeError(label+" intake ring wrong topology")
    if len(duct.data.vertices)!=56 or len(duct.data.polygons)!=28:
        raise RuntimeError(label+" duct must have two 28-vertex loops")
    if len(throat.data.polygons)!=1:raise RuntimeError(label+" throat wrong topology")
    co=[v.co for v in surround.data.vertices][28:]
    geometry[label]={
      "mouth_width_m":round(max(v.x for v in co)-min(v.x for v in co),4),
      "mouth_height_m":round(max(v.z for v in co)-min(v.z for v in co),4),
      "rim_vertices":len(surround.data.vertices),
      "duct_faces":len(duct.data.polygons),
      "front_engine_cap_faces":cap_count,
      "mouth_closed_by_engine_shell":False
    }
result["geometry"]=geometry
result["blender"]=bpy.app.version_string
result["N5_model_sha256"]=hashlib.sha256(model.read_bytes()).hexdigest()
result["limitations"]=[
 "No source-grounded VF-1J-specific IoU",
 "Airflow physically hollow at inlet plane; deeper region includes other components and has not undergone volumetric flow testing",
 "No GERWALK/Battroid rig or linkage validation",
 "No deployment to website"]
out=P/"N4_to_N5_acceptance.json"
out.write_text(json.dumps(result,indent=2),encoding="utf8")
print("N4_N5_ACCEPTANCE="+json.dumps(result),flush=True)
