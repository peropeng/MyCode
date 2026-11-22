// Academic content for the adopted title. Geometry helpers live in 前三章_HTML生成.mjs.
export const THESIS_TITLE='基于多关系图建模的智能体细粒度责任排序和状态恢复方法研究';
export const REFERENCES=[
  {id:1,authors:'YAO S, ZHAO J, YU D, et al.',title:'ReAct: Synergizing Reasoning and Acting in Language Models',venue:'ICLR, 2023',url:'https://arxiv.org/abs/2210.03629',use:'推理与行动交替的智能体执行方式'},
  {id:2,authors:'YANG J, JIMENEZ C E, WETTIG A, et al.',title:'SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering',venue:'NeurIPS, 2024',url:'https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html',use:'软件工具调用与外部状态变化'},
  {id:3,authors:'WU Q, BANSAL G, ZHANG J, et al.',title:'AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation',venue:'arXiv:2308.08155, 2023',url:'https://arxiv.org/abs/2308.08155',use:'通过多个智能体的交互与分工组织任务'},
  {id:4,authors:'ZHANG S, YIN M, ZHANG J, et al.',title:'Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems',venue:'ICML, 2025',url:'https://proceedings.mlr.press/v267/zhang25cq.html',use:'责任智能体与决定性错误步骤的归因任务'},
  {id:5,authors:'CHEN M, et al.',title:'Seeing the Whole Elephant: A Benchmark for Failure Attribution in LLM-based Multi-Agent Systems',venue:'ACL, 2026',url:'https://aclanthology.org/2026.acl-long.912/',use:'完整执行上下文与失败归因证据'},
  {id:6,authors:'ZHU T, WU Y, JIN W, et al.',title:'StepFinder: A Temporal Semantic Framework for Failure Attribution in Multi-Agent Systems',venue:'KDD, 2026',url:'https://arxiv.org/abs/2606.03467',use:'时序演化与跨步骤依赖建模'},
  {id:7,authors:'LYU Z, JI Z, CHEN S, et al.',title:'CAM: A Causality-based Analysis Framework for Multi-Agent Code Generation Systems',venue:'ISSTA, 2026',url:'https://conf.researchr.org/details/issta-2026/issta-2026-research-papers/147/CAM-A-Causality-based-Analysis-Framework-for-Multi-Agent-Code-Generation-Systems',use:'中间特征贡献与交互作用的分析动机'},
  {id:8,authors:'LIU S, CHEN Y, KRISHNA R, et al.',title:'Process-Centric Analysis of Agentic Software Systems',venue:'PACMPL / OOPSLA, 2026',url:'https://arxiv.org/abs/2512.02393',use:'执行过程的图结构表示与分析'},
  {id:9,authors:'CHEN Y, et al.',title:'STRATUS: A Multi-agent System for Autonomous Reliability Engineering of Modern Clouds',venue:'NeurIPS, 2025',url:'https://proceedings.neurips.cc/paper_files/paper/2025/file/47a6e9e2c3019f13ad94a0f259fe4970-Paper-Conference.pdf',use:'事务无回归、失败撤销及有限重试'},
  {id:10,authors:'CHANG E Y, GENG L.',title:'SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning',venue:'PVLDB, 18(12): 4874–4886, 2025',url:'https://www.vldb.org/pvldb/vol18/p4874-chang.pdf',use:'检查点、补偿执行与独立验证'},
  {id:11,authors:'SCHLICHTKRULL M, KIPF T N, BLOEM P, et al.',title:'Modeling Relational Data with Graph Convolutional Networks',venue:'ESWC, 2018',url:'https://arxiv.org/html/1703.06103v4',use:'有向带类型多关系图及按关系划分的邻域'},
  {id:12,authors:'BURGES C, SHAKED T, RENSHAW E, et al.',title:'Learning to Rank using Gradient Descent',venue:'ICML, 2005',url:'https://www.microsoft.com/en-us/research/wp-content/uploads/2005/08/icml_ranking.pdf',use:'基于样本对偏好学习实值排序函数'},
  {id:13,authors:'ELNOZAHY E N, ALVISI L, WANG Y M, JOHNSON D B.',title:'A Survey of Rollback-Recovery Protocols in Message-Passing Systems',venue:'ACM Computing Surveys, 34(3): 375–408, 2002',url:'https://www.cs.rice.edu/~dbj/pubs/csur-rollback.pdf',use:'检查点与事件记录支持的回滚恢复及状态一致性'},
  {id:14,authors:'SUN K, LI W, DONG B, et al.',title:'Scope Delineation Before Localization: A Two-Stage Framework for Enhancing Failure Attribution in Multi-Agent Systems',venue:'AAAI, 2026',url:'https://ojs.aaai.org/index.php/AAAI/article/view/40594',use:'先确定失败范围，再定位责任步骤'},
  {id:15,authors:'GENG M, GU S, LIU Z, et al.',title:'Failure Localization in Multi-Agent Code Generation via Knowledge-Guided and Transferable Reasoning',venue:'AAAI, 2026',url:'https://ojs.aaai.org/index.php/AAAI/article/view/36993',use:'行为编码、知识与策略对齐和一致性评分'},
  {id:16,authors:'ZHAO X, GAO F, SONG X, et al.',title:'ReAgent: Reversible Multi-Agent Reasoning for Knowledge-Enhanced Multi-Hop QA',venue:'EMNLP, 2025',url:'https://aclanthology.org/2025.emnlp-main.202/',use:'冲突触发的局部和全局推理回退'},
  {id:17,authors:'WU Q, GAO P, LIU W, LUAN J.',title:'BacktrackAgent: Enhancing GUI Agent with Error Detection and Backtracking Mechanism',venue:'EMNLP, 2025',url:'https://aclanthology.org/2025.emnlp-main.212/',use:'GUI执行中的错误检测、回退与反思'},
  {id:18,authors:'ZHU K, LIU Z, LI B, et al.',title:'Where LLM Agents Fail and How They can Learn From Failures',venue:'arXiv:2509.25370, 2025',url:'https://arxiv.org/abs/2509.25370',use:'错误分类、根因诊断与针对性纠正反馈'}
];
const cite=(...ids)=>ids.map(id=>`<a class="cite" href="${REFERENCES.find(r=>r.id===id).url}">[${id}]</a>`).join('');

