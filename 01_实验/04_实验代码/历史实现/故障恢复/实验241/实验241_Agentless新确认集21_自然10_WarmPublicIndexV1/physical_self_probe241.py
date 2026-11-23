"""Neutral self identity before any product or author import."""
import ctypes,json,os,sys
from pathlib import Path
from winjob241 import kernel,self_identity
def main():
 k=kernel();buf=ctypes.create_unicode_buffer(32768);n=k.GetModuleFileNameW(None,buf,len(buf))
 if not 0<n<len(buf):raise RuntimeError('ACTUAL_IMAGE_UNKNOWN')
 value=self_identity(os.environ['PATCHPILOT_JOB'],buf.value)
 value.update(python_version=sys.version,neutral_only=True,product_imports=0)
 Path(sys.argv[1]).write_text(json.dumps(value,indent=2),'utf-8')
if __name__=='__main__':main()
