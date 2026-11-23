"""Pure finance bounds qualification only; no old lazy transport or shared IO."""
from common166 import *
def bounds_for(body):
 p=read(E/'protocol225.json');provider=module('exp239_completion_bounds_only',p['finance_transport'])
 return provider.bounds(body,read(E/'finance_config239.json'))
