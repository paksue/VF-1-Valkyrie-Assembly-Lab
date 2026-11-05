import * as T from './vendor/three.module.js';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';

const H = Math.PI / 2;
export const ASSEMBLIES = [
  {id:'radome',name:'Nose radome',section:'Airframe',detail:'The tapered nose shell lifts away to reveal the radar antenna underneath.',f:[0,.05,-4.55],g:[0,1.05,-4.55],b:[0,-.28,-.82],br:[-H,0,0],explode:[0,0,-3.2]},
  {id:'radar',name:'Radar antenna',section:'Airframe',detail:'An independent antenna and support spindle inside the forward fuselage.',f:[0,.06,-4.5],g:[0,1.06,-4.5],b:[0,-.23,-.82],br:[-H,0,0],explode:[0,.2,-1.2]},
  {id:'cockpit',name:'Cockpit & forward fuselage',short:'Cockpit',section:'Airframe',detail:'The cockpit, seat and forward fuselage fold down into the center of the Battroid torso.',f:[0,.08,-3.12],g:[0,1.08,-3.12],b:[0,1.15,-.82],br:[-H,0,0],explode:[0,.35,-1.1]},
  {id:'canopy',name:'Canopy & frame',short:'Canopy',section:'Airframe',detail:'A separate smoked canopy with structural hoops. Detach it to inspect the pilot seat and instrument deck.',f:[0,.39,-3.12],g:[0,1.39,-3.12],b:[0,1.15,-1.13],br:[-H,0,0],explode:[0,3.4,-.8]},
  {id:'core',name:'Central airframe',short:'Airframe',section:'Airframe',detail:'The load-bearing center section carries the swing-wing mounts and becomes the Battroid chest.',f:[0,.05,-.15],g:[0,1.05,-.15],b:[0,2.1,-.05],br:[-H,0,0],explode:[0,0,0]},
  {id:'dorsal',name:'Dorsal fuselage',short:'Dorsal cover',section:'Airframe',detail:'The upper rear fuselage separates from the center frame, exposing its structural spars.',f:[0,.34,1.82],g:[0,1.34,1.82],b:[0,1.4,.7],br:[H,0,0],explode:[0,2.6,1.1]},
  ...[-1,1].map((s,i)=>({id:'wing'+i,name:(i?'Starboard':'Port')+' swing wing',short:(i?'R':'L')+' wing',section:'Flight surfaces',detail:'A swept, variable-geometry wing with a visible pivot, segmented trailing edge and red squadron stripe.',f:[s*1.25,.29,-.38],g:[s*1.25,1.29,-.38],gr:[0,-s*.10,0],b:[s*.62,2.4,1.05],br:[H,-s*1.24,0],explode:[s*3.6,.5,.2],side:s})),
  ...[-1,1].map((s,i)=>({id:'tail'+i,name:(i?'Starboard':'Port')+' tail assembly',short:(i?'R':'L')+' stabilizer',section:'Flight surfaces',detail:'Each tail assembly combines a vertical fin and horizontal stabilizer. The fins fold behind the Battroid.',f:[s*.98,.39,3.92],g:[s*.98,1.39,3.92],b:[s*.67,2.95,1.48],br:[H,0,s*.10],explode:[s*1.85,1.7,2.8],side:s})),
  ...[-1,1].map((s,i)=>({id:'intake'+i,name:(i?'Starboard':'Port')+' intake / thigh',short:(i?'R':'L')+' intake',section:'Propulsion & legs',detail:'The recessed intake housing and upper leg share this articulated module. The hip joint rotates during transformation.',f:[s*1.28,-.44,-.78],g:[s*1.28,-.01,.05],gr:[.92,0,s*-.07],b:[s*.92,-.72,.08],br:[H,0,s*-.045],explode:[s*2.1,-.7,-1.2],side:s})),
  ...[-1,1].map((s,i)=>({id:'engine'+i,name:(i?'Starboard':'Port')+' engine / lower leg',short:(i?'R':'L')+' engine',section:'Propulsion & legs',detail:'A long armored engine nacelle becomes the lower leg. Its shell carries access panels, cooling slots and an exposed knee joint.',f:[s*1.28,-.49,2.09],g:[s*1.43,-2.00,.52],gr:[2.0,0,s*-.055],b:[s*1.10,-3.14,.18],br:[H,0,s*-.045],explode:[s*2.8,-1.3,1.5],side:s})),
  ...[-1,1].map((s,i)=>({id:'nozzle'+i,name:(i?'Starboard':'Port')+' exhaust / foot',short:(i?'R':'L')+' exhaust',section:'Propulsion & legs',detail:'Split exhaust petals, a recessed turbine and ankle hardware form the engine outlet and foot.',f:[s*1.28,-.49,4.38],g:[s*1.49,-3.94,-.12],gr:[H,0,0],b:[s*1.20,-5.30,.14],br:[H,0,0],explode:[s*2.8,-1.0,3.8],side:s})),
  ...[-1,1].map((s,i)=>({id:'upperarm'+i,name:(i?'Right':'Left')+' shoulder & upper arm',short:(i?'R':'L')+' shoulder',section:'Arms & manipulators',detail:'The shoulder rotates out of its ventral stowage position. The exposed axle links it to the upper arm.',f:[s*.61,-.98,-.32],g:[s*2.48,.05,-.5],gr:[H,0,s*-.15],b:[s*1.98,1.82,-.05],br:[H,0,s*-.16],explode:[s*3.7,-1.6,-.7],side:s})),
  ...[-1,1].map((s,i)=>({id:'forearm'+i,name:(i?'Right':'Left')+' forearm',short:(i?'R':'L')+' forearm',section:'Arms & manipulators',detail:'An angular forearm shell with elbow hardware, a red wrist band and separate access covers.',f:[s*.61,-.98,1.40],g:[s*2.63,-1.03,-1.36],gr:[Math.PI,0,0],b:[s*2.26,.16,-.18],br:[1.28,0,s*-.10],explode:[s*4,-2.2,.9],side:s})),
  ...[-1,1].map((s,i)=>({id:'hand'+i,name:(i?'Right':'Left')+' manipulator',short:(i?'R':'L')+' hand',section:'Arms & manipulators',detail:'A separate wrist, palm, thumb and four segmented fingers. The right manipulator carries the gunpod in deployed modes.',f:[s*.61,-.98,2.51],g:[s*2.63,-1.03,-2.46],gr:[Math.PI,0,0],b:[s*2.37,-.93,.12],br:[1.28,0,s*-.10],explode:[s*4.2,-2.6,2.4],side:s})),
  {id:'head',name:'Head & twin laser cannons',short:'Head unit',section:'Command & equipment',detail:'The VF-1J-inspired command head has a green optical visor and two elevated laser cannons. It stows beneath the airframe in Fighter and GERWALK modes.',f:[0,-1.12,-1.24],fr:[-H,0,0],g:[0,-.12,-1.24],gr:[-H,0,0],b:[0,3.63,-.2],explode:[0,-3.5,-1.4]},
  {id:'gunpod',name:'GU-11 gunpod',short:'Gunpod',section:'Command & equipment',detail:'A detachable under-fuselage gunpod with three recessed barrels, cooling ribs and a sculpted rear housing.',f:[0,-1.80,.0],g:[2.63,-1.15,-3.02],b:[2.37,-1.2,-1.18],br:[-.17,0,0],explode:[0,-4.4,.2]}
].map((a,i)=>({...a,index:i+1,short:a.short||a.name,fr:a.fr||[0,0,0],gr:a.gr||a.fr||[0,0,0],br:a.br||[0,0,0]}));

