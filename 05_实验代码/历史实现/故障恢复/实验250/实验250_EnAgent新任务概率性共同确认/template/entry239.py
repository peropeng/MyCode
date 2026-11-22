"""Configured N2 controller, original auto tools and independent final acceptance."""
from common166 import *
import entry235,control235
from tool_bridge_v3 import ScopedBridgeV3
def install():
 entry235.install()
 class ScopedBridge(ScopedBridgeV3):pass
 entry235.worker.Bridge=ScopedBridge
 entry235.worker.METHOD='ENAGENT_BUDGET_N2_C24_S30_GO_FLASH'
 return entry235.worker
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--task',required=True);a=p.parse_args()
 worker=install();control235.verify(a.task,control235.PHASE)
 return worker.run(a.task,control235.PHASE)
if __name__=='__main__':main()
