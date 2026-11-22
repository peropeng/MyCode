"""Per-process path relocation for immutable historical source.

Frozen source and JSON stay byte-identical; only filesystem access is relocated.
"""
import ast
import builtins
import importlib.machinery
import io
import json
import os
from pathlib import Path as RealPath
import pathlib
import subprocess
import sys
import sysconfig

ROOT=RealPath(__file__).resolve().parents[2]
OLD_ROOT="D:/Code/毕设/graduate-thesis-experiments"
ALIASES=[]
_open=builtins.open
_io_open=io.open
_compile=builtins.compile
_loader_code=importlib.machinery.SourceFileLoader.get_code
_installed=False


def _norm(value):
    return os.fsdecode(value).replace("\\","/").rstrip("/")


def configure(root=None, extra_aliases=None):
    global ROOT,ALIASES
    ROOT=RealPath(root or ROOT).resolve()
    aliases=[
        (OLD_ROOT+"/工作区/0922-exp124-ranking-baselines/.venv/Lib/site-packages",sysconfig.get_paths()["purelib"]),
        (OLD_ROOT+"/工作区/0922-exp124-ranking-baselines/.venv/Scripts/python.exe",sys.executable),
        ("C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",sys.executable),
        ("C:/Users/Administrator",str(RealPath.home())),
        (OLD_ROOT,str(ROOT)),
        ("/Users/peroyang/My/MyWork/毕设实验",str(ROOT)),
        ("D:/Code/毕设/.codex-tmp",str(ROOT/"录音与转写")),
        ("D:/Code/毕设/资料",str(ROOT/"资料")),
    ]
    manifest=ROOT/"manifests/legacy_path_aliases.json"
    if manifest.is_file():
        for entry in json.loads(manifest.read_text(encoding="utf-8")):
            aliases.append((entry["old"],str(ROOT/entry["relative"])))
    for old,new in extra_aliases or []:
        aliases.append((old,str(new)))
    companions=[]
    for old,new in aliases:
        normalized=_norm(old)
        if normalized.casefold().startswith(OLD_ROOT.casefold()+"/"):
            companions.append((str(ROOT)+normalized[len(OLD_ROOT):],new))
    ALIASES=sorted([(_norm(old),_norm(new)) for old,new in [*aliases,*companions]],key=lambda item:len(item[0]),reverse=True)


def translate(value):
    if not isinstance(value,(str,bytes,os.PathLike)):
        return value
    text=_norm(value)
    lower=text.casefold()
    for old,new in ALIASES:
        if lower==old.casefold() or lower.startswith(old.casefold()+"/"):
            result=new+text[len(old):]
            return os.fsencode(result) if isinstance(value,bytes) else result
    return value


class _PathFactory(type):
    def __instancecheck__(cls,value):
        return isinstance(value,RealPath)
    def __getattr__(cls,name):
        return getattr(RealPath,name)


class Path(metaclass=_PathFactory):
    def __new__(cls,*args,**kwargs):
        return RealPath(*(translate(value) for value in args),**kwargs)


def __getattr__(name):
    return getattr(pathlib,name)


class RelocateImports(ast.NodeTransformer):
    def __init__(self):
        self.native_loader_path=False

    def visit_Module(self,node):
        self.generic_visit(node)
        if self.native_loader_path:
            position=1 if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str) else 0
            while position<len(node.body) and isinstance(node.body[position],ast.ImportFrom) and node.body[position].module=='__future__':position+=1
            node.body.insert(position,ast.ImportFrom(module='thesis_recovery.legacy_paths',names=[ast.alias(name='translate',asname='_thesis_relocated_loader_path')],level=0))
        return node

    def visit_Call(self,node):
        self.generic_visit(node)
        if not isinstance(node.func,ast.Attribute) or node.func.attr not in {'from_pretrained','from_file'}:return node
        if node.args and not isinstance(node.args[0],ast.Starred):
            node.args[0]=ast.Call(func=ast.Name(id='_thesis_relocated_loader_path',ctx=ast.Load()),args=[node.args[0]],keywords=[])
            self.native_loader_path=True
        else:
            for keyword in node.keywords:
                if keyword.arg in {'pretrained_model_name_or_path','filename','path'}:
                    keyword.value=ast.Call(func=ast.Name(id='_thesis_relocated_loader_path',ctx=ast.Load()),args=[keyword.value],keywords=[])
                    self.native_loader_path=True
                    break
        return node

    def visit_ImportFrom(self,node):
        if node.module!="pathlib":
            return node
        moved=[item for item in node.names if item.name=="Path"]
        remaining=[item for item in node.names if item.name!="Path"]
        result=[]
        if remaining:
            result.append(ast.copy_location(ast.ImportFrom(module="pathlib",names=remaining,level=0),node))
        if moved:
            result.append(ast.copy_location(ast.ImportFrom(module="thesis_recovery.legacy_paths",names=moved,level=0),node))
        return result or node


