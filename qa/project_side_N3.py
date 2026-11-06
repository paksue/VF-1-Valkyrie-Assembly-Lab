"""Project actual Blender mesh silhouettes directly into the original VF-1A drawing's
pixel coordinate system. This makes a visually honest registered QA overlay rather
than eyeballing independently scaled screenshots.

No copyrighted source art is committed. Restrict output to the local QA directory.
Run only in separate background Blender, not the user's interactive scene.
"""
import bpy, numpy as np, json, hashlib
from pathlib import Path

ROOT=Path(r"C:\Users\BlenderAI\Documents\VF1J_reference_build")
MODEL=ROOT/"rebuild_N3"/"VF1J_rebuild_N3.blend"
REF=ROOT/"qa_reference"/"vf1a_fiveview.png"
OUTPUT=ROOT/"qa_reference"
OUTPUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(MODEL))
scene=bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()

# Original 1800 x 1140 VF-1A drawing is the same 5-view from which N3
# was manually traced. +X is upper side of the reference top projection.
S=14.23/(1470-414)
def project(co):
    # source drawing: horizontal pixel u, vertical pixel v
    return (co.y+7.115)/S+414, 975-co.z/S

im=bpy.data.images.load(str(REF),check_existing=False)
width,height=im.size
if (width,height)!=(1800,1140):
    raise ValueError("Reference dimensions changed; refuse false registration")
pixels=np.empty(width*height*4,dtype=np.float32)
im.pixels.foreach_get(pixels)
original=pixels.reshape(height,width,4)[::-1,:,:3].copy()
ratio=2
hw,hh=width//ratio,height//ratio
mask=np.zeros((hh,hw),dtype=bool)
mesh_stats=[]
mesh_count=0
face_count=0
coll=bpy.data.collections["N1 newly traced replaceable components"]
dg=bpy.context.evaluated_depsgraph_get()

def draw_triangle(trip):
    pts=np.asarray(trip,dtype=np.float64)/ratio
    xs=pts[:,0];ys=pts[:,1]
    x0=max(int(np.floor(xs.min())),190)
    x1=min(int(np.ceil(xs.max())),755)
    y0=max(int(np.floor(ys.min())),380)
    y1=min(int(np.ceil(ys.max())),570)  # VF-1A side-view region only
    if x1<x0 or y1<y0:return
    a,b,c=pts
    area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    if abs(area)<0.005:return
    xx=np.arange(x0,x1+1,dtype=np.float64)[None,:]+0.5
    yy=np.arange(y0,y1+1,dtype=np.float64)[:,None]+0.5
    e0=(b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0])
    e1=(c[0]-b[0])*(yy-b[1])-(c[1]-b[1])*(xx-b[0])
    e2=(a[0]-c[0])*(yy-c[1])-(a[1]-c[1])*(xx-c[0])
    if area>0:
        inside=(e0>=0)&(e1>=0)&(e2>=0)
    else:
        inside=(e0<=0)&(e1<=0)&(e2<=0)
    mask[y0:y1+1,x0:x1+1] |= inside

for obj in coll.all_objects:
    if obj.type!="MESH" or obj.hide_render:continue
    eo=obj.evaluated_get(dg)
    me=eo.to_mesh()
    try:
        vertex_coords=[project(eo.matrix_world @ v.co) for v in me.vertices]
        for tri in me.loop_triangles:
            draw_triangle([vertex_coords[i] for i in tri.vertices])
            face_count+=1
        mesh_count+=1
    finally:
        eo.to_mesh_clear()

# Composite footprint translucently over original drawing. Contour is red.
out=original[::ratio,::ratio].copy()
out[mask] = 0.68*out[mask]+0.32*np.array([0.02,0.55,1.0])
edge=np.zeros_like(mask)
edge[1:,:] |= mask[1:,:] != mask[:-1,:]
edge[:,1:] |= mask[:,1:] != mask[:,:-1]
edge[:-1,:] |= mask[:-1,:] != mask[1:,:]
edge[:,:-1] |= mask[:,:-1] != mask[:,1:]
out[edge]=[1.0,.08,.02]
# The reference's upper half has only one wing. Don't count lower mirrored
# drawing as a mismatch.
crop=out[380:570,185:765,:]
result=bpy.data.images.new("N3 aligned side-view reference overlay",width=crop.shape[1],height=crop.shape[0],alpha=True)
rgba=np.empty((crop.shape[0],crop.shape[1],4),dtype=np.float32)
rgba[:,:,:3]=crop
rgba[:,:,3]=1.0
result.pixels.foreach_set(rgba[::-1].ravel())
result.file_format="PNG"
result.filepath_raw=str(OUTPUT/"vf1a_N3_side_registered_overlay.png")
result.save()
np.save(str(OUTPUT/"vf1a_N3_model_side_mask.npy"),mask)
summary={
    "source_reference":str(REF),"source_image_sha256":hashlib.sha256(REF.read_bytes()).hexdigest(),
    "model":str(MODEL),"model_sha256":hashlib.sha256(MODEL.read_bytes()).hexdigest(),
    "frame":1,"reference_pixels":[width,height],
    "mapping":"u=(model_y+7.115)/S+414;v=975-model_z/S;S=14.23/(1470-414)",
    "tested_source_half":"side view, v=760..1140 (original pixels)",
    "triangles":face_count,"meshes":mesh_count,
    "footprint_pixels_halfres":int(mask.sum()),
    "output":str(OUTPUT/"vf1a_N3_side_registered_overlay.png"),
    "pass":"N/A. This artifact is a registered visual overlay, NOT a measured accuracy grade.",
    "limitation":"VF-1A five-view provides common airframe only, not VF-1J-specific livery or Battroid",
}
(OUTPUT/"vf1a_N3_side_projection_manifest.json").write_text(json.dumps(summary,indent=2),encoding="utf8")
print("REGISTERED_OVERLAY="+json.dumps(summary),flush=True)
