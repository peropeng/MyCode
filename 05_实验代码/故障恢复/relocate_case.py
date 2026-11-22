"""创建路径重定位的公开运行视图，不修改历史原件或重新启动终态。"""
from pathlib import Path
import argparse, copy, hashlib, json, re

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'本地恢复/原始项目'
PATH_FIELDS=['business_root','support_root','public_view','frozen_root','pack','ranking_plan',
             'native_harness','original_contract','new_information_policy']
REF_FIELDS=['task_path','asset_root','G_frozen_plan']

def relocate_path(value,project):
    normalized=value.replace('\\','/')
    for prefix in ['D:/Code/毕设/graduate-thesis-experiments/','D:/Code/毕设/']:
        if normalized.startswith(prefix):return str(project/normalized[len(prefix):])
    raise ValueError('不能确认路径来源，不猜测映射：'+value)

def build_view(original,project,python):
    view=copy.deepcopy(original)
    for field in PATH_FIELDS:
        if field in view and isinstance(view[field],str):view[field]=relocate_path(view[field],project)
    for field in REF_FIELDS:
        if field in view['ref']:view['ref'][field]=relocate_path(view['ref'][field],project)
    view['python']=str(python)
    # 新主机必须重新观察公开C0，历史反馈仍在档案中，不改写其内容。
    view.pop('initial_validation',None)
    return view

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',required=True,help='原任务ID，仅作来源追溯')
    parser.add_argument('--python',required=True,type=Path,help='已重建的对应native环境解释器')
    parser.add_argument('--output',required=True,type=Path,help='本地恢复目录下的新case.json路径')
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.task):parser.error('任务标识不安全')
    source=PROJECT/'02_工作区/01_工程/.rebuild/rq2-controls/selection'/args.task/'case.json'
    if not source.is_file():parser.error('先恢复完整研究档案，缺少原case')
    if not args.python.is_file():parser.error('先重建对应native环境')
    target=args.output.resolve()
    if not target.is_relative_to(ROOT/'本地恢复'):parser.error('输出必须位于本地恢复忽略目录')
    original=json.loads(source.read_text(encoding='utf-8'));view=build_view(original,PROJECT,args.python.resolve())
    required=[view[k] for k in PATH_FIELDS if k in view and k!='new_information_policy']
    required += [view['ref'][k] for k in REF_FIELDS if k in view['ref']]
    missing=[v for v in required if not Path(v).exists()]
    if missing:raise FileNotFoundError('原件尚未全部恢复：'+json.dumps(missing,ensure_ascii=False))
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as f:json.dump(view,f,ensure_ascii=False,indent=2)
    receipt={'original_case_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'new_case_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
             'historical_original_unchanged':True,'initial_public_observation_required':True,
             'reuse_completed_trial_for_new_generation':False,'API_requests':0,'task_tests_run':0}
    with target.with_suffix('.relocation.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
    print(json.dumps({'new_case':str(target),'next':'重新核定环境与公开C0；新条件使用新trial，不启动旧终态','API_requests':0},ensure_ascii=False))

if __name__=='__main__':main()
