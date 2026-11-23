// Rebuild the editable HTML/SVG deck and its offline previews from the approved chapter-one source.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const {createCanvas, loadImage, GlobalFonts} = require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
const sharp=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT='D:/Code/毕设/graduate-thesis-experiments';
const DIR=path.join(ROOT,'开题/开题报告PPT');
const BUILD=path.join(ROOT,'工作区/0917-html-chapters-build');
const OUT=path.join(DIR,'开题报告_HTML_前三章演示版.html');
GlobalFonts.registerFromPath('C:/Windows/Fonts/msyh.ttc','Microsoft YaHei');
GlobalFonts.registerFromPath('C:/Windows/Fonts/msyhbd.ttc','Microsoft YaHei');
GlobalFonts.registerFromPath('C:/Windows/Fonts/cambria.ttc','Cambria Math');
const ctx=createCanvas(1280,720).getContext('2d');
const C={ink:'#171c20',slate:'#48616c',blue:'#35639c',orange:'#c46a2d',muted:'#697980',line:'#cad3d7',light:'#f3f5f6',bluePale:'#f1f5fa',orangePale:'#fcf4ed'};
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const decode=s=>s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&nbsp;/g,' ');
// Embed presentation-size copies; original template assets remain unchanged.
const logo='data:image/png;base64,'+(await sharp(path.join(DIR,'assets/whu-wordmark.png')).resize(110,110,{fit:'inside'}).png().toBuffer()).toString('base64');
const roof='data:image/png;base64,'+(await sharp(path.join(DIR,'assets/whu-roof-cutout.png')).resize(180,120,{fit:'inside'}).png().toBuffer()).toString('base64');
const slides=[];const issues=[];
function runs(html){
  let bold=false,href=null,script=null,citation=false;const out=[];
  for(const part of html.split(/(<[^>]*>)/g)){
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
function width(text,size,bold=false,family='Microsoft YaHei'){
  ctx.font=`${bold?'700':'400'} ${size}px "${family}"`;return ctx.measureText(text).width;
}
function layout(html,w,size,{bold=false,family='Microsoft YaHei',indent=0}={}){
  const lines=[[]];let used=indent;
  for(const r of runs(html)){
    const tokens=r.text.match(/\[\d+\]|[A-Za-z0-9_@]+(?:[./+−-][A-Za-z0-9_@]+)*|[^\x00-\x7F]|[\s\S]/gu)||[];
    for(const token of tokens){
      if(token==='\n'){lines.push([]);used=0;continue;}
      const scale=r.script?0.68:1;
      const tw=width(token,size*scale,bold||r.bold,family);
      const punctuation=/^[，。；：、！？）】》”’.,;:!?)]$/.test(token);
      if(used+tw>w&&lines.at(-1).length){
        if(punctuation&&lines.at(-1).length>1){const last=lines.at(-1).pop();lines.push([{...last,x:0}]);used=last.width;}
        else{lines.push([]);used=0;}
      }
      if(used+tw>w+size*0.8)issues.push({type:'text-width',text:token,width:used+tw,limit:w});
      if(token===' '&&!lines.at(-1).length)continue;
      lines.at(-1).push({...r,text:token,x:used,width:tw,size:size*scale,bold:bold||r.bold});used+=tw;
    }
  }
  return lines;
}
class Slide{
  constructor(title,ch,{divider=false,source='原PPT V3及冻结方法协议'}={}){
    this.title=title;this.ch=ch;this.divider=divider;this.source=source;this.parts=[];this.textBoxes=[];this.number=slides.length+1;slides.push(this);
    this.rect(0,0,1280,720,'#fff');
    if(!divider){
      this.parts.push(`<image href="${roof}" xlink:href="${roof}" x="12" y="1" width="75" height="56"/>`);
      this.parts.push(`<image href="${logo}" xlink:href="${logo}" x="1207" y="11" width="48" height="48"/>`);
      this.text(title,94,8,1094,55,{size:31,bold:true,fill:'#111',lineHeight:38});
      this.line(24,76,1256,76,C.line,1);
      this.rect(0,677,1280,43,'#f0f2f3');
      const labels=['背景与现状','目标与意义','内容与方法','难点与创新','实验与数据','进度与文献'];
      for(let i=0;i<6;i++){
        if(i+1===ch)this.rect(i*1280/6,677,1280/6,43,C.slate);
        this.text(labels[i],i*1280/6,684,1280/6,31,{size:19.5,align:'center',fill:i+1===ch?'#fff':C.muted});
      }
      this.text(String(this.number).padStart(2,'0'),1202,652,48,21,{size:13,fill:'#87949a',align:'right'});
    }
  }
  rect(x,y,w,h,fill='none',stroke='none',sw=1,rx=0){this.parts.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);}
  line(x1,y1,x2,y2,color=C.line,sw=1,dash=''){this.parts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${sw}" ${dash?`stroke-dasharray="${dash}"`:''}/>`);}
  arrow(points,color=C.slate,sw=2,dash=''){
    this.parts.push(`<polyline points="${points.map(p=>p.join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="${sw}" ${dash?`stroke-dasharray="${dash}"`:''}/>`);
    const [a,b]=points.slice(-2),angle=Math.atan2(b[1]-a[1],b[0]-a[0]),len=9,half=4.5;
    const back=[b[0]-len*Math.cos(angle),b[1]-len*Math.sin(angle)];
    const p1=[back[0]+half*Math.sin(angle),back[1]-half*Math.cos(angle)],p2=[back[0]-half*Math.sin(angle),back[1]+half*Math.cos(angle)];
    this.parts.push(`<path d="M${b.join(',')} L${p1.join(',')} L${p2.join(',')} Z" fill="${color}"/>`);
  }
  text(html,x,y,w,h,opts={}){
    const {size=24,bold=false,fill=C.ink,align='left',lineHeight=size*1.5,family='Microsoft YaHei',indent=0}=opts;
    const ls=layout(html,w,size,{bold,family,indent});const height=(ls.length-1)*lineHeight+size*1.3;
    if(height>h+1)issues.push({slide:this.number,type:'height',text:decode(html.replace(/<[^>]*>/g,'')).slice(0,80),height,available:h});
    this.textBoxes.push({x,y,w,h:height,text:decode(html.replace(/<[^>]*>/g,''))});
    ls.forEach((line,i)=>{
      const extent=line.length?line.at(-1).x+line.at(-1).width:0;
      const shift=align==='center'?(w-extent)/2:align==='right'?w-extent:0;
      // One SVG text node per line keeps copy/search behavior natural.
      let content='';
      for(const r of line){
        const dy=r.script==='sub'?size*.21:r.script==='sup'?-size*.4:0;
        const node=`<tspan x="${(x+shift+r.x).toFixed(2)}" y="${(y+size+i*lineHeight+dy).toFixed(2)}" font-size="${r.size}" font-weight="${r.bold?700:400}">${esc(r.text)}</tspan>`;
        content+=node;
      }
      this.parts.push(`<text font-family="${family}" fill="${fill}" xml:space="preserve">${content}</text>`);
      for(const r of line.filter(r=>r.href))this.parts.push(`<a href="${esc(r.href)}" xlink:href="${esc(r.href)}" target="_blank" rel="noopener noreferrer"><title>${esc(r.href)}</title><rect x="${x+shift+r.x}" y="${y+i*lineHeight}" width="${r.width}" height="${lineHeight}" fill="#fff" fill-opacity="0" pointer-events="all"/></a>`);
    });
    return height;
  }
  paragraph(html,y,h,opts={}){return this.text(html,88,y,1104,h,{size:25,lineHeight:38,indent:50,...opts});}
  lead(html,y=103,h=95){return this.text(html,88,y,1104,h,{size:25.5,lineHeight:38,bold:true,fill:C.slate});}
  formula(html,y,num,{size=29,h=65}={}){
    this.text(html,100,y,1045,h,{size,family:'Cambria Math',align:'center',lineHeight:size*1.55});
    this.text(`（${num}）`,1145,y+3,80,45,{size:22,align:'right'});
  }
  caption(html,y){this.text(html,58,y,1164,32,{size:19.5,fill:'#000',align:'center',lineHeight:27});}
  note(html,y=608,h=37){this.text(html,88,y,1104,h,{size:19.5,fill:C.slate,lineHeight:28});}
  section(title,body,y,{size=24,h=110}={}){
    this.text(title,88,y,1104,38,{size:25,bold:true,fill:C.slate});
    this.text(body,88,y+42,1104,h-42,{size,lineHeight:size*1.5});
  }
  svg(){
    const colors=[C.slate,C.blue,C.orange,'#777777'];
    return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1280 720" width="1280" height="720" role="img" aria-labelledby="slide-title-${this.number}"><title id="slide-title-${this.number}">${esc(this.title)}</title><desc>${esc(this.source)}</desc><defs>${colors.map(c=>`<marker id="arrow-${this.number}-${c.slice(1)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${c}"/></marker>`).join('')}</defs>${this.parts.join('\n')}</svg>`;
  }
}
function divider(n,title,en){
  const s=new Slide(title,n,{divider:true,source:'原PPT V3章节页：第3、12、18页的居中布局'});
  s.text(String(n).padStart(2,'0'),480,173,320,108,{size:80,bold:true,fill:'#d5dadd',family:'Georgia',align:'center'});
  s.text(title,240,317,800,82,{size:51,bold:true,fill:C.slate,align:'center'});
  s.text(en,220,416,840,47,{size:27,fill:C.slate,family:'Georgia',align:'center'});
  return s;
}
function table(s,caption,heads,rows,{x=88,y=220,widths=[200,450,454],rowHeights=null,size=23}={}){
  const w=widths.reduce((a,b)=>a+b,0);s.text(caption,x,y,w,36,{size:20.5,align:'center',fill:'#000'});
  const top=y+46,headerH=48;
  s.line(x,top,x+w,top,'#000',2);let cx=x;
  heads.forEach((h,i)=>{s.text(h,cx+12,top+8,widths[i]-24,35,{size,bold:true,fill:'#000'});cx+=widths[i];});
  s.line(x,top+headerH,x+w,top+headerH,'#000',1.3);let cy=top+headerH;
  rows.forEach((row,j)=>{
    const height=rowHeights?.[j]??100;cx=x;
    row.forEach((cell,i)=>{s.text(cell,cx+12,cy+14,widths[i]-24,height-24,{size,fill:'#000',lineHeight:size*1.45});cx+=widths[i];});cy+=height;
  });
  s.line(x,cy,x+w,cy,'#000',2);return cy;
}
function node(s,x,y,w,h,title,body,{color=C.blue,size=20}={}){
  s.rect(x,y,w,h,'#fff',color,1.4,2);
  s.text(title,x+10,y+9,w-20,34,{size:size+1,bold:true,fill:color,align:'center'});
  if(body)s.text(body,x+12,y+39,w-24,h-43,{size:size-1,lineHeight:(size-1)*1.25,align:'center'});
}
// Preserve all approved chapter-one prose; only its slide typography is rebuilt.
const source=await fs.readFile(path.join(DIR,'开题报告_HTML_第一章分页纯文字版.html'),'utf8');
const oldSlides=[...source.matchAll(/<section\b[\s\S]*?<\/section>/g)].map(m=>m[0]);
divider(1,'背景与现状','Background and current situation');
for(const raw of oldSlides.slice(1)){
  const title=raw.match(/<h1>(.*?)<\/h1>/)[1];const s=new Slide(title,1,{source:'保留已审阅第一章文字；布局对照原PPT V3'});
  const body=raw.match(/<div class="body">([\s\S]*?)<\/div><div class="foot">/)[1];
  const paras=[...body.matchAll(/<p(?: class="(lead|para)")?>([\s\S]*?)<\/p>/g)].map(m=>({lead:m[1]==='lead',html:m[2]}));
  const refs=body.includes('intro-refs')?[...body.matchAll(/<div><a href="([^"]+)"[^>]*>(.*?)<\/a><\/div>/g)].map(m=>`<a href="${m[1]}">${m[2]}</a>`):[];
  const avail=refs.length?480:532;let choice=null;
  for(const size of [28,27,26,25,24,23]){
    const heights=paras.map(p=>{const f=p.lead?Math.max(size,26):size;const lh=f*(p.lead?1.43:1.5);return {font:f,lh,height:(layout(p.html,1104,f,{bold:p.lead,indent:p.lead?0:2*f}).length-1)*lh+f*1.3};});
    const total=heights.reduce((a,b)=>a+b.height,0)+18*(paras.length-1);
    if(total<=avail){choice={size,heights,total};break;}
  }
  if(!choice)throw Error('Chapter 1 does not fit: '+title);
  const gap=Math.min(28,18+Math.max(0,avail-choice.total)/(paras.length+1));
  const used=choice.heights.reduce((a,b)=>a+b.height,0)+gap*(paras.length-1);let y=104+Math.max(0,(avail-used)/2);
  paras.forEach((p,i)=>{const g=choice.heights[i];s.text(p.html,88,y,1104,g.height+1,{size:g.font,bold:p.lead,lineHeight:g.lh,indent:p.lead?0:g.font*2,fill:p.lead?C.slate:C.ink});y+=g.height+gap;});
  if(refs.length){s.line(88,592,1192,592,C.line,1);refs.forEach((r,i)=>s.text(r,88,600+i*21,1104,24,{size:14.5,lineHeight:20,fill:C.muted}));}
}
divider(2,'目标与意义','Goal and meaning');
{
  const s=new Slide('2.1 总体研究框架',2,{source:'原PPT V3第13—17页；完整排序桥接协议；图中效果陈述均为开题预期结论'});
  const L=64,R=710,W=506;
  s.rect(48,87,1184,550,'#fff','#a9b8c0',1.4,2);
  s.rect(L,96,W,36,C.blue,C.blue,1.4,2);
  s.rect(R,96,W,36,C.orange,C.orange,1.4,2);
  s.text('RQ1  细粒度责任定位',L+12,98,W-24,34,{size:25.5,bold:true,fill:'#fff'});
  s.text('RQ2  诊断引导的可靠恢复',R+12,98,W-24,34,{size:25.5,bold:true,fill:'#fff'});
  s.rect(L,137,W,76,C.bluePale,C.blue,1.5,2);
  s.rect(R,137,W,76,C.orangePale,C.orange,1.5,2);
  s.text('<b>研究目的1：</b>形成完整责任排序，\n提高失败定位的准确性与稳定性。',L+16,149,W-32,58,{size:21,lineHeight:29});
  s.text('<b>研究目的2：</b>建立诊断引导的恢复机制，\n提高任务恢复能力并控制非目标副作用。',R+16,149,W-32,58,{size:21,lineHeight:29});
  s.rect(L,220,W,63,'#fff',C.blue,1.3,2);
  s.rect(R,220,W,63,'#fff',C.orange,1.3,2);
  s.text('<b>研究问题</b>  如何综合局部行为与跨步骤关系，\n形成覆盖全部候选步骤的责任次序？',L+12,224,W-24,57,{size:20.5,lineHeight:28});
  s.text('<b>研究问题</b>  如何据诊断选择恢复计划，\n恢复目标任务并控制非目标副作用？',R+12,224,W-24,57,{size:20.5,lineHeight:28});
  s.rect(L,289,W,29,C.bluePale,C.blue,1.3,2);
  s.rect(R,289,W,29,C.orangePale,C.orange,1.3,2);
  s.text('技术与流程',L+12,290,W-24,28,{size:20,bold:true,fill:C.slate});
  s.text('技术与流程',R+12,290,W-24,28,{size:20,bold:true,fill:C.slate});
  node(s,L,323,240,92,'局部行为排序','匿名步骤证据\n任务内成对比较');
  node(s,L+266,323,240,92,'跨步骤关系排序','四类关系与两轮聚合\n关系增强成对排序');
  s.line(L+120,416,L+120,433,C.blue,2);
  s.line(L+386,416,L+386,433,C.blue,2);
  s.line(L+120,433,L+386,433,C.blue,2);
  s.arrow([[L+253,433],[L+253,445]],C.blue);
  node(s,L,448,W,78,'任务组外预测融合','输出全部步骤责任分数与完整排序 π',{size:20});
  node(s,R,323,W,83,'候选计划与预算内选择','责任锚点 × 多粒度范围；预先冻结尝试次序',{color:C.orange,size:20});
  s.arrow([[R+253,407],[R+253,432]],C.orange);
  node(s,R,439,W,87,'隔离重放与双边验收','目标恢复且非目标保持：提交；否则撤销并继续',{color:C.orange,size:20});
  s.rect(582,398,104,128,'#fff',C.slate,1.3,2);
  s.arrow([[L+W+1,481],[579,481]],C.slate,2.5);
  s.arrow([[686,452],[R-15,452],[R-15,365],[R-6,365]],C.slate,2.5);
  s.text('完整排序 π\n只读传入',L+W+10,405,R-L-W-38,64,{size:19.5,bold:true,lineHeight:28,align:'center',fill:C.slate});
  s.text('结果不回写',589,485,90,30,{size:17.5,align:'center',fill:C.muted});
  s.rect(64,547,177,83,C.light,C.slate,1.3,2);
  s.text('预期结论\n与贡献',72,560,161,60,{size:23,bold:true,fill:C.slate,lineHeight:30,align:'center'});
  const results=[['排序质量','联合局部与关联证据，形成更准确、稳定的完整责任排序'],['诊断效用','连接诊断质量与执行收益，提高有限预算下的恢复效率'],['可靠恢复','依赖恢复与双边验收提高恢复成功率，并控制非目标回归']];
  results.forEach(([a,b],i)=>{const x=252+i*322;s.rect(x,547,314,83,'#fff',i===2?C.orange:C.blue,1.3,2);s.text(a,x+10,550,294,28,{size:20.5,bold:true,fill:i===2?C.orange:C.blue});s.text(b,x+10,580,294,49,{size:18,lineHeight:24});});
  s.caption('图1  责任排序与诊断引导恢复的总体研究框架',641);
}
{
  const s=new Slide('2.2 研究问题与目标分解',2,{source:'原PPT V3第13—14页；RQ1/RQ2正式问题表述'});
  s.lead('研究对象是具有持久化工具副作用的多步骤执行任务。两个研究问题分别回答责任次序如何形成，以及该次序如何转化为可靠恢复。');
  table(s,'表1  两个研究问题的输入、输出与研究目标',['研究问题','输入与输出','研究目标'],[
    ['RQ1\n细粒度责任定位','输入：完整失败轨迹与候选步骤\n输出：全部候选的责任分数与排序 π','联合局部证据和跨步骤关系，\n提高责任位置的排序质量与稳定性。'],
    ['RQ2\n诊断引导恢复','输入：冻结排序与可执行状态\n输出：恢复计划及提交／撤销结果','在固定预算内选择恢复计划，\n同时实现目标恢复与非目标保持。']
  ],{y:226,widths:[220,440,444],rowHeights:[126,126],size:23});
  s.note('共同目标：以统一候选边界和独立执行验收，连接“诊断是否可信”与“诊断是否有用”。',604);
}
{
  const s=new Slide('2.3 诊断结果与恢复决策的衔接',2,{source:'原PPT V3第14—17、25页；完整排序到恢复桥接协议'});
  s.lead('责任分数描述步骤的诊断优先级，但不直接等同于恢复成功概率。恢复还受到状态范围、候选可执行性和验收条件的共同约束。');
  s.section('诊断提供可复用的责任次序','RQ1保留全部候选步骤的得分和顺序，既提供首选检查位置，也为后续候选保留次序信息。完整输出避免将诊断压缩为一个无法继续展开的Top-1标签。',221,{h:122});
  s.section('恢复把次序转化为具体行动','RQ2只读接收排序，确定责任锚点与候选优先级，再生成干预范围、绑定恢复操作并执行验收。责任判断与执行决策保持分工，候选失败后沿冻结次序继续尝试。',363,{h:122});
  s.section('桥接实验单独检验诊断价值','在相同任务、候选池、执行预算和验收条件下比较预测、固定和置乱次序，将排序产生的收益与范围扩展、执行机制的作用区分开。',505,{h:124});
}
{
  const s=new Slide('2.4 研究意义与预期结论',2,{source:'原PPT V3第16—17、35页；所有效果表述为开题预期结论，不代表已完成正式实验'});
  s.lead('本研究的预期贡献形成连续链条：以过程证据解释失败，以可检验的排序衔接恢复，以可撤销的执行控制状态副作用。');
  s.section('过程级失败诊断','局部行为证据与跨步骤关系联合建模，提高责任步骤排序质量，形成覆盖全部候选的细粒度诊断方法，为多步骤任务提供连续、可比较的检查顺序。',218,{h:123});
  s.section('诊断输出的下游效用','在同候选池、同预算和同验收条件下，责任排序提高恢复计划的选择效率，建立从诊断质量到任务恢复效用的可检验证据链。',362,{h:117});
  s.section('依赖感知的可靠恢复','多粒度状态恢复与双边事务验收共同提高任务恢复成功率、控制非目标回归，形成可执行、可撤销、可验收的恢复机制。',505,{h:117});
}
divider(3,'内容与方法','Contents and methods');
{
  const s=new Slide('3.1 任务轨迹与信息边界',3,{source:'原PPT V3第19—21页；RQ1任务组隔离协议'});
  s.lead('方法以完整失败轨迹为分析对象，以任务组为数据划分单位。每个候选步骤都获得责任分数，最终形成可供恢复阶段读取的完整次序。');
  s.section('可观察步骤证据','输入包括动作与结果结构、匿名角色、轨迹相对位置和可观察状态变化。同一任务及其近重复轨迹始终处于同一分区，避免训练与测试共享任务信息。',216,{h:119});
  s.formula('s<sub>q,i</sub> = f<sub>θ</sub>(T<sub>q</sub>, x<sub>q,i</sub>),     π<sub>q</sub> = argsort<sub>i</sub>(−s<sub>q,i</sub>)',360,1,{size:30,h:57});
  s.paragraph('式（1）把候选责任分数转化为任务级完整排序。候选集合及并列处理规则在测试前确定，所有排序方法共享同一候选边界。',441,89);
  s.paragraph('责任标签仅用于训练中的成对样本构造和独立评价，不进入测试特征。恢复结果、人工故障词和隐藏推理同样不参与测试阶段的责任打分。',550,85);
}
{
  const s=new Slide('3.2 局部行为证据与成对责任排序',3,{source:'原PPT V3第21—22页；RQ1任务内正反成对差分'});
  s.lead('局部排序分支比较同一轨迹内两个步骤的责任优先关系，将动作结构、反馈形态和过程位置转化为可比较的步骤分数。');
  s.paragraph('训练时，以标注责任步骤与其他候选构造正向差分，再交换比较方向形成反向样本。模型学习的是任务内相对次序，而不是依靠任务名称或角色身份识别责任标签。',214,121);
  s.formula('P(y = 1 ∣ Δx) = σ(w<sup>T</sup>Δx + b)',359,2,{size:32,h:56});
  s.formula('L = CE<sub>ω</sub>(P, y) + λ ‖w‖<sub>2</sub><sup>2</sup>',431,3,{size:30,h:56});
  s.paragraph('式（2）刻画成对责任偏好，式（3）约束训练目标。推理时对全部候选生成分数，再在任务内部排序，为关系分支和最终融合提供局部行为证据。',530,114);
}
{
  const s=new Slide('3.3 跨步骤关系与邻域聚合',3,{source:'原PPT V3第23页；四通道、两轮固定聚合协议。图为显式请求的可编辑方法示意图'});
  s.lead('单步描述难以表达错误的延迟显现和跨步关联。关系分支在同一轨迹上建立四类可观察关系，将邻域证据补充到候选步骤表示中。',103,86);
  const labels=['执行序列相邻','同匿名角色','同完整结构签名','同非空动作结构'];
  labels.forEach((a,i)=>{const x=74+i*290;s.rect(x,219,260,43,'#f1f5fa',C.line,1);s.text(a,x+6,226,248,31,{size:20.5,bold:true,align:'center',fill:C.blue});});
  node(s,105,292,265,82,'局部步骤表示','动作、结果与过程位置',{size:20});
  node(s,508,292,265,82,'第一轮关系聚合','读取直接邻居证据',{size:20});
  node(s,911,292,265,82,'第二轮关系聚合','纳入二跳关系上下文',{size:20});
  s.arrow([[377,333],[493,333]],C.blue);s.arrow([[780,333],[896,333]],C.blue);
  s.caption('图2  四类关系上的两轮固定邻域聚合',386);
  s.formula('m<sub>i,c</sub><sup>(r)</sup> = mean<sub>j ∈ N_c(i)</sub> z<sub>j</sub><sup>(r−1)</sup>',435,4,{size:29,h:56});
  s.formula('z<sub>i</sub><sup>(r)</sup> = z<sub>i</sub><sup>(r−1)</sup> + aggregate<sub>c</sub>(m<sub>i,c</sub><sup>(r)</sup>),    r = 1, 2',503,5,{size:28,h:56});
  s.text('式（4）与式（5）组织邻域证据；聚合本身不学习参数，增强表示交由成对排序器学习责任次序。',88,583,1104,62,{size:22.5,lineHeight:32});
}
{
  const s=new Slide('3.4 折外预测融合与完整责任排序',3,{source:'原PPT V3第24页；严格inner-held OOF融合，outer-held只推断一次'});
  s.lead('局部分支提供单步行为证据，关系分支提供过程关联证据。融合阶段保留二者的互补信息与分歧，以统一分数形成最终责任次序。');
  s.section('训练阶段：融合输入来自未参与拟合的任务组','采用任务组外预测（Out-of-Fold，OOF）构造融合训练数据。每条训练轨迹的分支分数均由未见该任务组的模型产生，避免在已拟合样本上训练融合器。',222,{h:123});
  s.formula('s<sub>q,i</sub><sup>final</sup> = F<sub>φ</sub>(s<sub>q,i</sub><sup>local</sup>, s<sub>q,i</sub><sup>rel</sup>, ψ<sub>q,i</sub>)',368,6,{size:31,h:61});
  s.paragraph('式（6）综合两类责任分数及其互补、分歧信息，再按式（1）形成完整排序。局部与关系证据共同决定候选先后，使单步行为和轨迹上下文进入同一诊断尺度。',452,126);
  s.note('外层测试任务只执行一次前向推断，不参与特征选择、参数估计或融合规则调整。',601,42);
}
{
  const s=new Slide('3.5 RQ1到RQ2的只读接口',3,{source:'原PPT V3第25页；Exp122注册对照纠正完整排序直传与原生后验次序混淆'});
  s.lead('完整责任排序是诊断输出，不直接规定所有恢复决策。RQ2只读消费该排序，并将不同的候选次序来源置于相同执行条件下比较。');
  s.section('输出记录与候选对应','RQ1导出任务标识、候选步骤标识、责任分数和确定性名次。RQ2依据步骤标识绑定恢复锚点，保持候选对应关系和完整覆盖，不回写RQ1的分数或排序文件。',221,{h:122});
  s.section('区分原始责任次序与恢复侧重排','一条路线直接使用RQ1完整排序；另一条路线保留RQ1首位候选，并以训练任务上的候选成功后验排列其余候选。两类次序分别评价，避免将恢复侧重排的收益归给RQ1完整排序。',365,{h:124});
  s.section('次序冻结与失败后的继续执行','候选次序在测试结果揭示前固定。执行失败只触发撤销及下一候选，不根据当前测试结果在线改写排序。固定与置乱对照使用同一候选池和预算。',510,{h:121});
}
{
  const s=new Slide('3.6 恢复计划表示与预算内选择',3,{source:'原PPT V3第26—27页；不沿用未经原生实现核验的线性效用加权式'});
  s.lead('恢复计划把诊断锚点与状态干预绑定，使责任判断转化为可执行行动。每个候选都具备明确的处理范围、恢复操作和验收条件。');
  s.formula('p<sub>k</sub> = (a<sub>k</sub>, S<sub>k</sub>, o<sub>k</sub>, V<sub>k</sub>),     P<sub>q</sub> = {p<sub>1</sub>, …, p<sub>K</sub>}',223,7,{size:31,h:65});
  s.paragraph('式（7）统一责任锚点、干预范围、执行操作与验收函数。候选生成仅使用可观察状态与预先规定的范围规则，不读取测试任务的成功结果来筛选计划。',312,110);
  s.formula('|A<sub>q</sub>| ≤ B',453,8,{size:34,h:62});
  s.paragraph('式（8）限定每项任务的实际尝试数。执行器按冻结次序逐一尝试，验收通过即提交；失败则撤销并继续，直到预算耗尽或无可执行候选。所有排序对照采用同一预算。',536,110);
}
{
  const s=new Slide('3.7 多粒度恢复范围与依赖约束',3,{source:'原PPT V3第28—29、66页；同目标前向状态增量代理，等规模仅匹配数量及前向顺序'});
  s.lead('恢复范围既不能遗漏依赖于错误状态的后续增量，也不能任意扩大到无关正确工作。本文以同目标前向状态关联构造可执行恢复范围。',102,86);
  s.formula('C<sup>+</sup>(a) = {v ∈ V<sub>state</sub> ∣ κ(v) = κ(a), call(v) ≥ call(a)}',209,9,{size:27,h:59});
  s.text('式（9）包含锚点及同目标的后续合格状态增量；它是可观察依赖的代理，不等同于真实因果图。',88,279,1104,60,{size:22.5,lineHeight:32});
  table(s,'表2  恢复范围及其比较作用',['范围','干预规则','比较作用'],[
    ['单点范围','仅处理责任锚点对应增量','最小干预基线'],
    ['等规模前向范围','匹配处理数量并保持前向顺序','识别范围扩展作用'],
    ['同目标依赖范围','处理锚点及同目标前向增量','识别目标依赖身份的增量作用']
  ],{y:355,widths:[225,485,394],rowHeights:[62,62,62],size:21});
}
{
  const s=new Slide('3.8 一致检查点与隔离重放',3,{source:'原PPT V3第30页；每候选全新副本、保留调用位置、抑制状态增量'});
  s.lead('每个候选从一致检查点或全新工作副本启动。恢复操作保留原始调用位置和执行顺序，仅抑制计划指定的状态增量，保证候选之间可比较。');
  const xs=[73,371,669,967];
  node(s,xs[0],241,239,100,'一致检查点','恢复相同初始状态',{color:C.orange,size:20});
  node(s,xs[1],241,239,100,'确定性重放','按计划处理状态增量',{color:C.orange,size:20});
  node(s,xs[2],241,239,100,'双边验收','目标恢复与非目标保持',{color:C.orange,size:20});
  node(s,xs[3],241,239,100,'提交或撤销','通过提交；失败撤销',{color:C.orange,size:20});
  for(let i=0;i<3;i++)s.arrow([[xs[i]+245,291],[xs[i+1]-12,291]],C.orange);
  s.arrow([[1087,342],[1087,387],[193,387],[193,349]],C.slate,1.8,'6 5');
  s.text('验收失败：撤销本次变化，下一候选重新从一致状态开始',331,363,649,27,{size:18.5,align:'center',fill:C.slate});
  s.caption('图3  候选级隔离执行、双边验收与事务提交',406);
  s.section('保持状态边界与执行可比性','后续调用索引与控制流保持一致，候选之间不继承上一次尝试的污染。计划差异只体现在被处理的状态增量，而不来自不同的执行起点。',468,{h:110,size:23});
  s.note('冲突显式中止；无合格状态节点时弃权。空操作不能被记录为成功恢复。',605);
}
{
  const s=new Slide('3.9 双边验收与事务式提交',3,{source:'原PPT V3第31页；TNR与目标探针联合评价同一实际执行结果'});
  s.lead('恢复成功必须同时满足目标任务恢复与非目标状态保持。事务无回归（Transactional No-Regression，TNR）将副作用约束纳入提交条件。');
  s.text('非目标保持',88,225,1104,35,{size:25,bold:true,fill:C.slate});
  s.formula('TNR(p) = NonTargetEqual(p) ∧ GitDiffOK(p) ∧ NoNewConflict(p)',275,10,{size:25,h:62});
  s.paragraph('式（10）在同一执行结果上联合检查参考非目标状态、版本差分合规性和新增冲突，防止目标修复掩盖其他位置的退化。',355,84);
  s.text('候选成功与提交',88,460,1104,35,{size:25,bold:true,fill:C.slate});
  s.formula('Success(p) = Accepted(p) ∧ TargetProbe(p) ∧ TNR(p)',512,11,{size:27,h:60});
  s.note('式（11）成立才提交候选状态；任一条件失败均撤销，并在剩余预算内继续尝试。',604,40);
}
{
  const s=new Slide('3.10 排序与范围作用的独立验证',3,{source:'原PPT V3第29、32页；Exp122同缓存排序比较与跨范围受控比较'});
  s.lead('方法评价分开改变候选次序与干预范围，使责任排序、处理规模和依赖身份的作用分别可识别，而不是将组合方法的收益归于单一机制。');
  table(s,'表3  候选次序与恢复范围的控制变量设计',['比较轴','改变的条件','保持一致的条件'],[
    ['诊断次序','完整排序、保护首位的后验次序、\n固定与置乱次序','任务、候选池、预算、执行器、验收器'],
    ['范围扩展','单点范围与等规模前向范围','责任锚点、排序、预算、执行与验收'],
    ['依赖身份','等规模前向范围与同目标依赖范围','排序、处理规模、预算、执行与验收']
  ],{y:213,widths:[195,439,470],rowHeights:[104,82,82],size:21.5});
  s.note('RQ1独立评价排序质量；桥接实验与RQ2评价恢复成功、非目标回归和执行成本。',614,36);
}
// Static geometry is shared by the delivered SVG slides and the offline previews.
await fs.mkdir(path.join(BUILD,'preview'),{recursive:true});
const svgs=slides.map(s=>s.svg());
const chapterStarts=slides.filter(s=>s.divider).map(s=>s.number);
const html=`<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>智能体系统失败诊断与可靠恢复方法研究 · 前三章</title>
<style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#25353e;font-family:"Microsoft YaHei",sans-serif}#viewport{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}#deck{position:relative;flex:0 0 1280px;width:1280px;height:720px;transform-origin:center;box-shadow:0 16px 64px #0005;background:white}.slide{position:absolute;inset:0;display:none}.slide.active{display:block}.slide svg{display:block;width:1280px;height:720px}svg text{user-select:text}svg a{cursor:pointer}svg a:hover{text-decoration:underline}#controls{position:fixed;left:16px;bottom:12px;padding:8px 12px;display:flex;align-items:center;gap:12px;border-radius:6px;color:#fff;background:#17242bee;opacity:0;transition:opacity .15s;font-size:13px;z-index:10}#controls:hover,#controls:focus-within{opacity:1}button{color:inherit;border:0;background:none;font:inherit;cursor:pointer;padding:4px}#count{min-width:65px;text-align:center}@page{size:1280px 720px;margin:0}@media print{html,body{height:auto;overflow:visible;background:#fff}#viewport{position:static;display:block}#deck{transform:none!important;box-shadow:none;height:auto;width:1280px}.slide{display:block!important;position:relative;width:1280px;height:720px;break-after:page;page-break-after:always}.slide:last-child{break-after:auto;page-break-after:auto}#controls{display:none}svg{-webkit-print-color-adjust:exact;print-color-adjust:exact}}</style></head>
<body><div id="viewport"><main id="deck" aria-label="开题报告前三章">${svgs.map((svg,i)=>`<section class="slide${i===0?' active':''}" id="s${i+1}" data-chapter="${slides[i].ch}" aria-label="第${i+1}页 ${esc(slides[i].title)}">${svg}</section>`).join('\n')}</main></div>
<nav id="controls" aria-label="演示控制"><button id="prev" aria-label="上一页">◀</button><span id="count">1 / ${slides.length}</span><button id="next" aria-label="下一页">▶</button><button data-page="${chapterStarts[0]}">第一章</button><button data-page="${chapterStarts[1]}">第二章</button><button data-page="${chapterStarts[2]}">第三章</button><button id="fullscreen">全屏 F</button></nav>
<script>const slides=[...document.querySelectorAll('.slide')],deck=document.getElementById('deck'),count=document.getElementById('count');let current=0;function fit(){deck.style.transform='scale('+Math.min(innerWidth/1280,innerHeight/720)+')'}function show(i,update=true){current=Math.max(0,Math.min(i,slides.length-1));slides.forEach((s,j)=>{s.classList.toggle('active',j===current);s.setAttribute('aria-hidden',String(j!==current))});count.textContent=(current+1)+' / '+slides.length;if(update)history.replaceState(null,'','#'+(current+1))}function fromHash(){const i=Number(location.hash.slice(1));show(Number.isInteger(i)&&i>0?i-1:0,false)}function fullscreen(){if(document.fullscreenElement)document.exitFullscreen?.();else document.documentElement.requestFullscreen?.().catch(()=>{})}document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);document.getElementById('fullscreen').onclick=fullscreen;document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>show(Number(b.dataset.page)-1));addEventListener('resize',fit);addEventListener('hashchange',fromHash);addEventListener('keydown',e=>{if(e.ctrlKey||e.altKey||e.metaKey||e.target.closest('input,textarea,[contenteditable=true]')||(e.key===' '&&e.target.closest('button,a')))return;if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}else if(e.key==='Home')show(0);else if(e.key==='End')show(slides.length-1);else if(e.key.toLowerCase()==='f')fullscreen()});fit();fromHash();</script></body></html>`;
await fs.writeFile(OUT,html,'utf8');
for(let i=0;i<svgs.length;i++){
  await fs.writeFile(path.join(BUILD,'preview',`slide-${String(i+1).padStart(2,'0')}.svg`),svgs[i]);
  await sharp(Buffer.from(svgs[i])).png().toFile(path.join(BUILD,'preview',`slide-${String(i+1).padStart(2,'0')}.png`));
}
const thumbW=384,thumbH=216,gap=16,cols=3,rows=Math.ceil(slides.length/cols);
const contact=createCanvas(cols*(thumbW+gap)+gap,rows*(thumbH+40)+gap);const cc=contact.getContext('2d');cc.fillStyle='#dbe1e4';cc.fillRect(0,0,contact.width,contact.height);
for(let i=0;i<slides.length;i++){const x=gap+(i%cols)*(thumbW+gap),y=gap+Math.floor(i/cols)*(thumbH+40);cc.drawImage(await loadImage(path.join(BUILD,'preview',`slide-${String(i+1).padStart(2,'0')}.png`)),x,y,thumbW,thumbH);cc.fillStyle='#24343c';cc.font='16px Microsoft YaHei';cc.fillText(`${i+1}. ${slides[i].title}`,x,y+thumbH+23);}
await fs.writeFile(path.join(BUILD,'contact.png'),contact.toBuffer('image/png'));
await fs.copyFile(path.join(BUILD,'preview','slide-10.png'),path.join(DIR,'assets','前三章_总体框架预览.png'));
for(const s of slides){for(const b of s.textBoxes){if(b.x<0||b.y<0||b.x+b.w>1281||b.y+b.h>721)issues.push({slide:s.number,type:'canvas-bound',box:b});}}
await fs.writeFile(path.join(BUILD,'layout-report.json'),JSON.stringify({slides:slides.length,chapterStarts,issues,slideTitles:slides.map(s=>s.title)},null,2));
console.log(JSON.stringify({output:OUT,slides:slides.length,chapterStarts,issues},null,2));
