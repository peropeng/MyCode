"""Project only the current published workspace aliases into an owned actor clone."""
from pathlib import Path
import re
from bridge225 import IllegalTool

class PublishedAliasProjection:
    def public_aliases(self):
        aliases=tuple(sorted(set(getattr(self.env,'workspace_aliases',()))))
        if not aliases or any(not re.fullmatch(r'[A-Za-z0-9_.-]+',a) or a in {'.','..'} for a in aliases):
            raise IllegalTool('PUBLISHED_WORKSPACE_ALIAS_CONTRACT_INVALID')
        return ('repo',*aliases)

    def _project_alias_path(self,root,value):
        for alias in self.public_aliases():
            prefix='/workspace/'+alias
            if value==prefix or value.startswith(prefix+'/'):
                root=self._root(root)
                tail=value[len(prefix):].lstrip('/')
                suffix=''
                if '::' in tail:
                    tail,node=tail.split('::',1)
                    suffix='::'+node
                if '\\' in tail or ':' in tail or any(p in {'.','..'} for p in tail.split('/')):
                    raise IllegalTool('PUBLISHED_ALIAS_TRAVERSAL_OR_NONPOSIX_SUFFIX')
                candidate=root/tail
                if candidate.is_symlink() or not candidate.resolve().is_relative_to(root.resolve()):
                    raise IllegalTool('PUBLISHED_ALIAS_OUTSIDE_OWNED_ROOT')
                return candidate.as_posix()+suffix
        return value

    def path_map(self,root,value):
        if not isinstance(value,str):return super().path_map(root,value)
        direct=self._project_alias_path(root,value)
        if direct!=value:return super().path_map(root,direct)
        prefixes='|'.join(re.escape('/workspace/'+a) for a in self.public_aliases())
        pattern=r'(?<![A-Za-z0-9_./\\])(?:'+prefixes+r')(?:/[^\s\x27\x22`;|&<>]*)?(?=$|[\s\x27\x22`;|&<>])'
        mapped=re.sub(pattern,lambda m:self._project_alias_path(root,m.group()),value)
        return super().path_map(root,mapped)

    def _path(self,root,path):
        return super()._path(root,self._project_alias_path(root,str(path)))

    def command_runner(self,root,command):
        return super().command_runner(root,self.path_map(root,command))
