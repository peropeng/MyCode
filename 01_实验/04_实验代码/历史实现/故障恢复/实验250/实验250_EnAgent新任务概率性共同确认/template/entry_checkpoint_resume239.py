"""Authorized worker entry; restore old public author state, never private feedback."""
from common166 import *
import entry_sourceio_v4_239,control235,resume_controller239
def install():
 worker=entry_sourceio_v4_239.install();worker.controller225=resume_controller239;return worker
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args();worker=install();control235.verify(args.task,control235.PHASE);return worker.run(args.task,control235.PHASE)
if __name__=='__main__':main()
