import * as T from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { ASSEMBLIES, getPose } from './model.js';
import { assemblyTarget, pieceTarget } from './pieces.js';

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const modeNames = ['Fighter','GERWALK','Battroid'];
const captions = ['Wings extended. Arms and head stowed beneath the fuselage.','Engines swing down into legs. Arms unfold beneath the wings.','Fuselage folds into a torso. Wings tuck behind the deployed head.'];
const state = {mode:0,explosion:.52,catalog:false,selectedPiece:null,offsets:new Map(),selected:null,hover:null,isolated:false,labels:false,wire:false,rotate:false,camera:'perspective',demo:false,demoAt:0,ready:false};
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const container = $('#scene');
let renderer,scene,camera,controls,root,groups=new Map(),pickables=[],floor,stage,guideLines,guideArray;
let animationFrame,lastTime=0,toastTimer,viewTween=null,isPointerDown=false,downPoint=null,multiTouch=false;
let sceneHeight=0,sceneWidth=0;
const pointerIds=new Set(),raycaster=new T.Raycaster(),mouse=new T.Vector2(),tmp=new T.Vector3();
const poses = new Map(ASSEMBLIES.map(a=>[a.id,[0,1,2].map(mode=>getPose(a,mode))]));
const pieces=[],groupTargets=new Map(),pieceTargets=new Map();
let rayPiece=null,stageY=-2.9;
const studioFog=new T.Fog(0x080b12,70,190);
const labels = new Map(),materialBases=new Map(),originalCenters=new Map();

