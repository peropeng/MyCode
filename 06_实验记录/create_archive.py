"""为后续实验创建完整原件档案和加密发布副本，不修改输入文件。"""
from pathlib import Path
import argparse, base64, hashlib, json, os, struct, tarfile, tempfile

ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def seal_file(source,target,key):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aes=AESGCM(key);prefix=os.urandom(8);counter=0
    with Path(source).open('rb') as inp,Path(target).open('xb') as out:
        out.write(b'MYCODE01'+prefix)
        while True:
            raw=inp.read(4*1024*1024)
            data=aes.encrypt(prefix+counter.to_bytes(4,'big'),raw,b'MyCode/recovery/v1')
            out.write(struct.pack('>I',len(data)));out.write(data);counter+=1
            if not raw:break

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path,help='已停止运行、准备封存的完整实验目录')
    parser.add_argument('--output',required=True,type=Path,help='忽略目录中的输出加密附件路径')
    parser.add_argument('--key-file',required=True,type=Path,help='本地解密凭据路径，不是API Key')
    parser.add_argument('--new-key',action='store_true',help='明确创建新的随机密钥，旧附件仍需保留旧密钥')
    args=parser.parse_args();source=args.input.resolve();target=args.output.resolve();keypath=args.key_file.resolve()
    if not source.is_dir():parser.error('输入不是目录')
    if target.is_relative_to(source):parser.error('输出不能放在待封存目录内部')
    for p in [target,keypath]:
        if p.is_relative_to(ROOT) and not any(p.is_relative_to(ROOT/n) for n in ['本地配置','本地恢复']):
            parser.error('仓库内输出只能放在本地配置或本地恢复忽略目录')
    if args.new_key:
        keypath.parent.mkdir(parents=True,exist_ok=True)
        with keypath.open('x',encoding='utf-8') as f:json.dump({'format':'MyCode/recovery/v1','key':base64.b64encode(os.urandom(32)).decode()},f)
    key=base64.b64decode(json.loads(keypath.read_text(encoding='utf-8'))['key'])
    target.parent.mkdir(parents=True,exist_ok=True);records=[]
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        archive=Path(tmp)/'original.tar.gz'
        with tarfile.open(archive,'w:gz',compresslevel=3) as out:
            for d,dirs,files in os.walk(source):
                dirs[:]=sorted(v for v in dirs if v not in ['.git','.venv','__pycache__','.pytest_cache'])
                for name in sorted(files):
                    p=Path(d)/name
                    if p.is_symlink():raise ValueError('符号链接需要单独核定，未封存')
                    relative=p.relative_to(source).as_posix();before=sha(p)
                    out.add(p,arcname=source.name+'/'+relative,recursive=False)
                    if sha(p)!=before:raise RuntimeError('归档期间输入变化，先停止运行再封存')
                    records.append({'path':relative,'size':p.stat().st_size,'sha256':before})
        original_size=archive.stat().st_size;original_hash=sha(archive);seal_file(archive,target,key)
    receipt={'format':'MyCode/recovery/v1','archive_size':original_size,'archive_sha256':original_hash,
             'encrypted_size':target.stat().st_size,'encrypted_sha256':sha(target),'strip_prefix':source.name,
             'files':records,'API_requests':0}
    with target.with_suffix(target.suffix+'.manifest.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
    print(json.dumps({'files':len(records),'encrypted_archive':str(target),'API_requests':0},ensure_ascii=False))

if __name__=='__main__':main()
