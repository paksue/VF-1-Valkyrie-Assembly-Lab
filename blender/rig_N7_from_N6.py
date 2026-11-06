"""N7: auditable Fighter -> GERWALK leg/arm deployment study from N6.

Preserves N6 source: opens a *copy* in background Blender, builds actual separate
upper/lower nacelle mesh pieces and real hip/knee pivots. No scale tricks, pose
teleports, or claimed toy-accurate linkage. Original 1982 Macross visuals remain
the target; the L2 pose-only study is used for movement ideas, not geometry.

Run with:
  blender --background --python blender/rig_N7_from_N6.py
Windows Blender-MCP background runner overrides __file__ to its restricted
working directory. Never run from the interactive Blender Python console.
"""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parent
N6=BASE/"rebuild_N6"/"VF1J_rebuild_N6.blend"
OUT=BASE/"rebuild_N7"
OUT.mkdir(exist_ok=True,parents=True)
if not N6.is_file():
    raise FileNotFoundError("First reproduce N6 from blender/rebuild_N6.py: "+str(N6))
bpy.ops.wm.open_mainfile(filepath=str(N6))
scene=bpy.context.scene
model=bpy.data.collections["N1 newly traced replaceable components"]
root=bpy.data.objects["N1 AIRFRAME - new independent rebuild"]
scene.frame_set(1)
bpy.context.view_layer.update()
# Hard gate: every N6 source mesh must retain identical world positions
# when the N7 Fighter timeline is at frame 1.
def sampled_world_verts(obj):
    return {tuple(round(x,5) for x in obj.matrix_world@v.co) for v in obj.data.vertices}
baseline={o.name:sampled_world_verts(o) for o in model.all_objects if o.type=="MESH"}

S=14.23/(1470-414)
def yy(u):return (u-414)*S-7.115
def xx(v):return (569-v)*S
def zz(v):return (975-v)*S

# Reparent while preserving every source component's Fighter world transform.
def attach_keep(obj,parent):
    # Blender's matrix_world setter is not a durable parent inverse for a
    # keyframed hierarchy. Explicitly factor source world/basis transforms.
    wm=obj.matrix_world.copy()
    basis=obj.matrix_basis.copy()
    obj.parent=parent
    obj.matrix_parent_inverse=parent.matrix_world.inverted()@wm@basis.inverted()
    bpy.context.view_layer.update()

def pivot(name,position,parent):
    ob=bpy.data.objects.new(name,None)
    model.objects.link(ob)
    ob.empty_display_type="SPHERE";ob.empty_display_size=.16
    ob.location=position
    # Build at correct world coordinate before parenting.
    ob.parent=parent
    ob.matrix_parent_inverse=parent.matrix_world.inverted()
    bpy.context.view_layer.update()
    return ob

def section_piece(src,label,kmin,kmax,parent,close_rear=False):
    original=src.data
    n=16
    stations=len(original.vertices)//n
    if stations!=13:raise RuntimeError("Unexpected N6 shell topology: "+str(stations))
    if kmin<0 or kmax>=stations or kmin>=kmax:raise ValueError("Invalid section range")
    verts=[tuple(original.vertices[k*n+j].co) for k in range(kmin,kmax+1) for j in range(n)]
    faces=[]
    for k in range(kmax-kmin):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;c=(k+1)*n+(j+1)%n;d=(k+1)*n+j
            faces.append((a,b,c,d))
    if close_rear:
        faces.append(tuple((kmax-kmin)*n+j for j in range(n)))
    mesh=bpy.data.meshes.new(label)
    mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(label,mesh);model.objects.link(obj)
    for material in original.materials:mesh.materials.append(material)
    obj.parent=parent
    obj.matrix_parent_inverse=parent.matrix_world.inverted()@src.matrix_world
    bpy.context.view_layer.update()
    obj["N7_role"]="RIGID_NACELLE_SUBSEGMENT"
    obj["source_section_range"]=[kmin,kmax]
    obj["source_object"]=src.name
    return obj

