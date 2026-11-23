// Editable PowerPoint objects sharing the approved HTML's 1280×720 geometry.
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {Presentation,PresentationFile} from 'file:///C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const require=createRequire(import.meta.url);
const {createCanvas,GlobalFonts}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
GlobalFonts.registerFromPath('C:/Windows/Fonts/msyh.ttc','Microsoft YaHei');
GlobalFonts.registerFromPath('C:/Windows/Fonts/msyhbd.ttc','Microsoft YaHei');
GlobalFonts.registerFromPath('C:/Windows/Fonts/cambria.ttc','Cambria Math');
const ctx=createCanvas(1280,720).getContext('2d');
export const C={ink:'#171c20',slate:'#48616c',blue:'#35639c',orange:'#c46a2d',muted:'#697980',line:'#cad3d7',light:'#f3f5f6',bluePale:'#f1f5fa',orangePale:'#fcf4ed'};
const decode=s=>s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&nbsp;/g,' ');
export const plain=s=>decode(String(s).replace(/<br\s*\/?>/g,'\n').replace(/<[^>]+>/g,''));
export function runs(html){
 let bold=false,href=null,script=null,citation=false;const out=[];
 for(const part of String(html).split(/(<[^>]*>)/g)){
  if(!part)continue;
  if(part[0]==='<'){
   if(/^<(b|strong)(\s|>)/.test(part))bold=true;
   else if(/^<\/(b|strong)>/.test(part))bold=false;
   else if(/^<a\s/.test(part)){href=part.match(/href="([^"]*)"/)?.[1]||null;citation=part.includes('class="cite"');if(citation)script='sup';}
   else if(part==='</a>'){href=null;if(citation)script=null;citation=false;}
   else if(part==='<sub>')script='sub';else if(part==='<sup>')script='sup';
   else if(part==='</sub>'||part==='</sup>')script=null;
   else if(/^<br/.test(part))out.push({text:'\n',bold,href,script});
  }else out.push({text:decode(part),bold,href,script});
 }
 return out;
}
export function measure(text,size,bold=false,family='Microsoft YaHei'){
 ctx.font=`${bold?'700':'400'} ${size}px "${family}"`;return ctx.measureText(text).width;
}
export function layout(html,w,size,{bold=false,family='Microsoft YaHei',indent=0}={}){
 const lines=[[]];let used=indent;
 for(const r of runs(html))for(const token of r.text.match(/\[\d+\]|[A-Za-z0-9_@]+(?:[./+−-][A-Za-z0-9_@]+)*|[^\x00-\x7F]|[\s\S]/gu)||[]){
  if(token==='\n'){lines.push([]);used=0;continue;}
  const scale=r.script?.68:1,tw=measure(token,size*scale,bold||r.bold,family);
  if(used+tw>w&&lines.at(-1).length){
   if(/^[，。；：、！？）】》”’.,;:!?)]$/.test(token)&&lines.at(-1).length>1){const last=lines.at(-1).pop();lines.push([{...last,x:0}]);used=last.width;}
   else{lines.push([]);used=0;}
  }
  if(token===' '&&!lines.at(-1).length)continue;
  lines.at(-1).push({...r,text:token,x:used,width:tw,size:size*scale,bold:bold||r.bold});used+=tw;
 }
 return lines;
}
export function makeAuthoring(){
 const slides=[],issues=[];
 class Slide{
  constructor(title,ch,{divider=false,source=''}={}){this.title=title;this.ch=ch;this.divider=divider;this.source=source;this.ops=[];this.parts=[];this.number=slides.length+1;slides.push(this);}
  rect(x,y,w,h,fill='none',stroke='none',sw=1,rx=0){this.ops.push({type:'rect',x,y,w,h,fill,stroke,sw,rx});}
  line(x1,y1,x2,y2,color=C.line,sw=1,dash=''){this.ops.push({type:'line',x1,y1,x2,y2,color,sw,dash});}
  arrow(points,color=C.slate,sw=2,dash=''){this.ops.push({type:'arrow',points,color,sw,dash});}
  text(html,x,y,w,h,opts={}){
   this.ops.push({type:'text',html,x,y,w,h,opts});const size=opts.size??24,lh=opts.lineHeight??size*1.5;
   const height=(layout(html,w,size,opts).length-1)*lh+size*1.3;
   if(height>h+1)issues.push({slide:this.number,title:this.title,type:'height',text:plain(html).slice(0,65),height,limit:h});return height;
  }
  paragraph(html,y,h,opts={}){return this.text(html,88,y,1104,h,{size:25,lineHeight:38,indent:50,...opts});}
  lead(html,y=103,h=95){return this.text(html,88,y,1104,h,{size:25.5,lineHeight:38,bold:true,fill:C.slate});}
  formula(html,y,num,{size=29,h=65}={}){this.ops.push({type:'formula',html,x:100,y,w:1020,h,size,num});this.text(`（${num}）`,1127,y+3,105,45,{size:22,align:'right'});}
  caption(html,y){this.text(html,58,y,1164,32,{size:19.5,fill:'#000000',align:'center',lineHeight:27});}
  note(html,y=608,h=37){this.text(html,88,y,1104,h,{size:19.5,fill:C.slate,lineHeight:28});}
  section(title,body,y,{size=24,h=110}={}){this.text(title,88,y,1104,38,{size:25,bold:true,fill:C.slate});this.text(body,88,y+42,1104,h-42,{size,lineHeight:size*1.5});}
 }
 function divider(n,title,en){const s=new Slide(title,n,{divider:true});s.text(String(n).padStart(2,'0'),480,173,320,108,{size:80,bold:true,fill:'#d5dadd',family:'Times New Roman',align:'center'});s.text(title,240,317,800,82,{size:51,bold:true,fill:C.slate,align:'center'});s.text(en,220,416,840,47,{size:27,fill:C.slate,family:'Times New Roman',align:'center'});return s;}
 function table(s,caption,heads,rows,{x=88,y=220,widths=[200,450,454],rowHeights=null,size=23}={}){
  const w=widths.reduce((a,b)=>a+b,0);s.text(caption,x,y,w,36,{size:20.5,align:'center',fill:'#000000'});
  const rh=[48,...rows.map((_,i)=>rowHeights?.[i]??100)];s.ops.push({type:'table',x,y:y+46,w,h:rh.reduce((a,b)=>a+b,0),widths,rowHeights:rh,size,values:[heads,...rows]});return y+46+rh.reduce((a,b)=>a+b,0);
 }
 function node(s,x,y,w,h,title,body,{color=C.blue,size=20}={}){s.rect(x,y,w,h,'#fff',color,1.4,2);s.text(title,x+10,y+9,w-20,34,{size:size+1,bold:true,fill:color,align:'center'});if(body)s.text(body,x+12,y+39,w-24,h-43,{size:size-1,lineHeight:(size-1)*1.25,align:'center'});}
 return {slides,issues,Slide,divider,table,node,C,layout,logo:'',roof:''};
}
function shapeText(slide,text,x,y,w,h,opts={}){
 const {size=24,bold=false,fill=C.ink,align='left',family='Microsoft YaHei',href=null}=opts;
 const sh=slide.shapes.add({geometry:'textbox',name:opts.name||plain(text).slice(0,55),position:{left:x,top:y,width:Math.max(1,w),height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=text;sh.text.style={fontSize:size,typeface:family==='Microsoft YaHei'?'微软雅黑':family==='Georgia'?'Times New Roman':family,bold,color:fill,alignment:align,verticalAlignment:'top',autoFit:'none',wrap:'none',insets:{left:0,right:0,top:0,bottom:0},lineSpacing:1};
 if(href)sh.text.get(text).link={uri:href,isExternal:true};
 return sh;
}
function drawText(slide,op){
 const {size=24,bold=false,fill=C.ink,align='left',lineHeight=size*1.5,family='Microsoft YaHei',indent=0}=op.opts||{};
 const ls=layout(op.html,op.w,size,{bold,family,indent});
 for(let i=0;i<ls.length;i++){
  const line=ls[i];const extent=line.length?line.at(-1).x+line.at(-1).width:0;
  const shift=align==='center'?(op.w-extent)/2:align==='right'?op.w-extent:0;
  const chunks=[];
  for(const r of line){const prev=chunks.at(-1);if(prev&&r.bold===prev.bold&&r.script===prev.script&&r.href===prev.href){prev.text+=r.text;prev.width+=r.width;}else chunks.push({...r});}
  for(const r of chunks){const dy=r.script==='sub'?size*.22:r.script==='sup'?-size*.24:0;
   shapeText(slide,r.text,op.x+shift+r.x,op.y+i*lineHeight+dy,Math.max(r.width+8,12),size*1.55,{size:r.size,bold:r.bold,fill,family,href:r.href});
  }
 }
}
function lineShape(slide,x1,y1,x2,y2,color,sw,dash){
 return slide.shapes.add({geometry:'line',position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.max(.01,Math.abs(x2-x1)),height:Math.max(.01,Math.abs(y2-y1)),verticalFlip:(x2-x1)*(y2-y1)<0},fill:'none',line:{fill:color,width:sw,style:dash?'dashed':'solid'}});
}
function drawTable(slide,op){
 const t=slide.tables.add({rows:op.values.length,columns:op.widths.length,left:op.x,top:op.y,width:op.w,height:op.h,columnWidths:op.widths,values:op.values.map(row=>row.map(plain))});
 t.styleOptions={headerRow:false,totalRow:false,firstColumn:false,lastColumn:false,bandedRows:false,bandedColumns:false};
 t.borders.assign({outside:{fill:'none',width:0},inside:{fill:'none',width:0}});
 const all=t.cells.block({row:0,column:0,rowCount:op.values.length,columnCount:op.widths.length});
 all.assign({fill:'#ffffff',textStyle:{fontSize:op.size,typeface:'微软雅黑',color:'#000000'},margins:{left:12,right:12,top:12,bottom:8},anchor:'top'});
 for(let r=0;r<op.values.length;r++){
  t.rows[r].height=op.rowHeights[r];
  for(let c=0;c<op.widths.length;c++)t.getCell(r,c).text.style={fontSize:op.size,typeface:'微软雅黑',color:'#000000',bold:r===0,lineSpacing:1.2,autoFit:'none',insets:{left:12,right:12,top:r===0?8:12,bottom:8}};
 }
 t.cells.block({row:0,column:0,rowCount:1,columnCount:op.widths.length}).borders={top:{fill:'#000000',width:2},bottom:{fill:'#000000',width:1.3}};
 t.cells.block({row:op.values.length-1,column:0,rowCount:1,columnCount:op.widths.length}).borders={bottom:{fill:'#000000',width:2}};
 return t;
}
const tok=text=>({style:{typeface:'Cambria Math'},token:{text,kind:/^[\d.,\s]+$/.test(text)?2:/^[A-Za-zα-ωΑ-Ω]+$/.test(text)?5:/[\u4e00-\u9fff]/.test(text)?1:3}});
export function mathRoot(html){
 const parts=String(html).replace(/N_r/g,'N<sub>r</sub>').split(/(<\/?(?:sub|sup)>)/g).filter(Boolean);let cursor=0;
 function parse(){const children=[];
  while(cursor<parts.length){const p=parts[cursor++];if(p==='</sub>'||p==='</sup>')break;
   if(p==='<sub>'||p==='<sup>'){const val=parse(),key=p==='<sub>'?'subscript':'superscript';let base=children.pop()||tok('');
    if(base.scripts)base.scripts[key]=val;else base={scripts:{base,[key]:val}};children.push(base);
   }else for(const v of decode(p).match(/[A-Za-z]+|\d+(?:\.\d+)?|[\u4e00-\u9fff]+|\s+|[^\s]/gu)||[])children.push(tok(v));
  }return {sequence:{children}};
 }return parse();
}
function addMath(protoSlide,template,op,id){
 const eq=structuredClone(template);eq.id=String(id);eq.name=`native-equation-${op.num}`;delete eq.creationId;
 eq.bbox={xEmu:Math.round(op.x*9525),yEmu:Math.round(op.y*9525),widthEmu:Math.round(op.w*9525),heightEmu:Math.round(op.h*9525)};
 eq.textStyle={anchor:2,bottomInset:0,leftInset:0,rightInset:0,topInset:0,wrap:2,autoFit:{noAutofit:{}}};
 eq.paragraphs=[{id:'',runs:[],textStyle:{fontSize:op.size*75,fill:{type:1,color:{type:1,value:'171C20'},gradientStops:[],pictureEffects:[]},alignment:2,typeface:'Cambria Math'},inlineNodes:[{math:{displayMode:2,paragraphProperties:{justification:4},root:mathRoot(op.html)}}],paragraphStyle:{bulletCharacter:'',tabStops:[]}}];
 protoSlide.elements.push(eq);
}
export async function toNativeDeck(authored,templateProto,assetDir,{appendix=false}={}){
 const base=structuredClone(templateProto);base.slides=[];base.charts=[];base.threads=[];base.people=[];
 // Retain the original university master/layout assets, then use its blank layout.
 const p=Presentation.load(base);const logo=await fs.readFile(assetDir+'/whu-wordmark.png'),roof=await fs.readFile(assetDir+'/whu-roof-cutout.png');
 const mathTemplate=templateProto.slides.flatMap(s=>s.elements).find(e=>e.name==='native-equation-2');
 const tables=[],maths=[];
 for(let index=0;index<authored.length;index++){
  const a=authored[index],s=p.slides.add({layoutId:'/ppt/slideLayouts/slideLayout1.xml',width:1280,height:720});s.background.fill='#ffffff';
  if(!a.divider){
   s.images.add({blob:roof,contentType:'image/png',position:{left:12,top:1,width:75,height:56},fit:'contain',alt:'武汉大学建筑标识'});
   s.images.add({blob:logo,contentType:'image/png',position:{left:1207,top:11,width:48,height:48},fit:'contain',alt:'武汉大学校徽'});
   drawText(s,{html:a.title,x:94,y:8,w:1094,h:55,opts:{size:31,bold:true,fill:'#111111',lineHeight:38}});
   lineShape(s,24,76,1256,76,C.line,1);
   s.shapes.add({geometry:'rect',position:{left:0,top:677,width:1280,height:43},fill:'#f0f2f3',line:{fill:'none',width:0}});
   if(appendix){drawText(s,{html:'公式与参数说明',x:40,y:684,w:500,h:32,opts:{size:19.5,fill:C.slate}});}
   else{
    const labels=['背景与现状','目标与意义','内容与方法','难点与创新','实验与数据','进度与文献'];
    for(let j=0;j<6;j++){
     if(j+1===a.ch)s.shapes.add({geometry:'rect',position:{left:j*1280/6,top:677,width:1280/6,height:43},fill:C.slate,line:{fill:'none',width:0}});
     drawText(s,{html:labels[j],x:j*1280/6,y:684,w:1280/6,h:32,opts:{size:19.5,align:'center',fill:j+1===a.ch?'#ffffff':C.muted}});
    }
   }
   drawText(s,{html:String(index+1).padStart(2,'0'),x:1202,y:651,w:48,h:23,opts:{size:13,fill:'#87949a',align:'right'}});
  }
  for(const op of a.ops){
   if(op.type==='text')drawText(s,op);
   else if(op.type==='rect')s.shapes.add({geometry:op.rx?'roundRect':'rect',position:{left:op.x,top:op.y,width:op.w,height:op.h},fill:op.fill,line:{fill:op.stroke,width:op.sw},...(op.rx?{borderRadius:op.rx}:{})});
   else if(op.type==='line')lineShape(s,op.x1,op.y1,op.x2,op.y2,op.color,op.sw,op.dash);
   else if(op.type==='arrow'){
    for(let j=1;j<op.points.length;j++){const [x1,y1]=op.points[j-1],[x2,y2]=op.points[j];lineShape(s,x1,y1,x2,y2,op.color,op.sw,op.dash);}
    const [aa,bb]=op.points.slice(-2),ang=Math.atan2(bb[1]-aa[1],bb[0]-aa[0]),len=9,half=4.5;
    const back=[bb[0]-len*Math.cos(ang),bb[1]-len*Math.sin(ang)],p1=[back[0]+half*Math.sin(ang),back[1]-half*Math.cos(ang)],p2=[back[0]-half*Math.sin(ang),back[1]+half*Math.cos(ang)];
    const minx=Math.min(bb[0],p1[0],p2[0]),miny=Math.min(bb[1],p1[1],p2[1]),w=Math.max(bb[0],p1[0],p2[0])-minx,h=Math.max(bb[1],p1[1],p2[1])-miny;
    s.shapes.add({geometry:'custom',position:{left:minx,top:miny,width:w,height:h},fill:op.color,line:{fill:'none',width:0},customPaths:[{width:w,height:h,commands:[{moveTo:{x:bb[0]-minx,y:bb[1]-miny}},{lineTo:{x:p1[0]-minx,y:p1[1]-miny}},{lineTo:{x:p2[0]-minx,y:p2[1]-miny}},{close:{}}]}]});
   }
   else if(op.type==='table'){drawTable(s,op);if(!tables.includes(index+1))tables.push(index+1);}
   else if(op.type==='formula')maths.push({index,op});
   else if(op.type==='image')s.images.add({blob:await fs.readFile(op.path),contentType:'image/png',position:{left:op.x,top:op.y,width:op.w,height:op.h},fit:'contain',alt:op.alt||'武汉大学标识'});
  }
  s.speakerNotes.textFrame.setText(a.speaker||a.ops.filter(o=>o.type==='text'&&o.y<650).map(o=>plain(o.html)).join('\n\n'));
 }
 let proto=p.toProto();let id=900000;for(const m of maths)addMath(proto.slides[m.index],mathTemplate,m.op,id++);
 return {presentation:Presentation.load(proto),tableOwners:tables,mathCount:maths.length,proto};
}
export {PresentationFile};