function notify(message){clearTimeout(toastTimer);$('#toast').textContent=message;$('#toast').hidden=false;toastTimer=setTimeout(()=>$('#toast').hidden=true,3000);}
function setPressed(button,on){button.classList.toggle('active',on);button.setAttribute('aria-pressed',String(on));}
function showError(message){$('#loading').hidden=true;$('#error').hidden=false;$('#error-message').textContent=message;state.ready=false;}
function stopDemo(){state.demo=false;$('#transform-play').classList.remove('active');$('#transform-play span').textContent='Play transformation';$('#transform-play use').setAttribute('href','#i-play');}
function effectiveExplosion(id){return state.offsets.has(id)?state.offsets.get(id):state.explosion;}
function refreshTargets(){
  if(!root)return;
  for(const a of ASSEMBLIES)groupTargets.set(a.id,assemblyTarget(a,state.mode,effectiveExplosion(a.id),state.catalog));
  for(const p of pieces){const t=pieceTarget(p.mesh.userData,effectiveExplosion(p.assembly),state.catalog,pieces.length,sceneWidth<760?12:24);const g=groupTargets.get(p.assembly);
    const matrix=new T.Matrix4().compose(g.position,g.quaternion,new T.Vector3(1,1,1)).multiply(new T.Matrix4().compose(t.position,t.quaternion,new T.Vector3().setScalar(t.scale)));
    t.box=p.mesh.geometry.boundingBox.clone().applyMatrix4(matrix);pieceTargets.set(p.mesh.name,t);
  }
  stageY=Math.min(...[...pieceTargets.values()].map(t=>t.box.min.y))-.3;
}
function updateUI(){
  refreshTargets();
  setPressed($('#catalog-toggle'),state.catalog);
  $('#catalog-toggle span').textContent=state.catalog?'Return to model':'All pieces';
  $('#catalog-note').hidden=!state.catalog;

  $('#explode-output').textContent=String(Math.round(state.explosion*100)).padStart(3,'0')+'%';
  $('#explode-range').value=Math.round(state.explosion*100);$('#explode-range').style.setProperty('--progress',state.explosion*100+'%');
  $('#explode-all span').textContent=state.explosion>.5?'Assemble model':'Explode model';
  $('#view-status').textContent=(state.catalog?'424 ELEMENTS · NORMALIZED SCALE':state.isolated?'ISOLATED SELECTION':'24 ASSEMBLIES · 424 ELEMENTS')+' · '+modeNames[state.mode].toUpperCase();
  $('#mode-caption').textContent=captions[state.mode];
  $$('[data-mode]').forEach(b=>setPressed(b,Number(b.dataset.mode)===state.mode));
  for(const a of ASSEMBLIES){const row=document.getElementById('row-'+a.id);row.classList.toggle('active',a.id===state.selected);row.classList.toggle('detached',effectiveExplosion(a.id)>.08);row.querySelector('button').setAttribute('aria-pressed',String(a.id===state.selected));}
  if(state.selected){$('#detach').hidden=!!state.selectedPiece;$('#detach').textContent=effectiveExplosion(state.selected)>.08?'Reattach':'Detach';$('#isolate').textContent=state.isolated?'Show all':'Isolate';$('#isolate').setAttribute('aria-pressed',String(state.isolated));}
}
function updateMaterials(){
  if(!root)return;
  for(const a of ASSEMBLIES){const group=groups.get(a.id);group.visible=!state.isolated||a.id===state.selected;
    group.traverse(o=>{if(!o.isMesh)return;o.visible=!state.isolated||!state.selectedPiece||o.name===state.selectedPiece;const materials=Array.isArray(o.material)?o.material:[o.material];for(const mat of materials){const base=materialBases.get(mat.uuid);if(!base)continue;mat.color.copy(base.color);mat.emissive.copy(base.emissive);mat.emissiveIntensity=base.intensity;mat.wireframe=state.wire;
      if(a.id===state.selected&&(!state.selectedPiece||o.name===state.selectedPiece)){mat.emissive.set(0xbc321f);mat.emissiveIntensity=.17;}else if(a.id===state.hover){mat.emissive.set(0x849b89);mat.emissiveIntensity=.12;}
      if(state.wire){mat.color.set(a.id===state.selected?0xbb3b27:0x466359);mat.opacity=1;mat.transparent=false;}else{mat.opacity=base.opacity;mat.transparent=base.transparent;}
    }});
  }
}
function clearSelection(){state.selected=null;state.selectedPiece=null;state.isolated=false;$('#selection-card').hidden=true;$('.viewport').classList.remove('inspecting');updateUI();updateMaterials();}
function selectAssembly(id,{focus=false,piece=null}={}){
  if(!state.ready)return;stopDemo();
  if(!id){clearSelection();return;}
  if(state.selected!==id)state.isolated=false;
  state.selected=id;state.selectedPiece=piece;const a=ASSEMBLIES.find(a=>a.id===id);
  $('.viewport').classList.add('inspecting');
  $('#selected-code').textContent='ASSEMBLY '+String(a.index).padStart(2,'0')+' / 24';$('#selected-name').textContent=a.name;$('#selected-description').textContent=a.detail;$('#selection-card').hidden=false;
  if(piece){const el=pieces.find(p=>p.mesh.name===piece);$('#selected-code').textContent='ELEMENT '+String(el.mesh.userData.pieceIndex+1).padStart(3,'0')+' / 424';$('#selected-name').textContent=a.short+' · '+String(el.mesh.userData.element).padStart(2,'0');$('#selected-description').textContent='Individually modeled element of the '+a.name.toLowerCase()+'. Isolate it for a closer look, or return to the assembly from the components list.';}
  $('#assemblies-panel').classList.remove('open');$('#assemblies-toggle').classList.remove('active');$('#assemblies-toggle').setAttribute('aria-expanded','false');
  updateUI();updateMaterials();
  if(focus)fitView(true);
}
function setExplosion(amount,{manual=true}={}){
  if(!state.ready)return;if(manual)stopDemo();state.catalog=false;state.explosion=Math.max(0,Math.min(1,amount));state.offsets.clear();
  if(state.isolated){state.isolated=false;updateMaterials();}
  updateUI();
}
function setMode(mode,{manual=true}={}){
  if(!state.ready)return;if(manual)stopDemo();state.catalog=false;state.mode=mode;state.explosion=0;state.offsets.clear();clearSelection();updateUI();
  state.camera='perspective';$$('[data-camera]').forEach(b=>setPressed(b,b.dataset.camera===state.camera));
  fitView(false,true);
}
function createAssemblyList(){
  let lastSection='';const list=$('#assembly-list');
  for(const a of ASSEMBLIES){if(a.section!==lastSection){const header=document.createElement('div');header.className='assembly-group';header.textContent=a.section;list.append(header);lastSection=a.section;}
    const row=document.createElement('div');row.className='assembly-item';row.id='row-'+a.id;
    const button=document.createElement('button');button.type='button';button.setAttribute('aria-pressed','false');button.title=a.name;button.innerHTML='<span class="part-number">'+String(a.index).padStart(2,'0')+'</span><span class="part-label"></span><span class="pin-dot" aria-hidden="true"></span><svg aria-hidden="true"><use href="#i-arrow"/></svg>';
    button.querySelector('.part-label').textContent=a.name;button.addEventListener('click',()=>selectAssembly(a.id));row.append(button);list.append(row);
    const label=document.createElement('button');label.type='button';label.className='part-tag';label.textContent=String(a.index).padStart(2,'0')+'  '+a.short;label.title=a.name;label.hidden=true;label.addEventListener('click',()=>selectAssembly(a.id));$('#labels').append(label);labels.set(a.id,label);
  }
}
function studioEnvironment(){
  const env=new T.Scene();env.background=new T.Color(0x9ca9a2);
  const lightPanel=(color,intensity,w,h,p,look)=>{const m=new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({color:new T.Color(color).multiplyScalar(intensity),side:T.DoubleSide}));m.position.set(...p);m.lookAt(...look);env.add(m);};
  lightPanel(0xffffff,3.2,12,9,[-6,9,-6],[0,0,0]);lightPanel(0xd6f1ff,1.7,8,14,[8,3,3],[0,0,0]);lightPanel(0xffffff,2.4,5,12,[-4,1,8],[0,0,0]);
  const generator=new T.PMREMGenerator(renderer);const map=generator.fromScene(env,.06,.1,60,{size:128});generator.dispose();env.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});return map.texture;
}
function buildStage(){
  stage=new T.Group();scene.add(stage);
  floor=new T.Mesh(new T.PlaneGeometry(400,400),new T.MeshStandardMaterial({color:0x424e61,roughness:.75,metalness:.12}));floor.rotation.x=-Math.PI/2;floor.position.y=-.12;floor.receiveShadow=true;stage.add(floor);
  const platform=new T.Mesh(new T.CylinderGeometry(9.8,9.8,.12,128),new T.MeshStandardMaterial({color:0x63768b,metalness:.38,roughness:.42}));platform.position.y=-.06;platform.receiveShadow=true;stage.add(platform);
  for(const radius of [9.35,9.6]){const ring=new T.Mesh(new T.TorusGeometry(radius,.013,4,128),new T.MeshBasicMaterial({color:0xabc0d7,transparent:true,opacity:.50}));ring.rotation.x=Math.PI/2;ring.position.y=.005;stage.add(ring);}
  stage.position.y=-2.9;
  guideArray=new Float32Array(ASSEMBLIES.length*6);const geo=new T.BufferGeometry();geo.setAttribute('position',new T.BufferAttribute(guideArray,3));guideLines=new T.LineSegments(geo,new T.LineDashedMaterial({color:0x8c9e92,dashSize:.10,gapSize:.09,transparent:true,opacity:.40}));guideLines.frustumCulled=false;scene.add(guideLines);
}
function resize(){
  if(!renderer)return;const r=container.getBoundingClientRect();if(r.width<1||r.height<1)return;const previous=camera.aspect;sceneWidth=r.width;sceneHeight=r.height;camera.aspect=r.width/r.height;camera.updateProjectionMatrix();renderer.setSize(r.width,r.height,false);if(state.ready&&Math.abs(previous-camera.aspect)>.08){refreshTargets();fitView(state.isolated);}
}
function desiredBounds({selected=false}={}){
  const box=new T.Box3();
  for(const p of pieces){if(selected&&(p.assembly!==state.selected||(state.selectedPiece&&p.mesh.name!==state.selectedPiece)))continue;box.union(pieceTargets.get(p.mesh.name).box);}
  return box;
}
function fitView(selected=false,transitioning=false){
  if(!root)return;const box=desiredBounds({selected:selected&&!!state.selected});const center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3());
  let dir;if(state.catalog)dir=new T.Vector3(0,0,1);else if(state.camera==='top')dir=new T.Vector3(0,1,-.001);else if(state.camera==='side')dir=new T.Vector3(-1,.02,0);else dir=new T.Vector3(-.60,.48,-.90).normalize();
  // Fit all eight bounding-box corners in the unobstructed center of the canvas.
  const right=new T.Vector3().crossVectors(dir,new T.Vector3(0,1,0)).normalize();const up=new T.Vector3().crossVectors(right,dir).normalize();
  let halfW=0,halfH=0,depth=0;
  for(const piece of pieces){
    if(selected&&state.selected&&(piece.assembly!==state.selected||(state.selectedPiece&&piece.mesh.name!==state.selectedPiece)))continue;
    const b=pieceTargets.get(piece.mesh.name).box;
    for(const x of [b.min.x,b.max.x])for(const y of [b.min.y,b.max.y])for(const z of [b.min.z,b.max.z]){const v=new T.Vector3(x,y,z).sub(center);halfW=Math.max(halfW,Math.abs(v.dot(right)));halfH=Math.max(halfH,Math.abs(v.dot(up)));depth=Math.max(depth,Math.abs(v.dot(dir)));}
  }
  const isMobile=sceneWidth<620;
  const vfov=T.MathUtils.degToRad(camera.fov)/2;
  const usableH=selected ? (isMobile ? .32 : .65) : (isMobile ? .47 : .70),usableW=selected ? .71 : (isMobile ? .84 : .64);
  const distance=Math.max(halfH/(Math.tan(vfov)*usableH),halfW/(Math.tan(vfov)*camera.aspect*usableW))+depth*.55;
  const boundedDistance=T.MathUtils.clamp(distance,selected?3:12,650);
  const target=center.clone();
  // Offset the projected center away from the bottom controls, with room above on phones.
  const centerShift=isMobile?-.018:.035;
  target.addScaledVector(up,boundedDistance*Math.tan(vfov)*centerShift);
  viewTween={from:camera.position.clone(),to:target.clone().addScaledVector(dir,boundedDistance),targetFrom:controls.target.clone(),targetTo:target,started:performance.now(),duration:reducedMotion?0:transitioning?1700:700};
}
function hoveredAssembly(clientX,clientY){
  rayPiece=null;if(!state.ready)return null;const r=container.getBoundingClientRect();mouse.set((clientX-r.left)/r.width*2-1,-(clientY-r.top)/r.height*2+1);raycaster.setFromCamera(mouse,camera);
  const intersects=raycaster.intersectObjects(pickables,false);
  for(const hit of intersects){let o=hit.object,visible=true,id=null;while(o){if(!o.visible){visible=false;break;}if(o.userData.assemblyId)id=o.userData.assemblyId;o=o.parent;}if(visible&&id){rayPiece=hit.object.userData.pieceId||null;return id;}}
  return null;
}
function renderLabels(){
  const occupied=[];
  const isMobile=sceneWidth<620;
  const ordered=[...ASSEMBLIES].sort((a,b)=>(b.id===state.selected)-(a.id===state.selected));
  for(const a of ordered){const label=labels.get(a.id);const group=groups.get(a.id);
    let show=state.labels&&group.visible&&!state.catalog;
    if(!show){label.hidden=true;continue;}
    const point=originalCenters.get(a.id).getCenter(tmp).clone();point.y+=.4;group.localToWorld(point);point.project(camera);
    const x=(point.x*.5+.5)*sceneWidth,y=(-point.y*.5+.5)*sceneHeight;
    const width=Math.min(160,a.short.length*6+35),height=24;
    if(point.z>1||point.z<0||x<width/2+9||x>sceneWidth-width/2-50||y<185||y>sceneHeight-211){label.hidden=true;continue;}
    let ly=y;
    for(let attempt=0;attempt<4;attempt++){if(!occupied.some(r=>Math.abs(r.x-x)<(r.w+width)/2+5&&Math.abs(r.y-ly)<height+5))break;ly+=28;}
    if(ly>sceneHeight-210||occupied.some(r=>Math.abs(r.x-x)<(r.w+width)/2+5&&Math.abs(r.y-ly)<height+5)){label.hidden=true;continue;}
    occupied.push({x,y:ly,w:width});label.hidden=false;label.style.left=x+'px';label.style.top=ly+'px';label.classList.toggle('active',a.id===state.selected);
  }
}
function animate(now){
  animationFrame=requestAnimationFrame(animate);if(!state.ready)return;const dt=Math.min((now-lastTime)/1000||.016,.05);lastTime=now;
  if(state.demo&&now-state.demoAt>4000){state.demoAt=now;setMode((state.mode+1)%3,{manual:false});}
  const alpha=reducedMotion?1:1-Math.exp(-dt*4.6);
  let maxExplosion=0;
  for(const a of ASSEMBLIES){const g=groups.get(a.id),p=groupTargets.get(a.id),ex=effectiveExplosion(a.id);maxExplosion=Math.max(maxExplosion,ex);
    const target=tmp.copy(p.position);
    g.position.lerp(target,alpha);g.quaternion.slerp(p.quaternion,alpha);
    const idx=(a.index-1)*6;guideArray[idx]=p.position.x;guideArray[idx+1]=p.position.y;guideArray[idx+2]=p.position.z;guideArray[idx+3]=g.position.x;guideArray[idx+4]=g.position.y;guideArray[idx+5]=g.position.z;
  }
  for(const p of pieces){const t=pieceTargets.get(p.mesh.name);p.mesh.position.lerp(t.position,alpha);p.mesh.quaternion.slerp(t.quaternion,alpha);p.mesh.scale.lerp(tmp.setScalar(t.scale),alpha);}
  root.traverse(o=>{if(o.isLine)o.visible=maxExplosion<.04&&!state.catalog&&!state.isolated;});
  stage.visible=!state.catalog;scene.fog=state.catalog?null:studioFog;
  guideLines.visible=false;guideLines.geometry.attributes.position.needsUpdate=true;if(guideLines.visible)guideLines.computeLineDistances();
  const stageTarget=stageY;renderer.shadowMap.enabled=!state.catalog&&sceneWidth>=760;stage.position.y=T.MathUtils.lerp(stage.position.y,stageTarget,alpha);
  if(viewTween){const t=viewTween.duration?T.MathUtils.clamp((now-viewTween.started)/viewTween.duration,0,1):1,e=t*t*(3-2*t);camera.position.lerpVectors(viewTween.from,viewTween.to,e);controls.target.lerpVectors(viewTween.targetFrom,viewTween.targetTo,e);if(t>=1)viewTween=null;}
  controls.autoRotate=state.rotate&&!viewTween;controls.update(dt);root.updateMatrixWorld();renderLabels();renderer.render(scene,camera);
}
async function initialize(){
  createAssemblyList();
  try{
    renderer=new T.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});
    renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.65:2));renderer.setClearColor(0,0);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
    renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;container.append(renderer.domElement);
    renderer.domElement.setAttribute('aria-hidden','true');
    scene=new T.Scene();scene.background=new T.Color(0x080b12);scene.fog=studioFog;camera=new T.PerspectiveCamera(33,1,.1,2000);camera.position.set(-17,14,-26);
    controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.minDistance=2.5;controls.maxDistance=700;controls.maxPolarAngle=Math.PI*.93;controls.autoRotateSpeed=.65;controls.rotateSpeed=.7;controls.zoomSpeed=.85;controls.target.set(0,0,0);
    controls.addEventListener('start',()=>{viewTween=null;});
    scene.environment=studioEnvironment();
    scene.add(new T.HemisphereLight(0xe6f1ff,0x353b4e,1.5));
    const key=new T.DirectionalLight(0xfff9ec,4.0);key.position.set(-9,17,-10);key.castShadow=true;key.shadow.mapSize.set(innerWidth<760?1024:2048,innerWidth<760?1024:2048);Object.assign(key.shadow.camera,{left:-18,right:18,top:18,bottom:-18,near:1,far:60});key.shadow.normalBias=.045;key.shadow.bias=-.0003;key.shadow.radius=3;scene.add(key);
    const fill=new T.DirectionalLight(0xbce2eb,1.5);fill.position.set(12,7,5);scene.add(fill);const rim=new T.DirectionalLight(0xffffff,2);rim.position.set(-4,7,13);scene.add(rim);
    buildStage();resize();
    new ResizeObserver(()=>{resize();}).observe(container);
    const gltf=await new GLTFLoader().loadAsync(new URL('./assets/vf1-valkyrie.glb',import.meta.url).href);
    root=gltf.scene;scene.add(root);
    for(const a of ASSEMBLIES){const g=root.getObjectByName(a.id);if(!g)throw new Error('Missing assembly: '+a.id);groups.set(a.id,g);g.userData.assemblyId=a.id;
      const cloneCache=new Map();
      g.traverse(o=>{if(!o.isMesh)return;o.geometry.computeBoundingBox();o.geometry.computeBoundingSphere();o.castShadow=o.geometry.boundingSphere.radius>.18;o.receiveShadow=true;pickables.push(o);if(o.userData.pieceId)pieces.push({mesh:o,assembly:a.id});const convert=m=>{if(!cloneCache.has(o.name+m.uuid)){const clone=m.clone();cloneCache.set(o.name+m.uuid,clone);materialBases.set(clone.uuid,{color:clone.color.clone(),emissive:clone.emissive.clone(),intensity:clone.emissiveIntensity,opacity:clone.opacity,transparent:clone.transparent});}return cloneCache.get(o.name+m.uuid);};o.material=Array.isArray(o.material)?o.material.map(convert):convert(o.material);});
      const localBox=new T.Box3();g.updateWorldMatrix(true,true);const inv=g.matrixWorld.clone().invert();g.traverse(o=>{if(o.isMesh){o.geometry.computeBoundingBox();localBox.union(o.geometry.boundingBox.clone().applyMatrix4(new T.Matrix4().multiplyMatrices(inv,o.matrixWorld)));}});originalCenters.set(a.id,localBox);
    }
    state.ready=true;updateUI();fitView();viewTween.duration=0;$('#loading').hidden=true;
    bindControls();animate(performance.now());
  }catch(error){console.error(error);showError('The model could not load. Check your connection and refresh. If 3D is unavailable on this device, you can still download the model below.');}
}
function bindControls(){
  $('#explode-range').addEventListener('input',e=>{setExplosion(Number(e.target.value)/100);});
  $('#explode-range').addEventListener('change',()=>{fitView();});
  $('#explode-all').addEventListener('click',()=>{const amount=state.explosion>.5?0:1;setExplosion(amount);state.labels=amount===1;setPressed($('#labels-toggle'),state.labels);fitView();});
  $('#reassemble').addEventListener('click',()=>{setExplosion(0);state.labels=false;setPressed($('#labels-toggle'),false);clearSelection();fitView();notify('All 24 assemblies reattached.');});
  $$('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(Number(b.dataset.mode))));
  $$('[data-camera]').forEach(b=>b.addEventListener('click',()=>{state.camera=b.dataset.camera;$$('[data-camera]').forEach(v=>setPressed(v,v===b));fitView(state.isolated);}));
  $('#labels-toggle').addEventListener('click',()=>{state.labels=!state.labels;setPressed($('#labels-toggle'),state.labels);});
  $('#wire-toggle').addEventListener('click',()=>{state.wire=!state.wire;setPressed($('#wire-toggle'),state.wire);updateMaterials();});
  $('#orbit-toggle').addEventListener('click',()=>{state.rotate=!state.rotate;setPressed($('#orbit-toggle'),state.rotate);});
  $('#fit').addEventListener('click',()=>fitView(state.isolated));
  $('#selection-close').addEventListener('click',()=>{const wasIsolated=state.isolated;clearSelection();if(wasIsolated)fitView();});
  $('#catalog-toggle').addEventListener('click',()=>{if(!state.ready)return;stopDemo();state.catalog=!state.catalog;state.explosion=state.catalog?1:.52;state.offsets.clear();clearSelection();updateUI();fitView();});
  $('#detach').addEventListener('click',()=>{if(!state.selected)return;stopDemo();if(state.catalog)state.catalog=false;const ex=effectiveExplosion(state.selected);state.offsets.set(state.selected,ex>.08?0:1);updateUI();if(!state.isolated)fitView();});
  $('#isolate').addEventListener('click',()=>{if(!state.selected)return;state.isolated=!state.isolated;updateMaterials();updateUI();fitView(state.isolated);});
  $('#focus-part').addEventListener('click',()=>fitView(true));
  $('#transform-play').addEventListener('click',()=>{if(state.demo){stopDemo();return;}state.demo=true;state.demoAt=performance.now();setMode((state.mode+1)%3,{manual:false});$('#transform-play').classList.add('active');$('#transform-play span').textContent='Pause transformation';$('#transform-play use').setAttribute('href','#i-pause');});
  $('#assemblies-toggle').addEventListener('click',()=>{const panel=$('#assemblies-panel'),open=panel.classList.toggle('open');$('#assemblies-toggle').classList.toggle('active',open);$('#assemblies-toggle').setAttribute('aria-expanded',String(open));});
  const c=renderer.domElement;
  c.addEventListener('pointerdown',e=>{pointerIds.add(e.pointerId);if(pointerIds.size>1)multiTouch=true;if(pointerIds.size===1){multiTouch=false;downPoint={x:e.clientX,y:e.clientY,t:performance.now(),button:e.button};}isPointerDown=true;state.hover=null;updateMaterials();});
  c.addEventListener('pointerup',e=>{pointerIds.delete(e.pointerId);if(downPoint&&!multiTouch&&downPoint.button===0&&Math.hypot(e.clientX-downPoint.x,e.clientY-downPoint.y)<6&&performance.now()-downPoint.t<500){const id=hoveredAssembly(e.clientX,e.clientY);selectAssembly(id,{piece:state.catalog||state.explosion>.2?rayPiece:null});}if(pointerIds.size===0){isPointerDown=false;downPoint=null;}});
  c.addEventListener('pointercancel',e=>{pointerIds.delete(e.pointerId);isPointerDown=pointerIds.size>0;downPoint=null;});
  c.addEventListener('pointermove',e=>{if(isPointerDown||e.pointerType==='touch')return;const id=hoveredAssembly(e.clientX,e.clientY);if(id!==state.hover){state.hover=id;c.style.cursor=id?'pointer':'grab';updateMaterials();}});
  c.addEventListener('pointerleave',()=>{state.hover=null;updateMaterials();});
  c.addEventListener('webglcontextlost',e=>{e.preventDefault();cancelAnimationFrame(animationFrame);showError('The graphics connection was interrupted. Refresh the page to restore the workshop.');});
  document.addEventListener('keydown',e=>{if($('dialog[open]')||e.target.matches('input,textarea,select')||e.target.closest('button,a'))return;
    const k=e.key.toLowerCase();if([' ','1','2','3','r','f','l','w','a','escape'].includes(k))e.preventDefault();
    if(['1','2','3'].includes(k))setMode(Number(k)-1);else if(k===' '){$('#explode-all').click();}else if(k==='r'){state.wire=false;state.rotate=false;state.labels=false;setPressed($('#wire-toggle'),false);setPressed($('#orbit-toggle'),false);setPressed($('#labels-toggle'),false);setMode(0);}else if(k==='f')fitView(state.isolated);else if(k==='l')$('#labels-toggle').click();else if(k==='w')$('#wire-toggle').click();else if(k==='a')$('#orbit-toggle').click();else if(k==='escape'){const iso=state.isolated;clearSelection();if(iso)fitView();}
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(animationFrame);stopDemo();}else{lastTime=performance.now();animationFrame=requestAnimationFrame(animate);}});
}
$('#export').addEventListener('click',()=>$('#export-dialog').showModal());$('#help').addEventListener('click',()=>$('#help-dialog').showModal());
$$('.modal .close-modal').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
$$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
$('#export-current').addEventListener('click',async()=>{
  if(!state.ready){notify('Wait for the 3D model to finish loading.');return;}
  const button=$('#export-current');button.disabled=true;stopDemo();
  try{
    const {GLTFExporter}=await import('./vendor/GLTFExporter.js');const exported=root.clone(true);
    // Export exactly the target pose, even if the screen is still interpolating.
    for(const a of ASSEMBLIES){const g=exported.getObjectByName(a.id),p=groupTargets.get(a.id);g.position.copy(p.position);g.quaternion.copy(p.quaternion);g.visible=!state.isolated||a.id===state.selected;}
    for(const p of pieces){const mesh=exported.getObjectByName(p.mesh.name),t=pieceTargets.get(p.mesh.name);mesh.position.copy(t.position);mesh.quaternion.copy(t.quaternion);mesh.scale.setScalar(t.scale);mesh.visible=!state.isolated||!state.selectedPiece||mesh.name===state.selectedPiece;}
    exported.traverse(o=>{if(!o.isMesh)return;const restore=mat=>{const m=mat.clone(),base=materialBases.get(mat.uuid);if(base){m.color.copy(base.color);m.emissive.copy(base.emissive);m.emissiveIntensity=base.intensity;m.opacity=base.opacity;m.transparent=base.transparent;}m.wireframe=false;return m;};o.material=Array.isArray(o.material)?o.material.map(restore):restore(o.material);});
    const result=await new GLTFExporter().parseAsync(exported,{binary:true,onlyVisible:true});const blob=new Blob([result],{type:'model/gltf-binary'}),url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='vf1-'+modeNames[state.mode].toLowerCase()+(state.isolated?'-'+state.selected:state.explosion>.05?'-exploded':'')+'.glb';link.click();setTimeout(()=>URL.revokeObjectURL(url),60000);notify('Your 3D model is ready.');
  }catch(error){console.error(error);notify('Export did not finish. Try the animated model download.');}finally{button.disabled=false;}
});
$('#export-website').addEventListener('click',async()=>{
  const button=$('#export-website');button.disabled=true;notify('Preparing your portable workshop…');
  try{
    const {createZip}=await import('./zip.js');
    const manifestResponse=await fetch(new URL('./portable-files.json',import.meta.url));if(!manifestResponse.ok)throw new Error('Missing portable manifest');
    const files=await manifestResponse.json();
    const entries=await Promise.all(files.map(async name=>{const r=await fetch(new URL('./'+name,import.meta.url));if(!r.ok)throw new Error('Missing portable file '+name);return [name,new Uint8Array(await r.arrayBuffer())];}));
    const url=URL.createObjectURL(createZip(entries));const a=document.createElement('a');a.href=url;a.download='valkyrie-lab-portable.zip';a.click();setTimeout(()=>URL.revokeObjectURL(url),60000);notify('Portable workshop ready. Start with README.md.');
  }catch(error){console.error(error);notify('The website export could not finish. Please try again.');}finally{button.disabled=false;}
});
initialize();
