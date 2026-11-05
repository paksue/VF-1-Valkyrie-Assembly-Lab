import { writeFile, mkdir } from 'node:fs/promises';
import * as T from '../vendor/three.module.js';
import { mergeGeometries } from '../vendor/BufferGeometryUtils.js';
import { GLTFExporter } from '../vendor/GLTFExporter.js';
import { GLTFLoader } from '../vendor/GLTFLoader.js';
import { buildValkyrie, ASSEMBLIES, getPose, makeAnimationClips } from '../model.js';

// Node equivalent of the browser FileReader APIs used by Three's exporter.
globalThis.FileReader=class {
  readAsArrayBuffer(blob){blob.arrayBuffer().then(data=>{this.result=data;this.onloadend?.({target:this});});}
  readAsDataURL(blob){blob.arrayBuffer().then(data=>{this.result='data:'+blob.type+';base64,'+Buffer.from(data).toString('base64');this.onloadend?.({target:this});});}
};
const {root,groups}=buildValkyrie();
let sourceMeshes=0,triangles=0;
// Keep every authored mesh independent, while retaining the 24 assembly pivots.
for(const a of ASSEMBLIES){
  const group=groups.get(a.id);group.updateWorldMatrix(true,true);
  const inverse=group.matrixWorld.clone().invert(),pieces=[],segments=[];
  group.traverse(o=>{
    if(o.isMesh){
      const geo=o.geometry.clone();geo.applyMatrix4(new T.Matrix4().multiplyMatrices(inverse,o.matrixWorld));geo.computeBoundingBox();
      const center=geo.boundingBox.getCenter(new T.Vector3()),size=geo.boundingBox.getSize(new T.Vector3());
      geo.translate(-center.x,-center.y,-center.z);geo.computeBoundingBox();geo.computeBoundingSphere();
      const mesh=new T.Mesh(geo,o.material);mesh.name=a.id+'_piece_'+String(pieces.length+1).padStart(3,'0');mesh.position.copy(center);
      const n=pieces.length, lane=(n%5)-2;
      const peel=[center.x*.60+(n%2?1:-1)*.34,center.y*.7+lane*.30,center.z*.45+((n%3)-1)*.32];
      mesh.userData={pieceId:mesh.name,assemblyId:a.id,pieceIndex:sourceMeshes,element:n+1,rest:center.toArray(),peel,size:size.toArray()};
      mesh.castShadow=true;mesh.receiveShadow=true;pieces.push(mesh);sourceMeshes++;triangles+=(geo.index?geo.index.count:geo.attributes.position.count)/3;
      if(!Array.from(geo.attributes.position.array).every(Number.isFinite))throw new Error('Invalid geometry');
    }else if(o.isLine){const att=o.geometry.attributes.position,mat=new T.Matrix4().multiplyMatrices(inverse,o.matrixWorld),points=[];for(let i=0;i<att.count;i++)points.push(new T.Vector3().fromBufferAttribute(att,i).applyMatrix4(mat));if(o.isLineSegments)segments.push(...points);else for(let i=0;i<points.length-1;i++)segments.push(points[i],points[i+1]);}
  });
  group.clear();group.add(...pieces);
  if(segments.length){const lines=new T.LineSegments(new T.BufferGeometry().setFromPoints(segments),new T.LineBasicMaterial({color:0x4a5957,transparent:true,opacity:.45}));lines.name=a.id+'_seams';group.add(lines);}
}
const animations=makeAnimationClips(groups);
const fineTracks=[];
for(const a of ASSEMBLIES)groups.get(a.id).traverse(o=>{if(!o.userData.pieceId)return;const r=o.userData.rest,p=o.userData.peel,e=r.map((v,i)=>v+p[i]*2.4);fineTracks.push(new T.VectorKeyframeTrack(o.name+'.position',[0,1.5,4,6.5],[...r,...r,...e,...r]));});
animations[3].tracks.push(...fineTracks);
const buffer=await new GLTFExporter().parseAsync(root,{binary:true,animations,onlyVisible:true});
const out=new URL('../assets/vf1-valkyrie.glb',import.meta.url);await mkdir(new URL('../assets/',import.meta.url),{recursive:true});await writeFile(out,Buffer.from(buffer));
// Round-trip the shipped GLB with the same loader as the website.
const loaded=await new GLTFLoader().parseAsync(buffer,'');
for(const a of ASSEMBLIES){if(!loaded.scene.getObjectByName(a.id))throw new Error('Missing exported group '+a.id);}
if(loaded.animations.length!==4)throw new Error('Animation clips missing');
const bounds={};
for(let mode=0;mode<3;mode++){
  for(const a of ASSEMBLIES){const g=loaded.scene.getObjectByName(a.id),p=getPose(a,mode);g.position.copy(p.position);g.quaternion.copy(p.quaternion);}
  loaded.scene.updateMatrixWorld(true);const b=new T.Box3().setFromObject(loaded.scene);if(!b.min.toArray().concat(b.max.toArray()).every(Number.isFinite))throw new Error('Invalid pose bounds');bounds[['fighter','gerwalk','battroid'][mode]]={min:b.min.toArray().map(v=>+v.toFixed(2)),max:b.max.toArray().map(v=>+v.toFixed(2))};
}
// Verify every animation can be evaluated and returns finite transforms.
for(const clip of loaded.animations){const mixer=new T.AnimationMixer(loaded.scene);mixer.clipAction(clip).play();mixer.setTime(clip.duration*.53);loaded.scene.traverse(o=>{if(!o.position.toArray().concat(o.quaternion.toArray()).every(Number.isFinite))throw new Error('Invalid animation transform');});mixer.stopAllAction();}
console.log(JSON.stringify({assemblies:ASSEMBLIES.length,sourceMeshes,triangles,bytes:buffer.byteLength,animationClips:loaded.animations.map(c=>c.name),bounds},null,2));
