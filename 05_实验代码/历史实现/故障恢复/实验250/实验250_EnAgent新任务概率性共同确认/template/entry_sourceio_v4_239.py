"""Same sealed author core and InitialV3 observer, prospective readonly source I/O."""
from common166 import *
import entry_initial_v3_239,control235
from source_io_v4_239 import source_io_bridge
def install():
 worker=entry_initial_v3_239.install();worker.Bridge=source_io_bridge(worker.Bridge)
 from budget_local_bridge import local_bridge
 worker.Bridge=local_bridge(worker.Bridge);return worker
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--task',required=True);args=a.parse_args()
 worker=install();control235.verify(args.task,control235.PHASE);return worker.run(args.task,control235.PHASE)
if __name__=='__main__':main()
