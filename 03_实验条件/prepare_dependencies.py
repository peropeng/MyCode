"""预检当前依赖；仅在明确传入--prepare时准备，不启动实验或旧私库回退。"""
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / '09_工作区/恢复/原始项目/02_工作区/01_工程'
LEGACY_REPOSITORY = 'peropeng/graduate-thesis'
RESTORE_CODE = 'python 03_实验条件/restore.py --code'
RESTORE_INPUTS = 'python 03_实验条件/restore.py --history current-inputs-full.tar'


class DependencyError(RuntimeError):
    pass


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inside(base, relative):
    """清单只接受可跨平台解释且不越界的相对路径。"""
    value = PurePosixPath(relative)
    if value.is_absolute() or '\\' in relative or ':' in relative or '..' in value.parts:
        raise DependencyError('清单路径不安全：' + relative)
    target = (base / relative).resolve()
    if not target.is_relative_to(base.resolve()):
        raise DependencyError('清单路径越界：' + relative)
    return target


def load_catalog(engine):
    index_path = engine / 'manifests/archive/index.json'
    if not index_path.is_file():
        raise DependencyError('缺少完整工程清单；先运行：' + RESTORE_CODE)
    index = json.loads(index_path.read_text(encoding='utf-8'))
    objects = {}
    for relative in index['object_maps']:
        with gzip.open(inside(engine, relative), 'rt', encoding='utf-8') as stream:
            for line in stream:
                identity, record = json.loads(line)
                if identity in objects and objects[identity] != record:
                    raise DependencyError('内容清单存在冲突记录')
                objects[identity] = record
    return index, objects


def check_dependencies(engine, public_catalog):
    """只读取清单、源码字节和缓存身份，不执行冻结工具或下载。"""
    engine = engine.resolve()
    index, objects = load_catalog(engine)
    required = [
        'tools/restore_archive.py', 'tools/restore_current_method.py',
        'manifests/current_legacy_profiles.json', 'manifests/legacy_path_aliases.json',
        'manifests/external_models.json',
    ]
    missing = [name for name in required if not inside(engine, name).is_file()]
    if missing:
        raise DependencyError('完整工程缺少文件：' + ', '.join(missing) + '；先运行：' + RESTORE_CODE)
    git_objects = {identity: record for identity, record in objects.items() if record['kind'] == 'git'}
    expected = index['statistics']['object_kinds']['git']
    if len(git_objects) != expected:
        raise DependencyError('Git原件数量与冻结清单不一致；先运行：' + RESTORE_CODE)
    invalid = [record['path'] for identity, record in git_objects.items()
               if not (path := inside(engine, record['path'])).is_file() or digest(path) != identity]
    if invalid:
        raise DependencyError('Git原件缺少或不匹配：' + ', '.join(invalid) + '；先运行：' + RESTORE_CODE)
    public_assets = {row['name']: row for row in public_catalog['protected_archives']}
    for name, asset in index['assets'].items():
        if asset['name'] != name or PurePosixPath(name).name != name:
            raise DependencyError('资源包名称不安全')
        current = public_assets.get(name)
        if current is None or current['sha256'] != asset['sha256']:
            raise DependencyError('工程资源包身份未匹配MyCode恢复清单')
        path = inside(engine / '.restore-cache', name)
        if not path.is_file() or digest(path) != asset['sha256']:
            raise DependencyError('本地资源包缺少或不匹配：' + name + '；先运行：' + RESTORE_INPUTS)
        # 内容包是对象分块，不按源码目录树解包；这里只核对成员存在。
        with tarfile.open(path, 'r:') as archive:
            for record in objects.values():
                if record['kind'] != 'asset':
                    continue
                for chunk in record['chunks']:
                    if chunk['asset'] == name:
                        member = archive.getmember(chunk['member'])
                        if not member.isfile():
                            raise DependencyError('资源包中的内容分块不是普通文件')
    report = {
        'git_originals_checked': len(git_objects), 'asset_caches_checked': len(index['assets']),
        'private_repository_access': False, 'git_fallback_allowed': False,
        'experiments_executed': 0, 'API_requests': 0,
    }
    return index, objects, report