keyframes=(1,16,31,46,61,76,91)
hip_angles=(0,-12,-29,-47,-65,-72,-70)
knee_angles=(0,0,8,17,26,38,35)
arm_angles=(0,-8,-20,-36,-47,-60,-62)
root["N7_goal"]="Continuous first-pass GERWALK leg and arm deployment using preserved N6 Fighter geometry; NOT final toy mechanics"
all_hips=[];all_knees=[];all_arms=[]
manifest={"source_N6":str(N6),"source_sha256":hashlib.sha256(N6.read_bytes()).hexdigest(),
          "checkpoint":"N7","split_section_index":4,"split_u":1125,
          "pivots":{},"frames":list(keyframes),
          "limits":["Only first-pass Fighter/GERWALK, no Battroid yet",
                    "No collision-cleared real toy mechanism",
                    "Ankle/nozzle foot articulation and full elbow chain not yet modeled",
                    "Visual fidelity to VF-1J technical drawings not certified"]}

for s,label in [(-1,"LEFT"),(1,"RIGHT")]:
    scene.frame_set(1)
    bpy.context.view_layer.update()
    g=bpy.data.objects["JOINT "+label+" nacelle knee frame - unrigged"]
    shell=bpy.data.objects[label+" N6 contoured engine-leg casing"]
    if shell.parent!=g:raise RuntimeError("Unexpected shell parent")
    hip=pivot("N7 "+label+" HIP swing",Vector((s*xx(477),yy(1022),zz(1008))),root)
    attach_keep(g,hip)
    # Knee is nested under the original nacelle-group and is therefore coupled
    # to its corresponding HIP; the 1125 station is a *shared* ring of both
    # shell pieces, rotating about the registered knee axis.
    knee=pivot("N7 "+label+" KNEE reverse hinge",
               Vector((s*xx(477),yy(1125),zz(1003))),g)
    top=section_piece(shell,label+" N7 UPPER engine-thigh casing",0,4,g,False)
    lower=section_piece(shell,label+" N7 LOWER engine-shin casing",4,12,knee,True)
    bpy.data.objects.remove(shell,do_unlink=True)
    # Every existing part is moved with its actual 3D body. Front intake
    # remains on upper casing, service armor/nozzle/fins follow lower shin.
    lower_objects=[]
    for child in list(g.children):
        if child in (knee,top):
            continue
        name=child.name.lower()
        if ("n6 detachable engine side armor" in name or
            "nozzle" in name or "fan blade" in name or
            "ventral stabilizer" in name or "nacelle dorsal station" in name):
            attach_keep(child,knee)
            lower_objects.append(child.name)
    # The existing arm package has a *real* retract/deploy pivot. We do not
    # introduce hidden teleports or scale it from zero.
    arm=bpy.data.objects["COMPONENT "+label+" arm package"]
    shoulder=pivot("N7 "+label+" SHOULDER deploy",
                   Vector((s*.40,yy(850),zz(1037))),root)
    attach_keep(arm,shoulder)

    for i,fr in enumerate(keyframes):
        hip.location=(s*xx(477)+s*(.22*i/(len(keyframes)-1)),yy(1022),zz(1008))
        hip.rotation_euler=(math.radians(hip_angles[i]),0,math.radians(-s*3*i/(len(keyframes)-1)))
        knee.rotation_euler=(math.radians(knee_angles[i]),0,0)
        shoulder.location=(s*.40+s*.45*i/(len(keyframes)-1),yy(850),zz(1037))
        shoulder.rotation_euler=(math.radians(arm_angles[i]),0,math.radians(-s*8*i/(len(keyframes)-1)))
        for ob in (hip,knee,shoulder):
            ob.keyframe_insert("location",frame=fr)
            ob.keyframe_insert("rotation_euler",frame=fr)
    # Blender 5.2 uses layered Actions rather than the legacy action.fcurves
    # API. Default keyframe interpolation is Bézier; preserve that default.
    all_hips.append(hip);all_knees.append(knee);all_arms.append(shoulder)
    manifest["pivots"][label]={
        "hip":hip.name,"knee":knee.name,"shoulder":shoulder.name,
        "upper":top.name,"lower":lower.name,
        "parts_following_knee":lower_objects,
        "keyframe_hip_degrees":list(hip_angles),
        "keyframe_knee_degrees":list(knee_angles),
        "keyframe_shoulder_degrees":list(arm_angles)
    }

