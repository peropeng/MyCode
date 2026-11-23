"""按固定来源下载当前三个数据集，不解析数据、训练或读取评价标签。"""
from pathlib import Path
import argparse, hashlib, json, shutil, urllib.request

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name',help='来源清单中的资源名称；省略时只列名称')
    parser.add_argument('--filename',help='只下载所选资源的一个文件')
    args=parser.parse_args()
    rows=json.loads((ROOT/'01_实验/03_数据集/来源与下载.json').read_text(encoding='utf-8'))['datasets']
    if not args.name:
        print('\n'.join(r['name'] for r in rows));return
    row=next((r for r in rows if r['name']==args.name),None)
    if row is None:parser.error('资源不存在，请先列出名称')
    files=[v for v in row['downloads'] if not args.filename or v['filename']==args.filename]
    if not files:parser.error('文件名不存在')
    folder=ROOT/'04_工作区/数据'/args.name.replace('/','_');folder.mkdir(parents=True,exist_ok=True)
    for item in files:
        if Path(item['filename']).name!=item['filename']:raise ValueError('下载文件名不安全')
        target=folder/item['filename'];temporary=target.with_suffix(target.suffix+'.download')
        if not target.exists():
            with urllib.request.urlopen(urllib.request.Request(item['url'],headers={'User-Agent':'MyCode-data-source'}),timeout=180) as r,temporary.open('wb') as f:shutil.copyfileobj(r,f)
            if item.get('sha256'):
                with temporary.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
                if actual!=item['sha256']:raise RuntimeError('固定资源校验失败，保留下载副本')
            temporary.replace(target)
        with target.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
        if item.get('sha256') and actual!=item['sha256']:raise RuntimeError('已有文件与固定资源不一致')
        receipt={'name':row['name'],'version':row['version'],'url':item['url'],'size':target.stat().st_size,'sha256':actual,'original_hash_verified':bool(item.get('sha256')),'labels_parsed':False}
        target.with_suffix(target.suffix+'.receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('已取得：'+item['filename'])

if __name__=='__main__':main()
