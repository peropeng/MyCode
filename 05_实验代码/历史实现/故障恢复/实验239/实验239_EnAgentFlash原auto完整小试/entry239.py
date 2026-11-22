"""Original N3 controller, original auto tools, independent automatic acceptance."""
from common166 import *
import entry235,control235
from alias_projection import PublishedAliasProjection
def install():
 entry235.install()
 class ScopedBridge(PublishedAliasProjection,entry235.Bridge235):pass
 entry235.worker.Bridge=ScopedBridge
 entry235.worker.METHOD='ENAGENT_ICSE2026_N3_FLASH_AUTO239'
 return entry235.worker
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--task',required=True);a=p.parse_args()
 worker=install();control235.verify(a.task,control235.PHASE)
 return worker.run(a.task,control235.PHASE)
if __name__=='__main__':main()