# N6 wing sweep keyframes remain 1->30, physically rotate the existing wing
# geometry and then hold their extended stance through the GERWALK study.
scene.frame_start=1;scene.frame_end=91
for n,fr in [("Fighter source pose",1),("GERWALK partial",46),("GERWALK prototype",91)]:
    scene.timeline_markers.new("N7 "+n,frame=fr)
scene["N7_status"]="Kinematic proof-of-loop, not yet certified mechanically feasible GERWALK"
scene["N7_source_poses"]="Legacy L2 has endpoint-only manually authored poses; NOT imported into N7"
scene["N7_kinematics"]="Moving coherent N6 rigid body pieces; N7 shoulder+hip+knee keyframes 1..91"

# Save at Fighter frame before rendering. All existing Blender color/material
# and site-independent source assets remain editable and unchanged otherwise.
scene.frame_set(1)
bpy.context.view_layer.update()
for name,old in baseline.items():
    if name.endswith(" N6 contoured engine-leg casing"):
        label=name.split()[0]
        first=sampled_world_verts(bpy.data.objects[label+" N7 UPPER engine-thigh casing"])
        last=sampled_world_verts(bpy.data.objects[label+" N7 LOWER engine-shin casing"])
        delta=len(old.symmetric_difference(first|last))
    else:
        obj=bpy.data.objects.get(name)
        if obj is None:raise RuntimeError("Fighter part vanished: "+name)
        delta=len(old.symmetric_difference(sampled_world_verts(obj)))
    if delta:
        raise RuntimeError("FRAME1_FIDELITY_FAILURE "+name+" changed verts "+str(delta))
print("N7_FRAME1_FIDELITY_PASS="+str(len(baseline))+" source mesh sets; source N6 Fighter preserved",flush=True)
blend=OUT/"VF1J_rebuild_N7.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
manifest["blend_file"]=str(blend)
manifest["blender"]=bpy.app.version_string
manifest["scene_mesh_count"]=len([o for o in model.all_objects if o.type=="MESH"])

# Compare fixed orthographic cameras; same focal lengths for all modes, fixed
# target to prevent judging different perspectives at different frames.
for frame in (1,31,61,91):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    for view in ("fighter_side","fighter_threequarter","fighter_front"):
        camera=bpy.data.objects.get(view)
        if not camera:raise RuntimeError("N6 camera missing: "+view)
        scene.camera=camera
        scene.render.filepath=str(OUT/("pose_%03d_%s.png"%(frame,view.replace("fighter_",""))))
        scene.render.resolution_x=1000;scene.render.resolution_y=750
        scene.render.resolution_percentage=100
        if scene.render.engine=="CYCLES":
            scene.cycles.samples=24
        bpy.ops.render.render(write_still=True)
        print("N7_RENDER_READY",frame,view,flush=True)
scene.frame_set(1);scene.camera=bpy.data.objects["fighter_threequarter"]
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
manifest["blend_sha256"]=hashlib.sha256(blend.read_bytes()).hexdigest()
(OUT/"N7_kinematic_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
print("N7_BUILD_COMPLETE="+json.dumps({
    "blend":str(blend),"sha256":manifest["blend_sha256"],
    "meshes":manifest["scene_mesh_count"],
    "frames":list(keyframes)
}),flush=True)