def _owned(filename):
    try:
        target=RealPath(filename)
        return target.is_relative_to(ROOT/"实验") or target.is_relative_to(ROOT/"工作区") or target.is_relative_to(ROOT/"研究代码")
    except (TypeError,ValueError):
        return False


def relocated_compile(source,filename,mode,flags=0,dont_inherit=False,optimize=-1,**kwargs):
    if mode=="exec" and _owned(filename) and not(flags&ast.PyCF_ONLY_AST):
        tree=source if isinstance(source,ast.AST) else _compile(source,filename,"exec",ast.PyCF_ONLY_AST,dont_inherit=True)
        tree=ast.fix_missing_locations(RelocateImports().visit(tree))
        return _compile(tree,filename,mode,flags,dont_inherit,optimize,**kwargs)
    return _compile(source,filename,mode,flags,dont_inherit,optimize,**kwargs)


def install(root=None,allow_network=False):
    global _installed
    if _installed:
        return
    configure(root)
    builtins.open=lambda file,*a,**kw:_open(translate(file),*a,**kw)
    io.open=lambda file,*a,**kw:_io_open(translate(file),*a,**kw)
    builtins.compile=relocated_compile
    for name in ["stat","lstat","access","listdir","scandir","chdir","mkdir","makedirs","remove","unlink","rmdir","readlink"]:
        original=getattr(os,name)
        def wrapped(*a,_original=original,**kw):
            if a:
                a=(translate(a[0]),*a[1:])
            elif "path" in kw:
                kw["path"]=translate(kw["path"])
            return _original(*a,**kw)
        setattr(os,name,wrapped)
    for name in ["rename","replace"]:
        original=getattr(os,name)
        def wrapped(source,destination,*a,_original=original,**kw):
            return _original(translate(source),translate(destination),*a,**kw)
        setattr(os,name,wrapped)
    def get_code(loader,fullname):
        if _owned(loader.path):
            data=loader.get_data(loader.path)
            return relocated_compile(data,loader.path,"exec",dont_inherit=True)
        return _loader_code(loader,fullname)
    importlib.machinery.SourceFileLoader.get_code=get_code
    original_popen=subprocess.Popen
    class RelocatedPopen(original_popen):
        def __init__(self,args,*a,**kw):
            if isinstance(args,(list,tuple)):
                args=[translate(item) for item in args]
            if kw.get("cwd") is not None:
                kw["cwd"]=translate(kw["cwd"])
            if kw.get("executable") is not None:
                kw["executable"]=translate(kw["executable"])
            super().__init__(args,*a,**kw)
    subprocess.Popen=RelocatedPopen
    def audit(event,args):
        if event in {"open","os.listdir","os.scandir","os.chdir"} and args and isinstance(args[0],(str,bytes,os.PathLike)):
            value=_norm(args[0]).casefold()
            if value==OLD_ROOT.casefold() or value.startswith(OLD_ROOT.casefold()+"/"):
                raise RuntimeError("Original-machine filesystem access denied: "+os.fsdecode(args[0]))
        if not allow_network and event=="socket.connect":
            raise RuntimeError("Network disabled for legacy inspection/replay")
    sys.addaudithook(audit)
    sys.dont_write_bytecode=True
    _installed=True
