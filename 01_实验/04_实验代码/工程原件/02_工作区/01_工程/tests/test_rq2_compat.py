"""Offline checks use the actual archived audit callback, not a replica."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from thesis_recovery.rq2_compat import adapt_product_entry, check_entry

ENTRY = ROOT / ".rebuild/paper-inputs/experiment261/product_entry_pp.py"


def archived_callback(source, root):
    tree = ast.parse(source)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    functions = [n for n in ast.walk(main) if isinstance(n, ast.FunctionDef) and n.name in ("within", "audit")]
    helper = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_rq2_null_device"]
    namespace = {"os": os, "Path": Path, "source": root / "source", "frozen": root / "frozen", "out": root / "out", "allowed": [root / "source", root / "out"]}
    exec(compile(ast.Module(body=helper + functions, type_ignores=[]), str(ENTRY), "exec"), namespace)
    return namespace


@unittest.skipUnless(ENTRY.exists(), "restore experiment261 archive to exercise the actual guard")
class Rq2CompatTests(unittest.TestCase):
    def setUp(self):
        self.raw = ENTRY.read_bytes()
        self.source = self.raw.decode("utf-8-sig")

    def test_layout_and_original_bytes_are_preserved(self):
        receipt = check_entry(ENTRY)
        self.assertTrue(receipt["compiled"])
        self.assertFalse(receipt["full_runtime_qualified"])
        self.assertEqual(ENTRY.read_bytes(), self.raw)
        adapted = adapt_product_entry(self.source)
        with self.assertRaisesRegex(ValueError, "LAYOUT_NOT_RECOGNIZED"):
            adapt_product_entry(adapted)
        with self.assertRaisesRegex(ValueError, "LAYOUT_NOT_RECOGNIZED"):
            adapt_product_entry(self.source.replace("os.devnull.casefold()", "'unexpected'"))

    @unittest.skipUnless(os.name == "nt", "Windows-specific normalized null device")
    def test_actual_logging_null_open_before_and_after_adaptation(self):
        # A separate process contains the irreversible audit hook. It opens only
        # os.devnull through logging; no model, task tests or native task runs.
        script = """import logging,os,sys,tempfile
from pathlib import Path
sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2])
from test_rq2_compat import archived_callback,ENTRY
from thesis_recovery.rq2_compat import adapt_product_entry
source=ENTRY.read_text(encoding='utf-8-sig')
with tempfile.TemporaryDirectory() as d:
 root=Path(d).resolve()
 for name in ('source','frozen','out'):(root/name).mkdir()
 if sys.argv[3]=='adapted':source=adapt_product_entry(source)
 state=archived_callback(source,root)
 sys.addaudithook(state['audit'])
 handler=logging.FileHandler(os.devnull,mode='w',encoding='utf-8')
 handler.close()
 print('NULL_LOGGING_PASS')
 os._exit(0)
"""
        for mode in ("original", "adapted"):
            result = subprocess.run([sys.executable, "-u", "-I", "-c", script, str(ROOT / "src"), str(ROOT / "tests"), mode], capture_output=True, text=True)
            if mode == "original":
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue("PATCHPILOT_GENERATED_WRITE_SCOPE" in result.stderr or "WinError 87" in result.stderr, result.stderr)
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("NULL_LOGGING_PASS", result.stdout)

    def test_archived_boundaries_still_apply(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for name in ("source", "frozen", "out"):
                (root / name).mkdir()
            state = archived_callback(adapt_product_entry(self.source), root)
            audit = state["audit"]
            audit("open", (str(root / "source/model.py"), "r", 0))
            audit("open", (str(root / "out/log.txt"), "w", os.O_WRONLY))
            for path, mode in ((root / "source/model.py", "w"), (root / "source/tests/test_x.py", "r"), (root / "frozen/hidden.py", "r"), (root / "elsewhere.txt", "w"), (root / "elsewhere.txt", "r")):
                with self.assertRaises(PermissionError):
                    audit("open", (str(path), mode, 0))
            for event in ("subprocess.Popen", "os.system", "socket.connect", "socket.bind"):
                with self.assertRaises(PermissionError):
                    audit(event, ())
            if os.name == "nt":
                matcher = state["_rq2_null_device"]
                for path in ("nul", "NUL", r"\\.\nul", r"\\.\nul" + "\\", b"NUL"):
                    self.assertTrue(matcher(path), repr(path))
                for path in ("null", "nul.txt", r"\\.\pipe\name", r"\\.\nul\file", r"C:\outside\file", r"\\?\nul"):
                    self.assertFalse(matcher(path), repr(path))


if __name__ == "__main__":
    unittest.main()
