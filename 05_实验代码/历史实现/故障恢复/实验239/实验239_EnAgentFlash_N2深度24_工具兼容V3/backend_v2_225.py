"""Per-nested-request V2 authority and identical complete observation pack."""
import copy
from backend225 import Transport as OriginalTransport
from v2_control225 import verify,load_pack

def packed_payload(payload,rendered):
 result=copy.deepcopy(payload)
 if not any(rendered in str(m.get('content','')) for m in result['messages']):
  index=1 if result['messages'] and result['messages'][0].get('role')=='system' else 0
  result['messages'].insert(index,{'role':'user','content':rendered})
 return result

class Transport(OriginalTransport):
 def _request(self,payload):
  verify(self.env.task_id,self.env.finance_phase)
  pub,pack,_=load_pack(self.env.task_id)
  return super()._request(packed_payload(payload,pub.render(pack)))
