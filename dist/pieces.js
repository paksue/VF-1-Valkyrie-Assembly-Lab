import * as T from './vendor/three.module.js';
import { getPose } from './model.js';
const ease=t=>{t=T.MathUtils.clamp(t,0,1);return t*t*(3-2*t);};
export function assemblyTarget(assembly,mode,explosion,catalog){
  if(catalog)return {position:new T.Vector3(),quaternion:new T.Quaternion()};
  const p=getPose(assembly,mode);p.position.addScaledVector(new T.Vector3(...assembly.explode),ease(explosion/.8));return p;
}
export function pieceTarget(data,explosion,catalog,total,columns=24){
  if(catalog){
    const row=Math.floor(data.pieceIndex/columns),col=data.pieceIndex%columns,rows=Math.ceil(total/columns);
    return {position:new T.Vector3((col-(columns-1)/2)*2.35,((rows-1)/2-row)*2.05,0),quaternion:new T.Quaternion().setFromEuler(new T.Euler(.70,-.42,0)),scale:1.55/Math.max(...data.size,.12)};
  }
  const fine=ease((explosion-.18)/.82);
  return {position:new T.Vector3(...data.rest).addScaledVector(new T.Vector3(...data.peel),fine*2.4),quaternion:new T.Quaternion(),scale:1};
}
