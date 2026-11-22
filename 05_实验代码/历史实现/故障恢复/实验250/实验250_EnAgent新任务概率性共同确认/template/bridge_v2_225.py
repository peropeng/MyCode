"""V2-only distinction: completed empty import tracking is a normal probe."""
import json
from pathlib import Path
from owner225 import Bridge as OriginalBridge

class Bridge(OriginalBridge):
 def _valid(self,record,generated=False):
  if not generated:return super()._valid(record,generated=False)
  good=(record.get('executed') and record.get('guard_loaded') and record.get('business_state_unchanged') and record.get('frozen_tests_unchanged') and not record.get('timeout') and isinstance(record.get('exit_code'),int))
  tracked=Path(record.get('cwd',''))/'actual_product_imports.json'
  try:complete=(tracked.resolve().is_relative_to(Path(self.env.out).resolve()) and tracked.is_file() and json.loads(tracked.read_text('utf-8-sig'))==record.get('actual_product_imports'))
  except (OSError,ValueError):complete=False
  if not good or not complete:self._fatal('GENERATED_OR_PUBLIC_NATIVE_CERTIFICATE_UNKNOWN')
  # Original Environment already reports MODEL_REPRODUCTION_INVALID when no
  # product was imported or no semantic marker exists. No success is invented.
