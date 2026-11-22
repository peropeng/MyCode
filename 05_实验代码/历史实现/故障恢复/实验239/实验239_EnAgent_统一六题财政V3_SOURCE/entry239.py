"""Configured N3/200/30 controller, original auto tools and independent final acceptance."""
from common166 import *
import entry235,control235
from tool_bridge_v3 import ScopedBridgeV3
def install():
 entry235.install()
 from finite_environment239 import completion_environment
 entry235.worker.CommonEnvironment=completion_environment(entry235.worker.CommonEnvironment)
 class ScopedBridge(ScopedBridgeV3):pass
 entry235.worker.Bridge=ScopedBridge
 entry235.worker.METHOD='ENAGENT_ICSE2026_N3_FLASH_UNIFIED_SIX_V3'
 return entry235.worker
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--task',required=True);a=p.parse_args()
 worker=install();control235.verify(a.task,control235.PHASE)
 return worker.run(a.task,control235.PHASE)
if __name__=='__main__':main()
