"""Same sealed V3 worker with one narrow observer initial-ordinary cache."""
from common166 import *
import entry239,control235
from initial_v2_observer239 import initial_bridge

def install():
 worker=entry239.install();worker.Bridge=initial_bridge(worker.Bridge);return worker

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--task',required=True);a=p.parse_args()
 worker=install();control235.verify(a.task,control235.PHASE);return worker.run(a.task,control235.PHASE)
if __name__=='__main__':main()
