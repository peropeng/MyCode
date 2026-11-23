"""Keep original finance semantics; scope only request/response receipt writes."""
from pathlib import Path
from contracts241 import save,inside,EngineeringUnknown
from bounded_atomic_retry241 import patched_atomic
from shared_json_read241 import read_json_shared

def install(transport,owner):
 Original=transport.LegacyIO
 class ScopedLegacyIO(Original):
  def __init__(self):
   super().__init__()
   root=Path(owner.output_root).resolve()
   def write(path,value):
    if not inside(path,root):raise EngineeringUnknown('PATCHPILOT_FINANCE_ARTIFACT_SCOPE')
    save(path,value,scope=root)
   # The legacy ledger's atomic/lock/event/reserve/POST/settle functions are
   # untouched. Only its imported experiment-local artifact save is replaced.
   self.m.save=write
   # This isolated LegacyIO is constructed by the real shared generate()
   # only after owner.install(). Preserve atomic serialization/temp bytes;
   # change exactly one os.replace to bounded Win5 replacement retry.
   self.m.atomic=patched_atomic(self.m)
  def read(self):
   # Transport still invokes this inside its original byte0 transaction.
   # FILE_SHARE_DELETE also avoids blocking other atomic replacements.
   return read_json_shared(self.m.STATE)
 transport.LegacyIO=ScopedLegacyIO
