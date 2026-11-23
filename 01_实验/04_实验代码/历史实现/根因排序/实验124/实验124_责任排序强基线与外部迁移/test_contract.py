import tempfile,unittest
from pathlib import Path
import runner
class ContractTests(unittest.TestCase):
    def test_atomic_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'record.json'; runner.publish(p,{'a':1})
            with self.assertRaises(FileExistsError):runner.publish(p,{'a':2})
            self.assertEqual(runner.load(p),{'a':1})
    def test_projection_gold_free(self):
        a={'content':'observed','action':'tool','thought':'reasoning','mistake_step':2,'task_id':'secret','ground_truth':'answer'}
        self.assertEqual(runner.text_of(a),runner.text_of({k:a[k] for k in ['content','action','thought']}))
    def test_task_equal_metrics(self):
        records=[{'task_group':'a'},{'task_group':'a'},{'task_group':'b'}]
        self.assertEqual(runner.group_score({0:{'rank':1},1:{'rank':2},2:{'rank':4}},records),{'a':.75,'b':.25})
if __name__=='__main__':unittest.main()
