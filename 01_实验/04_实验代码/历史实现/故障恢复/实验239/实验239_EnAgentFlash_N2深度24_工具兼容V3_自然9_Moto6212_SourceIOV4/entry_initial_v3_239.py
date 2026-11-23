"""Original sealed actor core with prospective initial-source diagnostic observer."""
from common166 import *
import entry239,control235
from initial_v3_observer239 import diagnostic_bridge
def install():
 worker=entry239.install();worker.Bridge=diagnostic_bridge(worker.Bridge);return worker
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--task',required=True);args=a.parse_args()
 worker=install();control235.verify(args.task,control235.PHASE);return worker.run(args.task,control235.PHASE)
if __name__=='__main__':main()
