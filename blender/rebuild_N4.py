"""N4: independent inlet and nacelle detail refinement of Fighter blockout. UNFINISHED, no toy transformation claim.
Upper half of VF-1A five-view sheet supplies shared airframe top outline; side view
supplies vertical limits. VF-1J head/markings retained. Cross-sections are inferred.
Coordinates in source are pixels of the 1800x1140 reference. No K/L2 mesh imported.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
from math import pi,cos,sin
ROOT=Path(__file__).parent/'rebuild_N4';ROOT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.unit_settings.system='METRIC'
S=14.23/(1470-414)
def yy(u):return (u-414)*S-7.115
def xx(v):return (569-v)*S
def zz(v):return (975-v)*S
model=bpy.data.collections.new('N1 newly traced replaceable components');scene.collection.children.link(model)
studio=bpy.data.collections.new('STUDIO');scene.collection.children.link(studio)
def col(o,c=model):
 for c0 in list(o.users_collection):c0.objects.unlink(o)
 c.objects.link(o);return o
def material(n,c,rough=.37,metal=.12):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
white=material('Blockout pearl white',(.78,.8,.81));red=material('VF-1J red',(.72,.015,.02));black=material('Black cavity',(.012,.018,.023));grey=material('Structural grey',(.27,.31,.34));steel=material('Nozzle steel',(.12,.15,.17),.31,.6)
glass=material('Smoked blue shell',(.27,.42,.53),.12,0);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.88;p.inputs['IOR'].default_value=1.46
green=material('VF-1J visor',(.03,.5,.16),.2,.25)
def empty(n,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(n,None);model.objects.link(o);o.location=loc;o.parent=parent;o.empty_display_type='PLAIN_AXES';o.empty_display_size=.28;return o
root=empty('N1 AIRFRAME - new independent rebuild')
def mesh(n,v,f,ma=white,parent=None,bevel=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);model.objects.link(o);o.data.materials.append(ma);o.parent=parent or root
 if bevel:
  b=o.modifiers.new('Small manufactured edge radius','BEVEL');b.width=bevel;b.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cube(n,loc,dim,ma=white,parent=None,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);col(o);o.parent=parent or root;o.data.materials.append(ma)
 if bevel:b=o.modifiers.new('Small edge radius','BEVEL');b.width=bevel;b.segments=2
 return o
def line(n,points,ma=black,r=.012,parent=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(n,cu);model.objects.link(o);o.data.materials.append(ma);o.parent=parent or root;return o
def tube(n,a,b,r,ma=steel,parent=None):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();col(o);o.data.materials.append(ma);o.parent=parent or root;return o
# Generic section loft, with longitudinal stations and 12-sided engineered sections.
# Each section specifies u, center X, half width, top pixel v, bottom pixel v.
def sections(n,stations,ma,parent,roundness=1):
 verts=[];N=16
 for u,cx,w,top,bottom in stations:
  zt,zb=zz(top),zz(bottom);mid=(zt+zb)/2;rz=(zt-zb)/2
  for j in range(N):
   a=2*pi*j/N
   # Superellipse exponent <1 flattens top and sides for faceted nacelles.
   ex=math.copysign(abs(cos(a))**roundness,cos(a));ez=math.copysign(abs(sin(a))**roundness,sin(a))
   verts.append((cx+w*ex,yy(u),mid+rz*ez))
 faces=[]
 for k in range(len(stations)-1):
  for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 faces.extend([tuple(range(N-1,-1,-1)),tuple((len(stations)-1)*N+j for j in range(N))])
 return mesh(n,verts,faces,ma,parent)
nose=empty('COMPONENT radome',parent=root)
radome=[(414,0,0.008,974.6,975.4),(435,0,13*S,965,983),(470,0,22*S,955,989),(520,0,29*S,944,995),(580,0,34*S,931,1000),(638,0,37*S,923,1003)]
ob=sections('Radome traced outline',radome,white,nose)
# Subdivision keeps the long continuous radome without stacked-cone shoulders.
sub=ob.modifiers.new('Continuous radome surface','SUBSURF');sub.levels=2;sub.render_levels=2
fuselage=empty('JOINT nose canopy fold - not yet rigged',parent=root)
body=[(638,0,37*S,923,1003),(680,0,40*S,930,1001),(740,0,43*S,931,998),(810,0,45*S,923,995),(860,0,42*S,918,994),(920,0,37*S,916,1023),(974,0,31*S,926,1034)]
sections('Cockpit body traced sections',body,white,fuselage,.72)
# One thin radome separation line.
ring=[(37.3*S*cos(2*pi*j/64),yy(639),zz(963)+40*S*sin(2*pi*j/64)) for j in range(65)]
line('Single radome seam',ring,grey,.009,nose)
# Canopy is its own replaceable shell and frame; no hidden opaque duplicate.
canopy=empty('COMPONENT canopy shell',parent=fuselage)
canopy_stations=[(651,0,19*S,927,930),(690,0,27*S,910,931),(746,0,31*S,895,929),(786,0,33*S,891,925),(824,0,31*S,892,918),(847,0,22*S,897,913)]
verts=[];N=12
for u,cx,w,t,b in canopy_stations:
 for j in range(N+1):
  a=pi*j/N;verts.append((w*cos(a),yy(u),zz(b)+(zz(t)-zz(b))*sin(a)))
faces=[(k*(N+1)+j,k*(N+1)+j+1,(k+1)*(N+1)+j+1,(k+1)*(N+1)+j) for k in range(len(canopy_stations)-1) for j in range(N)]
mesh('Smoked transparent canopy traced crown',verts,faces,glass,canopy)
for j in [0,N]:
 line('Canopy lower seal',[verts[k*(N+1)+j] for k in range(len(canopy_stations))],black,.025,canopy)
for k in [0,3,len(canopy_stations)-1]:
 line('Canopy transverse frame',[verts[k*(N+1)+j] for j in range(N+1)],grey,.025,canopy)
cube('Pilot seat',(0,yy(776),zz(942)),(.38,.55,.58),black,canopy)
cube('Pilot torso',(0,yy(752),zz(939)),(.30,.3,.29),red,canopy)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.15,location=(0,yy(752),zz(913)));ob=bpy.context.object;ob.name='Pilot helmet';col(ob);ob.data.materials.append(white);ob.parent=canopy
# Shoulder outline is directly traced from TOP HALF, never from the underside half.
shoulder_outline=[(759,468,946),(789,465,939),(861,437,931),(970,406,930),(1074,434,938),(1127,512,946),(1065,530,943),(1059,563,939),(973,567,929),(973,550,926),(789,526,936)]
shoulders=[]
for s,label in [(-1,'LEFT'),(1,'RIGHT')]:
 group=empty('JOINT '+label+' chest armor hinge - unrigged',parent=root);shoulders.append(group)
 v=[(s*xx(v),yy(u),zz(z)) for u,v,z in shoulder_outline]
 v += [(x,y,z-.22) for x,y,z in v]
 count=len(shoulder_outline);faces=[tuple(range(count)),tuple(range(2*count-1,count-1,-1))]
 faces.extend((j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count))
 mesh(label+' faceted traced shoulder roof',v,faces,white,group,.012)
 # Broad black top intake follows the diagonal leading edge from the drawing.
 pts=[(789,516,930),(852,451,928),(868,451,927),(820,516,929)]
 pv=[(s*xx(v),yy(u),zz(z)+.016) for u,v,z in pts]
 mesh(label+' long diagonal top intake opening',pv,[(0,1,2,3)],black,group)
 # Opening wall depth gives a cavity instead of painted black square.
 low=[(x,y,z-.17) for x,y,z in pv];mesh(label+' intake recessed side walls',pv+low,[(0,1,5,4),(1,2,6,5),(2,3,7,6)],steel,group)
 # VF-1J's much broader white/red chest band; silhouette remains the N2 airframe.
 pp=[(852,522,938),(875,492,935),(941,422,930),(969,413,930),(1015,431,934),(1065,454,938),(1052,484,939),(1006,462,937),(961,455,933),(893,535,939)]
 mesh(label+' red shoulder chevron',[(s*xx(v),yy(u),zz(z)+.055) for u,v,z in pp],[tuple(range(len(pp)))],red,group)
# Center dorsal beam: separate from torso plates and replaceable for a real mechanism.
dorsal=empty('JOINT dorsal frame - unrigged',parent=root)
sections('Dorsal central spine',[(955,0,.48,916,947),(1080,0,.48,925,958),(1220,0,.38,931,961),(1380,0,.34,935,963),(1410,0,.18,940,960)],white,dorsal,.4)
# Engine-leg nacelles traced in side profile with front view inferred sections.
engines=[]
for s,label in [(-1,'LEFT'),(1,'RIGHT')]:
 g=empty('JOINT '+label+' nacelle knee frame - unrigged',parent=root);engines.append(g)
 cx=s*xx(477)
 st=[(1022,cx,.28,991,1025),(1060,cx,.40,978,1033),(1147,cx,.55,962,1042),(1260,cx,.55,957,1049),(1378,cx,.53,962,1047),(1412,cx,.43,971,1037)]
 sections(label+' engine six traced cross sections',st,white,g,.43)
 # N4: independent engine-intake lips, dark throat and crossbar, inspired by
 # the twin square-ish inlets visible in the VF-1A front technical drawing.
 # White nacelle cap remains behind the recessed shadow; these components
 # can later move together as a dedicated intake/upper-leg assembly.
 inlet_z=zz(1008)
 n_intake=24
 outer=[(cx+.291*cos(2*pi*j/n_intake),yy(1013.8),inlet_z+.249*sin(2*pi*j/n_intake)) for j in range(n_intake)]
 inner=[(cx+.232*cos(2*pi*j/n_intake),yy(1012.9),inlet_z+.197*sin(2*pi*j/n_intake)) for j in range(n_intake)]
 rim_faces=[(j,(j+1)%n_intake,n_intake+(j+1)%n_intake,n_intake+j) for j in range(n_intake)]
 mesh(label+' separate intake rim',outer+inner,rim_faces,grey,g)
 cavity=[(cx+.230*cos(2*pi*j/n_intake),yy(1017),inlet_z+.195*sin(2*pi*j/n_intake)) for j in range(n_intake)]
 mesh(label+' dark intake throat',cavity,[tuple(range(n_intake))],black,g)
 for zoff in [-.074,.075]:
  line(label+' intake guide vane',[(cx-.194,yy(1012.6),inlet_z+zoff),(cx+.194,yy(1012.6),inlet_z+zoff)],steel,.011,g)
 # Editable engine access-panel trim and maintenance hatch follow the technical
 # side view; they add no bulk and preserve the outer nacelle outline.
 panel_side_x=s*(abs(cx)+.472)
 yz=[(1156,1007),(1174,989),(1226,985),(1344,986),(1384,996),(1380,1019),(1332,1027),(1210,1027),(1170,1020),(1156,1007)]
 line(label+' engine flank access-panel seam',[(panel_side_x,yy(u),zz(v)) for u,v in yz],grey,.011,g)
 hatch_x=s*(abs(cx)+.49)
 hatch_center_y=yy(1335)
 hatch_center_z=zz(1007)
 hatch_pts=[(hatch_x,hatch_center_y+.222*cos(2*pi*j/48),hatch_center_z+.222*sin(2*pi*j/48)) for j in range(49)]
 line(label+' circular engine service hatch',hatch_pts,grey,.013,g)
 # A two-level nozzle, with inset dark mouth and fan disk.
 sections(label+' nozzle outer octagon',[(1411,cx,.43,971,1037),(1468,cx,.41,979,1034)],steel,g,.35)
 mesh(label+' nozzle black aperture',[(cx+.36*cos(2*pi*j/16),yy(1469),zz(1007)+.32*sin(2*pi*j/16)) for j in range(16)],[tuple(range(16))],black,g)
 tube(label+' nozzle central turbine',(cx,yy(1469),zz(1007)),(cx,yy(1471),zz(1007)),.19,steel,g)
 for j in range(9):
  a=2*pi*j/9;line(label+' fan blade',[(cx+.07*cos(a),yy(1472),zz(1007)+.07*sin(a)),(cx+.28*cos(a+.24),yy(1472),zz(1007)+.26*sin(a+.24))],grey,.017,g)
 # Simple section lines at measured shoulder and nozzle stations.
 for u in [1147,1260,1378]:
  line(label+' nacelle dorsal station',[(cx-.35,yy(u),zz(960)),(cx+.35,yy(u),zz(960))],grey,.008,g)
 # Ventral fin side silhouette.
 verts=[(cx,yy(u),zz(v)) for u,v in [(1182,1047),(1210,1080),(1340,1060),(1357,1047)]]
 mesh(label+' ventral stabilizer',verts,[tuple(range(4))],white,g)
# Rigid variable-sweep wing modules. Trace is NORMAL sweep line in schematic.
wingtrace=[(974,406),(1196,108),(1215,106),(1301,139),(1121,389),(1084,432)]
wings=[]
for s,label in [(-1,'LEFT'),(1,'RIGHT')]:
 pivot=Vector((s*xx(406),yy(974),zz(944)));g=empty('JOINT '+label+' wing sweep axle',pivot,root);wings.append(g)
 v=[Vector((s*xx(v),yy(u),zz(944)))-pivot for u,v in wingtrace];th=.065
 verts=[(p.x,p.y,p.z+th/2) for p in v]+[(p.x,p.y,p.z-th/2) for p in v];n=len(v)
 mesh(label+' traced normal-sweep wing',verts,[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],white,g,.009)
 # Red strip follows the main wing, kept simple for silhouette review.
 stripe=[(1010,397),(1220,124),(1247,157),(1040,421)]
 mesh(label+' red wing identification stripe',[(s*xx(v)-pivot.x,yy(u)-pivot.y,th/2+.006) for u,v in stripe],[(0,1,2,3)],red,g)
 g['normal_sweep_degrees']=0;g['approx_low_speed_sweep_degrees']=-s*26.5
 # Two frames only test the rigid wing sweep; no other mode claimed.
 g.rotation_euler.z=0;g.keyframe_insert(data_path='rotation_euler',frame=1)
 g.rotation_euler.z=math.radians(-s*26.5);g.keyframe_insert(data_path='rotation_euler',frame=30)
 g.rotation_euler.z=0
# Side-profile vertical fins: no tall knife improvisation.
for s,label in [(-1,'LEFT'),(1,'RIGHT')]:
 g=empty('COMPONENT '+label+' vertical tail',parent=dorsal)
 pts=[(1170,924),(1340,924),(1426,816),(1370,807)]
 v=[(s*(.87+.17*(924-v)/(924-807)),yy(u),zz(v)) for u,v in pts]
 mesh(label+' traced raked vertical tail',v,[(0,1,2,3)],white,g)
 line(label+' vertical fin red accent',[v[2],v[3]],red,.027,g)
# Simple replaceable folded arm and gun geometry, with no deploy poses in N1.
for s,label in [(-1,'LEFT'),(1,'RIGHT')]:
 g=empty('COMPONENT '+label+' arm package',parent=root)
 sections(label+' folded forearm',[(850,s*.40,.26,1045,1073),(1080,s*.40,.27,1046,1071)],white,g,.4)
gun=empty('COMPONENT GU11 stowed gunpod',parent=root)
tube('GU11 main body',(0,yy(835),zz(1052)),(0,yy(1140),zz(1052)),.20,steel,gun)
tube('GU11 muzzle',(0,yy(820),zz(1052)),(0,yy(835),zz(1052)),.14,steel,gun)
head=empty('COMPONENT VF-1J stowed head placeholder',parent=root)
cube('VF-1J stowed helmet',(0,yy(885),zz(1024)),(.54,.49,.33),white,head)
cube('VF-1J green optical strip',(0,yy(865),zz(1037)),(.39,.12,.04),green,head)
for s in [-1,1]:tube('VF-1J paired head cannon',(s*.31,yy(850),zz(1025)),(s*.31,yy(925),zz(1025)),.035,steel,head)
# A saved reference-landmark table distinguishes traced outlines from inferred sections.
landmarks={'reference_url':'https://www.macross2.net/m3/sdfmacross/vf-1a-valkyrie/vf-1a-schematics.png','reference_pixels':[1800,1140],'scale_definition':{'nose_u':414,'rear_u':1470,'top_center_v':569,'side_datum_v':975,'nominal_fictional_length':14.23},'scope':'Approximate anime drawing trace; not a measurement or scan of the Bandai toy. Upper top-view half only; lower half is underside. Cross sections inferred from separate orthographic outlines.','top_landmarks':{'canopy_front':[651,550],'canopy_rear':[847,547],'shoulder_front':[759,468],'shoulder_outer_pivot':[970,406],'shoulder_rear':[1127,512],'wing_normal_tip_leading':[1196,108],'wing_normal_tip_trailing':[1301,139],'engine_center_v':477},'radome_sections':radome,'cockpit_sections':body,'shoulder_outline_uv_sideheight':shoulder_outline,'normal_wing_uv':wingtrace,'limitations':['Fighter blockout only. GERWALK/Battroid retained in K/L2 separate files.','Cross-sectional curvature is inferred, not scanned.','No deployed robot joints or continuous transformation solved.','No surface-detail fidelity claim. VF-1A drawing shares airframe only, VF-1J helmet remains a placeholder.']}
(ROOT/'reference_landmarks.json').write_text(json.dumps(landmarks,indent=2))
# Studio and true orthographic cameras before any cosmetic detail pass.
world=bpy.data.worlds.new('Neutral studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.28,.34,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
floor=cube('Studio ground',(0,0,-2.25),(200,200,.1),material('Ground',(.16,.18,.21),.6,0));col(floor,studio)
for n,loc,power,size in [('KEY',(4,-10,15),2500,8),('FILL',(-12,-4,7),1900,9),('RIM',(4,10,12),2500,7)]:
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
def cam(n,loc,target,scale,rot=None):
 d=bpy.data.cameras.new(n);d.type='ORTHO';d.ortho_scale=scale;o=bpy.data.objects.new(n,d);studio.objects.link(o);o.location=loc;o.rotation_euler=rot if rot else (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cameras=[cam('fighter_threequarter',(18,-24,13),(0,0,0),18),cam('fighter_front',(0,-30,0),(0,0,0),16),cam('fighter_top',(0,0,30),(0,0,0),16,(0,0,pi/2)),cam('fighter_side',(30,0,0),(0,0,0),16)]
scene.frame_end=30;scene.frame_set(1);scene.camera=cameras[0]
scene['status']='N4 Fighter intake aperture and nacelle side access detail. Transformed rig not modeled.'
scene['wing_sweep_instructions']='Frame 1 normal-sweep trace; frame 30 approximate low-speed wing sweep only. All other components fixed.'
scene['previous_work']='Checkpoint K and L2 are separate untouched three-pose studies.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'VF1J_rebuild_N4.blend'))
for camera in cameras:
 scene.camera=camera;scene.render.filepath=str(ROOT/(camera.name+'.png'));bpy.ops.render.render(write_still=True);print('RENDER_READY '+camera.name,flush=True)
scene.camera=cameras[0];scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'VF1J_rebuild_N4.blend'))
print('REBUILD_N4_COMPLETE',flush=True)
