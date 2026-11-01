import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const runtimeModules=process.env.RUNTIME_NODE_MODULES;
if(!runtimeModules)throw new Error('Set RUNTIME_NODE_MODULES to the bundled Node package directory.');
const runtimeRequire=createRequire(path.join(runtimeModules,'package.json'));
const {Presentation,PresentationFile}=await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);
const sharp=runtimeRequire('sharp');

const root=path.dirname(fileURLToPath(import.meta.url));
const build=path.join(root,'.build');
const skill=process.env.PRESENTATION_SKILL_DIR;
if(!skill)throw new Error('Set PRESENTATION_SKILL_DIR to the installed Presentations skill directory.');
const python=process.env.RUNTIME_PYTHON??'python3';
const {finalizePresentation}=await import(path.join(skill,'container_tools/artifact_tool_utils.mjs'));
const font='Arial',width=1280,height=720;
for(const folder of ['math','previews','tmp','cache'])await fs.mkdir(path.join(build,folder),{recursive:true});
process.env.TMPDIR=path.join(build,'tmp');
process.env.XDG_CACHE_HOME=path.join(build,'cache');
process.env.TEXMFVAR=path.join(build,'texmfvar');
const source=await fs.readFile(path.join(root,'presentation.md'),'utf8');
const slides=source.trim().split(/\n---\n/).map(s=>s.trim()).map(s=>{
 const title=s.match(/^# (.+)/)[1];
 const sources=s.match(/^Source: (.+)$/m)?.[1]??'Original learning sequence';
 const body=s.replace(/^# .+\n/,'').replace(/^Source: .+$/m,'').trim();
 const segments=body.split('$$'),blocks=[];
 for(let k=0;k<segments.length;k++){
  if(k%2)blocks.push({type:'math',value:segments[k].trim()});
  else for(const p of segments[k].trim().split(/\n\s*\n/).filter(Boolean))blocks.push({type:'text',value:p.replace(/\n/g,' ').trim()});
 }
 return {title,sources,blocks};
});
const references={
 H:'Held, The barotropic vorticity equation. https://www.gfdl.noaa.gov/wp-content/uploads/files/user_files/pjp/barotropic.pdf',
 B:'Bonev et al. (2023), Spherical Fourier Neural Operators. https://proceedings.mlr.press/v202/bonev23a/bonev23a.pdf',
 T:'NVIDIA torch-harmonics, scalar/vector SHT and quadrature. https://github.com/NVIDIA/torch-harmonics. Repository dependency pins version 0.7.4.',
 R1:'Isca pinned a290bc376d84d0ee83adbb80eb374b9f629c3534: src/atmos_spectral_barotropic/barotropic_dynamics.F90. https://github.com/ExeClim/Isca/blob/a290bc376d84d0ee83adbb80eb374b9f629c3534/src/atmos_spectral_barotropic/barotropic_dynamics.F90',
 R2:'Isca pinned a290bc376d84d0ee83adbb80eb374b9f629c3534: src/atmos_spectral_barotropic/stirring.F90. https://github.com/ExeClim/Isca/blob/a290bc376d84d0ee83adbb80eb374b9f629c3534/src/atmos_spectral_barotropic/stirring.F90',
 R3:'sim/barotropic_stirring.py:20-27, at repository 51782c6a1b5fff2b40a981945cd7e05d70ae0321. https://github.com/tglanz/climatology/blob/51782c6a1b5fff2b40a981945cd7e05d70ae0321/sim/barotropic_stirring.py',
 R4:'ml/src/ml/training/model.py at repository 51782c6a1b5fff2b40a981945cd7e05d70ae0321. https://github.com/tglanz/climatology/blob/51782c6a1b5fff2b40a981945cd7e05d70ae0321/ml/src/ml/training/model.py',
 R5:'ml/src/ml/data/climatology.py at repository 51782c6a1b5fff2b40a981945cd7e05d70ae0321. https://github.com/tglanz/climatology/blob/51782c6a1b5fff2b40a981945cd7e05d70ae0321/ml/src/ml/data/climatology.py',
 R6:'ml/configs/default.toml at repository 51782c6a1b5fff2b40a981945cd7e05d70ae0321. https://github.com/tglanz/climatology/blob/51782c6a1b5fff2b40a981945cd7e05d70ae0321/ml/configs/default.toml',
 R7:'NeuralOperator pinned 98cd305099f4a2b232ed85773984f3e5991f9b1a: neuralop/layers/spherical_convolution.py. https://github.com/NeuralOperator/neuraloperator/blob/98cd305099f4a2b232ed85773984f3e5991f9b1a/neuralop/layers/spherical_convolution.py',
 R8:'NeuralOperator pinned 98cd305099f4a2b232ed85773984f3e5991f9b1a: neuralop/models/fno.py. https://github.com/NeuralOperator/neuraloperator/blob/98cd305099f4a2b232ed85773984f3e5991f9b1a/neuralop/models/fno.py'
};
async function equation(latex){
 const id=createHash('sha256').update('cream-v2'+latex).digest('hex').slice(0,16),base=path.join(build,'math',id);
 try{await fs.access(base+'.png');}
 catch{
  const tex='\\documentclass[border=2pt]{standalone}\n\\usepackage{amsmath,amssymb,xcolor}\n\\begin{document}\n\\pagecolor[HTML]{FBFAF6}\n\\color[HTML]{14374A}\n\\fontsize{24}{28}\\selectfont\n$\\displaystyle '+latex+'$\n\\end{document}\n';
  await fs.writeFile(base+'.tex',tex);
  try{execFileSync((process.env.PDFLATEX??'pdflatex'),['-interaction=nonstopmode','-halt-on-error','-output-directory',path.dirname(base),base+'.tex'],{stdio:'pipe',env:process.env});}
  catch(e){console.error('LaTeX failed:',latex,e.stdout?.toString().slice(-1800));throw e;}
  execFileSync((process.env.PDFTOPPM??'pdftoppm'),['-r','192','-png','-singlefile',base+'.pdf',base],{stdio:'pipe',env:process.env});
 }
 const bytes=await fs.readFile(base+'.png'),m=await sharp(bytes).metadata();
 return {bytes,width:m.width/2,height:m.height/2,latex};
}
const p=Presentation.create({slideSize:{width,height}});
function textBox(slide,value,x,y,w,h,size,color,bold=false,name='text'){
 const shape=slide.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;
 shape.text.style={typeface:font,fontSize:size,bold,color,alignment:'left',verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0,lineSpacing:1.13};
 for(const match of value.matchAll(/https?:\/\/[^\s]+/g))shape.text.get(match[0]).link={uri:match[0],isExternal:true};
 return shape;
}
function lineEstimate(value,w,size){return value.split('\n').reduce((sum,l)=>sum+Math.max(1,Math.ceil(l.length*size*.505/w)),0);}
for(let i=0;i<slides.length;i++){
 const s=slides[i],slide=p.slides.add();
 slide.background.fill=i===0?'#123448':'#FBFAF6';
 if(i===0){
  textBox(slide,'BVE, spherical harmonics,\nand SFNO',76,202,1120,165,60,'#FFFFFF',true,'cover-title');
  textBox(slide,'A study guide for the climatology prediction task',78,400,1100,62,30,'#DCE8EA',false,'cover-subtitle');
  textBox(slide,'Physics, representation, and the output head',78,554,1100,44,24,'#DCE8EA',false,'cover-scope');
 } else {
  textBox(slide,s.title,72,45,1136,82,44,'#14374A',true,'slide-title');
  for(const b of s.blocks)if(b.type==='math')b.asset=await equation(b.value);
  let fontSize=s.title.startsWith('References:')?24:28;
  let blocks=s.blocks.map(b=>{
   if(b.type==='text')return {...b,h:lineEstimate(b.value,1128,fontSize)*(fontSize*1.2)+5};
   const ratio=Math.min(1,1100/b.asset.width);
   return {...b,w:b.asset.width*ratio,h:b.asset.height*ratio+16};
  });
  const total=blocks.reduce((a,b)=>a+b.h,0)+(blocks.length-1)*13;
  if(total>493){
   fontSize=s.title.startsWith('References:')?23:26.7;
   blocks=s.blocks.map(b=>{
    if(b.type==='text')return {...b,h:lineEstimate(b.value,1128,fontSize)*(fontSize*1.2)+4};
    const ratio=Math.min(.94,1100/b.asset.width);
    return {...b,w:b.asset.width*ratio,h:b.asset.height*ratio+12};
   });
  }
  const occupied=blocks.reduce((a,b)=>a+b.h,0)+(blocks.length-1)*12;
  if(occupied>509)console.warn('DENSE',i+1,s.title,'estimated',occupied);
  let y=140;
  for(const [j,b]of blocks.entries()){
   if(b.type==='text')textBox(slide,b.value,76,y,1128,b.h,fontSize,'#283B46',false,'body-'+j);
   else{
    const arr=b.asset.bytes;
    slide.images.add({blob:arr.buffer.slice(arr.byteOffset,arr.byteOffset+arr.byteLength),contentType:'image/png',alt:b.value,fit:'contain',position:{left:78,top:y+2,width:b.w,height:b.h-12}});
   }
   y+=b.h+12;
  }
  const footer=s.sources.length>139?s.sources.slice(0,136)+'...':s.sources;
  textBox(slide,footer,76,674,1070,22,15,'#617781',false,'source-footer');
 }
 textBox(slide,String(i+1).padStart(2,'0'),1170,674,58,25,16,i===0?'#DCE8EA':'#617781',false,'slide-number');
 const keys=[...s.sources.matchAll(/\b(H|B|T|R[1-8])\b/g)].map(x=>x[1]);
 const refs=[...new Set(keys)].map(k=>k+': '+references[k]);
 slide.speakerNotes.text=['Source slide '+(i+1)+'. '+s.title,...s.blocks.map(b=>b.type==='math'?'LaTeX: '+b.value:b.value),'Evidence: '+s.sources,...refs].join('\n\n');
 console.log('built',i+1,s.title);
}
const candidate=path.join(build,'candidate.pptx');
await(await PresentationFile.exportPptx(p)).save(candidate);
console.log('candidate exported');
for(let i=0;i<p.slides.items.length;i++){
 const slide=p.slides.items[i],blob=await p.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(build,'previews','slide-'+String(i+1).padStart(2,'0')+'.png'),new Uint8Array(await blob.arrayBuffer()));
 const layout=await slide.export({format:'layout'});
 await fs.writeFile(path.join(build,'previews','slide-'+String(i+1).padStart(2,'0')+'.json'),await layout.text());
}

await fs.writeFile(path.join(build,'references.json'),JSON.stringify(references,null,2));
await fs.writeFile(path.join(build,'content.json'),JSON.stringify(slides.map(({blocks,...rest})=>({...rest,blocks:blocks.map(({asset,...b})=>b)})),null,2));
const finalDir=path.join(build,'final-'+Date.now());
await fs.mkdir(finalDir,{recursive:true});
const final=path.join(finalDir,'bve-harmonics-sfno.pptx');
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:candidate,finalPath:final,
 pythonExecutable:python,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 fontPolicy:{basis:'design',families:[font]},
 verifyArtifactToolImport:true,
 receiptPath:path.join(build,'validation-'+Date.now()+'.json')
});
console.log('finalized',JSON.stringify(result));
await fs.copyFile(final,path.join(root,'bve-harmonics-sfno.pptx'));
await fs.mkdir(path.join(build,'pdf'),{recursive:true});
execFileSync((process.env.SOFFICE??'soffice'),['--headless','--convert-to','pdf','--outdir',path.join(build,'pdf'),final],{stdio:'inherit',env:process.env});
await fs.copyFile(path.join(build,'pdf','bve-harmonics-sfno.pdf'),path.join(root,'bve-harmonics-sfno.pdf'));
console.log('PDF exported');
