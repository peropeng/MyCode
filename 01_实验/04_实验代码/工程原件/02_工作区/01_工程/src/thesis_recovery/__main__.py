import argparse
import json
import sys


def main():
    parser=argparse.ArgumentParser(description="Portable thesis source and artifact checks")
    parser.add_argument("command",choices=["verify-ranking", "prepare-rq1", "train-rq1"])
    parser.add_argument("--protocol", help="New protocol output for prepare-rq1, existing protocol for train-rq1")
    parser.add_argument("--condition", choices=["complete", "without_multirelation", "without_candidate_attention", "coding_only", "StepFinder"])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    args=parser.parse_args()
    if args.command=="verify-ranking":
        from .ranking import replay_source3
        print(json.dumps(replay_source3(),ensure_ascii=False,indent=2))
    elif args.command == "prepare-rq1":
        from pathlib import Path
        from .rq1_study import prepare
        protocol = prepare()
        if args.protocol:
            output = Path(args.protocol)
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8") as stream:
                json.dump(protocol, stream, ensure_ascii=False, indent=2)
            print(json.dumps({"protocol": str(output.resolve()), "new_training_steps": 0, "api_requests": 0}, ensure_ascii=False))
        else:
            print(json.dumps(protocol, ensure_ascii=False, indent=2))
    elif args.command == "train-rq1":
        if args.protocol is None or args.condition is None or args.seed is None:
            parser.error("train-rq1 requires --protocol, --condition and --seed")
        from .rq1_study import train
        print(json.dumps(train(args.protocol, args.condition, args.seed, args.device), ensure_ascii=False, indent=2))


if __name__=="__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
