"""One fresh or same-trial checkpoint-resumed complete EnAgent trajectory."""
from common166 import *
import entry_sourceio_v4_239,source_control250,controller250,public_environment250

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args()
 source_control250.verify(args.task,source_control250.PHASE)
 worker=entry_sourceio_v4_239.install();worker.controller225=controller250
 worker.METHOD='ENAGENT_ICSE2026_FULL_N3_C200_S30_CONFIRMATION'
 public_environment250.install(worker)
 return worker.run(args.task,source_control250.PHASE)

if __name__=='__main__':main()
