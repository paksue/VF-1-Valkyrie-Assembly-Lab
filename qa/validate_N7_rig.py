"""N7 rig continuity and topology evaluation, no claim of final mechanical fidelity."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
root=Path(r"C:\Users\BlenderAI\Documents\VF1J_reference_build")
source=root/"rebuild_N7"/"VF1J_rebuild_N7.blend"
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
model=bpy.data.collections["N1 newly traced replaceable components"]
frames=(1,16,31,46,61,76,91)
report={"source":str(source),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "blender":bpy.app.version_string,"samples":{},
        "metric_scope":"hinge-center continuity, rigid transform/no-scale, mesh topology, source-part preservation; NOT collision-certified or source accuracy"}
last={}
max_center_gap=0.0
max_motion={i:0.0 for i in ("LEFT","RIGHT")}
for frame in frames:
 scene.frame_set(frame);bpy.context.view_layer.update()
 measurements={}
 for label in ("LEFT","RIGHT"):
  hip=bpy.data.objects["N7 "+label+" HIP swing"]
  knee=bpy.data.objects["N7 "+label+" KNEE reverse hinge"]
  shoulder=bpy.data.objects["N7 "+label+" SHOULDER deploy"]
  up=bpy.data.objects[label+" N7 UPPER engine-thigh casing"]
  down=bpy.data.objects[label+" N7 LOWER engine-shin casing"]
  if down.parent!=knee or knee.parent != bpy.data.objects["JOINT "+label+" nacelle knee frame - unrigged"] or knee.parent.parent != hip:
   raise RuntimeError("N7 leg parent-chain broken "+label)
  assert len(up.data.vertices)==5*16 and len(down.data.vertices)==9*16
  assert len(up.data.polygons)==4*16 and len(down.data.polygons)==8*16+1
  def center(ob,ids):
   pts=[ob.matrix_world@ob.data.vertices[i].co for i in ids]
   return sum(pts,Vector((0,0,0)))/len(pts)
  a=center(up,range(64,80))
  b=center(down,range(0,16))
  gap=(a-b).length
  max_center_gap=max(max_center_gap,gap)
  if any(any(abs(x-1)>1e-6 for x in ob.scale) for ob in (hip,knee,shoulder,up,down)):
   raise RuntimeError("Scale changes forbidden in N7 "+label+" frame "+str(frame))
  if label in last:
   step=max((a-last[label][0]).length,(b-last[label][1]).length)
   max_motion[label]=max(max_motion[label],step)
  last[label]=(a,b)
  measurements[label]={
   "hinge_center_gap_m":round(gap,5),
   "upper_ring_center_xyz":[round(x,4) for x in a],
   "lower_ring_center_xyz":[round(x,4) for x in b],
   "hip_angle_x_deg":round(math.degrees(hip.rotation_euler.x),2),
   "knee_angle_x_deg":round(math.degrees(knee.rotation_euler.x),2),
   "shoulder_angle_x_deg":round(math.degrees(shoulder.rotation_euler.x),2),
   "knee_world_xyz":[round(x,4) for x in knee.matrix_world.translation]
  }
 report["samples"][str(frame)]=measurements
report["max_knee_center_gap_m"]=round(max_center_gap,6)
report["maximum_15_frame_joint_center_motion_m"]={x:round(v,4) for x,v in max_motion.items()}
report["centers_within_2cm"]=bool(max_center_gap<.02)
report["parent_chain_verified"]=True
report["all_tested_scales_are_unity"]=True
report["unverified"]=["No collision-free assurance","No engineered foot or knee linkage","Arms do not have elbow articulation","No Battroid pose","No original VF-1J source art score","No website transformation integration"]
out=root/"rebuild_N7"/"N7_rig_QA.json";out.write_text(json.dumps(report,indent=2),encoding="utf8")
print("N7_RIG_QA="+json.dumps(report),flush=True)
