// Rebuild the editable HTML/SVG deck and its offline previews from the approved chapter-one source.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const {createCanvas, loadImage, GlobalFonts} = require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
const sharp=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const ROOT='D:/Code/毕设/graduate-thesis-experiments';
const DIR=path.join(ROOT,'开题/开题报告PPT');
const BUILD=path.join(ROOT,'工作区/0917-html-title-theory-build');
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
// Author the adopted-title revision as editable text and evidence diagrams.
const {buildChapters,THESIS_TITLE,REFERENCES}=await import('./前三章_题目版内容.mjs');
buildChapters({Slide,divider,table,node,C,logo,roof,layout});
// Static geometry is shared by the delivered SVG slides and the offline previews.
await fs.mkdir(path.join(BUILD,'preview'),{recursive:true});
const svgs=slides.map(s=>s.svg());
const chapterStarts=slides.filter(s=>s.divider&&s.ch>0).map(s=>s.number);
const overviewPage=slides.find(s=>s.overview).number;
const html=`<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${THESIS_TITLE} · 前三章</title>
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
await fs.copyFile(path.join(BUILD,'preview',`slide-${String(overviewPage).padStart(2,'0')}.png`),path.join(DIR,'assets','前三章_总体框架预览.png'));
for(const s of slides){for(const b of s.textBoxes){if(b.x<0||b.y<0||b.x+b.w>1281||b.y+b.h>721)issues.push({slide:s.number,type:'canvas-bound',box:b});}}
await fs.writeFile(path.join(BUILD,'layout-report.json'),JSON.stringify({slides:slides.length,chapterStarts,overviewPage,issues,slideTitles:slides.map(s=>s.title)},null,2));
console.log(JSON.stringify({output:OUT,slides:slides.length,chapterStarts,overviewPage,issues},null,2));
