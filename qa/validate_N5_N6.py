"""N5→N6 quantitative checks. Runs inside isolated Blender in background."""
import bpy, numpy as np, math, json, hashlib
from pathlib import Path
ROOT=Path(r"C:\Users\BlenderAI\Documents\VF1J_reference_build")
ref=ROOT/"qa_reference"
out={"purpose":"N5→N6 geometry regression, assembly integrity and 3D side armor gap checks, NOT source-reference certification"}
for v,stem in [("top","model_top_mask"),("side","model_side_mask")]:
    a=np.load(ref/("vf1a_N5_"+stem+".npy"))
    b=np.load(ref/("vf1a_N6_"+stem+".npy"))
    if a.shape!=b.shape:raise ValueError("Projection alignment differs")
    out[v]={"n5_pixels":int(a.sum()),"n6_pixels":int(b.sum()),
            "changed_pixels":int((a^b).sum()),
            "n5_n6_iou":round(float((a&b).sum()/(a|b).sum()),7)}
src=ROOT/"rebuild_N6"/"VF1J_rebuild_N6.blend"
bpy.ops.wm.open_mainfile(filepath=str(src))
scene=bpy.context.scene;scene.frame_set(1)
assert scene.unit_settings.system=="METRIC"
S=14.23/(1470-414)
stations=[(1022,.28,991,1025),(1040,.34,986,1029),(1060,.40,978,1033),
 (1085,.46,971,1038),(1125,.515,965,1041),(1150,.54,962,1043),
 (1190,.55,960,1046),(1230,.55,959,1048),(1280,.55,958,1048),
 (1335,.54,960,1047),(1378,.53,962,1047),(1397,.49,969,1042),(1412,.43,971,1037)]
def expected_surface(u,z):
 for i in range(len(stations)-1):
  left,right=stations[i],stations[i+1]
  if left[0]<=u<=right[0]:
   f=(u-left[0])/(right[0]-left[0])
   w=left[1]+f*(right[1]-left[1])
   top=left[2]+f*(right[2]-left[2])
   bottom=left[3]+f*(right[3]-left[3])
   ztop=(975-top)*S;zbottom=(975-bottom)*S
   mid=(ztop+zbottom)/2;half=(ztop-zbottom)/2
   zratio=min(.999,max(0,abs((z-mid)/half)))
   return w*(1-zratio**(2/.27))**(.27/2)
 raise ValueError("u out of bounds: "+str(u))
out["objects"]={}
for s,label in [(-1,"LEFT"),(1,"RIGHT")]:
 shell=bpy.data.objects.get(label+" N6 contoured engine-leg casing")
 panel=bpy.data.objects.get(label+" N6 contoured leg armor panel")
 plate=bpy.data.objects.get("COMPONENT "+label+" N6 detachable engine side armor")
 if any(obj is None for obj in (shell,panel,plate)):
  raise RuntimeError(label+" missing N6 engine casing or detachable panel")
 assert panel.parent==plate, "Side armor panel must be independently grouped"
 assert plate.parent and plate.parent.name=="JOINT "+label+" nacelle knee frame - unrigged"
 assert len(panel.data.vertices)==11 and len(panel.data.polygons)==10
 assert len(shell.data.vertices)==13*16
 cx=s*(569-477)*S
 gaps=[]
 for vertex in panel.data.vertices:
  local=panel.matrix_world @ vertex.co
  u=(local.y+7.115)/S+414
  outward=s*(local.x-cx)
  gaps.append(float(outward-expected_surface(u,local.z)))
 out["objects"][label]={
  "shell_stations":len(shell.data.vertices)//16,
  "armor_outline_vertices":len(panel.data.vertices)-1,
  "panel_rig_parent":plate.parent.name,
  "panel_distance_to_outer_shell_m":{
   "min":round(min(gaps),5),
   "max":round(max(gaps),5),
   "avg":round(sum(gaps)/len(gaps),5)
  },
  "panel_through_shell":min(gaps)<-0.005,
  "panel_hovering_more_than_6cm":max(gaps)>.06
 }
 if min(gaps)<-0.005 or max(gaps)>.06:
  raise RuntimeError(label+" side panel is clipping or floating: "+str(gaps))
out["sha256"]=hashlib.sha256(src.read_bytes()).hexdigest()
out["blender"]=bpy.app.version_string
out["limitations"]=["No source-art ground truth IoU","No actual 3-mode rig","Plate offset compares to analytic loft approximation, not evaluated subsurf or other intersecting parts"]
(ref/"N5_to_N6_acceptance.json").write_text(json.dumps(out,indent=2),encoding="utf8")
print("N5_N6_ACCEPTANCE="+json.dumps(out),flush=True)
