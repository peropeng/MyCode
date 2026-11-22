"""Migration checks exercise frozen behavior, not new research experiments."""
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))


class MigrationTests(unittest.TestCase):
    def test_archive_survives_later_edits_and_deleted_working_files(self):
        spec=importlib.util.spec_from_file_location("archive_restore",ROOT/"tools/restore_archive.py")
        archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(["git","init","--quiet",str(root)],check=True)
            original=b"original research record\n";path=root/"notes.md";path.write_bytes(original)
            subprocess.run(["git","-C",str(root),"add","notes.md"],check=True)
            subprocess.run(["git","-C",str(root),"-c","user.name=Archive Test","-c","user.email=test@example.invalid","commit","--quiet","-m","Archive original"],check=True)
            commit=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
            archive.ROOT=root;archive.CACHE=root/".cache"
            digest=hashlib.sha256(original).hexdigest()
            restore=archive.Restore({"git_snapshot_commit":commit},{digest:{"kind":"git","path":"notes.md"}})
            path.write_bytes(b"later edited version\n")
            self.assertEqual(restore.content(digest),original)
            self.assertEqual(path.read_bytes(),b"later edited version\n")
            path.unlink()
            self.assertEqual(restore.content(digest),original)
            self.assertFalse(path.exists())

    def test_native_model_loader_receives_the_physical_relocated_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'实验').mkdir();(root/'manifests').mkdir();(root/'archive').mkdir()
            (root/'archive/checkpoint.bin').write_bytes(b'preserved checkpoint')
            old='D:/Code/毕设/graduate-thesis-experiments'
            (root/'manifests/legacy_path_aliases.json').write_text(json.dumps([{'old':old+'/old/checkpoint.bin','relative':'archive/checkpoint.bin'}]),encoding='utf-8')
            source=root/'实验/native_reader.py'
            source.write_text("from __future__ import annotations\nfrom pathlib import Path\ndata=Reader.from_pretrained(str(Path("+repr(old)+")/'old/checkpoint.bin'))\nassert data==b'preserved checkpoint'\n",encoding='utf-8')
            script="""import os,sys
sys.path.insert(0,sys.argv[1])
from thesis_recovery import legacy_paths as lp
class Reader:
 @staticmethod
 def from_pretrained(path):
  descriptor=os.open(path,os.O_RDONLY)
  try:return os.read(descriptor,1024)
  finally:os.close(descriptor)
lp.install(sys.argv[2]);source=sys.argv[3]
exec(lp.relocated_compile(open(source,'rb').read(),source,'exec'),{'Reader':Reader})
"""
            result=subprocess.run([sys.executable,'-I','-c',script,str(ROOT/'src'),str(root),str(source)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)

    def test_process_relocation_cannot_read_original_machine(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"实验").mkdir()
            (root/"manifests").mkdir()
            (root/"archive").mkdir()
            (root/"archive/plan.md").write_text("preserved plan",encoding="utf-8")
            (root/"manifests/legacy_path_aliases.json").write_text(json.dumps([{"old":"D:/Code/毕设/graduate-thesis-experiments/old/plan.md","relative":"archive/plan.md"}]),encoding="utf-8")
            data=b'unchanged-frozen-input\n'
            (root/"input.txt").write_bytes(data)
            source=root/"实验/example.py"
            source.write_text("from pathlib import Path\nassert Path('D:/Code/毕设/graduate-thesis-experiments/input.txt').read_bytes()==b'unchanged-frozen-input\\n'\nassert (Path('D:/Code/毕设/graduate-thesis-experiments')/'old/plan.md').read_text()=='preserved plan'\nassert isinstance(Path('input.txt'),Path)\n",encoding="utf-8")
            script="import sys;sys.path.insert(0,"+repr(str(ROOT/"src"))+");from thesis_recovery import legacy_paths as p;p.install("+repr(str(root))+");source="+repr(str(source))+";exec(p.relocated_compile(open(source,'rb').read(),source,'exec'));print('relocated')"
            result=subprocess.run([sys.executable,"-I","-c",script],capture_output=True,text=True,encoding="utf-8")
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn("relocated",result.stdout)
            self.assertEqual((root/"input.txt").read_bytes(),data)

    def test_frozen_progress_guard_protects_goal_identity(self):
        path=ROOT/"src/thesis_recovery/frozen/recovery/progress_guard240.py"
        spec=importlib.util.spec_from_file_location("frozen_progress_guard",path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        goals=["goal_a","goal_b"];ordinary=["regression"]
        def validation(passed):
            outcomes={name:{"status":"passed" if name in passed else "failed"} for name in goals+ordinary}
            native={key:True for key in ["executed","guard_loaded","business_state_unchanged","frozen_tests_unchanged","exact_test_coverage","completed_guarded_coverage"]}
            native.update({"timeout":False,"requested_nodes":goals+ordinary,"pytest":{"outcomes":outcomes},"expected_test_count":3,"passed_count":len(passed),"passed":len(passed)==3,"stop_receipt":{"owned_job_closed":True,"root_process_stopped":True,"all_owned_descendants_terminated":True}})
            return {"native_record":native,"outcomes":{"regression":outcomes["regression"]}}
        guard=module.RepairProgressGuard("PROGRESS_SET",goals,ordinary,validation({"goal_a","regression"}),{"code.py":"original-sha"})
        rejected=guard.consider(validation({"goal_b","regression"}),{"code.py":"regressed-sha"})
        self.assertFalse(rejected["accepted"])
        self.assertEqual(guard.frontier,{"goal_a"})
        accepted=guard.consider(validation({"goal_a","goal_b","regression"}),{"code.py":"fixed-sha"})
        self.assertTrue(accepted["accepted"])
        self.assertEqual(guard.frontier,{"goal_a","goal_b"})


if __name__=="__main__":
    unittest.main()
