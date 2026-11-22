"""使用已恢复的原模型做迁移回放，不启动训练或API调用。"""
from pathlib import Path
import argparse, subprocess

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python',required=True,help='已按原锁文件配置的Python 3.12解释器')
    args=parser.parse_args()
    engine=ROOT/'本地恢复/原始项目/02_工作区/01_工程'
    if not engine.is_dir():parser.error('先运行03_实验条件/restore.py --code')
    subprocess.run([str(Path(args.python).resolve()),'-m','thesis_recovery','verify-ranking'],cwd=engine,check=True,
                   env=__import__('os').environ|{'PYTHONPATH':str(engine/'src')})

if __name__=='__main__':main()