export function getPose(a,mode){
  const key=['f','g','b'][mode];
  return {position:new T.Vector3(...a[key]),quaternion:new T.Quaternion().setFromEuler(new T.Euler(...a[key+'r']))};
}

export function buildValkyrie(){
  const root=new T.Group();root.name='VF_1J_Valkyrie';
  root.userData={title:'VF-1J Valkyrie • original interpretive model',units:'arbitrary model units',source:'Valkyrie Assembly Lab',reference:'https://tamashiiweb.com/item/15096/?wovn=en'};
  const palette={
    white:new T.MeshStandardMaterial({color:0xe5e9df,roughness:.34,metalness:.24}),
    bright:new T.MeshStandardMaterial({color:0xf9fcf2,roughness:.29,metalness:.18}),
    grey:new T.MeshStandardMaterial({color:0x929f98,roughness:.45,metalness:.44}),
    red:new T.MeshStandardMaterial({color:0xd73525,roughness:.31,metalness:.16}),
    dark:new T.MeshStandardMaterial({color:0x202a2c,roughness:.42,metalness:.58}),
    black:new T.MeshStandardMaterial({color:0x101819,roughness:.59,metalness:.18}),
    metal:new T.MeshStandardMaterial({color:0x63706e,roughness:.26,metalness:.82}),
    gold:new T.MeshStandardMaterial({color:0xb7a061,roughness:.4,metalness:.72}),
    glass:new T.MeshPhysicalMaterial({color:0x2e626b,metalness:.25,roughness:.12,transparent:true,opacity:.63,depthWrite:false,clearcoat:1,side:T.DoubleSide}),
    green:new T.MeshStandardMaterial({color:0x6dd7ac,emissive:0x1c7852,emissiveIntensity:.6,metalness:.15,roughness:.15}),
    blue:new T.MeshStandardMaterial({color:0x55b9c5,emissive:0x1b6e92,emissiveIntensity:.4,metalness:.15,roughness:.2}),
    seam:new T.LineBasicMaterial({color:0x4a5957,transparent:true,opacity:.45})
  };
  const groups=new Map();let meshIndex=0;
  function mesh(parent,geo,mat,pos=[0,0,0],rot=[0,0,0],edge=false){
    const o=new T.Mesh(geo,palette[mat]||mat);o.position.set(...pos);o.rotation.set(...rot);o.name=parent.name+'_mesh_'+meshIndex++;o.castShadow=true;o.receiveShadow=true;parent.add(o);
    if(edge){const l=new T.LineSegments(new T.EdgesGeometry(geo,28),palette.seam);l.name='Panel_edges';o.add(l);}
    return o;
  }
  function box(g,size,pos,mat='white',r=[0,0,0],bevel=.04){return mesh(g,new RoundedBoxGeometry(...size,1,Math.min(bevel,...size.map(x=>x*.2))),mat,pos,r);}
  function cyl(g,rt,rb,h,pos,mat='metal',rot=[H,0,0],n=20){return mesh(g,new T.CylinderGeometry(rt,rb,h,n,1),mat,pos,rot);}
  function tube(g,r1,r2,len,pos,mat='metal',rot=[0,0,0]){
    const geo=new T.CylinderGeometry(r1,r2,len,24,1,true);return mesh(g,geo,mat,pos,[H+rot[0],rot[1],rot[2]]);
  }
  function ring(g,r,t,pos,mat='metal',rot=[0,0,0]){return mesh(g,new T.TorusGeometry(r,t,6,32),mat,pos,rot);}
  function line(g,pts,mat='seam'){const geo=new T.BufferGeometry().setFromPoints(pts.map(p=>new T.Vector3(...p)));const l=new T.Line(geo,palette[mat]);l.name='Panel_seam';g.add(l);return l;}
  function loft(g,rings,mat='white',n=16){
    const verts=[],ix=[];
    for(const [z,w,h,cy=0] of rings)for(let k=0;k<n;k++){const t=k*2*Math.PI/n;verts.push(Math.cos(t)*w,Math.sin(t)*h+cy,z);}
    for(let j=0;j<rings.length-1;j++)for(let k=0;k<n;k++){const a=j*n+k,b=j*n+(k+1)%n,c=(j+1)*n+k,d=(j+1)*n+(k+1)%n;ix.push(a,b,c,b,d,c);}
    for(let k=1;k<n-1;k++){ix.push(0,k+1,k);const o=(rings.length-1)*n;ix.push(o,o+k,o+k+1);}
    const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(verts,3));geo.setIndex(ix);geo.computeVertexNormals();return mesh(g,geo,mat);
  }
  function prism(g,pts,h,y,mat='white',edge=false){
    const shape=new T.Shape(pts.map(p=>new T.Vector2(p[0],-p[1])));
    const geo=new T.ExtrudeGeometry(shape,{depth:h,bevelEnabled:false,steps:1,curveSegments:1});geo.rotateX(-H);geo.translate(0,y-h/2,0);return mesh(g,geo,mat,[0,0,0],[0,0,0],edge);
  }
  function plateYZ(g,pts,t,x,mat='white',edge=false){
    const shape=new T.Shape(pts.map(p=>new T.Vector2(p[0],p[1])));
    const geo=new T.ExtrudeGeometry(shape,{depth:t,bevelEnabled:true,bevelThickness:.012,bevelSize:.012,bevelSegments:1});
    geo.rotateY(H);geo.translate(x-t/2,0,0);return mesh(g,geo,mat,[0,0,0],[0,0,0],edge);
  }
  function fastener(g,x,y,z,r=.035,rot=[H,0,0]){cyl(g,r,r,.016,[x,y,z],'metal',rot,12);}
  function digit(g,str,pos,scale=.20,rot=[0,0,0],mat='dark'){
    const sub=new T.Group();sub.position.set(...pos);sub.rotation.set(...rot);g.add(sub);
    const segs={0:[0,1,2,3,4,5],1:[1,2],2:[0,1,6,4,3],3:[0,1,6,2,3],4:[5,6,1,2],5:[0,5,6,2,3],6:[0,5,6,4,3,2],7:[0,1,2],8:[0,1,2,3,4,5,6],9:[0,1,2,3,5,6]};
    const bars=[[.25,.0,.42,.055],[.5,.22,.055,.4],[.5,.67,.055,.4],[.25,.90,.42,.055],[0,.67,.055,.4],[0,.22,.055,.4],[.25,.45,.42,.055]];
    [...str].forEach((c,i)=>(segs[c]||[]).forEach(j=>{const [x,z,w,d]=bars[j];box(sub,[w*scale,.008,d*scale],[(x+i*.75)*scale,0,z*scale],mat,[0,0,0],0);}));
  }
  function insignia(g,pos,scale=.4,rot=[0,0,0]){
    const sub=new T.Group();sub.position.set(...pos);sub.rotation.set(...rot);g.add(sub);ring(sub,scale,.018,[0,0,0],'red',[H,0,0]);
    prism(sub,[[0,-scale*.9],[-scale*.7,scale*.7],[0,scale*.3],[scale*.7,scale*.7]],.012,.015,'red');
  }
  function vent(g,pos,n=5,axis='z',width=.5){for(let i=0;i<n;i++)box(g,[width,.016,.047],[pos[0],pos[1],pos[2]+i*.115],'dark',[0,0,0],.007);}
  function axle(g,pos,r=.22,width=.8){cyl(g,r,r,width,pos,'metal',[0,0,H]);cyl(g,r*.65,r*.65,width+.025,pos,'dark',[0,0,H]);cyl(g,r*.26,r*.26,width+.04,pos,'gold',[0,0,H]);}

  for(const a of ASSEMBLIES){const g=new T.Group();g.name=a.id;g.userData={assemblyId:a.id,label:a.name,index:a.index,description:a.detail};const p=getPose(a,0);g.position.copy(p.position);g.quaternion.copy(p.quaternion);root.add(g);groups.set(a.id,g);}

  let g=groups.get('radome');
  loft(g,[[-2.47,.025,.025,-.1],[-2.3,.16,.115,-.07],[-1.72,.37,.24,-.025],[-.82,.59,.37,0],[-.1,.68,.43,0],[.0,.68,.43,0]],'white',32);
  const band=loft(g,[[-.16,.687,.438,0],[-.025,.687,.438,0]],'dark',32);
  for(const z of [-.75,-1.85]){const r=z===-.75?[.595,.38]:[.325,.215];const pts=[];for(let i=0;i<=48;i++){const t=i/48*Math.PI*2;pts.push([Math.cos(t)*r[0],Math.sin(t)*r[1],z]);}line(g,pts);}
  cyl(g,.08,.12,.32,[0,-.37,-.65],'red',[H,0,0],16);
  for(const s of [-1,1]){ring(g,.112,.024,[s*.63,.08,-.30],'dark',[0,H,0]);}

  g=groups.get('radar');
  cyl(g,.08,.08,.55,[0,0,-.02],'metal');
  const dish=mesh(g,new T.SphereGeometry(.49,24,12,0,Math.PI*2,0,.36*Math.PI),'gold',[0,0,-.16],[H,0,0]);dish.scale.set(1,.40,.74);
  ring(g,.44,.028,[0,0,-.25],'metal');
  for(let i=0;i<8;i++){const t=i*Math.PI/4;box(g,[.025,.025,.24],[Math.cos(t)*.36,Math.sin(t)*.30,-.06],'metal');}
  box(g,[.35,.29,.26],[0,0,.12],'dark');

  g=groups.get('cockpit');
  loft(g,[[-1.45,.68,.43,0],[-1.22,.73,.46,0],[-.25,.80,.46,0],[.9,.90,.43,0],[1.4,1.02,.34,0]],'white',16);
  box(g,[1.16,.15,2.15],[0,.41,-.07],'dark');
  box(g,[.66,.33,.55],[0,.5,.29],'black');box(g,[.68,.72,.18],[0,.71,.53],'dark',[-.18,0,0]);box(g,[.40,.17,.20],[0,1.04,.52],'dark');
  for(const s of [-1,1]){box(g,[.095,.08,.61],[s*.25,.61,.0],'gold');box(g,[.11,.5,.04],[s*.2,.80,.40],'gold',[-.18,0,0]);}
  box(g,[.72,.16,.3],[0,.59,-.68],'dark',[-.18,0,0]);
  box(g,[.20,.06,.11],[-.17,.695,-.67],'green');box(g,[.20,.06,.11],[.17,.695,-.67],'blue');
  cyl(g,.034,.034,.31,[0,.48,-.27],'metal',[0,0,.1]);
  for(const s of [-1,1]){
    box(g,[.021,.15,2.34],[s*.761,-.12,-.13],'red',[0,0,s*.08]);
    insignia(g,[s*.80,.12,-.4],.24,[0,0,s*H]);
    line(g,[[s*.63,-.25,-1.36],[s*.77,-.31,.35],[s*.93,-.23,1.15]]);
    for(const z of [-1.1,.67,1.12])fastener(g,s*.78,.22,z,.027,[0,0,H]);
  }
  digit(g,'101',[-.24,-.405,-.3],.20,[Math.PI,0,0]);

  g=groups.get('canopy');
  const verts=[],ix=[],canopyRings=[[-1.20,.49,.10],[-.8,.59,.45],[.02,.64,.64],[.65,.64,.58],[1.10,.60,.27],[1.25,.56,.10]];
  const cn=18;
  for(const [z,w,h] of canopyRings)for(let j=0;j<=cn;j++){const t=j/cn*Math.PI;verts.push(Math.cos(t)*w,Math.sin(t)*h,z);}
  for(let i=0;i<canopyRings.length-1;i++)for(let j=0;j<cn;j++){let a=i*(cn+1)+j,b=a+1,c=a+cn+1,d=c+1;ix.push(a,c,b,b,c,d);}
  const cg=new T.BufferGeometry();cg.setAttribute('position',new T.Float32BufferAttribute(verts,3));cg.setIndex(ix);cg.computeVertexNormals();mesh(g,cg,'glass');
  function canopyHoop(z,w,h,mat='dark',r=.035){const pts=[];for(let i=0;i<=24;i++){const t=i/24*Math.PI;pts.push(new T.Vector3(Math.cos(t)*w,Math.sin(t)*h,z));}mesh(g,new T.TubeGeometry(new T.CatmullRomCurve3(pts),24,r,5,false),mat);}
  canopyHoop(-1.20,.50,.105,'white',.04);canopyHoop(-.8,.595,.455,'dark',.03);canopyHoop(.65,.648,.585,'white',.045);canopyHoop(1.20,.58,.15,'white',.04);
  for(const s of [-1,1])mesh(g,new T.TubeGeometry(new T.CatmullRomCurve3(canopyRings.map(([z,w,h])=>new T.Vector3(s*w,0,z))),24,.048,6,false),'white');

  g=groups.get('core');
  prism(g,[[-1.02,-1.62],[1.02,-1.62],[2.03,-.75],[2.06,.36],[1.25,1.28],[-1.25,1.28],[-2.06,.36],[-2.03,-.75]],.51,0,'white',true);
  box(g,[1.0,.32,2.1],[0,-.28,.4],'dark');
  for(const s of [-1,1]){
    prism(g,[[s*.90,-1.43],[s*1.20,-1.37],[s*1.85,-.58],[s*1.77,-.37],[s*1.37,-.54]],.012,.262,'red');
    box(g,[.73,.02,.24],[s*1.29,.264,-.89],'dark',[0,s*.28,0]);
    cyl(g,.29,.29,.22,[s*1.38,.07,.60],'metal',[0,0,0]);cyl(g,.19,.19,.25,[s*1.38,.07,.60],'dark',[0,0,0]);
    vent(g,[s*.32,.27,-.61],4,'z',.27);
    line(g,[[s*.86,.264,-1.34],[s*1.45,.264,-.15],[s*1.4,.264,.42],[s*.92,.264,.88]]);
    fastener(g,s*1.7,.27,-.1,.035,[0,0,0]);
  }
  box(g,[.35,.075,.65],[0,.3,.48],'white');

  g=groups.get('dorsal');
  prism(g,[[-.98,-1.07],[.98,-1.07],[1.15,.25],[.98,1.65],[.71,2.30],[-.71,2.30],[-.98,1.65],[-1.15,.25]],.40,.0,'white',true);
  box(g,[.6,.20,1.9],[0,-.32,.2],'dark');
  for(const s of [-1,1]){
    box(g,[.18,.04,2.64],[s*.73,-.27,.2],'metal');
    prism(g,[[s*.65,-.85],[s*.88,-.85],[s*.93,.06],[s*.60,.12]],.009,.207,'red');
    line(g,[[s*.59,.207,-.64],[s*.48,.207,.15],[s*.60,.207,1.34],[s*.34,.207,1.86]]);
    vent(g,[s*.67,.215,.74],5,'z',.23);
  }
  for(const z of [-.43,.32,1.4])box(g,[1.1,.12,.11],[0,-.30,z],'metal');
  digit(g,'101',[-.20,.21,.2],.22);

  for(let i=0;i<2;i++){
    const s=i?1:-1;g=groups.get('wing'+i);
    const p=[[0,-.46],[1.12,-.48],[5.91,2.43],[5.98,2.84],[4.99,2.84],[.61,1.18],[0,.87]].map(([x,z])=>[s*x,z]);
    prism(g,p,.17,0,'bright',true);
    prism(g,[[.90,-.19],[1.15,-.22],[5.69,2.43],[5.74,2.64],[5.22,2.52]].map(([x,z])=>[s*x,z]),.009,.091,'red');
    prism(g,[[.95,.89],[1.42,1.1],[5.32,2.72],[4.95,2.72]].map(([x,z])=>[s*x,z]),.008,.091,'grey');
    for(const top of [-1,1]){
      line(g,[[s*.67,top*.089,.94],[s*1.38,top*.089,.73],[s*5.42,top*.089,2.73]]);
      line(g,[[s*3.59,top*.09,1.62],[s*3.45,top*.09,2.13]]);
      line(g,[[s*4.83,top*.09,2.32],[s*4.77,top*.09,2.73]]);
    }
    cyl(g,.34,.34,.26,[0,0,.12],'metal',[0,0,0]);cyl(g,.20,.20,.275,[0,0,.12],'dark',[0,0,0]);cyl(g,.07,.07,.29,[0,0,.12],'gold',[0,0,0]);
    insignia(g,[s*3.23,.10,1.55],.28);
    digit(g,'101',[s*1.57,.10,.50],.23,[0,s*.53,0]);
    box(g,[.07,.025,.14],[s*5.93,.09,2.59],i?'green':'red');
    for(const x of [1.3,2.1,4.1]){box(g,[.055,.015,.12],[s*x,.10,.20+x*.39],'dark');}

    g=groups.get('tail'+i);
    prism(g,[[0,-.4],[s*.78,-.20],[s*2.04,.67],[s*2.18,1.06],[s*.16,1.12]],.13,.02,'white',true);
    prism(g,[[s*.43,.15],[s*.73,.18],[s*1.88,.78],[s*1.99,.97],[s*1.52,.87]],.010,.093,'red');
    plateYZ(g,[[.38,0],[-1.14,0],[-1.28,1.89],[-.85,1.94],[.75,.0]],.10,0,'white',true);
    for(const side of [-1,1]){
      plateYZ(g,[[-1.10,.19],[-1.15,1.78],[-.91,1.80],[.44,.19]],.008,side*.065,'red');
      line(g,[[side*.071,.25,.54],[side*.071,1.73,1.00]]);
    }
    box(g,[.24,.18,1.23],[0,-.07,.22],'grey');

    g=groups.get('intake'+i);
    // Open intake: four separate walls surrounding a dark recessed compressor.
    box(g,[1.14,.13,2.03],[0,.49,.05],'white',[.015,0,0]);
    box(g,[1.10,.13,2.04],[0,-.46,.05],'white',[0,0,0]);
    for(const v of [-1,1])box(g,[.13,.85,2.03],[v*.52,.015,.05],'white');
    box(g,[.91,.79,.06],[0,.015,-.66],'black');
    for(let j=0;j<5;j++)box(g,[.91,.035,.035],[0,-.30+j*.155,-.705],'metal');
    box(g,[1.02,.06,.15],[0,.43,-1.03],'grey',[.26,0,0]);
    box(g,[1.15,.12,.2],[0,-.46,-1.01],'bright');
    box(g,[1.08,.16,.29],[0,.47,.49],'red');
    box(g,[1.05,.85,.48],[0,.01,.84],'white');
    axle(g,[0,0,1.04],.25,1.20);
    for(const v of [-1,1])line(g,[[v*.588,.34,-.9],[v*.588,.33,.24],[v*.588,-.20,.49]]);
    box(g,[.055,.38,.35],[s*.596,-.03,.18],'dark');

    g=groups.get('engine'+i);
    loft(g,[[-1.67,.43,.37],[-1.41,.52,.47],[-.95,.56,.50],[.65,.55,.49],[1.35,.47,.40],[1.71,.44,.35]],'white',8);
    axle(g,[0,0,-1.66],.23,1.1);
    box(g,[.74,.07,.54],[0,.49,-1.12],'white',[-.12,0,0]);
    box(g,[.43,.018,.26],[0,.536,-.87],i?'red':'blue');
    loft(g,[[-.60,.562,.505],[-.42,.562,.505]],'red',8);
    for(const v of [-1,1]){
      line(g,[[v*.50,.20,-1.1],[v*.55,.20,.75],[v*.47,.20,1.3]]);
      line(g,[[v*.45,-.27,-1.06],[v*.50,-.27,.6],[v*.42,-.27,1.28]]);
      box(g,[.018,.32,.91],[v*.553,.08,.34],'white');
      for(const z of [-.12,.2,.52])box(g,[.024,.05,.18],[v*.568,.16,z],'dark');
    }
    const fin=prism(g,[[s*.44,.25],[s*1.04,.98],[s*1.07,1.56],[s*.44,1.2]],.10,-.21,'white',true);
    prism(g,[[s*.53,.46],[s*.95,1.01],[s*.96,1.35],[s*.53,1.05]],.008,-.154,'red');
    line(g,[[-.29,.45,.05],[.29,.45,.05],[.29,.41,1.06],[-.29,.41,1.06],[-.29,.45,.05]]);
    for(const x of [-.27,.27])for(const z of [.12,1.0])fastener(g,x,.459,z,.027,[0,0,0]);

    g=groups.get('nozzle'+i);
    box(g,[.91,.75,.45],[0,0,-.36],'metal');
    tube(g,.34,.32,.60,[0,0,-.0],'dark');ring(g,.32,.04,[0,0,.30],'metal');
    cyl(g,.255,.255,.03,[0,0,-.04],'black');cyl(g,.085,.10,.08,[0,0,-.11],'gold');
    for(let j=0;j<14;j++){
      const t=j/14*Math.PI*2;
      box(g,[.026,.22,.055],[Math.cos(t)*.17,Math.sin(t)*.17,-.09],'metal',[0,0,t+.35]);
    }
    for(const v of [-1,1]){
      box(g,[.97,.18,.92],[0,v*.36,.17],'dark',[v*.13,0,0]);
      box(g,[.97,.11,.37],[0,v*.46,-.17],'white',[v*.18,0,0]);
      for(let j=0;j<5;j++)box(g,[.048,.02,.63],[-.37+j*.185,v*.455,.18],'metal');
    }
    box(g,[.13,.60,.86],[-.46,0,.15],'dark',[0,-.06,0]);box(g,[.13,.60,.86],[.46,0,.15],'dark',[0,.06,0]);

    g=groups.get('upperarm'+i);
    box(g,[.82,.79,.94],[0,0,-.30],'white');
    box(g,[.63,.024,.53],[0,.411,-.36],'dark');
    box(g,[.11,.04,.89],[s*.30,.43,-.29],'red');
    box(g,[.51,.52,.84],[0,0,.58],'white');
    axle(g,[0,0,-.70],.20,.97);axle(g,[0,0,1.02],.20,.60);
    box(g,[.26,.025,.49],[0,.281,.55],'grey');
    for(const x of [-.29,.29])fastener(g,x,.414,-.68,.026,[0,0,0]);

    g=groups.get('forearm'+i);
    box(g,[.77,.69,1.49],[0,0,.04],'white');
    box(g,[.54,.09,.85],[0,.386,-.05],'bright');
    box(g,[.785,.705,.13],[0,0,.57],'red');
    for(const v of [-1,1]){box(g,[.02,.36,.70],[v*.393,0,-.05],'grey');line(g,[[v*.393,.23,-.49],[v*.393,.23,.36],[v*.393,-.24,.36]]);}
    for(const z of [-.24,0,.24])box(g,[.32,.018,.033],[0,.440,z],'dark');
    cyl(g,.24,.24,.23,[0,0,.87],'metal');

    g=groups.get('hand'+i);
    cyl(g,.21,.21,.27,[0,0,-.20],'metal');
    box(g,[.57,.35,.40],[0,0,.09],'dark');
    for(let j=0;j<4;j++){
      const x=-.215+j*.143;
      box(g,[.12,.22,.24],[x,.03,.34],'white',[.2,0,0]);
      box(g,[.12,.21,.16],[x,-.03,.51],'white',[.5,0,0]);
    }
    box(g,[.18,.21,.29],[s*.34,-.01,.13],'white',[.3,s*-.35,0]);
  }

  g=groups.get('head');
  cyl(g,.19,.21,.38,[0,-.52,0],'metal',[0,0,0]);
  box(g,[.78,.70,.67],[0,0,0],'white');
  box(g,[.77,.08,.55],[0,.387,-.02],'bright');
  box(g,[.11,.032,.58],[0,.440,-.03],'red');
  box(g,[.69,.30,.10],[0,.02,-.367],'dark',[.05,0,0]);
  box(g,[.51,.14,.026],[0,.038,-.432],'green',[.05,0,0]);
  box(g,[.22,.33,.26],[0,-.22,-.36],'white',[-.16,0,0]);
  for(const s of [-1,1]){
    box(g,[.18,.38,.28],[s*.38,-.10,-.22],'grey',[0,0,s*.14]);
    cyl(g,.16,.16,.16,[s*.49,.17,.05],'metal',[0,0,H]);
    cyl(g,.063,.091,.83,[s*.52,.79,.05],'dark',[0,0,s*-.08]);
    cyl(g,.046,.063,.37,[s*.556,1.36,.05],'metal',[0,0,s*-.08]);
    cyl(g,.031,.031,.02,[s*.57,1.55,.05],'black',[0,0,s*-.08]);
  }

  g=groups.get('gunpod');
  loft(g,[[-1.32,.23,.24],[-1.15,.34,.35],[1.16,.34,.35],[1.52,.27,.29],[1.73,.18,.20]],'dark',12);
  cyl(g,.225,.27,.64,[0,0,-1.56],'metal');cyl(g,.201,.201,.016,[0,0,-1.89],'black');
  for(let i=0;i<3;i++){const t=i*Math.PI*2/3;const p=[Math.sin(t)*.11,Math.cos(t)*.11,-1.902];ring(g,.044,.013,p,'metal');}
  for(const z of [-1.04,-.90,.94,1.08])ring(g,.345,.035,[0,0,z],'metal');
  box(g,[.18,.18,1.78],[0,.35,.15],'grey');box(g,[.17,.20,.36],[0,.36,-.56],'red');
  box(g,[.17,.35,.41],[0,-.37,.26],'dark');box(g,[.18,.18,.87],[0,-.53,.66],'dark');
  for(let j=0;j<6;j++)box(g,[.018,.08,.16],[-.336,.08,-.46+j*.24],'grey');
  for(const s of [-1,1])digit(g,'11',[s*.35,.08,.21],.20,[0,0,s*H],'bright');

  root.updateMatrixWorld(true);
  return {root,groups,palette};
}

export function makeAnimationClips(groups){
  const clips=[];
  for(const [title,modes] of [['Fighter to GERWALK',[0,1]],['GERWALK to Battroid',[1,2]],['Full transformation',[0,1,2,1,0]]]){
    const tracks=[],times=modes.map((_,i)=>i*2.8);
    for(const a of ASSEMBLIES){
      const positions=[],quaternions=[];
      for(const mode of modes){const p=getPose(a,mode);positions.push(...p.position);quaternions.push(...p.quaternion);}
      tracks.push(new T.VectorKeyframeTrack(a.id+'.position',times,positions),new T.QuaternionKeyframeTrack(a.id+'.quaternion',times,quaternions));
    }
    clips.push(new T.AnimationClip(title,-1,tracks));
  }
  const tracks=[];
  for(const a of ASSEMBLIES){const p=getPose(a,0);const e=p.position.clone().add(new T.Vector3(...a.explode));tracks.push(new T.VectorKeyframeTrack(a.id+'.position',[0,2.5,4,6.5],[...p.position,...e,...e,...p.position]));}
  clips.push(new T.AnimationClip('Explode and reassemble',-1,tracks));
  return clips;
}
