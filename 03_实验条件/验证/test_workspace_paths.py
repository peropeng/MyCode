"""以合成文件核对活跃工具只向新的本地工作区写入。"""
from pathlib import Path
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)

    def test_code_restore_uses_workspace_recovery(self):
        restore = load('workspace_restore_fixture', '03_实验条件/restore.py')
        archive = self.base / 'synthetic.tar'
        with tarfile.open(archive, 'w') as stream:
            member = tarfile.TarInfo('原始项目/02_工作区/01_工程/fixture.txt')
            member.size = 7
            stream.addfile(member, io.BytesIO(b'fixture'))
        catalog = self.base / '06_实验记录/恢复清单.json'
        catalog.parent.mkdir()
        catalog.write_text(json.dumps({'public_code': {'sha256': restore.digest(archive)},
                                       'protected_archives': []}), encoding='utf-8')
        with mock.patch.object(restore, 'ROOT', self.base), mock.patch.object(sys, 'argv', [
                'restore.py', '--code', '--archive-file', str(archive)]), \
                mock.patch.object(restore, 'download', side_effect=AssertionError('不应下载')), \
                contextlib.redirect_stdout(io.StringIO()):
            restore.main()
        self.assertEqual((self.base / '工作区/恢复/原始项目/02_工作区/01_工程/fixture.txt').read_bytes(), b'fixture')
        self.assertFalse((self.base / '本地恢复').exists())

    def test_dataset_download_uses_workspace_data(self):
        fetch = load('workspace_fetch_fixture', '04_数据集/fetch_data.py')
        catalog = self.base / '04_数据集/来源与下载.json'
        catalog.parent.mkdir()
        catalog.write_text(json.dumps({'datasets': [{'name': '合成来源', 'version': 'synthetic',
            'downloads': [{'filename': 'fixture.txt', 'url': 'https://example.invalid/fixture',
                           'sha256': hashlib.sha256(b'fixture').hexdigest()}]}]}), encoding='utf-8')
        with mock.patch.object(fetch, 'ROOT', self.base), mock.patch.object(sys, 'argv', [
                'fetch_data.py', '--name', '合成来源']), \
                mock.patch.object(fetch.urllib.request, 'urlopen', return_value=io.BytesIO(b'fixture')), \
                contextlib.redirect_stdout(io.StringIO()):
            fetch.main()
        self.assertEqual((self.base / '工作区/数据/合成来源/fixture.txt').read_bytes(), b'fixture')

    def test_ranking_fallback_uses_workspace_recovery_engine(self):
        ranking = load('workspace_ranking_fixture', '05_实验代码/根因排序/run_ranking.py')
        engine = self.base / '工作区/恢复/原始项目/02_工作区/01_工程'
        engine.mkdir(parents=True)
        with mock.patch.object(ranking, 'ROOT', self.base), mock.patch.object(sys, 'argv', [
                'run_ranking.py', '--python', sys.executable]), mock.patch.object(ranking.subprocess, 'run') as run:
            ranking.main()
        self.assertEqual(run.call_args.kwargs['cwd'], engine)

    def test_archive_allows_workspace_output_and_private_key(self):
        create = load('workspace_archive_fixture', '06_实验记录/create_archive.py')
        source = self.base / 'synthetic-source'
        source.mkdir()
        (source / 'fixture.txt').write_bytes(b'fixture')
        keyfile = self.base / '工作区/私有配置/synthetic.json'
        keyfile.parent.mkdir(parents=True)
        keyfile.write_text(json.dumps({'key': base64.b64encode(b'x' * 32).decode()}), encoding='utf-8')
        target = self.base / '工作区/封存/synthetic.enc'
        with mock.patch.object(create, 'ROOT', self.base), mock.patch.object(sys, 'argv', [
                'create_archive.py', '--input', str(source), '--output', str(target), '--key-file', str(keyfile)]), \
                contextlib.redirect_stdout(io.StringIO()):
            create.main()
        self.assertTrue(target.is_file())
        self.assertTrue(target.with_suffix('.enc.manifest.json').is_file())

    def test_archive_rejects_output_in_shared_research_directories(self):
        create = load('workspace_archive_reject_fixture', '06_实验记录/create_archive.py')
        source = self.base / 'synthetic-source'
        source.mkdir()
        target = self.base / '06_实验记录/forbidden.enc'
        with mock.patch.object(create, 'ROOT', self.base), mock.patch.object(sys, 'argv', [
                'create_archive.py', '--input', str(source), '--output', str(target),
                '--key-file', str(self.base / '工作区/私有配置/key.json')]), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                create.main()
        self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
