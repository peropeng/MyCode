"""下载和校验研究原件；不运行训练、生成请求或测试集评价。"""
from pathlib import Path, PurePosixPath
import argparse, base64, hashlib, json, os, shutil, struct, tarfile, tempfile, urllib.request

ROOT=Path(__file__).resolve().parents[1]


def local_key(explicit=None):
    """只使用研究者明确传入或本机已保存的凭据，不访问在线密钥来源。"""
    path=explicit if explicit is not None else ROOT/'09_工作区/私有配置/mycode-recovery-key.json'
    return path if path.is_file() else None

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def safe(base,name):
    value=PurePosixPath(name)
    if value.is_absolute() or '\\' in name or ':' in name or '..' in value.parts:raise ValueError('归档路径不安全')
    out=(base/name).resolve()
    if not out.is_relative_to(base.resolve()):raise ValueError('归档路径越界')
    return out

def download(url,path,expected):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        temp=path.with_suffix(path.suffix+'.download')
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MyCode-recovery'}),timeout=180) as r,temp.open('wb') as f:shutil.copyfileobj(r,f)
        if digest(temp)!=expected:raise RuntimeError('下载文件校验失败，保留临时文件供诊断')
        temp.replace(path)
    if digest(path)!=expected:raise RuntimeError('缓存文件不匹配')
    return path

def unseal(source,target,keyfile):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key=base64.b64decode(json.loads(keyfile.read_text(encoding='utf-8'))['key'])
    aes=AESGCM(key)
    if target.exists():return
    temporary=target.with_suffix(target.suffix+'.decrypting')
    with source.open('rb') as src,temporary.open('wb') as out:
        if src.read(8)!=b'MYCODE01':raise ValueError('加密格式不识别')
        prefix=src.read(8);counter=0
        while True:
            size=src.read(4)
            if len(size)!=4:raise ValueError('加密附件不完整')
            length=struct.unpack('>I',size)[0]
            if not 16<=length<=8*1024*1024:raise ValueError('分块长度异常')
            block=src.read(length)
            data=aes.decrypt(prefix+counter.to_bytes(4,'big'),block,b'MyCode/recovery/v1');counter+=1
            if not data:
                if src.read(1):raise ValueError('加密附件尾部异常')
                break
            out.write(data)
    temporary.replace(target)


def publish_copy(source,target):
    """完整写入后才发布原件路径；中断不留下同名残缺缓存。"""
    temporary=None
    try:
        with source.open('rb') as stream,tempfile.NamedTemporaryFile(dir=target.parent,prefix='.恢复-',delete=False) as out:
            temporary=Path(out.name);shutil.copyfileobj(stream,out);out.flush();os.fsync(out.fileno())
        os.link(temporary,target)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)

def extract(archive,base,prefix=''):
    count=0
    with tarfile.open(archive,'r:*') as src:
        for member in src:
            if member.isdir():continue
            if not member.isfile():raise ValueError('不接受链接或设备文件')
            name=member.name
            if prefix:
                if not name.startswith(prefix+'/'):raise ValueError('归档成员不在指定前缀内')
                name=name[len(prefix)+1:]
            target=safe(base,name);target.parent.mkdir(parents=True,exist_ok=True)
            with src.extractfile(member) as stream:
                if target.exists():
                    h=hashlib.sha256()
                    for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
                    if digest(target)!=h.hexdigest():raise RuntimeError('同名原件不同，不覆盖：'+name)
                else:
                    temporary=None
                    try:
                        with tempfile.NamedTemporaryFile(dir=target.parent,prefix='.恢复-',delete=False) as f:
                            temporary=Path(f.name);shutil.copyfileobj(stream,f);f.flush();os.fsync(f.fileno())
                        os.link(temporary,target)
                    finally:
                        if temporary is not None:temporary.unlink(missing_ok=True)
            count+=1
    return count

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code',action='store_true',help='恢复公开代码原件与现有回放模型')
    parser.add_argument('--history',nargs='*',help='指定原件附件名；不列名称时恢复全部受保护附件')
    parser.add_argument('--key-file',type=Path,help='本机解密密钥；省略时使用09_工作区/私有配置/mycode-recovery-key.json现存文件')
    parser.add_argument('--archive-file',type=Path,help='离线使用已下载的代码附件')
    args=parser.parse_args()
    catalog=json.loads((ROOT/'06_实验记录/恢复清单.json').read_text(encoding='utf-8'))
    work=ROOT/'09_工作区/恢复';cache=work/'下载';engine=work/'原始项目/02_工作区/01_工程'
    if args.code:
        row=catalog['public_code'];path=args.archive_file or download(row['url'],cache/'current-code.tar.gz',row['sha256'])
        if digest(path)!=row['sha256']:raise RuntimeError('代码附件校验失败')
        print(json.dumps({'restored_files':extract(path,work),'new_experiments':0},ensure_ascii=False))
    if args.history is not None:
        keyfile=local_key(args.key_file)
        if keyfile is None:parser.error('缺少本机解密凭据；用--key-file指定，或先导入09_工作区/私有配置/mycode-recovery-key.json，密钥不能提交到公开仓库')
        if not engine.is_dir():parser.error('先使用--code恢复代码原件')
        names=args.history or [r['name'] for r in catalog['protected_archives']]
        for name in names:
            row=next((r for r in catalog['protected_archives'] if r['name']==name),None)
            if row is None:parser.error('未知附件名称：'+name)
            encrypted=download(row['url'],cache/(name+'.enc'),row['encrypted_sha256'])
            raw=cache/name;unseal(encrypted,raw,keyfile)
            if digest(raw)!=row['sha256']:raise RuntimeError('解密后的原件不匹配')
            parent=work/'原始项目' if row.get('restore_location','').startswith('project-') else engine
            base=safe(parent,row['restore_to']);base.mkdir(parents=True,exist_ok=True)
            if name=='current-inputs-full.tar':
                target=base/name
                if target.exists() and digest(target)!=row['sha256']:raise RuntimeError('已有资源包不同')
                if not target.exists():publish_copy(raw,target)
            else:extract(raw,base,row['strip_prefix'])
            print(json.dumps({'restored_archive':name,'new_experiments':0},ensure_ascii=False))
    if not args.code and args.history is None:
        print(json.dumps({'public_code':catalog['public_code']['url'],'protected_archives':[r['name'] for r in catalog['protected_archives']]},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
