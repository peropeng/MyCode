import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {makeAuthoring,toNativeDeck,plain,PresentationFile} from './PPT_原生适配器.mjs';
import {buildChapters,THESIS_TITLE} from './前三章_题目版内容.mjs';
import {buildLaterChapters} from './后章_正式PPT内容.mjs';
import {BIBLIOGRAPHY as bib} from './正式PPT_文献.mjs';
const assets=path.dirname(fileURLToPath(import.meta.url)),out=path.dirname(assets),repo=path.resolve(out,'../..');
const tmp=path.join(repo,'工作区/0917-formal-ppt-build');
const template=JSON.parse(await fs.readFile(path.join(tmp,'source-proto.json'),'utf8'));
const titleLines='基于多关系图建模的智能体\n细粒度责任排序和状态恢复方法研究';
const kind=process.argv[2]||'main';
const a=makeAuthoring();
function cover(subtitle){
 const s=new a.Slide(THESIS_TITLE,0,{divider:true});
 s.ops.push({type:'image',path:path.join(assets,'whu-wordmark.png'),x:585,y:66,w:110,h:110});
 s.text('武汉大学  开题报告',180,200,920,42,{size:25,align:'center',fill:a.C.slate});
 s.text(titleLines,70,279,1140,150,{size:43,bold:true,lineHeight:64,align:'center',fill:'#172d3a'});
 s.line(225,463,1055,463,a.C.line,1.3);
 s.text(subtitle,180,497,920,50,{size:26,align:'center',fill:a.C.slate});
 s.text('汇报人：杨亚鹏    2026年9月',180,563,920,36,{size:21,align:'center',fill:a.C.slate});
 s.speaker=THESIS_TITLE+'。'+subtitle+'。本研究围绕步骤级责任排序与可执行软件状态恢复展开。';
 return s;
}
const order=[],map={};
const cite=(...ids)=>ids.map(id=>`<a class="cite" href="${bib[id].url}">[${id}]</a>`).join('');
if(kind==='main'){
 buildChapters(a);a.slides.splice(a.slides.findIndex(s=>s.title.startsWith('前三章引用文献')));
 const originalFirst=a.slides.shift();
 const c=cover('研究方法、实验设计与前期研究结果');a.slides.pop();a.slides.unshift(c);
 const notes=await fs.readFile(path.join(out,'第三章_讲稿与术语备注.md'),'utf8');
 for(const m of notes.matchAll(/## 第(\d+)页：[^\n]+\n([\s\S]*?)(?=\n## |$)/g)){
  const s=a.slides[Number(m[1])-1];if(s)s.speaker=m[2].trim();
 }
 let eq=Math.max(...a.slides.flatMap(s=>s.ops.filter(o=>o.type==='formula').map(o=>Number(o.num))));
 buildLaterChapters({...a,cite,equation:(s,text,y,opts)=>{s.formula(text,y,++eq,opts);return eq;}});
 for(const s of a.slides){
  for(const op of s.ops){
   const strings=op.type==='table'?op.values.flat():op.html?[op.html]:[];
   for(const text of strings)for(const m of text.matchAll(/\[(\d+)\]/g)){
    const id=Number(m[1]);if(bib[id]&&!map[id]){order.push(id);map[id]=order.length;}
   }
  }
 }
 const renumber=text=>String(text).replace(/人工标注/g,'数据集标注').replace(/差分合规性/g,'差分格式检查').replace(/版本差分位于允许范围/g,'git diff --check通过').replace(/\[(\d+)\]/g,(x,n)=>map[n]?`[${map[n]}]`:x).replace(/文献(\d+)/g,(x,n)=>map[n]?`文献${map[n]}`:x);
 for(let i=0;i<a.slides.length;i++){
  const s=a.slides[i];
  if(!s.speaker){s.speaker=s.divider?`下面进入${s.title}。`:s.ops.filter(o=>o.type==='text'&&o.y<650).map(o=>plain(o.html)).join('\n\n');if(s.source)s.speaker+='\n\n依据：'+s.source;}
  const links=new Set(s.ops.flatMap(o=>o.type==='table'?o.values.flat():o.html?[o.html]:[]).flatMap(t=>[...t.matchAll(/href="([^"]+)"/g)].map(m=>m[1])));
  if(links.size)s.speaker+='\n\n论文来源：\n'+[...links].join('\n');
  s.speaker=renumber(s.speaker);
  for(const op of s.ops){if(op.html)op.html=renumber(op.html);if(op.values)op.values=op.values.map(r=>r.map(renumber));}
  for(const op of s.ops)if(op.type==='formula'&&op.num===4)op.html=op.html.replace('λ‖','(λ/2)‖').replace('λ ‖','(λ/2) ‖');
 }
 for(let start=0;start<order.length;start+=4){
  const ids=order.slice(start,start+4),s=new a.Slide(`6.3 参考文献（${start/4+1}/${Math.ceil(order.length/4)}）`,6);
  let y=110;
  for(const id of ids){const b=bib[id],text=`[${map[id]}] ${b.entry}`,h=a.layout(text,1104,23).length*33;
   s.text(`<a href="${b.url}">[${map[id]}]</a> ${b.entry}`,88,y,1104,h+8,{size:23,lineHeight:33,fill:'#000000'});y+=h+30;
  }
  s.speaker=ids.map(id=>`[${map[id]}] ${bib[id].entry}\n${bib[id].url}`).join('\n\n');
 }
 const thanks=new a.Slide('感谢聆听',6,{divider:true});
 thanks.ops.push({type:'image',path:path.join(assets,'whu-wordmark.png'),x:585,y:145,w:110,h:110});
 thanks.text('感谢聆听，敬请指正',140,324,1000,80,{size:49,bold:true,align:'center',fill:a.C.slate});
 thanks.speaker='以上是本次开题报告。期待老师们就研究问题、方法设计与实验安排提出意见。';
}else{
 cover('公式与参数说明 · 独立附件');
 const {buildAppendix}=await import('./附录_正式PPT内容.mjs');buildAppendix(a);
 for(const s of a.slides){s.speaker=s.speaker?.replace(/人工责任标签/g,'数据集责任标签');for(const op of s.ops)if(op.html)op.html=op.html.replace(/人工责任标签/g,'数据集责任标签');}
}
// Record immutable source fingerprints alongside the private validation records.
const hashes={};for(const name of ['开题报告_v13审定意见落实版_v15.pptx','开题报告_v15第三章重构与附录版_v16.pptx'])hashes[name]=crypto.createHash('sha256').update(await fs.readFile(path.join(out,name))).digest('hex');
await fs.writeFile(path.join(tmp,kind+'-source-hashes.json'),JSON.stringify(hashes,null,2));
await fs.writeFile(path.join(tmp,kind+'-authoring.json'),JSON.stringify({slides:a.slides,issues:a.issues,order,map},null,2));
console.log('AUTHORING',kind,a.slides.length,'issues',JSON.stringify(a.issues));
const result=await toNativeDeck(a.slides,template,assets,{appendix:kind!=='main'});
await fs.writeFile(path.join(tmp,kind+'-proto.json'),JSON.stringify(result.proto));
await fs.writeFile(path.join(tmp,kind+'-requirements.json'),JSON.stringify({tableOwners:result.tableOwners,mathCount:result.mathCount,slideCount:a.slides.length},null,2));
await(await PresentationFile.exportPptx(result.presentation)).save(path.join(tmp,kind+'-candidate.pptx'));
const renderDir=path.join(tmp,kind+'-render');await fs.mkdir(renderDir,{recursive:true});
for(let i=0;i<a.slides.length;i++){
 const png=await result.presentation.export({slide:result.presentation.slides.getItem(i),format:'png',scale:1});
 await fs.writeFile(path.join(renderDir,`${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 console.log('RENDER',kind,i+1,a.slides[i].title);
}
