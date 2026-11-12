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
const {createCanvas}=runtimeRequire('@napi-rs/canvas');
const measureContext=createCanvas(1,1).getContext('2d');

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
 Q:'NIST DLMF, section 3.5(v): Gauss quadrature. https://dlmf.nist.gov/3.5#v',
 Y:'NIST DLMF, section 14.30: Spherical harmonics. https://dlmf.nist.gov/14.30',
 C:'Schaeffer (2013), Efficient spherical harmonic transforms. https://arxiv.org/abs/1202.6522 ; Gaussian sampling and dealiasing: https://nschaeff.bitbucket.io/shtns/spat.html',
 E:'ECMWF, Gaussian grids: latitude nodes and full/reduced longitude layouts. https://confluence.ecmwf.int/spaces/FCST/pages/49415103/Gaussian%2Bgrids',
 H:'Held, The barotropic vorticity equation. https://www.gfdl.noaa.gov/wp-content/uploads/files/user_files/pjp/barotropic.pdf',
 B:'Bonev et al. (2023), Spherical Fourier Neural Operators. https://proceedings.mlr.press/v202/bonev23a/bonev23a.pdf',
 T:'NVIDIA torch-harmonics, scalar/vector SHT and quadrature. https://github.com/NVIDIA/torch-harmonics/blob/v0.7.4/torch_harmonics/sht.py. Repository dependency pins version 0.7.4.',
 R1:'Isca pinned a290bc376d84d0ee83adbb80eb374b9f629c3534: src/atmos_spectral_barotropic/barotropic_dynamics.F90. https://github.com/ExeClim/Isca/blob/a290bc376d84d0ee83adbb80eb374b9f629c3534/src/atmos_spectral_barotropic/barotropic_dynamics.F90',
 R2:'Isca pinned a290bc376d84d0ee83adbb80eb374b9f629c3534: src/atmos_spectral_barotropic/stirring.F90. https://github.com/ExeClim/Isca/blob/a290bc376d84d0ee83adbb80eb374b9f629c3534/src/atmos_spectral_barotropic/stirring.F90',
 R3:'sim/barotropic_stirring.py:20-27, at repository 185e086fed79420544a1f06485f7fedf425ec100. https://github.com/tglanz/climatology/blob/185e086fed79420544a1f06485f7fedf425ec100/sim/barotropic_stirring.py',
 R4:'ml/src/ml/training/model.py at repository 185e086fed79420544a1f06485f7fedf425ec100. https://github.com/tglanz/climatology/blob/185e086fed79420544a1f06485f7fedf425ec100/ml/src/ml/training/model.py',
 R5:'ml/src/ml/data/climatology.py at repository 185e086fed79420544a1f06485f7fedf425ec100. https://github.com/tglanz/climatology/blob/185e086fed79420544a1f06485f7fedf425ec100/ml/src/ml/data/climatology.py',
 R6:'ml/configs/default.toml at repository 185e086fed79420544a1f06485f7fedf425ec100. https://github.com/tglanz/climatology/blob/185e086fed79420544a1f06485f7fedf425ec100/ml/configs/default.toml',
 R7:'NeuralOperator pinned 98cd305099f4a2b232ed85773984f3e5991f9b1a: neuralop/layers/spherical_convolution.py. https://github.com/NeuralOperator/neuraloperator/blob/98cd305099f4a2b232ed85773984f3e5991f9b1a/neuralop/layers/spherical_convolution.py',
 R8:'NeuralOperator pinned 98cd305099f4a2b232ed85773984f3e5991f9b1a: neuralop/models/fno.py. https://github.com/NeuralOperator/neuraloperator/blob/98cd305099f4a2b232ed85773984f3e5991f9b1a/neuralop/models/fno.py'
};
async function equation(latex,inlineSize=null){
 const id=createHash('sha256').update('transparent-inline-v3'+inlineSize+latex).digest('hex').slice(0,16),base=path.join(build,'math',id);
 try{await fs.access(base+'.png');}
 catch{
  const pointSize=inlineSize ? inlineSize*72.27/96 : 24;
  const math=(inlineSize ? '\\textstyle ' : '\\displaystyle ')+latex;
  const tex='\\documentclass[border=1pt]{standalone}\n\\usepackage{amsmath,amssymb,xcolor}\n\\begin{document}\n\\color[HTML]{14374A}\n\\fontsize{'+pointSize+'}{'+(pointSize*1.2)+'}\\selectfont\n\\sbox0{$'+math+'$}\n\\typeout{MATHDEPTH:\\the\\dp0}\n\\noindent\\usebox0\n\\end{document}\n';
  await fs.writeFile(base+'.tex',tex.replace(/\n/g,'%\n'));
  try{execFileSync((process.env.PDFLATEX??'pdflatex'),['-interaction=nonstopmode','-halt-on-error','-output-directory',path.dirname(base),base+'.tex'],{stdio:'pipe',env:process.env});}
  catch(e){console.error('LaTeX failed:',latex,e.stdout?.toString().slice(-1800));throw e;}
  execFileSync((process.env.PDFTOCAIRO??'pdftocairo'),['-transp','-r','192','-png','-singlefile',base+'.pdf',base],{stdio:'pipe',env:process.env});
 }
 const bytes=await fs.readFile(base+'.png'),m=await sharp(bytes).metadata();
 const log=await fs.readFile(base+'.log','utf8');
 const depth=(Number(log.match(/MATHDEPTH:([\d.]+)pt/)[1])+1)*96/72.27;
 return {bytes,width:m.width/2,height:m.height/2,depth,latex};
}
const denseSlides=[];
const p=Presentation.create({slideSize:{width,height}});
function textBox(slide,value,x,y,w,h,size,color,bold=false,name='text'){
 const shape=slide.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;
 shape.text.style={typeface:font,fontSize:size,bold,color,alignment:'left',verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0,lineSpacing:1.13};
 for(const match of value.matchAll(/https?:\/\/[^\s]+/g))shape.text.get(match[0]).link={uri:match[0],isExternal:true};
 return shape;
}
// Prose stays editable. Each inline LaTeX expression is an image with a
// measured TeX baseline, so symbols and units keep their mathematical form.
function textWidth(value,size){
 measureContext.font=`${size}px ${font}`;
 return measureContext.measureText(value).width;
}
async function paragraph(value,size,maxWidth){
 const parts=value.split(/(\$[^$]+\$)/g),tokens=[];
 for(const part of parts){
  if(part.startsWith('$')){
   const asset=await equation(part.slice(1,-1),size);
   tokens.push({type:'math',asset,w:asset.width});
  }else for(const word of part.match(/\s+|\S+/g)??[])
   tokens.push({type:'text',value:word,w:textWidth(word,size)});
 }
 const lines=[];let line=[],used=0;
 function flush(){
  while(line.at(-1)?.type==='text' && /^\s+$/.test(line.at(-1).value))line.pop();
  if(!line.length)return;
  const ascent=Math.max(size*1.18,...line.filter(t=>t.type==='math').map(t=>t.asset.height-t.asset.depth));
  const descent=Math.max(size*.23,...line.filter(t=>t.type==='math').map(t=>t.asset.depth));
  lines.push({tokens:line,ascent,descent,h:ascent+descent+2});line=[];used=0;
 }
 for(const token of tokens){
  if(token.w>maxWidth)throw new Error('Inline expression or word exceeds line width: '+value);
  if(used+token.w>maxWidth)flush();
  if(!line.length && token.type==='text' && /^\s+$/.test(token.value))continue;
  line.push(token);used+=token.w;
 }
 flush();
 return {lines,h:lines.reduce((sum,l)=>sum+l.h,0)};
}
function addMath(slide,asset,x,y,w=asset.width,h=asset.height){
 const arr=asset.bytes;
 slide.images.add({blob:arr.buffer.slice(arr.byteOffset,arr.byteOffset+arr.byteLength),contentType:'image/png',alt:asset.latex,fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
function drawParagraph(slide,layout,x,y,size,name){
 for(const [row,line]of layout.lines.entries()){
  let xx=x,prose='',start=x;
  const baseline=y+line.ascent;
  function flushText(){
   if(prose.trim())textBox(slide,prose,start,baseline-size*1.18,Math.max(4,textWidth(prose,size)+4),size*1.5,size,'#283B46',false,`${name}-${row}-${start}`);
   prose='';
  }
  for(const token of line.tokens){
   if(token.type==='text'){
    if(!prose)start=xx;
    prose+=token.value;
   }else{
    flushText();addMath(slide,token.asset,xx,baseline-token.asset.height+token.asset.depth);
   }
   xx+=token.w;
  }
  flushText();y+=line.h;
 }
}
async function layoutBlocks(blocks,size){
 return Promise.all(blocks.map(async b=>{
  if(b.type==='text'){
   const layout=await paragraph(b.value,size,1118);
   return {...b,layout,h:layout.h};
  }
  const ratio=Math.min(1,1100/b.asset.width);
  return {...b,w:b.asset.width*ratio,h:b.asset.height*ratio+10};
 }));
}
for(let i=0;i<slides.length;i++){
 const s=slides[i],slide=p.slides.add();
 slide.background.fill=i===0?'#123448':'#FBFAF6';
 if(i===0){
  textBox(slide,'BVE, spherical harmonics,\nand SFNO',76,202,1120,165,60,'#FFFFFF',true,'cover-title');
  textBox(slide,'A lecture and study guide for the climatology prediction task',78,400,1100,62,30,'#DCE8EA',false,'cover-subtitle');
  textBox(slide,'Fluid dynamics, the SHT, Gaussian grids, and learned operators',78,554,1100,44,24,'#DCE8EA',false,'cover-scope');
 } else {
  const titleSize=textWidth(s.title,44)>1136?38:44;
  textBox(slide,s.title,72,45,1136,82,titleSize,'#14374A',true,'slide-title');
  for(const b of s.blocks)if(b.type==='math')b.asset=await equation(b.value);
  let fontSize=s.title.startsWith('References:')?24:28;
  let blocks=await layoutBlocks(s.blocks,fontSize);
  let occupied=blocks.reduce((a,b)=>a+b.h,0)+(blocks.length-1)*12;
  if(occupied>507){
   fontSize=s.title.startsWith('References:')?23:26;
   blocks=await layoutBlocks(s.blocks,fontSize);
   occupied=blocks.reduce((a,b)=>a+b.h,0)+(blocks.length-1)*12;
  }
  if(occupied>507){denseSlides.push(`${i+1}: ${s.title} (${Math.round(occupied)}px)`);console.warn('DENSE',denseSlides.at(-1));}
  let y=140;
  for(const [j,b]of blocks.entries()){
   if(b.type==='text')drawParagraph(slide,b.layout,76,y,fontSize,'body-'+j);
   else addMath(slide,b.asset,78,y+2,b.w,b.h-10);
   y+=b.h+12;
  }
  const footer=s.sources.length>139?s.sources.slice(0,136)+'...':s.sources;
  textBox(slide,footer,76,674,1070,22,15,'#617781',false,'source-footer');
 }
 textBox(slide,String(i+1).padStart(2,'0'),1170,674,58,25,16,i===0?'#DCE8EA':'#617781',false,'slide-number');
 const keys=[...s.sources.matchAll(/\b(H|B|T|Q|Y|C|E|R[1-8])\b/g)].map(x=>x[1]);
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

if(denseSlides.length)throw new Error('Split or shorten dense slides: '+denseSlides.join('; '));
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