def reject_private_source(source):
    reference = source.get('git_blob', {})
    url = source.get('url', '').lower().rstrip('/')
    if (reference.get('repository', '').lower() == LEGACY_REPOSITORY
            or LEGACY_REPOSITORY in url):
        raise DependencyError('已停用旧私库下载；请使用MyCode恢复入口')


def guarded_restore_class(legacy, engine, checked_assets):
    """覆盖两条旧回退，即使预检后文件变化也不调用Git或私库。"""
    class LocalOriginals(legacy.Restore):
        instances = []

        def __init__(self, *args):
            super().__init__(*args)
            self.instances.append(self)

        def close(self):
            for handle in list(self.tars.values()) + list(self.package_archives.values()):
                handle.close()
            for handle, _ in self.upstreams.values():
                handle.close()

        def content(self, identity):
            record = self.objects[identity]
            if record['kind'] == 'git':
                path = inside(engine, record['path'])
                if not path.is_file():
                    raise DependencyError('本地Git原件在准备期间缺失；重新运行：' + RESTORE_CODE)
                data = path.read_bytes()
                if hashlib.sha256(data).hexdigest() != identity:
                    raise DependencyError('本地Git原件在准备期间变化；重新运行：' + RESTORE_CODE)
                return data
            return super().content(identity)

        def release(self, asset):
            name = asset['name']
            if name not in checked_assets or asset != checked_assets[name]:
                raise DependencyError('准备期间资源包清单变化，停止恢复')
            path = inside(engine / '.restore-cache', name)
            if not path.is_file() or digest(path) != asset['sha256']:
                raise DependencyError('本地资源包在准备期间缺失或变化；重新运行：' + RESTORE_INPUTS)
            if path not in self.tars:
                self.tars[path] = tarfile.open(path, 'r:')
            return self.tars[path]

        def download(self, source):
            reject_private_source(source)
            return super().download(source)

        def upstream(self, source):
            reject_private_source(source)
            return super().upstream(source)

    return LocalOriginals


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(engine, public_catalog, component):
    index, objects, report = check_dependencies(engine, public_catalog)
    legacy = load_module('_mycode_archive_reader', engine / 'tools/restore_archive.py')
    if Path(legacy.ROOT).resolve() != engine.resolve():
        raise DependencyError('冻结恢复器工程路径不匹配')
    previous_module = sys.modules.get('restore_archive')
    previous_argv = sys.argv
    guarded = None
    try:
        sys.modules['restore_archive'] = legacy
        current = load_module('_mycode_dependency_preparation', engine / 'tools/restore_current_method.py')
        guarded = guarded_restore_class(legacy, engine, index['assets'])
        current.Restore = guarded
        # 固定使用已校验的内存清单，避免再次加载产生未校验输入。
        current.load_catalog = lambda: (index, objects)
        sys.argv = [str(engine / 'tools/restore_current_method.py'), '--component', component]
        current.main()
    finally:
        if guarded is not None:
            for reader in guarded.instances:
                reader.close()
        sys.argv = previous_argv
        if previous_module is None:
            sys.modules.pop('restore_archive', None)
        else:
            sys.modules['restore_archive'] = previous_module
    return report | {'mode': 'prepared', 'optional_embedding_model_download_requested': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true', help='显式准备选定组件；可能下载清单锁定的公共上游依赖')
    parser.add_argument('--component', choices=['ranking', 'recovery', 'both'], default='both')
    args = parser.parse_args()
    try:
        public_catalog = json.loads((ROOT / '06_实验记录/恢复清单.json').read_text(encoding='utf-8'))
        if args.prepare:
            result = prepare(ENGINE, public_catalog, args.component)
        else:
            _, _, result = check_dependencies(ENGINE, public_catalog)
            result['mode'] = 'check-only'
        print(json.dumps(result, ensure_ascii=False))
    except (DependencyError, OSError, ValueError, KeyError, tarfile.TarError) as error:
        parser.exit(2, '依赖准备停止：' + str(error) + '\n')


if __name__ == '__main__':
    main()
