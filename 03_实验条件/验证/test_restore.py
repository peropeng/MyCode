"""用合成文件验证恢复边界，不访问网络、数据集或真实密钥。"""
from pathlib import Path
import base64, importlib.util, io, json, os, tarfile, tempfile, unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[2]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

restore=load('restore_fixture',ROOT/'03_实验条件/restore.py')
create=load('archive_fixture',ROOT/'06_实验记录/create_archive.py')

class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name)
        self.key=os.urandom(32);self.keyfile=self.base/'key.json'
        self.keyfile.write_text(json.dumps({'key':base64.b64encode(self.key).decode()}),encoding='utf-8')

    def test_real_seal_and_restore_preserve_multiblock_bytes(self):
        source=self.base/'source';source.write_bytes(os.urandom(5*1024*1024))
        encrypted=self.base/'sealed';create.seal_file(source,encrypted,self.key)
        target=self.base/'restored';restore.unseal(encrypted,target,self.keyfile)
        self.assertEqual(restore.digest(source),restore.digest(target))

    def test_tampered_archive_does_not_publish_plaintext(self):
        from cryptography.exceptions import InvalidTag
        source=self.base/'source';source.write_bytes(b'fixture')
        encrypted=self.base/'sealed';create.seal_file(source,encrypted,self.key)
        raw=bytearray(encrypted.read_bytes());raw[-1]^=1;encrypted.write_bytes(raw)
        target=self.base/'restored'
        with self.assertRaises(InvalidTag):restore.unseal(encrypted,target,self.keyfile)
        self.assertFalse(target.exists())

    def test_truncated_archive_requires_authenticated_ending(self):
        source=self.base/'source';source.write_bytes(b'fixture')
        encrypted=self.base/'sealed';create.seal_file(source,encrypted,self.key)
        encrypted.write_bytes(encrypted.read_bytes()[:-20])
        with self.assertRaises(ValueError):restore.unseal(encrypted,self.base/'restored',self.keyfile)

    def test_archive_cannot_escape_destination(self):
        archive=self.base/'fixture.tar'
        with tarfile.open(archive,'w') as f:
            info=tarfile.TarInfo('../escape');info.size=1;f.addfile(info,io.BytesIO(b'x'))
        with self.assertRaises(ValueError):restore.extract(archive,self.base/'target')
        self.assertFalse((self.base/'escape').exists())

    def test_different_existing_file_is_never_overwritten(self):
        archive=self.base/'fixture.tar'
        with tarfile.open(archive,'w') as f:
            info=tarfile.TarInfo('file.txt');info.size=3;f.addfile(info,io.BytesIO(b'new'))
        target=self.base/'target';target.mkdir();(target/'file.txt').write_bytes(b'old')
        with self.assertRaises(RuntimeError):restore.extract(archive,target)
        self.assertEqual((target/'file.txt').read_bytes(),b'old')

    def test_interrupted_member_write_leaves_no_partial_final_file(self):
        archive=self.base/'fixture.tar'
        with tarfile.open(archive,'w') as f:
            info=tarfile.TarInfo('file.txt');info.size=3;f.addfile(info,io.BytesIO(b'new'))
        target=self.base/'target'
        def interrupt(source,out):
            out.write(b'n');raise OSError('合成磁盘写入失败')
        with mock.patch.object(restore.shutil,'copyfileobj',side_effect=interrupt):
            with self.assertRaises(OSError):restore.extract(archive,target)
        self.assertFalse((target/'file.txt').exists())
        restore.extract(archive,target)
        self.assertEqual((target/'file.txt').read_bytes(),b'new')

    def test_interrupted_cache_copy_can_be_retried_without_partial_final(self):
        source=self.base/'source.tar';source.write_bytes(b'synthetic input')
        target=self.base/'target.tar'
        def interrupt(inp,out):
            out.write(b's');raise OSError('合成复制中断')
        with mock.patch.object(restore.shutil,'copyfileobj',side_effect=interrupt):
            with self.assertRaises(OSError):restore.publish_copy(source,target)
        self.assertFalse(target.exists())
        restore.publish_copy(source,target)
        self.assertEqual(target.read_bytes(),source.read_bytes())

    def test_case_relocation_keeps_historical_text_and_resets_observation(self):
        relocate=load('relocate_fixture',ROOT/'05_实验代码/故障恢复/relocate_case.py')
        original={'business_root':'D:/Code/毕设/02_工作区/data',
                  'ref':{'task_path':'D:/Code/毕设/02_工作区/task','mapping':[{'text':'原始D:/Code/毕设/历史文本'}]},
                  'initial_validation':'D:/Code/毕设/旧观察.json','python':'old-python'}
        result=relocate.build_view(original,self.base/'project',self.base/'python')
        self.assertEqual(result['ref']['mapping'],original['ref']['mapping'])
        self.assertNotIn('initial_validation',result)
        self.assertIn('initial_validation',original)
        self.assertEqual(Path(result['business_root']),self.base/'project/02_工作区/data')

if __name__=='__main__':unittest.main()