export function buildChapters({Slide,divider,table,node,C,logo,roof,layout}){
  let eqNumber=0;
  const equation=(s,text,y,opts={})=>{const n=++eqNumber;s.formula(text,y,n,opts);return n;};
  function prose(title,ch,lead,paragraphs,source=''){
    const s=new Slide(title,ch,{source});
    const items=[{html:lead,lead:true},...paragraphs.map(html=>({html,lead:false}))];
    let chosen;
    for(const size of [26,25,24,23]){
      const boxes=items.map(p=>{const f=p.lead?26:size,lh=f*1.5;return {...p,size:f,lh,h:(layout(p.html,1104,f,{bold:p.lead,indent:p.lead?0:2*f}).length-1)*lh+f*1.3};});
      const total=boxes.reduce((n,p)=>n+p.h,0)+22*(items.length-1);
      if(total<=532){chosen={boxes,total};break;}
    }
    if(!chosen)throw Error('Content does not fit: '+title);
    const gap=22+Math.min(12,(532-chosen.total)/Math.max(1,items.length-1));
    let y=103+Math.max(0,(532-(chosen.boxes.reduce((n,p)=>n+p.h,0)+gap*(items.length-1)))/2);
    for(const p of chosen.boxes){s.text(p.html,88,y,1104,p.h+1,{size:p.size,lineHeight:p.lh,bold:p.lead,indent:p.lead?0:2*p.size,fill:p.lead?C.slate:C.ink});y+=p.h+gap;}
    return s;
  }
  function sections(title,ch,lead,items,source=''){
    const s=new Slide(title,ch,{source});s.lead(lead);
    items.forEach(([h,b],i)=>s.section(h,b,218+i*142,{h:124,size:24}));
    return s;
  }

  // The cover retains the existing university artwork and the adopted wording exactly.
  {
    const s=new Slide(THESIS_TITLE,0,{divider:true,source:'开题报告题目与研究范围'});
    s.parts.push(`<image href="${logo}" x="592" y="73" width="96" height="96"/>`);
    s.text('武汉大学  开题报告',180,192,920,42,{size:25,align:'center',fill:C.slate});
    s.text('基于多关系图建模的智能体\n细粒度责任排序和状态恢复方法研究',84,277,1112,145,{size:44,bold:true,lineHeight:65,align:'center',fill:'#172d3a'});
    s.line(225,470,1055,470,C.line,1.3);
    s.text('第一章  背景与现状     第二章  目标与意义     第三章  内容与方法',130,503,1020,45,{size:23,align:'center',fill:C.slate});
  }
  divider(1,'背景与现状','Background and current situation');
  prose('1.1 研究背景：智能体可靠性',1,
    '大语言模型与工具执行结合后，任务质量取决于完整执行过程及其对环境状态的影响。',[
    '大语言模型（Large Language Model，LLM）能够理解任务描述并生成文本。面对检索信息、修改文件和运行程序等任务，模型需要通过工具与外部环境交互。',
    `基于大语言模型的智能体将推理、动作选择和环境反馈组织为多步骤过程。推理与行动交替，使系统能够获取新信息并调整后续决策${cite(1)}。`,
    `软件智能体通过接口浏览仓库、编辑文件并执行测试${cite(2)}。这些操作会留下持久化变化，后续步骤在已有状态上继续执行，局部错误因而可能在较晚的验收阶段才显现。`,
    '本研究围绕两个连续问题展开：如何对失败轨迹的全部步骤形成责任次序，以及如何据此选择恢复计划，处理错误状态并保留无关的正确工作。'
  ],'ReAct与SWE-agent支持背景事实。最后一段为本研究的问题界定。');
  sections('1.1 研究背景：应用场景与研究范围',1,
    `多智能体系统通过具有不同职责的智能体交互和协作完成任务。主体分工与跨主体消息使失败证据分散在多个执行步骤中${cite(3,4)}。`,[
    ['诊断对象：多智能体失败轨迹','研究一以多智能体失败轨迹为主要对象，在统一轨迹内比较不同角色的执行步骤。分析单位为执行步骤，匿名角色作为可观察的结构特征参与建模。'],
    ['恢复对象：软件工具执行状态','研究二在可执行的软件仓库任务上验证恢复。当前资产采用单个助手的工具动作流，检查文件与仓库状态的变化，尚不覆盖多写入主体的协同恢复。'],
    ['适用范围：步骤级诊断与软件状态恢复','多智能体协作构成本文的主要诊断场景，软件仓库任务构成状态恢复的验证环境。两类实验分别评价责任排序质量与执行恢复效用，恢复结论限定于现有执行模型。']
  ],'AutoGen与Who&When说明多智能体场景；本地恢复协议明确single assistant action stream。');
  sections('1.2 症状、责任与恢复边界',1,
    `任务失败的观测位置与责任步骤的位置并不必然一致${cite(4)}。本文分别研究步骤责任的诊断次序，以及与候选步骤对应的状态干预范围。`,[
    ['失败症状与诊断证据','测试失败、目标检查不通过或版本冲突反映任务约束未满足。本文将这些现象作为失败观测，并结合完整轨迹分析候选步骤的相对责任。'],
    ['步骤责任与候选优先级',`步骤级归因关注与任务失败相关的责任动作${cite(4)}。本文对全部候选赋分并排序，责任分数表示给定标注体系下的诊断优先级，以独立任务上的排序质量评价其有效性。`],
    ['状态关联与干预范围','单点干预可能残留关联错误，扩大干预范围则可能损失正确状态。本文依据候选锚点和可观察状态关联构造恢复范围，通过执行与验收评价其作用。']
  ]);
  prose('1.3 国外研究现状：失败归因与过程分析',1,
    '国外相关研究形成了步骤级失败归因、过程结构分析和诊断反馈修正等研究方向，为责任建模提供任务定义与过程证据。',[
    `<b>Who&amp;When</b>将多智能体失败归因分为责任智能体识别与决定性错误步骤定位，并建立相应标注数据与评价任务${cite(4)}。本文沿用步骤级诊断单位，进一步研究覆盖全部候选的责任次序。`,
    `<b>Process-Centric Analysis</b>以过程图组织轨迹，分析执行阶段、策略变化和低效模式${cite(8)}。该工作侧重过程理解，本文将关系表示用于步骤责任评分与排序。`,
    `<b>AgentDebug</b>建立模块化错误分类，识别关键错误并提供反馈，引导重新执行${cite(18)}。其诊断与修正形成反馈闭环。本文进一步区分完整排序、候选重排和状态干预范围的独立作用。`
  ],'国外研究按论文主要署名机构归类，含国际合作工作。文献依据[4][8][18]，本文比较边界依据冻结协议。');
  prose('1.3 国外研究现状：可逆执行与事务恢复',1,
    '可逆推理、事务补偿与无回归约束分别处理错误传播、长流程一致性和执行安全问题，恢复机制的适用范围取决于其状态模型。',[
    `<b>ReAgent</b>在多跳问答中采用局部与全局回退，发现冲突后返回此前有效状态${cite(16)}。其主要干预对象是推理过程，软件工具产生的文件与仓库变化仍需独立的恢复与验收机制。`,
    `<b>STRATUS</b>以检测、诊断和缓解状态机组织云可靠性任务，提出事务无回归约束，在明确前提下支持失败撤销与重试${cite(9)}。本文借鉴无回归思想，并将其具体化为可检查的软件状态条件。`,
    `<b>SagaLLM</b>通过持久化上下文、模块化检查点、补偿执行与独立验证维护长流程一致性${cite(10)}。本文关注有限预算下的候选选择，分别评价诊断次序与恢复执行机制的作用。`
  ]);
  prose('1.4 国内研究现状：定位范围与诊断证据',1,
    '国内相关研究从长轨迹搜索、角色行为可比性和完整执行观测等方面改进失败归因，扩展了步骤责任分析的证据来源。',[
    `<b>Scope Delineation</b>先确定失败范围，再定位责任步骤，并通过逐步范围划分与专家知识辅助减轻长日志推理负担${cite(14)}。该方法将搜索范围作为定位中间对象，本文则在统一候选集合上研究完整责任次序。`,
    `<b>Failure Localization</b>提出知识引导的FLKR框架，结合行为编码、知识与策略对齐以及一致性评分，处理多智能体代码生成中的解法差异${cite(15)}。其行为可比性问题与本文的任务内成对责任学习相关。`,
    `<b>Seeing the Whole Elephant</b>通过完整执行轨迹与可复现环境补充仅观察输出时缺失的输入和上下文证据${cite(5)}。本文采用匿名结构特征，需明确其可见信息范围，并独立检验该表示下的排序质量。`
  ]);
  prose('1.4 国内研究现状：步骤交互与执行恢复',1,
    '跨步骤交互建模与错误后的回退机制分别扩展诊断和执行能力。本文在保留两类研究边界的基础上构建排序到恢复的评价接口。',[
    `<b>StepFinder</b>结合时序语义表示与智能体感知的步骤交互，学习步骤错误分数并评价归因和排序质量${cite(6)}。本文采用匿名多关系结构与固定聚合，研究局部和关系证据融合后的完整责任排序及其下游效用。`,
    `<b>CAM</b>分析中间特征及交互对代码生成正确性的贡献${cite(7)}。本文借鉴跨步骤关联的分析视角，以可观察结构构造关系图，所得关系和分数不解释为已经识别的因果效应。`,
    `<b>BacktrackAgent</b>通过验证、回退判断和反思模块检测并处理GUI执行错误${cite(17)}。其恢复对象是界面交互过程，本文将干预对象限定为软件状态增量，并联合验收目标恢复与非目标保持。`
  ]);
  sections('1.5 研究缺口与本文切入点',1,
    '已有研究分别覆盖步骤归因、关系建模、反馈修正和事务恢复。本文进一步研究匿名结构下的证据融合，以及诊断信息在受控状态恢复中的独立效用。',[
    ['多关系图建模：跨步骤结构上下文表示','分别构造时序相邻、角色与行为结构关系，按关系类型聚合邻域信息，为局部责任评分补充跨步骤结构上下文。'],
    ['细粒度责任排序：全候选相对责任估计','在同一失败轨迹内学习步骤的相对责任，融合局部与关系分支分数。排序结果覆盖全部候选，为首选及后续候选提供统一的诊断优先级。'],
    ['状态恢复：诊断引导的状态干预与验收','依据候选步骤构造状态干预范围，按冻结次序执行回滚重放。联合检查目标恢复与非目标保持，分别评价诊断信息和恢复执行机制的作用。']
  ]);

  divider(2,'目标与意义','Goals and significance');
  {
    const s=new Slide('2.1 总体研究框架',2,{source:'多关系图定义见[11]，成对排序思想见[12]，回滚恢复与无回归思想见[13][9]。图中四类关系、固定聚合、融合和恢复范围规则均为本研究设计。效果表述为预期结论。'});
    s.overview=true;
    const L=64,R=710,W=506;
    s.rect(48,87,1184,550,'#fff','#a9b8c0',1.4,2);
    for(const [x,color,label] of [[L,C.blue,'RQ1  细粒度责任排序'],[R,C.orange,'RQ2  状态恢复']]){
      s.rect(x,96,W,36,color,color,1.4,2);s.text(label,x+12,98,W-24,34,{size:25.5,bold:true,fill:'#fff'});
    }
    s.rect(L,137,W,76,C.bluePale,C.blue,1.5,2);s.rect(R,137,W,76,C.orangePale,C.orange,1.5,2);
    s.text('<b>研究目的1：</b>形成步骤级完整责任次序，\n提高失败轨迹的排序质量与稳定性。',L+16,149,W-32,58,{size:21,lineHeight:29});
    s.text('<b>研究目的2：</b>恢复可检查的执行状态，\n提高恢复成功率并控制非目标回归。',R+16,149,W-32,58,{size:21,lineHeight:29});
    s.rect(L,220,W,63,'#fff',C.blue,1.3,2);s.rect(R,220,W,63,'#fff',C.orange,1.3,2);
    s.text('<b>研究问题</b>  如何利用局部信息和多类关系，\n对失败轨迹的全部步骤学习责任次序？',L+12,224,W-24,57,{size:20.5,lineHeight:28});
    s.text('<b>研究问题</b>  如何据诊断安排候选与范围，\n恢复目标状态并保留无关正确状态？',R+12,224,W-24,57,{size:20.5,lineHeight:28});
    for(const [x,color,fill] of [[L,C.blue,C.bluePale],[R,C.orange,C.orangePale]]){s.rect(x,289,W,29,fill,color,1.3,2);s.text('本研究设计与执行流程',x+12,290,W-24,28,{size:20,bold:true,fill:C.slate});}
    node(s,L,323,240,92,'局部责任排序','匿名步骤结构\n任务内成对学习');
    node(s,L+266,323,240,92,'多关系图建模','四类关系分别聚合\n关系增强责任评分');
    s.line(L+120,416,L+120,433,C.blue,2);s.line(L+386,416,L+386,433,C.blue,2);s.line(L+120,433,L+386,433,C.blue,2);s.arrow([[L+253,433],[L+253,445]],C.blue);
    node(s,L,448,W,78,'细粒度完整责任排序','折外分数融合，输出全部步骤的得分与次序 π');
    node(s,R,323,W,83,'诊断引导的计划选择','冻结候选次序，构造同目标前向依赖范围',{color:C.orange});
    s.arrow([[R+253,407],[R+253,432]],C.orange);
    node(s,R,439,W,87,'状态恢复与双边验收','隔离回滚重放，目标恢复且非目标保持才提交',{color:C.orange});
    s.rect(582,398,104,128,'#fff',C.slate,1.3,2);s.arrow([[L+W+1,481],[579,481]],C.slate,2.5);s.arrow([[686,452],[R-15,452],[R-15,365],[R-6,365]],C.slate,2.5);
    s.text('完整排序\n只读传入',589,405,90,64,{size:18.5,bold:true,lineHeight:28,align:'center',fill:C.slate});s.text('结果不回写',589,485,90,30,{size:17.5,align:'center',fill:C.muted});
    s.rect(64,547,177,83,C.light,C.slate,1.3,2);s.text('预期结论\n与贡献',72,560,161,60,{size:23,bold:true,fill:C.slate,lineHeight:30,align:'center'});
    const expected=[['完整责任排序','多关系与局部信息互补，\n提高全步骤排序质量'],['诊断与恢复衔接','诊断信息结合恢复选择，\n提高有限预算下的恢复效用'],['可验证状态恢复','依赖范围与双边验收配合，\n提高恢复成功率并控制回归']];
    expected.forEach(([h,b],i)=>{const x=252+i*322;s.rect(x,547,314,83,'#fff',i===2?C.orange:C.blue,1.3,2);s.text(h,x+10,550,294,28,{size:20.5,bold:true,fill:i===2?C.orange:C.blue});s.text(b,x+10,580,294,49,{size:18,lineHeight:24});});
    s.caption('图1  多关系图建模支持的细粒度责任排序与状态恢复框架',641);
  }
  {
    const s=new Slide('2.2 研究问题与目标分解',2);
    s.lead('研究一在失败轨迹上学习完整责任次序，研究二在可执行任务上选择并验证恢复方案。两章共享诊断接口，各自使用独立的评价结果。');
    table(s,'表1  两个研究问题的输入、输出与目标',['研究问题','输入与输出','研究目标'],[
      ['RQ1\n细粒度责任排序','输入：失败轨迹和全体候选步骤\n输出：全部步骤的分数与完整次序','构建多关系步骤图，融合局部与关系信息，提高责任排序质量。'],
      ['RQ2\n状态恢复','输入：冻结诊断记录和可执行状态\n输出：恢复计划与验收后的状态','选择候选和依赖范围，在有限预算内实现目标恢复与非目标保持。']
    ],{y:220,widths:[225,435,444],rowHeights:[130,130],size:22.5});
    s.note('诊断的基本单位是步骤，恢复的操作对象是状态变化。两者通过步骤标识和责任次序对应。',615,37);
  }
  {
    const s=new Slide('2.3 理论概念与本研究设计的对应',2);
    s.lead('文献提供概念定义与方法基础，本研究将其落实为关系构造、全步骤排序和可执行状态干预，分别处理信息不足、次序缺失与恢复副作用。');
    table(s,'表2  概念定义、本研究设计与所解决的问题',['概念及依据','本研究引入的设计','针对的问题'],[
      [`多关系图${cite(11)}\n边具有明确关系类型`,'步骤为节点，四类关系分通道聚合，\n结合局部行为形成责任评分。','单步证据难以利用\n跨步骤结构关联。'],
      [`步骤归因与排序学习${cite(4,12)}\n以相对偏好学习次序`,'对责任步骤和其他候选构造成对监督，\n融合分数后输出全部步骤的排序。','单个判断不能提供\n完整的候选优先级。'],
      [`回滚恢复与无回归${cite(13,9)}\n恢复状态并约束退化`,'诊断引导范围选择，独立重放，\n目标检查和非目标检查共同验收。','局部撤销残留关联错误，\n过度回滚损失正确状态。']
    ],{y:213,widths:[300,475,329],rowHeights:[96,96,96],size:21});
    s.note('四类关系、两轮固定聚合、恢复范围代理及具体验收条件均属于本研究设计。',626,28);
  }
  sections('2.4 研究意义与预期结论',2,
    '本研究以跨步骤责任建模和可验证状态干预为主线，形成责任排序、诊断信息下游效用及状态恢复三方面的预期结论。',[
    ['细粒度责任排序','多关系图补充局部证据，分数融合利用两类信息的互补性，形成全步骤责任次序。该设计提高排序质量与跨任务稳定性。'],
    ['诊断信息的下游效用','诊断信息结合恢复侧候选选择，提高固定预算下的计划选择效率。同候选池的次序对照区分原始完整排序与恢复重排的作用。'],
    ['可验证的状态恢复','依赖约束范围、隔离重放和双边验收共同提高恢复成功率，并控制非目标状态回归，形成可执行且失败可撤销的恢复方法。']
  ],'所有效果句均为明确标注的预期结论。');

  divider(3,'内容与方法','Contents and methods');
  {
    const s=new Slide('3.1 研究问题1：责任排序任务',3);
    s.lead(`研究问题1关注完整失败轨迹中各步骤的诊断优先级。针对局部行为证据难以表达跨步骤关联的问题，本文结合步骤归因${cite(4)}与成对排序学习${cite(12)}，研究完整责任排序方法。`);
    s.section('本研究的任务定义','给定完整失败轨迹，为每个候选步骤估计责任分数，并输出覆盖全部候选的确定次序。细粒度对应执行步骤这一分析单位，完整性对应候选集合的全覆盖。',223,{h:123});
    const n=equation(s,'s<sub>q,i</sub> = f<sub>θ</sub>(T<sub>q</sub>, x<sub>q,i</sub>),     π<sub>q</sub> = argsort<sub>i</sub>(−s<sub>q,i</sub>)',373,{size:30,h:60});
    s.paragraph(`式（${n}）把步骤分数转化为轨迹内的完整次序，用于确定首选及后续候选。模型按现有责任标签学习相对优先级，评价以独立任务上的排序质量为准。`,459,110);
    s.note('监督信息来自标注责任步骤与其他候选的成对关系，未标注候选之间的完整责任等级不作假设。',606,36);
  }
  sections('3.1 研究问题1：两条评分路径',3,
    '本文围绕同一候选步骤构建局部证据评分路径与关系增强评分路径，分别利用步骤自身的行为结构及其跨步骤上下文，再融合得到完整责任次序。',[
    ['局部证据评分路径','根据匿名行为结构与相对位置学习成对责任分数，并结合首选候选提升规则形成局部路径输出。该路径提供不依赖关系图聚合的诊断依据。'],
    ['关系增强评分路径','在相同轨迹上构造四类步骤关系，分类型汇总邻居信息，学习图特征责任分数，再与基础成对分数组合。后文“关系分支”专指这一评分路径。'],
    ['融合排序与方法假设','使用任务组外预测学习两条路径的分数组合。研究假设是跨步骤结构能够补充局部证据，其独立作用通过分支删除和关系置乱对照检验。']
  ]);
  {
    const s=new Slide('3.2 RQ1证据建模：步骤关系图',3);
    s.lead(`多关系图用带类型的边表达对象之间不同性质的联系。文献以有向带类型图表示关系数据，并区分各类关系下的邻域${cite(11)}。`);
    const n=equation(s,'G<sub>q</sub> = (V<sub>q</sub>, E<sub>q</sub>, R),     (v<sub>i</sub>, r, v<sub>j</sub>) ∈ E<sub>q</sub>',221,{size:30,h:61});
    s.paragraph(`式（${n}）定义本文的执行步骤图：节点对应执行步骤，带类型的边表示可观察规则所确定的步骤关联。各关系分别计算邻域表示，以保留不同关联类型的结构信息。`,305,115);
    s.section('本研究的引入方式','采用时序相邻、同匿名角色、同完整结构签名和同非空动作形状四类关系，进行固定邻域聚合，再由成对排序器学习责任评分。该设计为局部步骤补充结构上下文。',455,{h:130});
    s.note('本文采用关系图表示与分类型聚合，聚合阶段无可训练参数，关系边仅具有观察性关联语义。',612,35);
  }
  {
    const s=new Slide('3.2 RQ1证据建模：四类步骤关系',3);
    s.lead('四类关系分别刻画时序、角色和行为结构关联。各关系共享步骤节点集合，通过不同邻接规则形成独立的邻域信息通道。');
    table(s,'表3  本研究的关系构造规则与信息作用',['关系通道','构造规则','为步骤评分补充的信息'],[
      ['时序相邻','连接前一步与后一步','执行顺序中的直接上下文'],
      ['同匿名角色','连接前后最近的同角色步骤','同一角色跨位置的行为关联'],
      ['同完整结构签名','连接前后最近的同结构步骤','结构相似行为的上下文比较'],
      ['同非空动作形状','连接前后最近的同动作形状步骤','结构相似动作的上下文比较']
    ],{y:206,widths:[225,440,439],rowHeights:[68,68,68,68],size:21.5});
    s.note('关系构造仅使用可观察的匿名结构。诊断采用完整失败轨迹，允许利用候选步骤之后的执行信息。',615,38);
  }
  {
    const s=new Slide('3.2 RQ1证据建模：成对责任学习',3);
    s.lead(`成对排序学习以两个候选的相对优先关系训练评分函数${cite(12)}。本文在同一轨迹中比较步骤，使责任判断转化为可学习的次序问题。`);
    s.paragraph('以标注责任步骤与其他候选构造正向差分，交换方向形成反向样本。基础评分使用匿名行为结构与相对位置，不纳入任务名称和具名角色标识。相同的成对学习方式也用于后续图特征评分。',218,121);
    const a=equation(s,'P(y = 1 ∣ Δx) = σ(w<sup>T</sup>Δx + b)',363,{size:32,h:56});
    const b=equation(s,'L = CE<sub>ω</sub>(P, y) + λ ‖w‖<sub>2</sub><sup>2</sup>',435,{size:30,h:56});
    s.paragraph(`式（${a}）估计候选对的责任偏好概率，式（${b}）以交叉熵和正则项学习参数。基础成对分数供两条路径使用，局部路径进一步结合首选候选提升规则形成输出。`,532,113);
  }
  {
    const s=new Slide('3.2 RQ1证据建模：关系信息聚合',3,{source:'四通道两轮固定均值与残差聚合来自本研究协议。图示为当前方法，不是R-GCN网络架构。'});
    s.lead('关系增强路径按关系类型汇总相连步骤的信息。第一轮读取直接相连的步骤，第二轮进一步引入经两条图边可达的上下文，为后续责任评分提供结构特征。',103,86);
    ['时序相邻','同匿名角色','同完整结构','同动作形状'].forEach((a,i)=>{const x=74+i*290;s.rect(x,213,260,40,C.bluePale,C.line,1);s.text(a,x+6,218,248,31,{size:21,bold:true,align:'center',fill:C.blue});});
    node(s,105,285,265,82,'匿名步骤表示','结构特征与相对位置');node(s,508,285,265,82,'第一轮分关系聚合','读取直接邻域');node(s,911,285,265,82,'第二轮分关系聚合','补充二跳上下文');
    s.arrow([[377,326],[493,326]],C.blue);s.arrow([[780,326],[896,326]],C.blue);s.caption('图2  多关系图上的两轮固定邻域聚合',376);
    const a=equation(s,'m<sub>i,r</sub><sup>(l)</sup> = mean<sub>j ∈ N_r(i)</sub> h<sub>j</sub><sup>(l−1)</sup>',424,{size:29,h:54});
    const b=equation(s,'h<sub>i</sub><sup>(l)</sup> = h<sub>i</sub><sup>(l−1)</sup> + ∑<sub>r ∈ R</sub> m<sub>i,r</sub><sup>(l)</sup>,    l = 1, 2',488,{size:28,h:56});
    s.text(`式（${a}）按关系计算邻域均值，式（${b}）通过残差连接更新节点表示。各轮关系表示共同构成排序特征。聚合过程不学习参数，空邻域以零向量表示。`,88,567,1104,88,{size:22,lineHeight:32});
  }
  {
    const s=new Slide('3.3 RQ1融合排序：完整诊断输出',3);
    s.lead('局部路径输出经过首选提升的责任分数，关系增强路径组合基础成对分数与图特征分数。本文进一步学习两条路径的融合函数，形成全部候选的责任次序。');
    s.section('本研究设计：以任务组外预测构造融合输入','任务组外预测（Out-of-Fold，OOF）保证每条训练轨迹的分支分数来自未见过该任务组的模型。融合器学习两类分数及其差异、交互信息，减少拟合内评分造成的偏差。',222,{h:126});
    const n=equation(s,'s<sub>q,i</sub><sup>final</sup> = F<sub>φ</sub>(s<sub>q,i</sub><sup>local</sup>, s<sub>q,i</sub><sup>rel</sup>, ψ<sub>q,i</sub>)',373,{size:31,h:61});
    s.paragraph(`式（${n}）将互补证据映射到统一责任分数，再按式（1）输出全部步骤。方法保留确定性的并列处理规则，并用分支删除与关系置乱检验信息来源的作用。`,459,118);
    s.note('外层测试任务不参与特征选择、参数估计或融合调整。恢复结果也不反向修改责任评分。',613,35);
  }
  sections('3.3 RQ1融合排序：诊断与恢复接口',3,
    '完整责任次序确定优先检查哪些步骤，但恢复执行仍需决定干预哪些状态以及如何判断恢复有效。两项研究通过只读诊断记录衔接，各自承担独立决策。',[
    ['研究问题1的输出','为每条轨迹导出任务标识、步骤标识、责任分数及确定性名次。该记录保持全步骤覆盖，不包含恢复操作，也不直接规定状态干预范围。'],
    ['研究问题2的输入与新增决策','恢复侧将步骤标识映射到可执行的状态锚点，生成带范围和验收条件的候选计划。在有限尝试预算内，进一步确定计划次序与干预范围。'],
    ['接口约束与联合验证','恢复结果不回写责任评分。直接采用原始完整次序与恢复侧重排分别设置对照，以区分诊断信息的下游效用和恢复选择机制的增量作用。']
  ]);
  {
    const s=new Slide('3.4 研究问题2：诊断引导的恢复决策',3);
    s.lead('研究问题2以只读责任次序和可执行状态记录为输入，研究有限预算下的恢复计划选择。目标是在修复目标状态的同时保持非目标状态，解决诊断优先级到状态干预的转换问题。');
    s.section('恢复对象与理论依据',`回滚恢复以检查点和事件记录支持重新执行${cite(13)}。本文在软件工具环境中恢复文件与仓库状态，各候选从相同基准启动，保留调用位置，仅抑制选定的状态增量。`,224,{h:122});
    s.section('诊断引导的状态干预','以诊断步骤作为恢复锚点，依据同目标前向关联构造干预范围。执行器独立尝试各候选计划，以目标探针和非目标状态检查共同决定接受或撤销。',367,{h:120});
    s.section('针对的问题','过小的范围可能留下关联错误，过大的范围可能破坏正确工作。隔离重放与联合验收使不同恢复范围可比较，并阻止失败候选的残留影响后续尝试。',509,{h:120});
  }
  sections('3.4 研究问题2：恢复候选次序',3,
    '责任分数表示步骤级诊断优先级，恢复选择进一步利用训练任务中的候选执行信息。两者通过只读接口衔接，以受控次序对照评价各自的恢复效用。',[
    ['直接采用责任次序','将诊断步骤映射为恢复候选，按原始责任名次确定尝试顺序，不使用恢复侧评分重新排列。该路线用于检验完整诊断次序本身的下游作用。'],
    ['恢复侧候选选择','分别评价直接使用完整责任次序，以及保留诊断首位、按训练任务候选后验安排其余候选的路线。恢复侧重排的收益单独统计。'],
    ['测试前冻结执行次序','候选顺序在测试结果揭示前固定。执行失败触发撤销并继续下一候选，不依据当前测试任务结果在线重排。同池次序对照共享执行预算与验收器。']
  ]);
  {
    const s=new Slide('3.4 研究问题2：计划表示与预算',3);
    s.lead('本文将恢复计划定义为诊断锚点、干预范围、执行操作与验收条件构成的四元组，建立步骤级责任排序与可执行状态干预的对应关系。');
    const a=equation(s,'p<sub>k</sub> = (a<sub>k</sub>, S<sub>k</sub>, o<sub>k</sub>, V<sub>k</sub>)',224,{size:32,h:62});
    s.paragraph(`式（${a}）将锚点与状态操作对应。范围规则仅使用可观察信息，候选生成阶段不根据测试成功结果筛选计划。`,311,92);
    const b=equation(s,'|A<sub>q</sub>| ≤ B',446,{size:34,h:62});
    s.paragraph(`式（${b}）限定每项任务的实际尝试数。执行器按冻结次序依次尝试，通过验收即停止，失败则撤销并继续，直到预算耗尽。固定预算使不同次序的恢复效用能够公平比较。`,532,115);
  }
  {
    const s=new Slide('3.5 RQ2状态干预：依赖范围',3);
    s.lead('本文采用同目标前向关联作为状态依赖的操作性代理，以候选锚点为起点构造联合干预范围。范围设计同时考虑关联错误残留与非目标状态保持。',103,87);
    const n=equation(s,'C<sup>+</sup>(a) = {v ∈ V<sub>state</sub> ∣ κ(v) = κ(a), call(v) ≥ call(a)}',209,{size:27,h:60});
    s.text(`式（${n}）生成锚点及同目标后续合格增量的集合。该规则描述可观察状态关联，不代表完整程序依赖分析。`,88,282,1104,63,{size:22.5,lineHeight:32});
    table(s,'表4  恢复范围与作用对照',['范围','干预规则','比较作用'],[
      ['单点范围','仅处理锚点对应状态增量','最小干预基线'],
      ['等规模前向范围','匹配处理数量，保持向前顺序','分析扩大范围的作用'],
      ['同目标依赖范围','处理锚点及同目标前向增量','分析依赖身份的增量作用']
    ],{y:359,widths:[225,485,394],rowHeights:[62,62,62],size:21});
  }
  {
    const s=new Slide('3.5 RQ2状态干预：隔离重放',3);
    s.lead('每个恢复候选从一致检查点或全新工作副本开始。选定范围决定抑制哪些状态增量，其余调用按原有位置继续执行。');
    const xs=[73,371,669,967];
    node(s,xs[0],237,239,100,'共同基准状态','独立克隆或检查点',{color:C.orange});node(s,xs[1],237,239,100,'按计划重放','抑制选定状态增量',{color:C.orange});node(s,xs[2],237,239,100,'双边验收','目标与非目标检查',{color:C.orange});node(s,xs[3],237,239,100,'接受或撤销','通过保留，失败撤销',{color:C.orange});
    for(let i=0;i<3;i++)s.arrow([[xs[i]+245,287],[xs[i+1]-12,287]],C.orange);
    s.arrow([[1087,338],[1087,385],[193,385],[193,344]],C.slate,1.8,'6 5');s.text('失败后撤销，下一候选重新从共同基准开始',350,360,610,28,{size:19,align:'center',fill:C.slate});s.caption('图3  独立重放、联合验收与失败撤销',404);
    s.section('候选隔离与执行起点控制','各候选使用独立工作副本，调用索引和控制流保持一致。统一执行起点消除前序候选残留状态的影响，为比较候选次序和干预范围提供受控条件。',466,{h:122});
    s.note('执行冲突显式中止。没有合格状态节点时弃权，空操作不计为成功恢复。',610,36);
  }
  {
    const s=new Slide('3.5 RQ2状态干预：无回归验收',3);
    s.lead(`STRATUS以事务无回归（Transactional No-Regression，TNR）约束可观察状态的恶化，并在假设成立时撤销失败操作${cite(9)}。本文据此设计可检查的恢复验收条件。`);
    const a=equation(s,'TNR(p) = NonTargetEqual(p) ∧ GitDiffOK(p) ∧ NoNewConflict(p)',241,{size:25,h:62});
    s.paragraph(`式（${a}）定义本文的非目标无回归判据，联合检查非目标状态一致性、差分合规性和新增冲突。验收覆盖范围限定于上述可观测软件状态，安全性结论以本研究的执行证据为准。`,324,111);
    const b=equation(s,'Success(p) = Accepted(p) ∧ TargetProbe(p) ∧ TNR(p)',468,{size:27,h:61});
    s.paragraph(`式（${b}）同时要求执行有效、目标恢复和非目标保持。全部满足才接受候选状态，否则撤销并继续，避免目标通过掩盖其他状态的退化。`,550,95);
  }
  {
    const s=new Slide('3.6 RQ1与RQ2的验证设计',3);
    s.lead('实验分别改变候选次序与干预范围，通过受控对照评价责任排序、范围规模和依赖身份的作用。组合方法的总体收益与单项设计的增量效应分别报告。');
    table(s,'表5  候选次序与恢复范围的控制变量设计',['比较轴','改变的条件','保持一致的条件'],[
      ['候选次序','原始完整排序、恢复后验次序、\n固定与置乱次序','任务、候选池、预算、执行与验收'],
      ['范围规模','单点范围与等规模前向范围','锚点、排序、预算、执行与验收'],
      ['依赖身份','等规模前向范围与同目标范围','排序、处理数量、预算、执行与验收']
    ],{y:214,widths:[195,439,470],rowHeights:[104,82,82],size:21.5});
    s.note('RQ1独立评价全步骤排序质量，RQ2和桥接实验评价恢复成功、非目标回归与执行成本。',615,36);
  }
  // The three-chapter excerpt includes the sources it cites, without waiting for chapter six.
  const groups=[REFERENCES.slice(0,5),REFERENCES.slice(5,9),REFERENCES.slice(9,13),REFERENCES.slice(13)];
  groups.forEach((refs,index)=>{
    const s=new Slide(`前三章引用文献（${index+1}/${groups.length}）`,3,{source:'条目按本演示稿编号；点击题名可打开论文。经典文献用于概念定义，当前方法设计由本研究协议规定。'});
    const rowH=refs.length===5?109:132;
    refs.forEach((r,i)=>{
      const y=103+i*rowH;
      s.text(`[${r.id}] ${r.authors}`,88,y,1104,31,{size:18,bold:true,lineHeight:24});
      const titleLines=layout(r.title,1104,20).length;
      s.text(`<a href="${r.url}">${r.title}</a>`,88,y+27,1104,titleLines*26,{size:20,lineHeight:26,fill:C.blue});
      s.text(`${r.venue}。研究关联：${r.use}。`,88,y+30+titleLines*26,1104,29,{size:17,lineHeight:23,fill:C.slate});
    });
  });
}
