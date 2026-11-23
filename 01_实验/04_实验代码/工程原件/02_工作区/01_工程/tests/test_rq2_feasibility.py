"""Public-only checks of the missing-final wrapper; no task tests are run."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rq2_final_tool', ROOT / 'tools/run_rq2_feasibility.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class RQ2FinalWrapperTests(unittest.TestCase):
    def test_verified_bytes_cannot_escape_or_overwrite_changed_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b'original-bytes'
            expected = hashlib.sha256(raw).hexdigest()
            with self.assertRaises(RuntimeError):
                tool._write_verified(root, '../outside', raw, expected)
            tool._write_verified(root, 'repo/source.py', raw, expected)
            target = root / 'repo/source.py'
            target.write_bytes(b'changed')
            with self.assertRaises(RuntimeError):
                tool._write_verified(root, 'repo/source.py', raw, expected)
            self.assertEqual(target.read_bytes(), b'changed')

    def test_actual_selected_public_witnesses_and_whole_inventory_agree(self):
        contract, result, business, whole = tool.public_preflight()
        self.assertEqual(len(business), 119)
        self.assertEqual(tool.digest(whole), result['final_snapshot']['inventory_sha256'])
        self.assertEqual(set(business), set(contract['c0_business_paths_sha256']))
        self.assertEqual(result['hidden_acceptance_calls'], 0)


if __name__ == '__main__':
    unittest.main()
