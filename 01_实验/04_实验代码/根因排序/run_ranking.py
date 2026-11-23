"""使用已恢复的原模型做迁移回放，不启动训练或API调用。"""
from pathlib import Path
import argparse, subprocess

ROOT=Path(__file__).resolve().parents[3]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python',required=True,help='已按原锁文件配置的Python 3.12解释器')
    args=parser.parse_args()
    engine=ROOT/'01_实验/04_实验代码/工程原件/02_工作区/01_工程'
    if not (engine/'assets/current/features257.pt').is_file():
        engine=ROOT/'04_工作区/恢复/原始项目/02_工作区/01_工程'
    if not engine.is_dir():parser.error('缺少工程源码；可运行01_实验/02_实验条件/restore.py --code恢复完整原件')
    subprocess.run([str(Path(args.python).resolve()),'-m','thesis_recovery','verify-ranking'],cwd=engine,check=True,
                   env=__import__('os').environ|{'PYTHONPATH':str(engine/'src')})

if __name__=='__main__':main()
