"""Fresh complete N3/200/30 task; no actor private observer or old candidate input."""
from common166 import *
import entry_sourceio_v4_239,control235,controller245
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args();worker=entry_sourceio_v4_239.install();worker.controller225=controller245;worker.METHOD='ENAGENT_FULL_N3_C200_S30_FLASH';control235.verify(args.task,control235.PHASE);return worker.run(args.task,control235.PHASE)
if __name__=='__main__':main()
