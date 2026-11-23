"""以合成清单验证依赖门禁，不读取真实密钥、模型或任务数据。"""
from pathlib import Path
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import tarfile
import tempfile
import unittest
import zlib
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare = load('prepare_fixture', ROOT / '03_实验条件/prepare_dependencies.py')
restore = load('local_restore_fixture', ROOT / '03_实验条件/restore.py')


class DependencyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.engine = self.base / 'engine'
        (self.engine / 'tools').mkdir(parents=True)
        frozen = ROOT / '05_实验代码/工程原件/02_工作区/01_工程/tools'
        for name in ['restore_archive.py', 'restore_current_method.py']:
            shutil.copyfile(frozen / name, self.engine / 'tools' / name)
        (self.engine / 'manifests/archive').mkdir(parents=True)
        (self.engine / 'verification').mkdir()
        self.git_data = b'fixture git original\n'
        self.git_id = hashlib.sha256(self.git_data).hexdigest()
        self.git_path = self.engine / 'reproduction/fixture.txt'
        self.git_path.parent.mkdir()
        self.git_path.write_bytes(self.git_data)
        self.asset_data = b'fixture packed input\n'
        self.asset_id = hashlib.sha256(self.asset_data).hexdigest()
        self.cache = self.engine / '.restore-cache/current-inputs-full.tar'
        self.cache.parent.mkdir()
        packed = zlib.compress(self.asset_data)
        with tarfile.open(self.cache, 'w') as archive:
            member = tarfile.TarInfo('fixture.zpart')
            member.size = len(packed)
            archive.addfile(member, io.BytesIO(packed))
        asset = {'name': self.cache.name, 'sha256': prepare.digest(self.cache), 'size': self.cache.stat().st_size}
        self.index = {
            'repository': 'peropeng/graduate-thesis', 'release_tag': 'unused',
            'git_snapshot_commit': 'must-never-fetch',
            'object_maps': ['manifests/archive/objects.jsonl.gz'],
            'assets': {self.cache.name: asset}, 'statistics': {'object_kinds': {'git': 1}},
        }
        self.objects = {
            self.git_id: {'kind': 'git', 'path': 'reproduction/fixture.txt'},
            self.asset_id: {'kind': 'asset', 'encoding': 'zlib', 'chunks': [
                {'asset': self.cache.name, 'member': 'fixture.zpart'}]},
        }
        self.public = {'protected_archives': [dict(asset)]}
        self.write_catalog()
        files = [{'original_path': 'D:/Code/毕设/graduate-thesis-experiments/' + name, 'sha256': identity}
                 for name, identity in [('实验/git.txt', self.git_id), ('实验/asset.txt', self.asset_id)]]
        for name, value in [
            ('current_legacy_profiles.json', {'ranking': {'files': files}}),
            ('legacy_path_aliases.json', []), ('external_models.json', {'files': []}),
        ]:
            (self.engine / 'manifests' / name).write_text(json.dumps(value), encoding='utf-8')
        # 所有测试一旦尝试进程或网络即失败，包括旧Git与gh回退。
        self.process = self.enterContext(mock.patch('subprocess.run', side_effect=AssertionError('禁止进程调用')))
        self.enterContext(mock.patch('subprocess.check_output', side_effect=AssertionError('禁止进程调用')))
        self.enterContext(mock.patch('urllib.request.urlopen', side_effect=AssertionError('禁止网络调用')))

    def enterContext(self, context):
        return self.addCleanup(context.__exit__, None, None, None) or context.__enter__()

    def write_catalog(self):
        (self.engine / 'manifests/archive/index.json').write_text(json.dumps(self.index), encoding='utf-8')
        with gzip.open(self.engine / 'manifests/archive/objects.jsonl.gz', 'wt', encoding='utf-8') as stream:
            for row in self.objects.items():
                stream.write(json.dumps(row) + '\n')

    def test_check_only_verifies_originals_without_preparing(self):
        _, _, report = prepare.check_dependencies(self.engine, self.public)
        self.assertEqual(report['git_originals_checked'], 1)
        self.assertEqual(report['asset_caches_checked'], 1)
        self.assertFalse((self.engine / '.rebuild').exists())
        self.process.assert_not_called()

    def test_missing_original_stops_before_any_preparation(self):
        self.git_path.unlink()
        with self.assertRaisesRegex(prepare.DependencyError, 'restore.py --code'):
            prepare.prepare(self.engine, self.public, 'ranking')
        self.assertFalse((self.engine / '.rebuild').exists())
        self.process.assert_not_called()

    def test_incomplete_asset_stops_before_any_preparation(self):
        self.cache.write_bytes(self.cache.read_bytes()[:30])
        with self.assertRaisesRegex(prepare.DependencyError, '--history current-inputs-full.tar'):
            prepare.prepare(self.engine, self.public, 'ranking')
        self.assertFalse((self.engine / '.rebuild').exists())

    def test_unmatched_public_asset_is_rejected(self):
        self.public['protected_archives'][0]['sha256'] = 'other'
        with self.assertRaisesRegex(prepare.DependencyError, 'MyCode'):
            prepare.check_dependencies(self.engine, self.public)

    def test_catalog_path_cannot_escape_engine(self):
        self.objects[self.git_id]['path'] = '../outside.txt'
        self.write_catalog()
        with self.assertRaisesRegex(prepare.DependencyError, '路径不安全'):
            prepare.check_dependencies(self.engine, self.public)

    def test_preparation_reads_synthetic_inputs_without_old_git(self):
        with contextlib.redirect_stdout(io.StringIO()):
            result = prepare.prepare(self.engine, self.public, 'ranking')
        restored = self.engine / '.rebuild/current-method/ranking/实验'
        self.assertEqual((restored / 'git.txt').read_bytes(), self.git_data)
        self.assertEqual((restored / 'asset.txt').read_bytes(), self.asset_data)
        self.assertEqual(result['mode'], 'prepared')
        self.process.assert_not_called()

    def test_missing_after_preflight_still_cannot_call_git(self):
        original = prepare.guarded_restore_class

        def change_after_check(*args):
            guarded = original(*args)
            self.git_path.unlink()
            return guarded

        with mock.patch.object(prepare, 'guarded_restore_class', side_effect=change_after_check):
            with self.assertRaisesRegex(prepare.DependencyError, '准备期间缺失'):
                prepare.prepare(self.engine, self.public, 'ranking')
        self.process.assert_not_called()

    def test_runtime_asset_and_git_guards_reject_changed_bytes(self):
        legacy = prepare.load_module('guard_fixture', self.engine / 'tools/restore_archive.py')
        guarded = prepare.guarded_restore_class(legacy, self.engine, self.index['assets'])
        reader = guarded(self.index, self.objects)
        self.git_path.write_bytes(b'changed')
        with self.assertRaisesRegex(prepare.DependencyError, '准备期间变化'):
            reader.content(self.git_id)
        self.cache.unlink()
        with self.assertRaisesRegex(prepare.DependencyError, '准备期间缺失或变化'):
            reader.content(self.asset_id)
        self.process.assert_not_called()

    def test_private_sources_are_blocked_and_public_sources_still_pass(self):
        for source in [
            {'url': 'https://github.com/peropeng/graduate-thesis/releases/download/old/a'},
            {'url': 'https://api.github.com/repos/peropeng/graduate-thesis/git/blobs/a'},
            {'git_blob': {'repository': 'peropeng/graduate-thesis'}},
        ]:
            with self.assertRaises(prepare.DependencyError):
                prepare.reject_private_source(source)
        prepare.reject_private_source({'url': 'https://github.com/dask/dask.git'})

    def test_local_key_is_existing_private_file_or_explicit_file(self):
        with mock.patch.object(restore, 'ROOT', self.base):
            self.assertIsNone(restore.local_key())
            default = self.base / '工作区/私有配置/mycode-recovery-key.json'
            default.parent.mkdir(parents=True)
            default.write_text('synthetic key placeholder', encoding='utf-8')
            self.assertEqual(restore.local_key(), default)
            self.assertIsNone(restore.local_key(self.base / 'missing.json'))
            explicit = self.base / 'explicit.json'
            explicit.write_text('synthetic explicit placeholder', encoding='utf-8')
            self.assertEqual(restore.local_key(explicit), explicit)


if __name__ == '__main__':
    unittest.main()
