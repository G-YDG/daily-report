#!/usr/bin/env python3
"""
读取或保存 daily-report 技能的配置。
用法:
  python3 config.py get          # 读取配置（不存在则返回空 JSON）
  python3 config.py set --root D:/Develop  # 保存代码主目录
"""
import argparse
import json
import os
import sys

CONFIG_PATH = os.path.join(
    os.path.expanduser('~'), '.claude', 'skills', 'daily-report', 'config.json'
)


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'rb') as f:
            return json.loads(f.read().decode('utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(cfg: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'wb') as f:
        f.write(json.dumps(cfg, ensure_ascii=False, indent=2).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='daily-report 配置管理')
    sub = parser.add_subparsers(dest='action', required=True)

    sub.add_parser('get', help='读取配置')

    set_parser = sub.add_parser('set', help='保存配置')
    set_parser.add_argument('--root', help='代码主目录')
    set_parser.add_argument('--report-dir', help='日报输出目录（默认主目录下的 daily-reports）')

    args = parser.parse_args()

    if args.action == 'get':
        print(json.dumps(load_config(), ensure_ascii=False, indent=2))
    elif args.action == 'set':
        cfg = load_config()
        if args.root:
            if not os.path.isdir(args.root):
                print(json.dumps({'error': f'目录不存在: {args.root}'}, ensure_ascii=False))
                sys.exit(1)
            cfg['root'] = os.path.abspath(args.root)
        if args.report_dir:
            cfg['report_dir'] = os.path.abspath(args.report_dir)
        save_config(cfg)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
